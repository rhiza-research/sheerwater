"""A decorator for identifying data sources."""

import warnings
import xarray as xr
import pandas as pd
from nuthatch.processor import NuthatchProcessor
from nuthatch import cache

from sheerwater.utils import (convert_init_time_to_pred_time, convert_pred_time_to_init_time,
                              add_spatial_attrs, check_spatial_attr, shift_by_days)
from sheerwater.interfaces import spatial
from sheerwater.spatial_subdivisions import clip_region, apply_mask


from .events import get_event_fn

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
            raise ValueError("Dataset decorator requires grid, agg_days, and variable to be passed.")

        # Default to global region and no masking if not passed
        self.start_time = bound_args.arguments.get('start_time', None)
        self.end_time = bound_args.arguments.get('end_time', None)
        self.region = bound_args.arguments.get('region', 'global')
        self.mask = bound_args.arguments.get('mask', None)
        self.variable = bound_args.arguments.get('variable', None)

        # Event and lookback handling
        self.lookback_source = kwargs.get('lookback_source', None)
        self.event = kwargs.get('event', None)
        if self.event:
            if self.agg_days != 1:
                warnings.warn(f"Event {self.event} requires agg_days to be 1, setting to 1.")
            self.agg_days = 1  # All events must be called with an agg days of 1
        self.event_kwargs = kwargs.get('event_kwargs', {})
        # Remove from kwargs so they don't get passed to the underlying function
        for kwarg in ['event', 'event_kwargs', 'lookback_source']:
            if kwarg in kwargs:
                del kwargs[kwarg]

        if self.event is not None and not isinstance(self.event, list):
            self.event = [self.event]
        if not isinstance(self.event_kwargs, list):
            self.event_kwargs = [self.event_kwargs]
        if self.event is not None:
            self.event_fns = [get_event_fn(event)(**event_kwargs)
                              for event, event_kwargs in zip(self.event, self.event_kwargs)]
        else:
            self.event_fns = []

        # If variable is not passed, attempt to set it by the first event in the chain
        if self.variable is None:
            args, kwargs = self.set_variable_by_event(args, kwargs, bound_args)

        # Units
        if self.variable == 'precip':
            self.units = 'mm / day'
        elif self.variable == 'tmp2m':
            self.units = 'avg. daily C'
        else:
            self.units = None

        return args, kwargs

    def set_variable_by_event(self, args, kwargs, bound_args):
        """Update the args and kwargs to use the default variable for the first event in the chain."""
        if self.event is None:
            raise ValueError("Dataset decorator requires variable to be passed if no event is specified.")

        # Get the default variable for the first event in the chain
        self.variable = get_event_fn(self.event[0])(**self.event_kwargs[0]).default_variable

        # Modify the input args, kwargs to use the default variable
        if 'variable' in bound_args.arguments:
            idx = list(bound_args.signature.parameters).index('variable')
            if idx < len(args):
                args = list(args)
                args[idx] = self.variable
                args = tuple(args)
            elif 'variable' in kwargs:
                kwargs = dict(kwargs)
                kwargs['variable'] = self.variable
        return args, kwargs

    def clip_and_mask(self, ds):
        """Clip and mask the dataset."""
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
        if 'end_time' in bound_args.arguments:
            end_time = bound_args.arguments['end_time']
            if end_time is not None:
                end_time = shift_by_days(end_time, self.agg_days-1)
            idx = list(bound_args.signature.parameters).index('end_time')
            if idx < len(args):
                args = list(args)
                args[idx] = end_time
                args = tuple(args)
            elif 'end_time' in kwargs:
                kwargs = dict(kwargs)
                kwargs['end_time'] = end_time
        return args, kwargs

    def post_process(self, ds):
        """Post-processor for a Sheerwater data. It supports xarray datasets."""
        if not isinstance(ds, xr.Dataset):
            raise RuntimeError(f"Sheerwater datasets must return xarray datasets. Received {type(ds)}.")
        # Clip and mask the dataset
        ds = self.clip_and_mask(ds)

        # Run the events on the dataset
        if self.event is not None and 'processed' not in ds.attrs:
            for event_fn in self.event_fns:
                # Run each event in the chain in order
                ds = event_fn(ds)

        # Remove all unneeded dimensions
        ds = ds.drop_vars([var for var in ds.coords if var not in ['time', 'lat', 'lon', 'member', 'station_id']])

        # Add a flag to the dataset to indicate that it has been processed
        ds = ds.assign_attrs({'processed': True})

        return ds


class forecast(SheerwaterDataset):
    """Processor for a Sheerwater forecast. It supports xarray datasets."""

    def __call__(self, func):
        """Call the forecast decorator and register it in the global forecast registry."""
        wrapped = SheerwaterDataset.__call__(self, func)
        FORECAST_REGISTRY[func.__name__] = wrapped
        return wrapped

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

        # Get the lookback periods for the observations
        # @spatial()
        @cache(cache=True, cache_args=['lookback_source', 'variable', 'grid', 'agg_days'],
               backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'init_time': 365, 'prediction_timedelta': 1}})
        def obs_with_lookback(start_time, end_time, lookback_source, variable, grid, agg_days):
            # Get observational dataset on the global grid and with no mask; spatial decorator will handle the rest
            ds_obs = get_data(lookback_source)(start_time=start_time, end_time=end_time,
                                               variable=variable, grid=grid,
                                               agg_days=agg_days,
                                               mask=None, region='global')
            lookbacks = pd.timedelta_range(start=f"-{lookback_days}D", end="-1D", freq='D')
            ds_obs = ds_obs.expand_dims({"prediction_timedelta": lookbacks.values})
            ds_obs = convert_pred_time_to_init_time(ds_obs)
            ds_obs = ds_obs.chunk({'lat': 300, 'lon': 300, 'init_time': 365, 'prediction_timedelta': 1})
            return ds_obs

        # Get the observations for forecast period + the lookback period
        new_start = shift_by_days(fcst.init_time.values.min(), -lookback_days)
        new_end = fcst.init_time.values.max()
        obs = obs_with_lookback(new_start, new_end, lookback_source, variable=self.variable, grid=self.grid, agg_days=1)

        # Clip and mask the observational product, and select on the forecasting times
        obs = self.clip_and_mask(obs)
        obs = obs.sel(init_time=fcst.init_time)

        # Concat with forecast on prediction_timedelta
        combined = xr.concat([fcst, obs], dim="prediction_timedelta")
        combined = combined.sortby("prediction_timedelta")

        # Ensure we've done the proper selection of the observations
        # orig_obs = get_data(self.lookback_source)(start_time=new_start, end_time=new_end,
        #                                           variable=self.variable, grid=self.grid, agg_days=1)
        # ds1 = orig_obs.sel(time="2016-02-10")
        # import numpy as np
        # ds2 = combined.sel(init_time="2016-02-15", prediction_timedelta=np.timedelta64(-5, "D"))
        # import matplotlib.pyplot as plt
        # (ds1 - ds2).precip.plot(x='lon')
        # plt.show()

        return combined

    def post_process(self, ds):
        """Post process the forecast.

        Enables blending the forecast and observations, event definition, conversion of init time to valid time,
        and general spatial postprocessing, including region clipping and masking.
        """
        if not isinstance(ds, xr.Dataset):
            raise RuntimeError(f"Sheerwater datasets must return xarray datasets. Received {type(ds)}.")
        # Clip and mask the dataset
        ds = self.clip_and_mask(ds)

        # Run the events on the forecast: requires blending in lookback obs and renaming time labels
        if self.event is not None and 'processed' not in ds.attrs:
            # If the first event has a lookback period, blend in the lookback observations
            lookback_days = self.event_fns[0].duration

            ds = self.blend_fcst_and_obs(ds, lookback_source=self.lookback_source, lookback_days=lookback_days)
            ds = ds.assign_attrs({'lookback_source': self.lookback_source})

            # For the first event, rename prediction timedelta to time to act along leads
            ds = ds.rename({'prediction_timedelta': 'time'})
            ds = self.event_fns[0](ds)
            ds = ds.rename({'time': 'prediction_timedelta'})

            if 'init_time' in ds.coords and 'prediction_timedelta' in ds.coords:
                ds = convert_init_time_to_pred_time(ds)

            for event_fn in self.event_fns[1:]:
                # Run each event in the chain after the first
                ds = event_fn(ds)

        # Remove all unneeded dimensions
        ds = ds.drop_vars([var for var in ds.coords if
                           var not in ['time', 'prediction_timedelta', 'lat', 'lon', 'member']])

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
