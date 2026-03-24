"""A decorator for identifying data sources."""

import xarray as xr

from nuthatch.processor import NuthatchProcessor
from nuthatch import cache
from sheerwater.utils import convert_init_time_to_pred_time, add_spatial_attrs, check_spatial_attr, shift_by_days
from sheerwater.spatial_subdivisions import clip_region, apply_mask

import logging
logger = logging.getLogger(__name__)

# Global registry of data sources
DATA_REGISTRY = {}
FORECAST_REGISTRY = {}


class SheerwaterDataset(NuthatchProcessor):
    """Processor for a Sheerwater dataset, either forecast or data of a standard format.

    This processor is used to convert forecast with init time and prediction timedelta to a valid time coordinate.

    It also implements spatial clipping and masking, and timeseries filtering.

    It supports xarray datasets.
    """

    def __call__(self, func):
        """Call the parent class and register the data in the global data registry."""
        wrapped = super().__call__(func)
        self.fname = func.__name__
        return wrapped


    def __init__(self,  **kwargs):
        """Initialize the spatial processor.

        Args:
            kwargs: Additional keyword arguments to pass to the NuthatchProcessor.
        """
        super().__init__(**kwargs)

    def process_arguments(self, sig, *args, **kwargs):
        """Process the arguments for the datasets decorator."""
        # Get default values for the function signature
        bound_args = self.bind_signature(sig, *args, **kwargs)

        # Default arguments if they aren't passed or present in the default of the signature
        self.region = bound_args.arguments.get('region', 'global')
        self.mask = bound_args.arguments.get('mask', None)
        self.grid = bound_args.arguments.get('grid', 'global0_25')
        self.agg_days = bound_args.arguments.get('agg_days', 1)

        # If the arguments aren't in the signature we shouldn't pass them through as kwargs
        filtered_kwargs = kwargs.copy()
        for k, v in kwargs.items():
            if k in ['region', 'mask', 'grid', 'agg_days']:
                if k not in sig.parameters:
                    del filtered_kwargs[k]

        self.unique_key_args = {}
        for k, v in bound_args.arguments.items():
            if k not in ['start_time', 'end_time', 'region', 'mask', 'grid', 'agg_days']:
                self.unique_key_args[k] = v


        return args, filtered_kwargs

    def post_process(self, ds):
        """Post-process the dataset to implement masking and region clipping and timeseries postprocessing."""
        if not isinstance(ds, xr.Dataset) and ds is not None:
            raise RuntimeError(f"Sheerwater cannot post process data type {type(ds)}")

        if 'time' not in ds.dims:
            raise RuntimeError("All sheerwater datasets and forecasts must have a time dimension.")

        @cache(cache_args=['grid', 'regirdder_cache_key'],
               backend_kwargs={
                    'chunking': {'lat': 300, 'lon': 300, 'time': 365}
               })
        def internal_regrid(ds, grid, regridder_cache_key):
            ds = regrid(ds, grid, base='base180', method='conservative')

        # First we need to regrid to the requested grid if it is not on that grid already. This should be cached
        if 'grid' in ds.attrs and ds.attrs['grid'] == self.grid:
            # We are already on the right grid
            pass
        elif ('source_grid' in ds.attrs and ds.attrs['source_grid'] == self.grid) or self.grid == 'source':
            # We are on the source grid or the source grid has been requested
            pass
        else:
            # We need to regrid
            if 'lat' not in ds.dims or 'lon' not in ds.dims:
                raise RuntimeError("Only datasets with lat and lon dimensions can be regridded. For curved grids you can get the data on the 'source' grid only.")

            self.unique_key_args['function_name'] = self.fname
            ds = internal_regrid(ds, self.grid, unique_cache_key=self.unique_key_args)
            ds = ds.attrs.update({'grid': self.grid})

        # Then we need to aggregate to the requested agg days if it isn't aggregated already
        if 'agg_days' in ds.attrs and ds.attrs['agg_days'] == self.agg_days:
            # we are already at appropriate aggregation
            pass
        else:
            ds = roll_and_agg(ds, agg=self.agg_days, agg_col="time", agg_fn='mean')
            ds = ds.attrs.update({'agg_days': self.agg_days})

        # Then we need to mask and clip
        # Clip to specified region
        if not check_spatial_attr(ds, region=self.region):
            # Only clip region if the dataframe hasn't already been clipped
            ds = clip_region(ds, grid=self.grid, region=self.region)
        if not check_spatial_attr(ds, mask=self.mask):
            # Only apply mask if this dataframe has not already been masked
            ds = apply_mask(ds, self.mask, grid=self.grid)
        attrs = {
            'variable': self.variable,
        }

        #if self.units is not None:
        #    attrs['units'] = self.units
        ds = ds.assign_attrs(attrs)
        ds = add_spatial_attrs(ds, grid=self.grid, mask=self.mask, region=self.region)

        # Then we can add units to variables as appropriate
        #if self.variable == 'precip':
        #    self.units = 'mm / day'
        #elif self.variable == 'tmp2m':
        #    self.units = 'avg. daily C'
        #else:
        #    self.units = None

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
        wrapped = super().__call__(func)
        DATA_REGISTRY[func.__name__] = wrapped
        return wrapped

    def process_arguments(self, sig, *args, **kwargs):
        """Process the arguments for the data decorator."""
        args, kwargs = super().process_arguments(sig, *args, **kwargs)
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
        ds = super().post_process(ds)
        # Remove all unneeded dimensions
        ds = ds.drop_vars([var for var in ds.coords if var not in ['time', 'lat', 'lon', 'member', 'station_id']])
        return ds


class forecast(SheerwaterDataset):
    """Processor for a Sheerwater forecast. It supports xarray datasets."""

    def __call__(self, func):
        """Call the forecast decorator and register it in the global forecast registry."""
        wrapped = super().__call__(func)
        FORECAST_REGISTRY[func.__name__] = wrapped
        return wrapped

    def post_process(self, ds):
        """Convert the init time and prediction timedelta to a valid time coordinate labeled 'time'."""
        # # Convert the init time and prediction timedelta to a valid time coordinate labeled 'time'
        if 'init_time' in ds.coords and 'prediction_timedelta' in ds.coords:
            # If we haven't converted from init time to valid times, do so now
            ds = convert_init_time_to_pred_time(ds)

        # Implment masking and region clipping and timeseries postprocessing
        ds = super().post_process(ds)

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
