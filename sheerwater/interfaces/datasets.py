"""A decorator for identifying data sources."""

import xarray as xr
import pandas as pd
import numpy as np
from nuthatch.processor import NuthatchProcessor
from nuthatch import cache
import warnings
from sheerwater.utils import (convert_init_time_to_pred_time, convert_pred_time_to_init_time,
                              add_spatial_attrs, check_spatial_attr, shift_by_days,
                              densify_fcst, detect_in_time, get_dates)
from sheerwater.spatial_subdivisions import clip_region, apply_mask

from .events import get_event_fn
from .spatial import spatial

import logging
logger = logging.getLogger(__name__)

# Global registry of data sources
DATA_REGISTRY = {}
FORECAST_REGISTRY = {}


class SheerwaterDataset(NuthatchProcessor):
    """Processor for a Sheerwater dataset, either forecast or data of a standard format.

    It also implements spatial clipping and masking, and timeseries filtering.

    It only supports xarray datasets.
    """

    def __init__(self, region_dim=None, **kwargs):
        """Initialize the spatial processor.

        Args:
            region_dim (str): The name of the region dimension. If None, the returned dataset will not be
                assumed to have a region dimesion and region data will be fetched from the region registry
                before clipping.
            kwargs: Additional keyword arguments to pass to the NuthatchProcessor.
        """
        NuthatchProcessor.__init__(self, **kwargs)
        self.region_dim = region_dim

    def process_arguments(self, sig, *args, **kwargs):
        """Process the arguments for the datasets decorator."""
        # Get default values for the function signature
        bound_args = self.bind_signature(sig, *args, **kwargs)

        # Get required arguments, these are required for all datasets
        try:
            self.grid = bound_args.arguments['grid']
            self.agg_days = bound_args.arguments['agg_days']
        except KeyError:
            raise ValueError("Dataset decorator requires grid and agg_days to be passed.")

        # Set other arguments to reasonable defaults
        self.region = bound_args.arguments.get('region', 'global')
        self.mask = bound_args.arguments.get('mask', None)
        self.variable = bound_args.arguments.get('variable', None)

        # Event handling
        self.event = bound_args.arguments.get('event', None)
        if self.event is not None and self.agg_days != 1:
            raise ValueError(f"Event {self.event} requires agg_days to be 1.")
        self.event_kwargs = bound_args.arguments.get('event_kwargs') or {}
        self.event_fn = get_event_fn(self.event) if self.event is not None else None

        if 'detect_in_time' in self.event_kwargs:
            self.detect_in_time = self.event_kwargs['detect_in_time']
            del self.event_kwargs['detect_in_time']
        else:
            self.detect_in_time = None

        # Handle the case where variable is not passed, but an event is specified by setting variable to default event
        if self.variable is None:
            if self.event is None:
                raise ValueError("Dataset decorator requires variable to be passed if no event is specified.")
            elif self.event_fn.default_variable is None:
                raise ValueError(f"Event {self.event} has no default variable. Please specify a variable.")
            else:
                self.variable = self.event_fn.default_variable
                args, kwargs = self.update_args_or_kwargs(
                    values={'variable': self.variable}, args=args, kwargs=kwargs, bound_args=bound_args)

        # Units
        if self.variable == 'precip':
            self.units = 'mm / day'
        elif self.variable == 'tmp2m':
            self.units = 'avg. daily C'
        else:
            self.units = None

        return args, kwargs

    def post_process(self, ds):
        """Clip and mask the dataset."""
        if not isinstance(ds, xr.Dataset):
            raise RuntimeError(
                f"Sheerwater data and forecast decorators must return xarray datasets. Received {type(ds)}.")

        # Reindex to fill out the time to a daily time series
        # Fill in any missing times between the start and end dates of the dataset
        if 'processed' not in ds.attrs:
            daily_timeseries = get_dates(ds.time.values.min(), ds.time.values.max(), stride='day', return_string=False)
            ds = ds.reindex(time=daily_timeseries, fill_value=np.nan)

        # Clip to specified region
        if not check_spatial_attr(ds, region=self.region):
            # Only clip region if the dataframe hasn't already been clipped
            ds = clip_region(ds, grid=self.grid, region=self.region)
        if not check_spatial_attr(ds, mask=self.mask):
            # Only apply mask if this dataframe has not already been masked
            ds = apply_mask(ds, self.mask, grid=self.grid)

        # Assign attributes, preserving any existing ones (especially 'prob_type')
        ds = ds.assign_attrs({
            'agg_days': float(self.agg_days),
            'variable': self.variable,
            'units': self.units,
        })
        ds = add_spatial_attrs(ds, grid=self.grid, mask=self.mask, region=self.region)
        return ds

    def update_args_or_kwargs(self, values, args, kwargs, bound_args):
        """Update args or kwargs with a given value dictionary.

        NOTE: this will eventually be replaced by a Nuthatch function that handles this more generically.
        """
        for key, value in values.items():
            # If key is in kwargs, we can proceed immediately
            if key in kwargs:
                kwargs[key] = value
                continue
            elif key in bound_args.arguments:
                idx = list(bound_args.signature.parameters).index(key)
                if idx < len(args):
                    args = list(args)
                    args[idx] = value
                    args = tuple(args)
            else:
                # Key not found in the bound arguments, raise an error
                raise ValueError(f"Key {key} not found in the bound arguments or kwargs.")
        return args, kwargs

    def validate(self, ds):
        """Validate the cached data to ensure it has data within the region."""
        # Check to see if the dataset extends roughly the full time series set
        test = clip_region(ds, grid=self.grid, region=self.region)
        test = apply_mask(test, self.mask, grid=self.grid)
        if test.notnull().count().compute() == 0:
            logger.warning(f"""The cached array does not have data within
                        the region {self.region}. Triggering recompute.
                        If you do not want to recompute the result set
                        `validate_data=False`""")
            return False
        else:
            return True


class data(SheerwaterDataset):
    """Processor for a Sheerwater data. It supports xarray datasets."""

    def __call__(self, func):
        """Call the parent class and register the data in the global data registry."""
        wrapped = SheerwaterDataset.__call__(self, func)
        DATA_REGISTRY[func.__name__] = wrapped
        return wrapped

    def process_arguments(self, sig, *args, **kwargs):
        """Process the arguments for the data decorator."""
        args, kwargs = SheerwaterDataset.process_arguments(self, sig, *args, **kwargs)
        bound_args = self.bind_signature(sig, *args, **kwargs)

        # Adjust the end_time to account for the aggregation days, so that
        # agg days past the end time is included in the final aggregation.
        end_time = bound_args.arguments.get('end_time', None)
        if self.event_fn is not None:
            duration = self.event_fn.duration(self.event_kwargs) if callable(self.event_fn.duration) \
                else self.event_fn.duration
        else:
            duration = self.agg_days
        if end_time is not None:
            end_time = shift_by_days(end_time, duration-1)
        args, kwargs = self.update_args_or_kwargs(
            values={'end_time': end_time}, args=args, kwargs=kwargs, bound_args=bound_args)
        return args, kwargs

    def post_process(self, ds):
        """Post-processor for a Sheerwater data. It supports xarray datasets."""
        # Clip and mask the dataset
        ds = SheerwaterDataset.post_process(self, ds)

        # Run the events on the dataset
        if self.event is not None and 'processed' not in ds.attrs:
            ds = self.event_fn(ds, **self.event_kwargs)

        if self.detect_in_time is not None and 'processed' not in ds.attrs:
            ds = detect_in_time(ds, **self.detect_in_time)

        # Remove all unneeded dimensions
        ds = ds.drop_vars([var for var in ds.coords if var not in [
                          'time', 'lat', 'lon', 'member', 'group', 'station_id']])

        # Add a flag to the dataset to indicate that it has been processed
        ds = ds.assign_attrs({'processed': True})

        return ds


@spatial()
@cache(cache=True, cache_args=['lookback_source', 'variable', 'grid'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "init_time": 1000, "prediction_timedelta": 1},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "init_time": 30, "prediction_timedelta": 1}
               },
           }
})
def obs_with_lookback(start_time, end_time, lookback_source, variable, grid,  mask='lsm', region='global'):  # noqa: ARG001
    """Observational data expanded out to contain a 30 day lookback period, easily merged with the forecast dataset."""
    # Get observational dataset on the global grid and with no mask; spatial decorator will handle the rest
    ds_obs = get_data(lookback_source)(start_time=start_time, end_time=end_time,
                                       variable=variable, grid=grid,
                                       mask=None, region='global')
    lookback_days = 30  # Hard coded 30 day lookback period
    lookbacks = pd.timedelta_range(start=f"-{lookback_days}D", end="-1D", freq='D')
    ds_obs = ds_obs.expand_dims({"prediction_timedelta": lookbacks.values})
    ds_obs = convert_pred_time_to_init_time(ds_obs)
    return ds_obs


class forecast(SheerwaterDataset):
    """Processor for a Sheerwater forecast. It supports xarray datasets."""

    def __call__(self, func):
        """Call the forecast decorator and register it in the global forecast registry."""
        wrapped = SheerwaterDataset.__call__(self, func)
        FORECAST_REGISTRY[func.__name__] = wrapped
        return wrapped

    def process_arguments(self, sig, *args, **kwargs):
        """Process the arguments for the data decorator."""
        args, kwargs = SheerwaterDataset.process_arguments(self, sig, *args, **kwargs)
        bound_args = self.bind_signature(sig, *args, **kwargs)
        self.lookback_source = bound_args.arguments.get('lookback_source', None)
        self.densify = bound_args.arguments.get('densify', False)
        return args, kwargs

    def blend_fcst_and_obs(self, fcst, lookback_source, lookback_days=0):
        """Blend the forecast and observations.

        Args:
            fcst (xr.Dataset): The forecast dataset, indexed by init_time and prediction_timedelta.
            lookback_source (str): The source of the observations to look back to.
            lookback_days (int): The number of days to look back, integer.

        Returns:
            xr.Dataset: The combined dataset, with -lookback days of observations added to the beginning of the forecast
        """
        if lookback_days == 0:
            return fcst
        if lookback_days > 30:
            # We have only cached an observation lookback period of 30 days; if we want more than this
            # would need to write a new cache
            warnings.warn(f"Lookback days {lookback_days} is greater than 30, only the last 30 days will be used.")
            lookback_days = 30

        # Get the observations for forecast period + the lookback period
        new_start = shift_by_days(fcst.init_time.values.min(), -lookback_days)
        new_end = fcst.init_time.values.max()
        obs = obs_with_lookback(new_start, new_end, lookback_source=lookback_source, variable=self.variable,
                                grid=self.grid, mask=self.mask, region=self.region)

        # Select the approriate lookback periods for the duration of the event and on the forecast init times.
        lookbacks = pd.timedelta_range(start=f"-{lookback_days}D", end="-1D", freq='D')
        obs = obs.sel(init_time=fcst.init_time, prediction_timedelta=lookbacks)

        # Concat with forecast on prediction_timedelta
        # Transpose both to have the same dimensions
        combined = xr.concat([fcst, obs], dim="prediction_timedelta", join='outer')
        combined = combined.sortby("prediction_timedelta")
        return combined

    def post_process(self, ds):
        """Post process the forecast.

        Enables blending the forecast and observations, event definition, conversion of init time to valid time,
        and general spatial postprocessing, including region clipping and masking.
        """
        # Clip and mask the dataset
        ds = SheerwaterDataset.post_process(self, ds)

        # Run the events on the forecast: requires blending in lookback obs and renaming time labels
        if self.event is not None and 'processed' not in ds.attrs:
            # If the first event has a lookback period, blend in the lookback observations

            #################################################################################################
            # 1. Desnify the forecast if requested (fill in missing init time gaps with previous forecast values)
            ##################################################################################################
            if self.densify or self.event_kwargs.get('densify', False):
                ds = densify_fcst(ds)

            ##################################################################################################
            # 2. Blend in the lookback observations up to the event duration
            ##################################################################################################
            lookback_days = self.event_fn.duration(self.event_kwargs) if callable(self.event_fn.duration) \
                else self.event_fn.duration

            if self.lookback_source is not None:
                ds = self.blend_fcst_and_obs(ds, lookback_source=self.lookback_source, lookback_days=lookback_days)
            elif lookback_days > 0:
                warnings.warn(
                    f"Lookback days {lookback_days} specified but no lookback source provided. Ignoring lookback days.")
            ds = ds.assign_attrs({'lookback_source': self.lookback_source})

            ##################################################################################################
            # 3. Run the event on the forecast
            ##################################################################################################
            # For the first event, rename prediction timedelta to time to act along leads
            ds = ds.rename({'prediction_timedelta': 'time'})
            ds = self.event_fn(ds, **self.event_kwargs)
            ds = ds.rename({'time': 'prediction_timedelta'})

        if 'init_time' in ds.coords and 'prediction_timedelta' in ds.coords:
            ds = convert_init_time_to_pred_time(ds)

        if self.detect_in_time is not None and 'processed' not in ds.attrs:
            ds = detect_in_time(ds, **self.detect_in_time)

        # Remove all unneeded dimensions
        ds = ds.drop_vars([var for var in ds.coords if
                           var not in ['time', 'prediction_timedelta', 'lat', 'lon', 'member', 'group']])

        ds = ds.assign_attrs({'processed': True})
        return ds


def get_forecast(forecast_name):
    """Get a forecast from the global forecast registry."""
    # The imports below ensure that all forecast modules are registered when this is called.
    import sheerwater.forecasts  # noqa: F401
    import sheerwater.climatology  # noqa: F401
    return FORECAST_REGISTRY[forecast_name]


def list_forecasts():
    """List all forecasts in the global forecast registry."""
    # The imports below ensure that all forecast modules are registered when this is called.
    import sheerwater.forecasts  # noqa: F401
    import sheerwater.climatology  # noqa: F401
    return list(FORECAST_REGISTRY.keys())


def get_data(data_name):
    """Get a data source from the global data registry."""
    # The imports below ensure that all forecast modules are registered when this is called.
    import sheerwater.data  # noqa: F401
    import sheerwater.climatology  # noqa: F401
    import sheerwater.reanalysis  # noqa: F401
    if data_name not in DATA_REGISTRY:
        raise ValueError(f"Data source {data_name} not found in the global data registry.")
    return DATA_REGISTRY[data_name]


def list_data():
    """List all data sources in the global data registry."""
    # The imports below ensure that all forecast modules are registered when this is called.
    import sheerwater.data  # noqa: F401
    import sheerwater.climatology  # noqa: F401
    import sheerwater.reanalysis  # noqa: F401
    return list(DATA_REGISTRY.keys())
