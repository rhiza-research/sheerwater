"""A decorator for identifying data sources."""
from functools import wraps
from inspect import signature

import xarray as xr

from nuthatch.processor import NuthatchProcessor
from sheerwater.utils import convert_init_time_to_pred_time, clip_region, apply_mask

import logging
logger = logging.getLogger(__name__)

# Global registry of data sources
DATA_REGISTRY = {}
FORECAST_REGISTRY = {}

class SheerwaterDataset(NuthatchProcessor):
    """
    Processor for a Sheerwater dataset, either forecast or data of a standard format. 

    This processor is used to convert forecast with init time and prediction timedelta to a valid time coordinate.

    It also implements spatial clipping and masking, and timeseries filtering.

    It supports xarray datasets.
    """

    def __init__(self, region_dim=None, **kwargs):
        """
        Initialize the spatial processor.

        Args:
            region_dim: The name of the region dimension. If None, the returned dataset will not be 
                assumed to have a region dimesion and region data will be fetched from the region registry
                before clipping.
        """
        super().__init__(**kwargs)
        self.region_dim = region_dim

    def process_arguments(self, sig, *args, **kwargs):
        # Get default values for the function signature
        bound_args = self.bind_signature(sig, *args, **kwargs)

        # Default to global region and no masking if not passed
        self.region = bound_args.arguments.get('region', 'global')
        self.mask = bound_args.arguments.get('mask', None)
        try:
            self.grid = bound_args.arguments['grid']
            self.agg_days = bound_args.arguments['agg_days']
            self.variable = bound_args.arguments['variable']
        except KeyError:
            raise ValueError("Forecast decorator requires grid, agg_days, and variable to be passed.")

        if self.variable == 'precip':
            self.units = 'mm / day'
        elif self.variable == 'tmp2m':
            self.units = 'avg. daily C'
        else:
            self.units = None
        return args, kwargs

    def post_process(self, ds):
        if isinstance(ds, xr.Dataset):
            # Clip to specified region
            ds = clip_region(ds, region=self.region, region_dim=self.region_dim)
            ds = apply_mask(ds, self.mask, grid=self.grid)
            attrs = {
                'agg_days': float(self.agg_days),
                'variable': self.variable,
                'grid': self.grid,
                'mask': self.mask,
                'region': self.region
            }
            if self.units is not None:
                attrs['units'] = self.units
            ds = ds.assign_attrs(attrs)

        else:
            raise RuntimeError(f"Cannot clip by region and mask for data type {type(ds)}")
        return ds

    def validate(self, ds):
        # Check to see if the dataset extends roughly the full time series set
        test = clip_region(ds, region=self.region, region_dim=self.region_dim)
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
        wrapped = super().__call__(func)
        DATA_REGISTRY[func.__name__] = wrapped
        return wrapped

    def post_process(self, ds):
        # Implment masking and region clipping and timeseries postprocessing
        ds = super().post_process(ds)

        # Remove all unneeded dimensions
        ds = ds.drop_vars([var for var in ds.coords if var not in [
                            'time', 'lat', 'lon']])
        return ds

class forecast(SheerwaterDataset):
    """Processor for a Sheerwater forecast. It supports xarray datasets."""
    def __call__(self, func):
        wrapped = super().__call__(func)
        FORECAST_REGISTRY[func.__name__] = wrapped
        return wrapped

    def post_process(self, ds):
        # # Convert the init time and prediction timedelta to a valid time coordinate labeled 'time'
        if 'init_time' in ds.coords and 'prediction_timedelta' in ds.coords:
            # If we haven't converted from init time to valid times, do so now
            ds = convert_init_time_to_pred_time(ds)

        # Implment masking and region clipping and timeseries postprocessing
        ds = super().post_process(ds)

        # Remove all unneeded dimensions
        ds = ds.drop_vars([var for var in ds.coords if var not in [
                            'time', 'prediction_timedelta', 'lat', 'lon', 'member']])
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
    import sheerwater.forecasts # noqa: F401
    import sheerwater.climatology # noqa: F401
    return list(FORECAST_REGISTRY.keys())


def get_data(data_name):
    """Get a data source from the global data registry."""
    # The imports below ensure that all forecast modules are registered when this is called.
    import sheerwater.data # noqa: F401
    import sheerwater.climatology # noqa: F401
    import sheerwater.reanalysis # noqa: F401
    return DATA_REGISTRY[data_name]


def list_data():
    """List all data sources in the global data registry."""
    # The imports below ensure that all forecast modules are registered when this is called.
    import sheerwater.data # noqa: F401
    import sheerwater.climatology # noqa: F401
    import sheerwater.reanalysis # noqa: F401
    return list(DATA_REGISTRY.keys())
