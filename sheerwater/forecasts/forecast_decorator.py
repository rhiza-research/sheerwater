"""A utility for decorating forecasts."""
from functools import wraps
from inspect import signature

from sheerwater.utils import apply_mask, clip_region, convert_init_time_to_pred_time

# Global forecast registry
FORECAST_REGISTRY = {}

def forecast(func):
    """Decorator to mark a function as a forecast and concat the leads."""
    # Register the forecast in the global forecast registry when defined

    # Get function signature to access default values
    sig = signature(func)

    @wraps(func)
    def forecast_wrapper(*args, **kwargs):
        try:
            ds = func(*args, **kwargs)
            # Filter kwargs to only include parameters in the function signature
            # This allows other decorators to pass additional arguments
            sig_params = set(sig.parameters.keys())
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig_params}
            # Bind arguments to get all parameter values including defaults
            bound_args = sig.bind(*args, **filtered_kwargs)
            bound_args.apply_defaults()

            # Get mask, region, grid, and agg_days from bound args (includes defaults)
            mask = bound_args.arguments.get('mask')
            grid = bound_args.arguments.get('grid')
            region = bound_args.arguments.get('region')
            agg_days = bound_args.arguments.get('agg_days')
            variable = bound_args.arguments.get('variable')
            units = 'mm' if variable == 'precip' else 'C'

            # Create a new coordinate for valid_time, that is the start_date plus the lead time
            ds = convert_init_time_to_pred_time(ds)
            # Apply masking
            ds = apply_mask(ds, mask, grid=grid)
            # Clip to specified region
            ds = clip_region(ds, region=region)
            # Remove all unneeded dimensions
            ds = ds.drop_vars([var for var in ds.coords if var not in [
                              'time', 'prediction_timedelta', 'lat', 'lon', 'member']])

            # Assign attributes
            ds = ds.assign_attrs({'agg_days': float(agg_days),
                                  'variable': variable,
                                  'units': units,
                                  'grid': grid,
                                  'mask': mask,
                                  'region': region})


        except Exception as e:
            raise ValueError(f"Error in forecast {func.__name__}: {e}")
        return ds

    FORECAST_REGISTRY[func.__name__] = forecast_wrapper
    return forecast_wrapper

def get_forecast(forecast_name):
    """Get a forecast from the global forecast registry."""
    return FORECAST_REGISTRY[forecast_name]

def list_forecasts():
    """List all forecasts in the global forecast registry."""
    return list(FORECAST_REGISTRY.keys())
