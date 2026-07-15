"""Library of metrics implementations for verification."""
# flake8: noqa: D102
from abc import ABC, abstractmethod

import numpy as np
import xarray as xr


from sheerwater.climatology import climatology, seeps_dry_fraction, seeps_wet_threshold
from sheerwater.interfaces import get_data, get_forecast, get_event_fn
from sheerwater.masks import spatial_mask
from sheerwater.statistics_library import statistic_factory
from sheerwater.utils import groupby_time, latitude_weights
from sheerwater.spatial_subdivisions import space_grouping_labels, clip_region

from .advanced_metrics import get_experiment_kwargs

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
                 metric_kwargs=None,
                 event=None, event_kwargs=None,
                 filter_event=None, filter_event_kwargs=None,
                 time_grouping=None, spatial=False, grid="global1_5",
                 mask='lsm', space_grouping='country', region='global',
                 memoize_forecast=True, memoize_truth=True):
        """Initialize the metric."""
        # Save the configuration kwargs for the metric
        self.metric_kwargs = {} if metric_kwargs is None else metric_kwargs
        self.metric_data = {}  # dictionary to store the data for the metric calculation
        self.densify = self.metric_kwargs.get('densify', False)

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
        self.memoize_forecast = memoize_forecast
        self.memoize_truth = memoize_truth

        # Initialize the event kwargs for the metric and filter and check validity.
        self.init_event_kwargs(event, event_kwargs,
                               metric_kwargs.get('pre_filter_event', None),
                               metric_kwargs.get('pre_filter_event_kwargs', None),
                               filter_event, filter_event_kwargs)

    def init_event_kwargs(self,
                          event, event_kwargs,
                          pre_filter_event, pre_filter_event_kwargs,
                          filter_event, filter_event_kwargs):
        """Initialize the event kwargs for the metric and filter and check validity.

        For both event_kwargs and filter_event_kwargs, the kwargs can be passed in one of two formats:
            1. As a dictionary of kwrags, which will be used for both fcst and obs
            2. As a dictionary of fcst kwargs and a dictionary of obs kwargs, which will be used respectively
            For example, to pass different thresholds for fcst and obs, you can pass:
                event_kwargs = {'fcst': {'threshold': 1.0}, 'obs': {'threshold': 2.0}}
                filter_event_kwargs = {'fcst': {'threshold': 1.0}, 'obs': {'threshold': 2.0}}
            or
                event_kwargs = {'threshold': 1.0}
                filter_event_kwargs = {'threshold': 1.0}
            The latter will be used for both fcst and obs.
        """
        self.event = event
        self.event_kwargs = event_kwargs

        self.filter_event = filter_event
        self.filter_event_kwargs = filter_event_kwargs

        self.pre_filter_event = pre_filter_event
        self.pre_filter_event_kwargs = pre_filter_event_kwargs

        # Check the validity of the pre-filter function
        event_fn = get_event_fn(pre_filter_event)
        if pre_filter_event and not event_fn.filter:
            raise ValueError(
                f"Can only run filtering with events of type filter. Event {pre_filter_event} is not a boolean event.")

        # Check the validity of the filter function
        event_fn = get_event_fn(filter_event)
        if filter_event and not event_fn.filter:
            raise ValueError(
                f"Can only run filtering with events of type filter. Event {filter_event} is not a boolean event.")

        self.do_forecast_filter = filter_event is not None and self.metric_kwargs.get('forecast_filter', False)
        self.do_obs_filter = filter_event is not None and self.metric_kwargs.get('obs_filter', False)
        self.do_pre_filter = pre_filter_event is not None and self.metric_kwargs.get('pre_filter', False)

        if event_kwargs and ('fcst' in event_kwargs or 'obs' in event_kwargs):
            if not ('fcst' in event_kwargs and 'obs' in event_kwargs):
                raise ValueError("Event kwargs must contain both fcst and obs keys if one is present.")
            self.event_kwargs_fcst = event_kwargs['fcst'] if event_kwargs['fcst'] is not None else {}
            self.event_kwargs_obs = event_kwargs['obs'] if event_kwargs['obs'] is not None else {}
        else:
            self.event_kwargs_fcst = event_kwargs if event_kwargs is not None else {}
            self.event_kwargs_obs = event_kwargs if event_kwargs is not None else {}

        if filter_event_kwargs and ('fcst' in filter_event_kwargs or 'obs' in filter_event_kwargs):
            if not ('fcst' in filter_event_kwargs and 'obs' in filter_event_kwargs):
                raise ValueError("Filter event kwargs must contain both fcst and obs keys if one is present.")
            self.filter_event_kwargs_fcst = filter_event_kwargs['fcst'] \
                if filter_event_kwargs['fcst'] is not None else {}
            self.filter_event_kwargs_obs = filter_event_kwargs['obs'] \
                if filter_event_kwargs['obs'] is not None else {}
        else:
            self.filter_event_kwargs_fcst = filter_event_kwargs if filter_event_kwargs is not None else {}
            self.filter_event_kwargs_obs = filter_event_kwargs if filter_event_kwargs is not None else {}

    def prepare_data(self):
        """Prepare the data for metric calculation, including forecast, observation, and event processing."""
        # Arguments for calling the data and forecast functions.
        # TODO: we don't want to always be calling an event
        self.event = self.event if self.event is not None else self.default_event
        self.fcst_obs_kwargs = {'start_time': self.start_time, 'end_time': self.end_time,
                                'variable': self.variable, 'agg_days': self.agg_days,
                                'grid': self.grid, 'mask': self.mask, 'region': self.region}

        """
        1. Fetch the data to be evaluated. This can either be a forecast or a dataset.
        For example, to evaluate ECMWF vs IMERG, we make fcst ECMWF and obs IMERG.
                     to evaluate IMERG vs GHNC stations, we make fcst IMERG and obs GHNC stations.
        """
        try:
            # Try to get the forecast from the forecast registry
            fcst_fn = get_forecast(self.forecast)
            try:
                # Pass lookback separaetly b/c it is not a cachable argument for the data function
                fcst = fcst_fn(**self.fcst_obs_kwargs,
                               event=self.event, event_kwargs=self.event_kwargs_fcst,
                               lookback_source=self.truth, densify=self.densify,
                               prob_type=self.prob_type, memoize=self.memoize_forecast)
                if self.do_forecast_filter:
                    filter_fcst = fcst_fn(**self.fcst_obs_kwargs,
                                          event=self.filter_event, event_kwargs=self.filter_event_kwargs_fcst,
                                          lookback_source=self.truth, densify=self.densify,
                                          prob_type=self.prob_type, memoize=self.memoize_forecast, cache=True)  # noqa: E501
            except TypeError:
                # If the forecast is not a cacheable function the memoize kwarg will throw an error
                fcst = fcst_fn(**self.fcst_obs_kwargs,
                               event=self.event, event_kwargs=self.event_kwargs_fcst,
                               lookback_source=self.truth, densify=self.densify, prob_type=self.prob_type)
                if self.do_forecast_filter:
                    filter_fcst = fcst_fn(**self.fcst_obs_kwargs,
                                          event=self.filter_event, event_kwargs=self.filter_event_kwargs_fcst,
                                          lookback_source=self.truth, densify=self.densify, prob_type=self.prob_type)
            enhanced_prob_type = fcst.attrs['prob_type']
            forecast_or_truth = 'forecast'
        except KeyError:
            data_fn = get_data(self.forecast)
            try:
                fcst = data_fn(**self.fcst_obs_kwargs,
                               event=self.event, event_kwargs=self.event_kwargs_fcst, memoize=self.memoize_forecast)
                if self.do_forecast_filter:
                    filter_fcst = data_fn(**self.fcst_obs_kwargs,
                                          event=self.filter_event, event_kwargs=self.filter_event_kwargs_fcst,
                                          memoize=self.memoize_forecast, cache=True)  # noqa: E501
            except TypeError:
                # If the data is not a cacheable function the memoize kwarg will throw an error
                fcst = data_fn(**self.fcst_obs_kwargs,
                               event=self.event, event_kwargs=self.event_kwargs_fcst)
                if self.do_forecast_filter:
                    filter_fcst = data_fn(**self.fcst_obs_kwargs,
                                          event=self.filter_event, event_kwargs=self.filter_event_kwargs_fcst)
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
            obs = truth_fn(**self.fcst_obs_kwargs,
                           event=self.event, event_kwargs=self.event_kwargs_obs,
                           memoize=self.memoize_truth)
            if self.do_obs_filter:
                filter_obs = truth_fn(**self.fcst_obs_kwargs,
                                      event=self.filter_event, event_kwargs=self.filter_event_kwargs_obs,
                                      memoize=self.memoize_truth, cache=True)  # noqa: E501
            if self.do_pre_filter:
                pre_filter_obs = truth_fn(**self.fcst_obs_kwargs,
                                      event=self.pre_filter_event, event_kwargs=self.pre_filter_event_kwargs,
                                      memoize=self.memoize_truth, cache=True)  # noqa: E501
        except TypeError:
            # If the truth is not a cacheable function the memoize kwarg will throw an error
            obs = truth_fn(**self.fcst_obs_kwargs,
                           event=self.event, event_kwargs=self.event_kwargs_obs)
            if self.do_obs_filter:
                filter_obs = truth_fn(**self.fcst_obs_kwargs,
                                      event=self.filter_event, event_kwargs=self.filter_event_kwargs_obs)
            if self.do_pre_filter:
                pre_filter_obs = truth_fn(**self.fcst_obs_kwargs,
                                      event=self.pre_filter_event, event_kwargs=self.pre_filter_event_kwargs)
        # We need a lead specific obs, so we know which times are valid for the forecast
        if forecast_or_truth == 'forecast':
            leads = fcst.prediction_timedelta.values
            obs = obs.expand_dims({'prediction_timedelta': leads})
            if self.do_obs_filter:
                filter_obs = filter_obs.expand_dims({'prediction_timedelta': leads})

        # Select the variable of interest
        obs = obs[[self.variable]]
        fcst = fcst[[self.variable]]
        # Our filters are 0, 1, np.nan int type, so we must first fill with zeros before
        # converting to booleans, otherwise np.nans will be treated as True.
        if self.do_pre_filter:
            pre_filter_obs = pre_filter_obs[[self.variable]].fillna(0).astype(bool)
        if self.do_obs_filter:
            filter_obs = filter_obs[[self.variable]].fillna(0).astype(bool)
        if self.do_forecast_filter:
            filter_fcst = filter_fcst[[self.variable]].fillna(0).astype(bool)

        """3. Ensure that the forecast and truth have the same times and null patterns."""
        sparse = False  # A variable used to indicate whether the metricis expected to be sparse
        # Assign sparsity if it exists
        if 'sparse' in fcst.attrs:
            sparse = fcst.attrs['sparse']
        # Assign sparsity if it exists
        if 'sparse' in obs.attrs:
            sparse |= obs.attrs['sparse']

        """ Filter data."""
        # Everthing will be a daily timeseries at this point, so it will not introduce gaps, just
        # Ensure that we're covering latest start time to the earliest end time of the data
        valid_times = set(obs.time.values).intersection(set(fcst.time.values))
        if self.do_pre_filter:
            valid_times = valid_times.intersection(set(pre_filter_obs.time.values))
        if self.do_obs_filter:
            valid_times = valid_times.intersection(set(filter_obs.time.values))
        if self.do_forecast_filter:
            valid_times = valid_times.intersection(set(filter_fcst.time.values))
        valid_times = list(valid_times)
        valid_times.sort()

        # Cast the longitude and latitude coordinates to floats with precision 4
        # This fixes a bug where the lon and lat don't match deep in their floating point precision
        # and this shows up as errors in the join
        datasets = [obs, fcst]
        if self.do_pre_filter:
            datasets.append(pre_filter_obs)
        if self.do_obs_filter:
            datasets.append(filter_obs)
        if self.do_forecast_filter:
            datasets.append(filter_fcst)
        for dfs in datasets:
            dfs['lon'] = dfs['lon'].astype(np.float32).round(4)
            dfs['lat'] = dfs['lat'].astype(np.float32).round(4)

        # To ensure chunks align for nullification, place all of time in one single chunk
        # TODO: make sure chunks are reasonable for differnt time stretches
        for dfs in datasets:
            dfs = dfs.chunk({'time': -1, 'lat': 100, 'lon': 100})

        # Select forecast and obs on their valid times
        obs = obs.sel(time=valid_times)
        fcst = fcst.sel(time=valid_times)
        if self.do_pre_filter:
            pre_filter_obs = pre_filter_obs.sel(time=valid_times)
        if self.do_obs_filter:
            filter_obs = filter_obs.sel(time=valid_times)
        if self.do_forecast_filter:
            filter_fcst = filter_fcst.sel(time=valid_times)

        """5. Save the data for all downstream metric calculations."""
        # Save the data into the metric data dictionary
        self.metric_data['obs'] = obs
        self.metric_data['fcst'] = fcst
        if self.do_forecast_filter:
            self.metric_data['filter_fcst'] = filter_fcst
        if self.do_obs_filter:
            self.metric_data['filter_obs'] = filter_obs
        if self.do_pre_filter:
            self.metric_data['pre_filter_obs'] = pre_filter_obs
        self.metric_data['prob_type'] = enhanced_prob_type

        # Save the pattern of valid and non-null times, needed for derived metrics like ACC to
        # properly compute the climatology
        self.metric_data['valid_times'] = valid_times

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
    def default_event(self) -> str:
        """Default event processing for the metric?"""
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
        # Seed no_null with the joint validity of fcst and obs so that the original
        # null pattern is honored even when statistics (e.g. boolean comparisons in
        # contingency metrics) don't propagate NaN through their outputs.
        no_null = self.metric_data['fcst'].notnull() & self.metric_data['obs'].notnull()
        for statistic in self.statistics:
            # Get the statistic function from the registry
            stat_fn = statistic_factory(statistic)

            # Call the statistic function
            # Must be called with all of the event / filter preprocessing that has been done so far.
            ds = stat_fn(data=self.metric_data,
                         metric_kwargs=self.metric_kwargs,
                         event=self.event,
                         event_kwargs=self.event_kwargs,
                         filter_event=self.filter_event,
                         filter_event_kwargs=self.filter_event_kwargs,
                         start_time=self.start_time,
                         end_time=self.end_time,
                         variable=self.variable,
                         agg_days=self.agg_days,
                         forecast=self.forecast,
                         truth=self.truth,
                         grid=self.grid)

            if ds is None:
                # If any statistic is None, return None
                self.statistic_values = None
                return

            if self.statistic_values is None:
                self.statistic_values = ds.rename({self.variable: statistic})
            else:
                self.statistic_values[statistic] = ds[self.variable]

            # Update the no null array
            # If a statistic has added any nulls, we update the nonull array to include them here.
            # So, if for example, SEEPS has nulled out cells, no_null will be updated to exclude those cells.
            no_null = no_null & ds.notnull()

        # Ensure a matching null pattern
        # If the observations are sparse, the forecaster and the obs must be the same length
        # for metrics like ACC to work
        if self.prob_type == 'probabilistic':
            # Squeeze the member dimension and drop all other coords except lat, lon, time, and lead_time
            no_null = no_null.isel(member=0).drop('member')
            if self.do_forecast_filter:
                self.metric_data['filter_fcst'] = self.metric_data['filter_fcst'].sel(member=0).drop('member')
            if self.do_obs_filter:
                self.metric_data['filter_obs'] = self.metric_data['filter_obs'].sel(member=0).drop('member')
            if self.do_pre_filter:
                self.metric_data['pre_filter_obs'] = self.metric_data['pre_filter_obs'].sel(member=0).drop('member')

        # Do event filtering
        filter = no_null  # baseline no nulls
        if self.do_pre_filter:
            filter = filter & self.metric_data['pre_filter_obs']  # add in pre-filter
        if self.do_forecast_filter and self.do_obs_filter:
            filter = filter & (self.metric_data['filter_fcst'] | self.metric_data['filter_obs'])
        elif self.do_forecast_filter:
            filter = filter & self.metric_data['filter_fcst']
        elif self.do_obs_filter:
            filter = filter & self.metric_data['filter_obs']

        # Apply the filter to each statistic
        for stat in self.statistics:
            stat_vals = self.statistic_values[stat]
            # The filter and the data may have different leads - select their common set if there are both
            #  TODO: this should be the same for all statistics, so maybe could save by running only once
            if 'prediction_timedelta' in stat_vals.coords and 'prediction_timedelta' in filter.coords:
                common = np.intersect1d(stat_vals.prediction_timedelta.values, filter.prediction_timedelta.values)
                stat_vals = stat_vals.sel(prediction_timedelta=common)
                filt = filter.sel(prediction_timedelta=common)
            else:
                filt = filter
            self.statistic_values[stat] = stat_vals.where(filt[self.variable], np.nan, drop=False)

    def group_statistics(self) -> dict[str, xr.DataArray]:
        """Group the statistics by the metric's configuration.

        By default, returns the statistic values as is.
        Subclasses can override this for more complex groupings.
        """
        ############################################################
        # 1. Fetch the region and mask data
        ############################################################
        space_grouping_ds = space_grouping_labels(grid=self.grid, space_grouping=self.space_grouping)
        mask_ds = spatial_mask(self.mask, self.grid, memoize=True)

        space_grouping_ds = clip_region(space_grouping_ds, grid=self.grid, region=self.region)
        mask_ds = clip_region(mask_ds, grid=self.grid, region=self.region)

        ############################################################
        # 2. Aggregate in time
        ############################################################
        ds = self.statistic_values  # ds will already be clipped to the region and masked

        # Drop any extra random coordinates that shouldn't be there
        for coord in ds.coords:
            if coord not in ['time', 'prediction_timedelta', 'lat', 'lon']:
                ds = ds.reset_coords(coord, drop=True)

        # Create a non_null indicator and add it to the statistic
        # Group by time
        ds = groupby_time(ds, self.time_grouping, agg_fn='mean')

        # Put evertyhing on the same chunk before spatial aggregation
        ds = ds.chunk({dim: -1 for dim in ds.dims})

        # Add the region coordinate to the statistic
        ds = ds.assign_coords(space_grouping=(('lat', 'lon'), space_grouping_ds.region.values))

        ############################################################
        # 3. Aggregate in space and apply spatial weighting
        ############################################################
        if not self.spatial:
            # Group by region and average in space, while applying weighting for mask
            weights = latitude_weights(ds.lat)
            # Expand weights to have a time dimension that matches ds
            weights = weights.expand_dims(lon=ds.lon)
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

            if self.space_grouping is None:
                ds = ds.sum(dim=['lat', 'lon'], skipna=True, min_count=1)
            elif ds.space_grouping.size > 0:
                ds = ds.groupby('space_grouping').sum(dim=['lat', 'lon'], skipna=True, min_count=1)

                # If we've passed a global region and clipped, drop any null groups
                # Currently commenting out because it was hurting performance
                # hopefully a future change can drop nan regions more efficiently
                # until then it's fine to return NaN
                # ds = ds.dropna(dim='space_grouping', how='all')
            else:
                # If we don't have any valid space groups after clipping, the dataframe is empty
                # we can just continue
                pass

            for stat in self.statistics:
                ds[stat] = xr.where(ds['weights'] != 0, ds[stat] / ds['weights'], np.nan)
            ds = ds.drop_vars(['weights'])
        else:
            # If returning a spatial metric, mask and drop
            ds = ds.where(mask_ds.mask, np.nan, drop=False)

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


class ContingencyMetric(Metric):  # noqa: N801
    """Base class for contingency metrics, both dichotomous and multiclass."""

    def prepare_data(self):
        """Prepare the bin data for the contingency metric."""
        ############################################################
        # Enable contingency metrics to be called in the form 'heidke-1-5-10-20' and set up the digitized event.
        ############################################################
        # What event are we running? If no event was passed, use the default event.
        event = self.event if self.event is not None else self.default_event
        if 'user_input_config' not in self.metric_kwargs:
            self.metric_kwargs['user_input_config'] = 'none'

        # Handle agg days
        if event in ('digitized', 'above_threshold'):
            # Check that the agg days passed to the metric, event, fcst event, and obs event are all the same
            passed_agg_days = self.agg_days
            agg_days_fcst = self.event_kwargs_fcst.get('agg_days', None)
            agg_days_obs = self.event_kwargs_obs.get('agg_days', None)

            # Get the non-null agg day values and ensure that they're all equal
            valid_agg_days = [x for x in [passed_agg_days, agg_days_fcst, agg_days_obs] if x is not None]
            agg_days = valid_agg_days[0] if any(valid_agg_days) else None
            if not all(x == agg_days for x in valid_agg_days):
                raise ValueError("Agg days passed to the event must match the agg days passed to the metric.")

            # Set the agg days to the non-null value
            self.event_kwargs_fcst['agg_days'] = agg_days
            self.event_kwargs_obs['agg_days'] = agg_days

            # Reset the agg days to one and let the event handle the aggregation
            self.agg_days = 1

        if event == 'digitized':
            # We try to figure out the bins from the metric key
            if self.metric_kwargs['user_input_config'] != 'none':
                bins = [-np.inf] + [float(x) for x in self.metric_kwargs['user_input_config'].split('-')] + [np.inf]
                for event_kwargs in [self.event_kwargs_fcst, self.event_kwargs_obs]:
                    if 'bins' not in event_kwargs:
                        event_kwargs['bins'] = bins
                    elif event_kwargs['bins'] != bins:
                        raise ValueError("Bins passed to the event must match the bins specified in the key.")
                del self.metric_kwargs['user_input_config']
        elif event == 'above_threshold':
            # We try to figure out the threshhold from the metric key,
            # allowing users to pass, e.g., pod-obs_threshold-fcst_threshold as pod-5-6.5.
            if self.metric_kwargs['user_input_config'] != 'none':
                thresholds = self.metric_kwargs['user_input_config'].split('-')
                if len(thresholds) == 1:
                    # Set both thresholds to the same value
                    obs_threshold = float(thresholds[0])
                    fcst_threshold = float(thresholds[0])
                elif len(thresholds) == 2:
                    # Set the thresholds to the values passed in the key
                    obs_threshold = float(thresholds[0])
                    fcst_threshold = float(thresholds[1])
                else:
                    raise ValueError("Threshold key must be in the format 'obs_threshold-fcst_threshold'.")

                # Check for consistancy
                f_thresh = self.event_kwargs_fcst.get('threshold', None)
                o_thresh = self.event_kwargs_obs.get('threshold', None)
                if f_thresh is not None and f_thresh != fcst_threshold:
                    raise ValueError("Forecast threshold passed does not match the threshold specified in the key.")
                if o_thresh is not None and o_thresh != obs_threshold:
                    raise ValueError("Observation threshold passed does not match the threshold specified in the key.")

                self.event_kwargs_fcst['threshold'] = fcst_threshold
                self.event_kwargs_obs['threshold'] = obs_threshold

        if event == 'digitized':
            if len(self.event_kwargs_fcst['bins']) != len(self.event_kwargs_obs['bins']):
                raise ValueError("Bins passed to the event must match the bins specified in the key.")

        # Call the parent prepare_data method to get the forecast and observation
        Metric.prepare_data(self)


class MAE(Metric):
    """Mean Absolute Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    default_event = None
    statistics = ['mae']


class ForecastValue(Metric):
    """Forecast value metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    default_event = None
    statistics = ['fcst']


class ObsValue(Metric):
    """Observation value metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    default_event = None
    statistics = ['obs']


class MSE(Metric):
    """Mean Squared Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    default_event = None
    statistics = ['mse']


class RMSE(Metric):
    """Root Mean Squared Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    default_event = None
    statistics = ['mse']

    def compute_metric(self):
        return self.grouped_statistics['mse'] ** 0.5


class Bias(Metric):
    """Bias metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None  # all variables are valid
    default_event = None
    statistics = ['bias']


class CRPS(Metric):
    """Continuous Ranked Probability Score metric."""
    sparse = False
    prob_type = 'probabilistic'
    valid_variables = None  # all variables are valid
    default_event = None
    statistics = ['crps']


class Brier(ContingencyMetric):
    """Brier score metric."""
    sparse = False
    prob_type = 'probabilistic'
    valid_variables = ['precip']
    default_event = 'above_threshold'
    statistics = ['brier']


class SMAPE(Metric):
    """Symmetric Mean Absolute Percentage Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = ['precip']
    default_event = None
    statistics = ['smape']


class MAPE(Metric):
    """Mean Absolute Percentage Error metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = ['precip']
    default_event = None
    statistics = ['mape']


class SEEPS(Metric):
    """Spatial Error in Ensemble Prediction Scale metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    default_event = None
    statistics = ['seeps']

    def prepare_data(self):
        """Prepare specific data for the SEEPS metric."""
        # Call the parent prepare_data method to get the forecast and observation
        super().prepare_data()

        first_year = 1991
        last_year = 2020
        # Get the wet threshold and dry fraction
        self.metric_data['wet_threshold'] = seeps_wet_threshold(
            first_year=first_year, last_year=last_year, agg_days=self.agg_days,
            grid=self.grid, mask=self.mask, region=self.region)
        self.metric_data['dry_fraction'] = seeps_dry_fraction(
            first_year=first_year, last_year=last_year,
            agg_days=self.agg_days, grid=self.grid, mask=self.mask, region=self.region)

        # Update the metric data key to include the wet threshold and dry fraction year range
        self.metric_kwargs['first_year'] = first_year
        self.metric_kwargs['last_year'] = last_year


class ACC(Metric):
    """ACC (Anomaly Correlation Coefficient) metric."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = None
    default_event = None
    statistics = ['squared_fcst_anom', 'squared_obs_anom', 'anom_covariance']

    def prepare_data(self):
        """Prepare specific data for the ACC metric."""
        # Call the parent prepare_data method to get the forecast and observation
        Metric.prepare_data(self)
        assert self.event is None, "ACC metric does not support events."

        # Get the appropriate climatology dataframe for metric calculation
        if self.truth == 'imerg_final':
            first_year = 1998
            last_year = 2015
            clim_source = 'imerg_final'
        else:
            first_year = 1985
            last_year = 2014
            clim_source = 'era5'

        clim_ds = climatology(data=clim_source, first_year=first_year, last_year=last_year,
                              **self.fcst_obs_kwargs, prob_type='deterministic')

        # Expand climatology to the same lead times as the forecast
        if 'prediction_timedelta' in self.metric_data['fcst'].dims:
            leads = self.metric_data['fcst'].prediction_timedelta.values
            # Add in a matching prediction_timedelta coordinate
            clim_ds = clim_ds.expand_dims({'prediction_timedelta': leads})

        # Subset the climatology to the valid times and non-null times of the forecaster
        clim_ds = clim_ds.sel(time=self.metric_data['valid_times'])
        # Add the climatology to the metric data
        self.metric_data['climatology'] = clim_ds

        # Update the metric kwargs to include the climatology year range
        self.metric_kwargs['clim_source'] = clim_source
        self.metric_kwargs['first_year'] = first_year
        self.metric_kwargs['last_year'] = last_year

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
    default_event = None
    statistics = ['fcst', 'obs', 'squared_fcst', 'squared_obs', 'covariance']

    def compute_metric(self):
        gs = self.grouped_statistics
        numerator = gs['covariance'] - gs['fcst'] * gs['obs']
        denominator = (gs['squared_fcst'] - gs['fcst']**2) ** 0.5 * (gs['squared_obs'] - gs['obs']**2) ** 0.5
        return numerator / denominator


class Heidke(ContingencyMetric):
    """Heidke Skill Score metric for streaming data."""
    sparse = False
    prob_type = 'deterministic'
    valid_variables = ['precip']
    default_event = 'digitized'

    @property
    def statistics(self):
        stats = ['n_correct', 'n_valid']
        # fcst and obs have the same number of bins, so we can use either here
        stats += [f'n_fcst_bin_{i}' for i in range(1, len(self.event_kwargs_fcst['bins']))]
        stats += [f'n_obs_bin_{i}' for i in range(1, len(self.event_kwargs_obs['bins']))]
        return stats

    def compute_metric(self):
        gs = self.grouped_statistics
        prop_correct = gs['n_correct'] / gs['n_valid']
        n2 = gs['n_valid']**2
        right_by_chance = xr.zeros_like(gs['n_correct'])
        # fcst and obs have the same number of bins, so we can use either here
        for i in range(1, len(self.event_kwargs_fcst['bins'])):
            right_by_chance += (gs[f'n_fcst_bin_{i}'] * gs[f'n_obs_bin_{i}']) / n2

        return (prop_correct - right_by_chance) / (1 - right_by_chance)


class POD(ContingencyMetric):
    """Probability of Detection metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    default_event = 'above_threshold'
    statistics = ['true_positives', 'false_negatives']

    def compute_metric(self):
        tp = self.grouped_statistics['true_positives']
        fn = self.grouped_statistics['false_negatives']
        return tp / (tp + fn)


class FAR(ContingencyMetric):
    """False Alarm Rate metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    default_event = 'above_threshold'
    statistics = ['false_positives', 'true_negatives']

    def compute_metric(self):
        fp = self.grouped_statistics['false_positives']
        tn = self.grouped_statistics['true_negatives']
        return fp / (fp + tn)


class ETS(ContingencyMetric):
    """Equitable Threat Score metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    default_event = 'above_threshold'
    statistics = ['true_positives', 'false_positives', 'false_negatives', 'true_negatives']

    def compute_metric(self):
        gs = self.grouped_statistics
        tp = gs['true_positives']
        fp = gs['false_positives']
        fn = gs['false_negatives']
        tn = gs['true_negatives']
        chance = ((tp + fp) * (tp + fn)) / (tp + fp + fn + tn)
        return (tp - chance) / (tp + fp + fn - chance)


class CSI(ContingencyMetric):
    """Critical Success Index metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    default_event = 'above_threshold'
    statistics = ['true_positives', 'false_positives', 'false_negatives']

    def compute_metric(self):
        tp = self.grouped_statistics['true_positives']
        fp = self.grouped_statistics['false_positives']
        fn = self.grouped_statistics['false_negatives']
        return tp / (tp + fp + fn)


class FrequencyBias(ContingencyMetric):
    """Frequency Bias metric."""
    sparse = True
    prob_type = 'deterministic'
    valid_variables = ['precip']
    default_event = 'above_threshold'
    statistics = ['true_positives', 'false_positives', 'false_negatives']

    def compute_metric(self):
        tp = self.grouped_statistics['true_positives']
        fp = self.grouped_statistics['false_positives']
        fn = self.grouped_statistics['false_negatives']
        return (tp + fp) / (tp + fn)


def metric_factory(metric_name: str, metric_kwargs=None, **init_kwargs) -> Metric:
    """Get a metric class by name from the registry."""
    try:
        experiment_kwargs = get_experiment_kwargs(metric_name, init_kwargs['region'], input_metric_kwargs=metric_kwargs)
        exp_metric_name, exp_metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = experiment_kwargs
        metric = SHEERWATER_METRIC_REGISTRY[exp_metric_name.lower()]

        # Update the experiment kwargs with their values in init_kwargs if passed
        if metric_kwargs is not None:
            exp_metric_kwargs.update(metric_kwargs)

        # Remove the experiment kwargs from the init kwargs
        for key in ['event', 'event_kwargs', 'filter_event', 'filter_event_kwargs']:
            if key in init_kwargs:
                del init_kwargs[key]

        # Add runtime metric configuration to the metric class
        return metric(metric_kwargs=exp_metric_kwargs,
                      event=event,
                      event_kwargs=event_kwargs,
                      filter_event=filter_event,
                      filter_event_kwargs=filter_event_kwargs,
                      **init_kwargs)
    except ValueError:
        if metric_kwargs is None:
            metric_kwargs = {}
        # Convert
        if '-' in metric_name:
            mn = metric_name.split('-')[0]  # support for contingency metric names of the form 'metric-datakey...'
            metric_kwargs['user_input_config'] = metric_name[metric_name.find('-')+1:]
        else:
            mn = metric_name

        metric = SHEERWATER_METRIC_REGISTRY[mn.lower()]
        # Add runtime metric configuration to the metric class
        return metric(metric_kwargs=metric_kwargs, **init_kwargs)

    except KeyError:
        raise ValueError(f"Unknown metric: {metric_name}. Available metrics: {list_metrics()}")


def list_metrics():
    """List all available metrics in the registry."""
    return list(SHEERWATER_METRIC_REGISTRY.keys())
