"""A decorator for identifying data sources."""
from functools import wraps
from inspect import signature

from sheerwater.utils import convert_init_time_to_pred_time

# Global registry of data sources
DATA_REGISTRY = {}
FORECAST_REGISTRY = {}


def bind_signature(sig, *args, **kwargs):
    """Utility function to bind the function signature to the default values"""
    sig_params = set(sig.parameters.keys())
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig_params}
    # Bind arguments to get all parameter values including defaults
    bound_args = sig.bind(*args, **filtered_kwargs)
    bound_args.apply_defaults()
    return bound_args


def data(func):
    """Decorator to mark a function as a data source."""
    # Get function signature to access default values
    sig = signature(func)

    @wraps(func)
    def data_wrapper(*args, **kwargs):
        try:
            ds = func(*args, **kwargs)

            # Get the set of arguments, enhanced with default values, from the function signature
            bound_args = bind_signature(sig, *args, **kwargs)

            # Get mask, region, and grid from bound args (includes defaults)
            grid = bound_args.arguments.get('grid')
            mask = bound_args.arguments.get('mask')
            region = bound_args.arguments.get('region')
            agg_days = bound_args.arguments.get('agg_days')
            variable = bound_args.arguments.get('variable')
            units = 'mm / day' if variable == 'precip' else 'avg. daily C'

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

    # Register the data source in the global data registry when defined
    DATA_REGISTRY[func.__name__] = data_wrapper
    return data_wrapper


def get_data(data_name):
    """Get a data source from the global data registry."""
    return DATA_REGISTRY[data_name]


def list_data():
    """List all data sources in the global data registry."""
    return list(DATA_REGISTRY.keys())


def forecast(func):
    """Decorator to mark a function as a forecast and concat the leads."""
    # Register the forecast in the global forecast registry when defined

    # Get function signature to access default values
    sig = signature(func)

    @wraps(func)
    def forecast_wrapper(*args, **kwargs):
        try:
            ds = func(*args, **kwargs)
            # Get the set of arguments, enhanced with default values, from the function signature
            bound_args = bind_signature(sig, *args, **kwargs)

            # Get mask, region, grid, and agg_days from bound args (includes defaults)
            mask = bound_args.arguments.get('mask')
            grid = bound_args.arguments.get('grid')
            region = bound_args.arguments.get('region')
            agg_days = bound_args.arguments.get('agg_days')
            variable = bound_args.arguments.get('variable')
            units = 'mm / day' if variable == 'precip' else 'avg. daily C'

            # Create a new coordinate for valid_time, that is the start_date plus the lead time
            ds = convert_init_time_to_pred_time(ds)
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
