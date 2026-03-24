"""A decorator for identifying data sources."""

import xarray as xr
import pandas as pd
from nuthatch.processor import NuthatchProcessor
from sheerwater.utils import convert_init_time_to_pred_time, add_spatial_attrs, check_spatial_attr, shift_by_days
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

        # Default to global region and no masking if not passed
        self.start_time = bound_args.arguments.get('start_time', None)
        self.end_time = bound_args.arguments.get('end_time', None)
        self.region = bound_args.arguments.get('region', 'global')
        self.mask = bound_args.arguments.get('mask', None)
        self.variable = bound_args.arguments.get('variable', None)
        self.event = kwargs.get('event', None)
        self.event_kwargs = kwargs.get('event_kwargs', {})
        self.lookback_days = kwargs.get('lookback_days', None)
        self.lookback_data_source = kwargs.get('lookback_data_source', None)
        if 'event' in kwargs:
            del kwargs['event']
        if 'event_kwargs' in kwargs:
            del kwargs['event_kwargs']
        if self.variable is None:
            if self.event is None:
                raise ValueError("Dataset decorator requires variable to be passed.")
            else:
                # Get the default variable for the event
                func = get_event_fn(self.event)
                self.variable = func.variable
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
        try:
            self.grid = bound_args.arguments['grid']
            self.agg_days = bound_args.arguments['agg_days']
        except KeyError:
            raise ValueError("Dataset decorator requires grid, agg_days, and variable to be passed.")

        if self.event is not None and self.agg_days != 1:
            raise ValueError("Event decorators cannot be used with aggregation days other than 1.")

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

        if self.event is not None:
            # Apply the event postprocessing to the dataset
            if f"{self.variable}_{self.event}" not in ds.variables:  # TODO: delete once we're not calling twice
                ds = get_event_fn(self.event)(ds, **self.event_kwargs)
                ds = ds.rename({self.variable: f"{self.variable}_{self.event}"})

        # Clip to specified region
        if not check_spatial_attr(ds, region=self.region):
            # Only clip region if the dataframe hasn't already been clipped
            ds = clip_region(ds, grid=self.grid, region=self.region)
        if not check_spatial_attr(ds, mask=self.mask):
            # Only apply mask if this dataframe has not already been masked
            ds = apply_mask(ds, self.mask, grid=self.grid)

        # Assign attributes, preserving any existing ones (especially 'prob_type')
        attrs = dict(ds.attrs) if hasattr(ds, "attrs") else {}
        attrs.update({
            'agg_days': float(self.agg_days),
            'variable': self.variable,
        })
        if self.units is not None:
            attrs['units'] = self.units
        ds = ds.assign_attrs(attrs)
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
        lookbacks = pd.timedelta_range(start=f"-{lookback_days}D", end="-1D", freq='D')
        max_time = obs.time.max()
        min_time = obs.time.min() + pd.Timedelta(days=lookback_days)
        # Broadcast obs across init_time by assigning a dummy init_time coord,
        # then shift the time coordinate to prediction_timedelta space
        obs_broadcast = [obs.assign_coords(prediction_timedelta=lookback, time=obs.time - lookback).expand_dims("prediction_timedelta") for lookback in lookbacks.values]
        combined_obs = xr.concat(obs_broadcast, dim="prediction_timedelta").chunk({'prediction_timedelta': -1})

        # # Ensure we've done the proper selection of the observations
        # ds1 = obs.sel(time="2018-02-10")
        # import numpy as np
        # ds2 = combined.sel(init_time="2018-02-15", prediction_timedelta=np.timedelta64(-5, "D"))
        # import matplotlib.pyplot as plt
        # (ds1 - ds2).precip.plot(x='lon')

        combined_obs = combined_obs.sel(time=slice(min_time, max_time))
        combined_obs = combined_obs.rename({"time": "init_time"})
        combined_obs = combined_obs.sel(init_time=fcst.init_time)

        combined = xr.concat([fcst, combined_obs], dim="prediction_timedelta")
        combined = combined.sortby("prediction_timedelta")
        return combined

    def blend_fcst_and_obs_hold(self, fcst, obs, lookback_days=30):
        """Blend the forecast and observations.

        Args:
            fcst (xr.Dataset): The forecast dataset, indexed by init_time and prediction_timedelta.
            obs (xr.Dataset): The observations dataset, indexed by time.
            lookback_days (int): The number of days to look back, integer.

        Returns:
            xr.Dataset: The combined dataset, with -lookback days of observations added to the beginning of the forecast.
        """
        # Get the lookback periods for the observations
        lookbacks = pd.timedelta_range(start=f"-{lookback_days}D", end="-1D", freq='D')

        # Build a 2D DataArray of valid times
        lookback_times = xr.DataArray(
            fcst.init_time.values[:, None] + lookbacks.values[None, :],
            dims=["init_time", "prediction_timedelta"],
            coords={
                "init_time": fcst.init_time.values,
                "prediction_timedelta": lookbacks.values,
            }
        )
        # Select the observations
        obs_lookback = obs.sel(time=lookback_times)
        obs_lookback = obs_lookback.drop_vars('time')

        # Concat the observations and forecast
        combined = xr.concat([fcst, obs_lookback], dim="prediction_timedelta")
        combined = combined.sortby('prediction_timedelta')
        return combined
    def post_process(self, ds):
        """Post process the forecast.

        Enables blending the forecast and observations, event definition, conversion of init time to valid time, 
        and general spatial postprocessing, including region clipping and masking.
        """
        if not bool((ds.prediction_timedelta < 0).any()): # TODO: remove extra check once we're not calling twice
            if self.lookback_days is not None and self.lookback_data_source is not None \
                and isinstance(self.lookback_days, int):
                # Get the observations for forecast period + the lookback period
                new_start = shift_by_days(ds.init_time.values.min(), -self.lookback_days)
                new_end = ds.init_time.values.max()
                obs = get_data(self.lookback_data_source)(start_time=new_start, end_time=new_end,
                        variable=self.variable, grid=self.grid, mask=self.mask, region=self.region)
                ds = self.blend_fcst_and_obs(ds, obs, self.lookback_days)
                attrs = dict(ds.attrs) if hasattr(ds, "attrs") else {}
                attrs.update({
                    'lookback_days': self.lookback_days,
                    'lookback_data_source': self.lookback_data_source,
                })
                ds = ds.assign_attrs(attrs)

        # TODO: remove extra check once we're not calling twice
        if self.event is not None and f"{self.variable}_{self.event}" not in ds.variables:
            # Rename prediction timedelta event_time for event postprocessing
            ds = ds.rename({'prediction_timedelta': 'time'})

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
