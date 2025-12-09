"""Library of metrics implementations for verification."""
# flake8: noqa: D102
from abc import ABC, abstractmethod

import numpy as np
import xarray as xr

from sheerwater.climatology import climatology_2020, seeps_dry_fraction, seeps_wet_threshold
from sheerwater.data.data_decorator import get_data
from sheerwater.forecasts.forecast_decorator import get_forecast
from sheerwater.regions_and_masks import region_labels
from sheerwater.statistics_library import statistic_factory
from sheerwater.utils import get_mask, get_region_level, groupby_time, latitude_weights, clip_region

# Global metric registry dictionary
SHEERWATER_METRIC_REGISTRY = {}


class Metric(ABC):
    """Abstract base class for metrics.

    Based on the implementation in WeatherBenchX, a metric is defined in terms of a nonlinear computation
    involving the mean value of (multiple) statistics per grouping.
    This enables the metric to be computed across all groupings at once in a a single pass, and enables the
    caching and re-use of the statistics across metrics for efficiency.

    Metrics defined here are automatically registered with the metric registry, and can be used by the grouped_metric
    function in the metrics.py file by setting metric equal to the name of the metric class in lower camel case.
    For example, by defining a metric class MAE here, the grouped_metric function in the metrics.py file can be
    called with metric = 'mae'.

    By default, it is assumed that the metric is computed from a single statistic, and the metric will be computed
    as the mean value of the statistic in each grouping. If a metric depends on a nonlinear calculation involving
    multiple statistics, simply define those statistics in a list, e.g.,
        self.statistics = ['squared_fcst_anom', 'squared_obs_anom', 'anom_covariance']
    and the metric will be computed as the mean value of the nonlinear calculation in each grouping.

    Each of the statistics is implemented by the global_statistic function. The metric class
    will be provided with the mean value of each statistic in each grouping at runtime to operate on and return
    one metric value per grouping.
    """
    def __init_subclass__(cls, **kwargs):
        """Automatically register derived Metrics classes with the metric registry."""
        super().__init_subclass__(**kwargs)
        # Register this metric class with the registry
        cls.name = cls.__name__.lower()
        SHEERWATER_METRIC_REGISTRY[cls.name] = cls

    def __init__(self, start_time, end_time, variable, agg_days, forecast, truth,
                 time_grouping=None, spatial=False, grid="global1_5",
                 mask='lsm', space_grouping='country', region='global', data_key='none'):
        """Initialize the metric."""
        # Save the configuration kwargs for the metric
        self.start_time = start_time
        self.end_time = end_time
        self.variable = variable
        self.agg_days = agg_days
        self.forecast = forecast
        self.truth = truth
        self.grid = grid
        self.spatial = spatial
        self.mask = mask
        self.region = region
        self.time_grouping = time_grouping if time_grouping != 'None' else None
        self.space_grouping = space_grouping if space_grouping != 'None' else None

        # Initialize the data dictionary, a place to store all the data needed for the metric calculation.
        # This is a dictionary that contains a data entry and a key entry.
        # data is a dictionary containing any data needed
        # for the metric calculation, such as the forecasts dataframe, the array of bins, etc.
        # key is a string and should uniquely identify the contents of the metric data dictionary,
        # other than the standard cache args.
        self.metric_data = {'key': data_key, 'data': {}}

    def prepare_data(self):
        """Prepare the data for metric calculation, including forecast, observation, and categorical bins."""
        # Arguments for calling the data and forecast functions.
        kwargs = {'start_time': self.start_time, 'end_time': self.end_time,
                  'variable': self.variable, 'agg_days': self.agg_days,
                  'grid': self.grid, 'mask': None, 'region': self.region}

        """
        1. Fetch the data to be evaluated. This can either be a forecast or a dataset.
        For example, to evaluate ECMWF vs IMERG, we make fcst ECMWF and obs IMERG.
                     to evaluate IMERG vs GHNC stations, we make fcst IMERG and obs GHNC stations.
        """
        try:
            # Try to get the forecast from the forecast registry
            fcst_fn = get_forecast(self.forecast)
            try:
                fcst = fcst_fn(**kwargs, prob_type=self.prob_type, memoize=True)
            except TypeError:
                # If the forecast is not a cacheable function the memoize kwarg will throw an error
                fcst = fcst_fn(**kwargs, prob_type=self.prob_type)
            enhanced_prob_type = fcst.attrs['prob_type']
            forecast_or_truth = 'forecast'
        except KeyError:
            data_fn = get_data(self.forecast)
            try:
                fcst = data_fn(**kwargs, memoize=True)
            except TypeError:
                # If the data is not a cacheable function the memoize kwarg will throw an error
                fcst = data_fn(**kwargs)
            enhanced_prob_type = "deterministic"
            forecast_or_truth = 'truth'

        # Make sure the prob type is consistent
        if enhanced_prob_type == 'deterministic' and self.prob_type == 'probabilistic':
            raise ValueError("Cannot run probabilistic metric on deterministic forecasts.")
        elif (enhanced_prob_type == 'ensemble' or enhanced_prob_type == 'quantile') \
                and self.prob_type == 'deterministic':
            raise ValueError("Cannot run deterministic metric on probabilistic forecasts.")

        """2. Fetch the truth data. This must be a dataset, often either a gridded truth or station."""
        # Get the truth dataframe
        truth_fn = get_data(self.truth)
        try:
            obs = truth_fn(**kwargs, memoize=True)
        except TypeError:
            # If the truth is not a cacheable function the memoize kwarg will throw an error
            obs = truth_fn(**kwargs)
        # We need a lead specific obs, so we know which times are valid for the forecast
        if forecast_or_truth == 'forecast':
            leads = fcst.prediction_timedelta.values
            obs = obs.expand_dims({'prediction_timedelta': leads})

        """3. Ensure that the forecast and truth have the same times and null patterns."""
        sparse = False  # A variable used to indicate whether the metricis expected to be sparse
        # Assign sparsity if it exists
        if 'sparse' in fcst.attrs:
            sparse = fcst.attrs['sparse']
        # Assign sparsity if it exists
        if 'sparse' in obs.attrs:
            sparse |= obs.attrs['sparse']

        # Drop all times not in fcst
        valid_times = set(obs.time.values).intersection(set(fcst.time.values))
        valid_times = list(valid_times)
        valid_times.sort()

        # Cast the longitude and latitude coordinates to floats with precision 4
        # This fixs a bug where the long and lat don't match deep in their floating point precision
        # TODO: this is mysterious, and I feel like we've fixed this before ...
        obs['lon'] = obs['lon'].astype(np.float32).round(4)
        obs['lat'] = obs['lat'].astype(np.float32).round(4)
        fcst['lon'] = fcst['lon'].astype(np.float32).round(4)
        fcst['lat'] = fcst['lat'].astype(np.float32).round(4)

        obs = obs.sel(time=valid_times)
        fcst = fcst.sel(time=valid_times)

        # To ensure chunks align for nullification, place all of time in one single chunk
        # TODO: make sure chunks are reasonable for differnt time stretches
        obs = obs.chunk({'time': -1, 'lat': 100, 'lon': 100})
        fcst = fcst.chunk({'time': -1, 'lat': 100, 'lon': 100})

        # Ensure a matching null pattern
        # If the observations are sparse, the forecaster and the obs must be the same length
        # for metrics like ACC to work
        no_null = obs.notnull() & fcst.notnull()
        if self.prob_type == 'probabilistic':
            # Squeeze the member dimension and drop all other coords except lat, lon, time, and lead_time
            no_null = no_null.isel(member=0).drop('member')
        fcst = fcst.where(no_null, np.nan, drop=False)
        obs = obs.where(no_null, np.nan, drop=False)

        """4. Save the data for all downstream metric calculations."""
        # Save the data into the metric data dictionary
        self.metric_data['data']['obs'] = obs
        self.metric_data['data']['fcst'] = fcst
        self.metric_data['data']['prob_type'] = enhanced_prob_type

        # Save the pattern of valid and non-null times, needed for derived metrics like ACC to
        # properly compute the climatology
        self.metric_data['data']['no_null'] = no_null
        self.metric_data['data']['valid_times'] = valid_times

        # If categorical, populate the data with the bin information
        if self.categorical:
            if self.metric_data['key'] == 'none':
                raise ValueError("A categorical metric must have a key that specifies the bins.")
            # Get the bins
            bins = [-np.inf] + [float(x) for x in self.metric_data['key'].split('-')] + [np.inf]
            if len(bins) > 10:
                raise ValueError("Categorical metrics can only have up to 10 bins.")
            self.metric_data['data']['bins'] = bins

    @property
    @abstractmethod
    def sparse(self) -> bool:
        """Whether the metric induces NaNs."""
        pass

    @property
    @abstractmethod
    def prob_type(self) -> str:
        """Either 'deterministic' or 'probabilistic'."""
        pass

    @property
    @abstractmethod
    def valid_variables(self) -> list[str]:
        """What variables is the metric valid for?"""
        pass

    @property
    @abstractmethod
    def categorical(self) -> bool:
        """Is the metric categorical?"""
        pass

    @property
    def statistics(self) -> list[str]:
        """List of statistics that the metric is computed from."""
        pass

    def gather_statistics(self) -> dict[str, xr.DataArray]:
        """Gather the statistics by the metric's configuration.

        By default, returns the statistic values as is.
        Subclasses can override this for more complex groupings.
        """
        self.statistic_values = None
        for statistic in self.statistics:
            # Get the statistic function from the registry
            stat_fn = statistic_factory(statistic)

            # Call the statistic function
            ds = stat_fn(data=self.metric_data['data'],
                         start_time=self.start_time,
                         end_time=self.end_time,
                         variable=self.variable,
                         agg_days=self.agg_days,
                         forecast=self.forecast,
                         truth=self.truth,
                         data_key=self.metric_data['key'],
                         grid=self.grid)

            if ds is None:
                # If any statistic is None, return None
                self.statistic_values = None
                return

            if self.statistic_values is None:
                self.statistic_values = ds.rename({self.variable: statistic})
            else:
                self.statistic_values[statistic] = ds[self.variable]

    def group_statistics(self) -> dict[str, xr.DataArray]:
        """Group the statistics by the metric's configuration.

        By default, returns the statistic values as is.
        Subclasses can override this for more complex groupings.
        """
        region_level, _ = get_region_level(self.space_grouping)
        region_ds = region_labels(grid=self.grid, space_grouping=region_level,
                                  region=self.region, memoize=True).compute()
        mask_ds = get_mask(self.mask, self.grid, memoize=True)
        if self.region != 'global':
            mask_ds = clip_region(mask_ds, region=self.region)

        ############################################################
        # Aggregate and and check validity of the statistic
        ############################################################
        ds = self.statistic_values

        # Drop any extra random coordinates that shouldn't be there
        for coord in ds.coords:
            if coord not in ['time', 'prediction_timedelta', 'lat', 'lon']:
                ds = ds.reset_coords(coord, drop=True)

        ############################################################
        # Statistic aggregation
        ############################################################
        # Create a non_null indicator and add it to the statistic
        # Group by time
        ds = groupby_time(ds, self.time_grouping, agg_fn='mean')

        # Put evertyhing on the same chunk before spatial aggregation
        ds = ds.chunk({dim: -1 for dim in ds.dims})

        # Add the region coordinate to the statistic
        ds = ds.assign_coords(region=region_ds.region)

        # Aggregate in space
        if not self.spatial:
            # Group by region and average in space, while applying weighting for mask
            weights = latitude_weights(ds, lat_dim='lat', lon_dim='lon')
            # Expand weights to have a time dimension that matches ds
            if 'time' in ds.dims:  # Enable a time specific null pattern per time
                weights = weights.expand_dims(time=ds.time)
            weights = weights.chunk({dim: -1 for dim in weights.dims})
            # Ensure the weights null pattern matches the ds null pattern
            weights = weights.where(ds[self.statistics[0]].notnull(), np.nan, drop=False)

            # Mulitply by weights
            weights = weights * mask_ds.mask
            ds['weights'] = weights
            for stat in self.statistics:
                ds[stat] = ds[stat] * ds['weights']

            if region_level == 'global':
                ds = ds.sum(dim=['lat', 'lon'], skipna=True)
            else:
                ds = ds.groupby('region').sum(dim=['lat', 'lon'], skipna=True)

            for stat in self.statistics:
                ds[stat] = ds[stat] / ds['weights']
            ds = ds.drop_vars(['weights'])
        else:
            # If returning a spatial metric, mask and drop
            ds = ds.where(mask_ds.mask, np.nan, drop=False)
            ds = ds.where((ds.region == self.region).compute(), drop=True)
            ds = ds.drop_vars('region')

        # Assign the final statistic value
        self.grouped_statistics = ds

    def compute_metric(self) -> xr.DataArray:
        """Compute the metric from the statistics.

        By default, returns the single statistic value.
        Subclasses can override this for more complex computations.
        """
        if len(self.statistics) != 1:
            raise ValueError("Metric must have exactly one statistic to use default compute.")
        return self.grouped_statistics[self.statistics[0]]

    def compute(self) -> xr.DataArray:
        # Check that the variable is valid for the metric
        if self.valid_variables and self.variable not in self.valid_variables:
            raise ValueError(f"Variable {self.variable} is not valid for metric {self.name}")

        # Prepare the forecasting, observation, and auxiliary data for the metric
        self.prepare_data()
        # Gather the statistics
        self.gather_statistics()
        # Group and mean the statistics
        self.group_statistics()
        # Apply nonlinearly and compute the metric
        da = self.compute_metric()

        # Convert from dataarray to dataset and return.
        ds = da.to_dataset(name=self.name)
        return ds


class MAE(Metric):
    """Mean Absolute Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    categorical = False
    statistics = ['mae']


class MSE(Metric):
    """Mean Squared Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    categorical = False
    statistics = ['mse']


class RMSE(Metric):
    """Root Mean Squared Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    categorical = False
    statistics = ['mse']

    def compute_metric(self):
        return self.grouped_statistics['mse'] ** 0.5


class Bias(Metric):
    """Bias metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    categorical = False
    statistics = ['bias']


class CRPS(Metric):
    """Continuous Ranked Probability Score metric."""
    sparse = False
    prob_type = 'probabilistic'
    valid_variables = None  # all variables are valid
    categorical = False
    statistics = ['crps']


class Brier(Metric):
    """Brier score metric."""
    sparse = False
    prob_type = 'probabilistic'
    valid_variables = ['precip']
    categorical = True
    statistics = ['brier']


class SMAPE(Metric):
    """Symmetric Mean Absolute Percentage Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = False
    statistics = ['smape']


class MAPE(Metric):
    """Mean Absolute Percentage Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = False
    statistics = ['mape']


class SEEPS(Metric):
    """Spatial Error in Ensemble Prediction Scale metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = False
    statistics = ['seeps']

    def prepare_data(self):
        """Prepare specific data for the SEEPS metric."""
        # Call the parent prepare_data method to get the forecast and observation
        super().prepare_data()

        first_year = 1991
        last_year = 2020
        # Get the wet threshold and dry fraction
        self.metric_data['data']['wet_threshold'] = seeps_wet_threshold(
            first_year=first_year, last_year=last_year, agg_days=self.agg_days, grid=self.grid)
        self.metric_data['data']['dry_fraction'] = seeps_dry_fraction(
            first_year=first_year, last_year=last_year, agg_days=self.agg_days, grid=self.grid)

        # Update the metric data key to include the wet threshold and dry fraction year range
        self.metric_data['key'] = f'{self.metric_data["key"]}-{first_year}-{last_year}'


class ACC(Metric):
    """ACC (Anomaly Correlation Coefficient) metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None
    categorical = False
    statistics = ['squared_fcst_anom', 'squared_obs_anom', 'anom_covariance']

    def prepare_data(self):
        """Prepare specific data for the ACC metric."""
        # Call the parent prepare_data method to get the forecast and observation
        super().prepare_data()

        # Get the appropriate climatology dataframe for metric calculation
        clim_ds = climatology_2020(self.start_time, self.end_time, self.variable, agg_days=self.agg_days,
                                   prob_type='deterministic',
                                   grid=self.grid, mask=None, region=self.region)

        # Expand climatology to the same lead times as the forecast
        if 'prediction_timedelta' in self.metric_data['data']['fcst'].dims:
            leads = self.metric_data['data']['fcst'].prediction_timedelta.values
            # Remove the prediction_timedelta coordinate
            clim_ds = clim_ds.squeeze('prediction_timedelta')
            # Add in a matching prediction_timedelta coordinate
            clim_ds = clim_ds.expand_dims({'prediction_timedelta': leads})

        # Subset the climatology to the valid times and non-null times of the forecaster
        clim_ds = clim_ds.sel(time=self.metric_data['data']['valid_times'])
        clim_ds = clim_ds.where(self.metric_data['data']['no_null'], np.nan, drop=False)
        # Add the climatology to the metric data
        self.metric_data['data']['climatology'] = clim_ds
        # Update the metric data key to include the climatology year range
        self.metric_data['key'] = f'{self.metric_data["key"]}-1990-2019'

    def compute_metric(self):
        gs = self.grouped_statistics
        fcst_norm = np.sqrt(gs['squared_fcst_anom'])
        gt_norm = np.sqrt(gs['squared_obs_anom'])
        dot = gs['anom_covariance']
        ds = (dot / (fcst_norm * gt_norm))
        return ds


class Pearson(Metric):
    """Pearson's correlation coefficient metric.

    Implemented with a rewrite of the standard formula to enable grouping first.

    The standard formula is:
    r = sum((x - E(x)) * (y - E(y))) / sqrt(sum(x - E(x))^2 * sum(y - E(y))^2)

    This can be rewritten as:
    r = (covariance - fcst_mean * obs_mean) / (sqrt(squared_fcst - fcst_mean^2) * sqrt(squared_obs - obs_mean^2))
    """
    sparse = False
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = False
    statistics = ['fcst', 'obs', 'squared_fcst', 'squared_obs', 'covariance']

    def compute_metric(self):
        gs = self.grouped_statistics
        numerator = gs['covariance'] - gs['fcst'] * gs['obs']
        denominator = (gs['squared_fcst'] - gs['fcst']**2) ** 0.5 * (gs['squared_obs'] - gs['obs']**2) ** 0.5
        return numerator / denominator


class Heidke(Metric):
    """Heidke Skill Score metric for streaming data."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = True

    @property
    def statistics(self):
        stats = ['n_correct', 'n_valid']
        stats += [f'n_fcst_bin_{i}' for i in range(1, len(self.metric_data['data']['bins']))]
        stats += [f'n_obs_bin_{i}' for i in range(1, len(self.metric_data['data']['bins']))]
        return stats

    def compute_metric(self):
        gs = self.grouped_statistics
        prop_correct = gs['n_correct'] / gs['n_valid']
        n2 = gs['n_valid']**2
        right_by_chance = xr.zeros_like(gs['n_correct'])
        for i in range(1, len(self.metric_data['data']['bins'])):
            right_by_chance += (gs[f'n_fcst_bin_{i}'] * gs[f'n_obs_bin_{i}']) / n2

        return (prop_correct - right_by_chance) / (1 - right_by_chance)


class POD(Metric):
    """Probability of Detection metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = True
    statistics = ['true_positives', 'false_negatives']

    def compute_metric(self):
        tp = self.grouped_statistics['true_positives']
        fn = self.grouped_statistics['false_negatives']
        return tp / (tp + fn)


class FAR(Metric):
    """False Alarm Rate metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = True
    statistics = ['false_positives', 'true_negatives']

    def compute_metric(self):
        fp = self.grouped_statistics['false_positives']
        tn = self.grouped_statistics['true_negatives']
        return fp / (fp + tn)


class ETS(Metric):
    """Equitable Threat Score metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = True
    statistics = ['true_positives', 'false_positives', 'false_negatives', 'true_negatives']

    def compute_metric(self):
        gs = self.grouped_statistics
        tp = gs['true_positives']
        fp = gs['false_positives']
        fn = gs['false_negatives']
        tn = gs['true_negatives']
        chance = ((tp + fp) * (tp + fn)) / (tp + fp + fn + tn)
        return (tp - chance) / (tp + fp + fn - chance)


class CSI(Metric):
    """Critical Success Index metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = True
    statistics = ['true_positives', 'false_positives', 'false_negatives']

    def compute_metric(self):
        tp = self.grouped_statistics['true_positives']
        fp = self.grouped_statistics['false_positives']
        fn = self.grouped_statistics['false_negatives']
        return tp / (tp + fp + fn)


class FrequencyBias(Metric):
    """Frequency Bias metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    categorical = True
    statistics = ['true_positives', 'false_positives', 'false_negatives']

    def compute_metric(self):
        tp = self.grouped_statistics['true_positives']
        fp = self.grouped_statistics['false_positives']
        fn = self.grouped_statistics['false_negatives']
        return (tp + fp) / (tp + fn)


def metric_factory(metric_name: str, **init_kwargs) -> Metric:
    """Get a metric class by name from the registry."""
    try:
        # Convert
        if '-' in metric_name:
            mn = metric_name.split('-')[0]  # support for categorical metric names of the form 'metric-datakey...'
            data_key = metric_name[metric_name.find('-')+1:]
        else:
            mn = metric_name
            data_key = 'none'
        metric = SHEERWATER_METRIC_REGISTRY[mn.lower()]
        # Add runtime metric configuration to the metric class
        return metric(data_key=data_key, **init_kwargs)

    except KeyError:
        raise ValueError(f"Unknown metric: {metric_name}. Available metrics: {list_metrics()}")


def list_metrics():
    """List all available metrics in the registry."""
    return list(SHEERWATER_METRIC_REGISTRY.keys())
