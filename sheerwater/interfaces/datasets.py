"""A decorator for identifying data sources."""

import xarray as xr
import pandas as pd
from nuthatch.processor import NuthatchProcessor
from sheerwater.utils import convert_init_time_to_pred_time, convert_pred_time_to_init_time, add_spatial_attrs, check_spatial_attr, shift_by_days
from sheerwater.spatial_subdivisions import clip_region, apply_mask
import numpy as np
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

        # Default to global region and no masking if not passed
        self.start_time = bound_args.arguments.get('start_time', None)
        self.end_time = bound_args.arguments.get('end_time', None)
        self.region = bound_args.arguments.get('region', 'global')
        self.mask = bound_args.arguments.get('mask', None)
        self.variable = bound_args.arguments.get('variable', None)

        # Forecaster specific arguments
        self.lookback_source = kwargs.get('lookback_source', None)
        self.event = kwargs.get('event', None)
        self.event_kwargs = kwargs.get('event_kwargs', {})
        if self.event is not None:
            self.event_fn = get_event_fn(self.event)(**self.event_kwargs)

        if self.variable is None:
            if self.event is None:
                raise ValueError("Dataset decorator requires variable to be passed.")
            else:
                # Get the default variable for the event
                self.variable = get_event_fn(self.event)(*self.event_kwargs).default_variable
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

        # Get required arguments
        try:
            self.grid = bound_args.arguments['grid']
            self.agg_days = bound_args.arguments['agg_days']
            if self.event:
                self.agg_days = 1  # All events must be called with an agg days of 1
        except KeyError:
            raise ValueError("Dataset decorator requires grid, agg_days, and variable to be passed.")

        # Remove from kwargs so they don't get passed to the underlying function
        if 'event' in kwargs:
            del kwargs['event']
        if 'event_kwargs' in kwargs:
            del kwargs['event_kwargs']
        if 'lookback_source' in kwargs:
            del kwargs['lookback_source']

        # Units
        if self.variable == 'precip':
            self.units = 'mm / day'
        elif self.variable == 'tmp2m':
            self.units = 'avg. daily C'
        else:
            self.units = None

        if 'lookback_days' in kwargs:
            del kwargs['lookback_days']
        if 'lookback_data_source' in kwargs:
            del kwargs['lookback_data_source']

        return args, kwargs

    def post_process(self, ds):
        """Post-process the dataset to implement masking and region clipping and timeseries postprocessing."""
        if not isinstance(ds, xr.Dataset):
            raise RuntimeError(f"Sheerwater datasets must return xarray datasets. Received {type(ds)}.")

        if self.event is not None and ds is not None and "event" not in ds.attrs:
            ds = self.event_fn(ds)

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
        # Implment masking and region clipping and timeseries postprocessing
        ds = SheerwaterDataset.post_process(self, ds)
        # Remove all unneeded dimensions
        ds = ds.drop_vars([var for var in ds.coords if var not in ['time', 'lat', 'lon', 'member', 'station_id']])
        return ds


class forecast(SheerwaterDataset):
    """Processor for a Sheerwater forecast. It supports xarray datasets."""

    def __call__(self, func):
        """Call the forecast decorator and register it in the global forecast registry."""
        wrapped = SheerwaterDataset.__call__(self, func)
        FORECAST_REGISTRY[func.__name__] = wrapped
        return wrapped

    def blend_fcst_and_obs(self, fcst, obs, lookback_days=30):
        """Blend the forecast and observations.

        Args:
            fcst (xr.Dataset): The forecast dataset, indexed by init_time and prediction_timedelta.
            obs (xr.Dataset): The observations dataset, indexed by time.
            lookback_days (int): The number of days to look back, integer.

        Returns:
            xr.Dataset: The combined dataset, with -lookback days of observations added to the beginning of the forecast.
        """
        # Get the lookback periods for the observations
        obs = obs.chunk({'time': -1, 'lat': 100, 'lon': 100})
        lookbacks = pd.timedelta_range(start=f"-{lookback_days}D", end="-1D", freq='D')
        obs_broadcast = obs.expand_dims({"prediction_timedelta": lookbacks.values})
        obs_broadcast = convert_pred_time_to_init_time(obs_broadcast)
        obs_broadcast = obs_broadcast.sel(init_time=fcst.init_time)

        # Concat with forecast on prediction_timedelta
        combined = xr.concat([fcst, obs_broadcast], dim="prediction_timedelta")
        combined = combined.sortby("prediction_timedelta")

        # # Ensure we've done the proper selection of the observations
        # ds1 = obs.sel(time="2016-02-10")
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
        # Check for negative pred
        if all(ds.prediction_timedelta >= 0):  # TODO: could remove this if we fix double blending
            if self.event is not None:
                lookback_days = self.event_fn.duration
            else:
                lookback_days = self.agg_days

            # Get the observations for forecast period + the lookback period
            new_start = shift_by_days(ds.init_time.values.min(), -lookback_days)
            new_end = ds.init_time.values.max()
            obs = get_data(self.lookback_source)(start_time=new_start, end_time=new_end,
                                                 variable=self.variable, grid=self.grid,
                                                 agg_days=1,
                                                 mask=self.mask, region=self.region)
            ds = self.blend_fcst_and_obs(ds, obs, lookback_days)
            ds = ds.assign_attrs({'lookback_source': self.lookback_source})

        if 'event' not in ds.attrs:
            # Rename prediction timedelta event_time for event postprocessing
            ds = ds.rename({'prediction_timedelta': 'time'})

        # Parent class postprocessing, will apply event postprocessing if it exists
        ds = SheerwaterDataset.post_process(self, ds)

        # TODO: remove extra checks once we're not calling twice
        # Rename event_time back to prediction_timedelta
        if self.event is not None and 'prediction_timedelta' not in ds.coords and 'init_time' in ds.coords:
            ds = ds.rename({'time': 'prediction_timedelta'})

        # # Convert the init time and prediction timedelta to a valid time coordinate labeled 'time'
        if 'init_time' in ds.coords and 'prediction_timedelta' in ds.coords:
            # If we haven't converted from init time to valid times, do so now
            ds = convert_init_time_to_pred_time(ds)

        # Remove all unneeded dimensions
        ds = ds.drop_vars([var for var in ds.coords if
                           var not in ['time', 'prediction_timedelta', 'lat', 'lon', 'member']])
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
