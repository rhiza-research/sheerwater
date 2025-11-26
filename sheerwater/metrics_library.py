"""Library of metrics implementations for verification."""
# flake8: noqa: D102
from abc import ABC, abstractmethod
from inspect import signature

import xarray as xr
import numpy as np
import pandas as pd

from sheerwater.statistics_library import statistic_factory
from sheerwater.utils import get_datasource_fn, get_region_level, get_mask
from sheerwater.climatology import climatology_2020, seeps_wet_threshold, seeps_dry_fraction
from sheerwater.regions_and_masks import region_labels


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
                 mask='lsm', region='global', data_key='none'):
        """Initialize the metric."""
        # Save the configuration kwargs for the metric
        self.start_time = start_time
        self.end_time = end_time
        self.variable = variable
        self.agg_days = agg_days
        self.forecast = forecast
        self.truth = truth
        self.grid = grid
        self.time_grouping = time_grouping
        self.spatial = spatial
        self.mask = mask
        self.region = region

        # Initialize the data dictionary, a place to store all the data needed for the metric calculation.
        # This is a dictionary that contains a data entry and a key entry.
        # data is a dictionary containing any data needed
        # for the metric calculation, such as the forecasts dataframe, the array of bins, etc.
        # key is a string and should uniquely identify the contents of the metric data dictionary,
        # other than the standard cache args.
        self.metric_data = {'key': data_key, 'data': {}}

    def prepare_data(self):
        """Prepare the data for metric calculation, including forecast, observation, and categorical bins."""
        # Get the forecast dataframe
        fcst_fn = get_datasource_fn(self.forecast)
        # TODO: could update with a forecast or truth decorator to handle more consistantly
        if 'prob_type' in signature(fcst_fn).parameters:
            forecast_or_truth = 'forecast'
            fcst = fcst_fn(self.start_time, self.end_time, self.variable, agg_days=self.agg_days,
                           prob_type=self.prob_type, grid=self.grid, mask=None, region='global', memoize=True)
            enhanced_prob_type = fcst.attrs['prob_type']
        else:
            forecast_or_truth = 'truth'
            fcst = fcst_fn(self.start_time, self.end_time, self.variable, agg_days=self.agg_days,
                           grid=self.grid, mask=None, region='global', memoize=True)
            enhanced_prob_type = "deterministic"
        # Make sure the prob type is consistent
        if enhanced_prob_type == 'deterministic' and self.prob_type == 'probabilistic':
            raise ValueError("Cannot run probabilistic metric on deterministic forecasts.")
        elif (enhanced_prob_type == 'ensemble' or enhanced_prob_type == 'quantile') \
                and self.prob_type == 'deterministic':
            raise ValueError("Cannot run deterministic metric on probabilistic forecasts.")

        # Get the truth dataframe
        truth_fn = get_datasource_fn(self.truth)
        obs = truth_fn(self.start_time, self.end_time, self.variable, agg_days=self.agg_days,
                       grid=self.grid, mask=None, region='global', memoize=True)

        # We need a lead specific obs, so we know which times are valid for the forecast
        if forecast_or_truth == 'forecast':
            leads = fcst.prediction_timedelta.values
            obs = obs.expand_dims({'prediction_timedelta': leads})

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

        # Ensure a matching null pattern
        # If the observations are sparse, the forecaster and the obs must be the same length
        # for metrics like ACC to work
        no_null = obs.notnull() & fcst.notnull()
        if self.prob_type == 'probabilistic':
            # Squeeze the member dimension and drop all other coords except lat, lon, time, and lead_time
            no_null = no_null.isel(member=0).drop('member')
        fcst = fcst.where(no_null, np.nan, drop=False)
        obs = obs.where(no_null, np.nan, drop=False)

        # Save the data into the metric data dictionary
        self.metric_data['data']['obs'] = obs
        self.metric_data['data']['fcst'] = fcst
        self.metric_data['data']['prob_type'] = enhanced_prob_type
        self.metric_data['data']['sparse'] = sparse
        if sparse:
            self.metric_data['data']['fcst_orig'] = fcst
        # If the metric is sparse, save a copy of the original forecast for validity checking
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
        self.statistic_values = {}
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

            self.statistic_values[statistic] = ds

    def group_statistics(self) -> dict[str, xr.DataArray]:
        """Group the statistics by the metric's configuration.

        By default, returns the statistic values as is.
        Subclasses can override this for more complex groupings.
        """
        self.grouped_statistics = {}
        region_level, _ = get_region_level(self.region)
        if self.spatial and (region_level == self.region and self.region != 'global'):
            raise ValueError(f"Cannot compute spatial metrics for region level '{self.region}'. " +
                             "Pass in a specific region instead.")
        region_ds = region_labels(grid=self.grid, region_level=region_level, memoize=True)
        mask_ds = get_mask(self.mask, self.grid, memoize=True)

        is_valid = None

        # Iterate through the statistics and compute them
        for i, statistic in enumerate(self.statistics):
            ############################################################
            # Aggregate and and check validity of the statistic
            ############################################################
            ds = self.statistic_values[statistic]

            # Drop any extra random coordinates that shouldn't be there
            for coord in ds.coords:
                if coord not in ['time', 'prediction_timedelta', 'lat', 'lon']:
                    ds = ds.reset_coords(coord, drop=True)

            # Prepare the check_ds for validity checking, considering sparsity
            if i == 0:
                if ds.attrs['sparse']:
                    print("Statistic is sparse, need to check the underlying forecast validity directly.")
                    check_ds = self.metric_data['data']['fcst_orig']
                else:
                    check_ds = ds

                ############################################################
                # Statistic aggregation
                ############################################################
                # Create a non_null indicator and add it to the statistic
                ds['non_null'] = check_ds[self.variable].notnull().astype(float)

            # Group by time
            ds = groupby_time(ds, self.time_grouping, agg_fn='mean')

            if i == 0:
                # For any lat / lon / lead where there is at least one non-null value, reset to one for space validation
                ds['non_null'] = (ds['non_null'] > 0.0).astype(float)
                # Create an indicator variable that is 1 for all dimensions
                ds['indicator'] = xr.ones_like(ds['non_null'])

            # Add the region coordinate to the statistic
            ds = ds.assign_coords(region=region_ds.region)

            # Aggregate in space
            if not self.spatial:
                # Group by region and average in space, while applying weighting for mask
                weights = latitude_weights(ds, lat_dim='lat', lon_dim='lon')
                ds['weights'] = weights * mask_ds.mask

                ds[self.variable] = ds[self.variable] * ds['weights']
                if i == 0:
                    ds['non_null'] = ds['non_null'] * ds['weights']
                    ds['indicator'] = ds['indicator'] * ds['weights']

                if self.region != 'global':
                    ds = ds.groupby('region').apply(mean_or_sum, agg_fn='sum', dims='stacked_lat_lon')
                else:
                    ds = ds.apply(mean_or_sum, agg_fn='sum', dims=['lat', 'lon'])
                ds[self.variable] = ds[self.variable] / ds['weights']

                if i == 0:
                    ds['non_null'] = ds['non_null'] / ds['weights']
                    ds['indicator'] = ds['indicator'] / ds['weights']

                ds = ds.drop_vars(['weights'])
            else:
                # If returning a spatial metric, mask and drop
                # Mask and drop the region coordinate
                ds = ds.where(mask_ds.mask, np.nan, drop=False)
                ds = ds.where((ds.region == self.region).compute(), drop=True)
                ds = ds.drop_vars('region')

            if i == 0:
                # Check if the statistic is valid per grouping
                is_valid = (ds['non_null'] / ds['indicator'] > 0.98)
                ds = ds.where(is_valid, np.nan, drop=False)
                ds = ds.drop_vars(['indicator', 'non_null'])
            elif is_valid is not None:
                ds = ds.where(is_valid, np.nan, drop=False)

            # Assign the final statistic value
            self.grouped_statistics[statistic] = ds

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
        # Apply nonlinearly and return the metric
        return self.compute_metric()


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
                                   grid=self.grid, mask=None, region='global')

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


def mean_or_sum(ds, agg_fn, dims=['lat', 'lon']):
    """A light wrapper around standard groupby aggregation functions."""
    # Note, for some reason:
    # ds.groupby('region').mean(['lat', 'lon'], skipna=True).compute()
    # raises:
    # *** AttributeError: 'bool' object has no attribute 'blockwise'
    # or
    # *** TypeError: reindex_intermediates() missing 1 required positional argument: 'array_type'
    # So we have to do it via apply
    if agg_fn == 'mean':
        return ds.mean(dims, skipna=True)
    else:
        return ds.sum(dims, skipna=True)


def groupby_time(ds, time_grouping, agg_fn='mean'):
    """Aggregate a statistic over time."""
    if time_grouping is not None:
        if time_grouping == 'month_of_year':
            coords = [f'M{x:02d}' for x in ds.time.dt.month.values]
        elif time_grouping == 'year':
            coords = [f'Y{x:04d}' for x in ds.time.dt.year.values]
        elif time_grouping == 'quarter_of_year':
            coords = [f'Q{x:02d}' for x in ds.time.dt.quarter.values]
        elif time_grouping == 'day_of_year':
            coords = [f'D{x:03d}' for x in ds.time.dt.dayofyear.values]
        elif time_grouping == 'month':
            coords = [f'{pd.to_datetime(x).year:04d}-{pd.to_datetime(x).month:02d}-01' for x in ds.time.values]
        else:
            raise ValueError("Invalid time grouping")
        ds = ds.assign_coords(group=("time", coords))
        ds = ds.groupby("group").apply(mean_or_sum, agg_fn=agg_fn, dims='time')
        # Rename the group coordinate to time
        ds = ds.rename({"group": "time"})
    else:
        # Average in time
        if agg_fn == 'mean':
            ds = ds.mean(dim="time")
        elif agg_fn == 'sum':
            ds = ds.sum(dim="time")
        else:
            raise ValueError(f"Invalid aggregation function {agg_fn}")
    return ds


def latitude_weights(ds, lat_dim='lat', lon_dim='lon'):
    """Return latitude weights as an xarray DataArray.

    This function weights each latitude band by the actual cell area,
    which accounts for the fact that grid cells near the poles are smaller
    in area than those near the equator.
    """
    # Calculate latitude cell bounds
    lat_rad = np.deg2rad(ds[lat_dim].values)
    pi_over_2 = np.array([np.pi / 2], dtype=ds[lat_dim].dtype)
    if lat_rad.min() == -pi_over_2 and lat_rad.max() == pi_over_2:
        # Dealing with the full globe
        lower_bound = -pi_over_2
        upper_bound = pi_over_2
    else:
        # Compute the difference in between cells
        diff = np.diff(lat_rad)
        if diff.std() > 0.5:
            raise ValueError(
                "Nonuniform grid! Need to think about spatial averaging more carefully.")
        diff = diff.mean()
        lower_bound = np.array([lat_rad[0] - diff / 2.0], dtype=lat_rad.dtype)
        upper_bound = np.array([lat_rad[-1] + diff / 2.0], dtype=lat_rad.dtype)

    bounds = np.concatenate([lower_bound, (lat_rad[:-1] + lat_rad[1:]) / 2, upper_bound])

    # Calculate cell areas from latitude bounds
    upper = bounds[1:]
    lower = bounds[:-1]
    # normalized cell area: integral from lower to upper of cos(latitude)
    weights = np.sin(upper) - np.sin(lower)

    # Normalize weights
    weights /= np.mean(weights)
    # Return an xarray DataArray with dimensions lat
    weights = xr.DataArray(weights, coords=[ds[lat_dim]], dims=[lat_dim])
    weights = weights.expand_dims({lon_dim: ds[lon_dim]})
    return weights
