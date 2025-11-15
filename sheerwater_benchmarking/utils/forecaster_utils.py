"""Variable-related utility functions for all parts of the data pipeline."""

from functools import wraps
import numpy as np

from .space_utils import apply_mask, clip_region

# Global forecast registry
FORECAST_REGISTRY = {}


def forecast(func):
    """Decorator to mark a function as a forecast and concat the leads."""
    # Register the forecast in the global forecast registry when defined
    FORECAST_REGISTRY[func.__name__] = func

    @wraps(func)
    def forecast_wrapper(*args, **kwargs):
        ds = func(*args, **kwargs)
        try:
            # Create a new coordinate for valid_time, that is the start_date plus the lead time
            ds = convert_init_time_to_pred_time(ds)
            # Assign attributes
            ds = ds.assign_attrs(agg_days=float(kwargs['agg_days']))
            # Apply masking
            ds = apply_mask(ds, kwargs['mask'], grid=kwargs['grid'])
            # Clip to specified region
            ds = clip_region(ds, region=kwargs['region'])
        except Exception as e:
            import pdb
            pdb.set_trace()
        return ds
    return forecast_wrapper


def convert_init_time_to_pred_time(ds, init_time_dim='init_time',
                               lead_time_dim='prediction_timedelta', valid_time_dim='time'):
    """Convert the start_date and lead_time coordinates to a valid_time coordinate."""
    ds = ds.assign_coords({valid_time_dim: ds[init_time_dim] + ds[lead_time_dim]})
    tmp = ds.stack(z=(init_time_dim, lead_time_dim))
    tmp = tmp.set_index(z=(valid_time_dim, lead_time_dim))
    ds = tmp.unstack('z')
    ds = ds.rename({lead_time_dim: 'prediction_timedelta'})
    ds = ds.drop_vars(init_time_dim)
    return ds


def get_forecast(forecast_name):
    """Get a forecast from the global forecast registry."""
    return FORECAST_REGISTRY[forecast_name]


def get_variable(variable_name, variable_type='era5'):
    """Converts a variable in any other type to a variable name of the requested type."""
    variable_ordering = ['sheerwater', 'era5', 'ecmwf_hres', 'ecmwf_ifs_er', 'salient', 'abc', 'ghcn']

    weather_variables = [
        # Static variables (2):
        ('z', 'geopotential', 'geopotential', None, None, None, None),
        ('lsm', 'land_sea_mask', 'land_sea_mask', None, None, None, None),

        # Surface variables (6):
        ('tmp2m', '2m_temperature', '2m_temperature', '2m_temperature', 'temp', 'tmp2m', 'temp'),
        ('precip', 'total_precipitation', 'total_precipitation_6hr', 'total_precipitation_24hr',
         'precip', 'precip', 'precip'),
        ("vwind10m", "10m_v_component_of_wind", "10m_v_component_of_wind", None, None, None, None),
        ("uwind10m", "10m_u_component_of_wind", "10m_u_component_of_wind", None, None, None, None),
        ("msl", "mean_sea_level_pressure", "mean_sea_level_pressure", None, None, None, None),
        ("tisr", "toa_incident_solar_radiation", "toa_incident_solar_radiation", None, "tsi", None, None),
        ("ssrd", "surface_solar_radiation_downwards", None, None, "tsi", None, None),

        # Atmospheric variables (6):
        ("tmp", "temperature", "temperature", None, None, None, None),
        ("uwind", "u_component_of_wind", "u_component_of_wind", None, None, None, None),
        ("vwind", "v_component_of_wind", "v_component_of_wind", None, None, None, None),
        ("hgt", "geopotential", "geopotential", None, None, None, None),
        ("q", "specific_humidity", "specific_humidity", None, None, None, None),
        ("w", "vertical_velocity", "vertical_velocity", None, None, None, None),
    ]

    name_index = variable_ordering.index(variable_type)

    for tup in weather_variables:
        for name in tup:
            if name == variable_name:
                val = tup[name_index]
                if val is None:
                    raise ValueError(f"Variable {variable_name} not implemented.")
                return val

    raise ValueError(f"Variable {variable_name} not found")
