"""A decorator for identifying data sources."""
from functools import wraps
from inspect import signature

from sheerwater.utils import apply_mask, clip_region

# Global registry of data sources
DATA_REGISTRY = {}

def data(func):
    """Decorator to mark a function as a data source."""
    # Get function signature to access default values
    sig = signature(func)

    @wraps(func)
    def data_wrapper(*args, **kwargs):
        try:
            ds = func(*args, **kwargs)
            # Filter kwargs to only include parameters in the function signature
            # This allows other decorators to pass additional arguments
            sig_params = set(sig.parameters.keys())
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig_params}
            # Bind arguments to get all parameter values including defaults
            bound_args = sig.bind(*args, **filtered_kwargs)
            bound_args.apply_defaults()

            # Get mask, region, and grid from bound args (includes defaults)
            grid = bound_args.arguments.get('grid', 'global0_25')
            mask = bound_args.arguments.get('mask', 'lsm')
            region = bound_args.arguments.get('region', 'global')
            agg_days = bound_args.arguments.get('agg_days')
            variable = bound_args.arguments.get('variable')
            units = 'mm' if variable == 'precip' else 'C'

            # Apply masking
            ds = apply_mask(ds, mask, grid=grid)
            # Clip to specified region
            ds = clip_region(ds, region=region)
            # Remove all unneeded dimensions
            ds = ds.drop_vars([var for var in ds.coords if var not in [
                              'time', 'lat', 'lon']])
            # Assign attributes
            ds = ds.assign_attrs({'agg_days': float(agg_days),
                                  'variable': variable,
                                  'units': units,
                                  'grid': grid,
                                  'mask': mask,
                                  'region': region})

        except Exception as e:
            raise ValueError(f"Error in data source {func.__name__}: {e}")
        return ds

    # Register the forecast in the global forecast registry when defined
    DATA_REGISTRY[func.__name__] = data_wrapper
    return data_wrapper


def get_data(data_name):
    """Get a forecast from the global forecast registry."""
    return DATA_REGISTRY[data_name]

def list_data():
    """List all data sources in the global data registry."""
    return list(DATA_REGISTRY.keys())
