# ruff: noqa: E501

"""Variable-related utility functions for all parts of the data pipeline."""
import xarray as xr


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


def convert_pred_time_to_init_time(ds, time_dim='time',
                                   lead_time_dim='prediction_timedelta', init_time_dim='init_time'):
    """The inverse of the above. Converts a valid time to an init time for a specific prediction timedelta."""
    ds = ds.assign_coords({init_time_dim: ds[time_dim] - ds[lead_time_dim]})
    tmp = ds.stack(z=(time_dim, lead_time_dim))
    tmp = tmp.set_index(z=(init_time_dim, lead_time_dim))
    ds = tmp.unstack('z')
    ds = ds.rename({lead_time_dim: 'prediction_timedelta'})
    ds = ds.drop_vars(time_dim)
    return ds


def desnify_fcst(fcst):
    """Desnify the forecast."""
    if not isinstance(fcst, xr.Dataset):
        raise ValueError(f"fcst must be an xarray dataset. Received {type(fcst)}.")

    # Figure out which input mode the data is in
    if 'init_time' not in fcst.coords and 'prediction_timedelta' in fcst.coords:
        mode = 'init_time'
    elif 'time' in fcst.coords and 'prediction_timedelta' in fcst.coords:
        mode = 'time'
    else:
        raise ValueError("Forecast is not in standard mode.")

    if mode == 'init_time':
        # Convert to time mode
        start_time = fcst.time.values.min()
        end_time = fcst.time.values.max()
        fcst = convert_init_time_to_pred_time(fcst)
    else:
        temp = convert_pred_time_to_init_time(fcst)
        start_time = temp.init_time.values.min()
        end_time = temp.init_time.values.max()

    # Forward fill NaNs along the prediction_timedelta dimension, takes the `staler` value for the same timepoint
    fcst = fcst.bfill(dim='prediction_timedelta')
    # Forward fill NaNs along the time dimension, takes the 'staler' value for the same timepoint
    # This covers what happens off the end of the forecast period from the previous init time, where
    # there are no values to fill backwards from
    fcst = fcst.ffill(dim='time')

    # Convert back to init time
    fcst = convert_pred_time_to_init_time(fcst)

    # Trim back to origional start and end times, b/c the conversion will add new times at
    fcst = fcst.sel(init_time=slice(start_time, end_time))
    return fcst


def get_variable(variable_name, variable_type='era5'):
    """Converts a variable in any other type to a variable name of the requested type."""
    variable_ordering = ['sheerwater', 'era5', 'ecmwf_hres', 'ecmwf_ifs_er', 'salient', 'abc', 'ghcn', 'era5_land']

    weather_variables = [
        # Static variables (2):
        ('z', 'geopotential', 'geopotential', None, None, None, None, None),
        ('lsm', 'land_sea_mask', 'land_sea_mask', None, None, None, None, None),

        # Surface variables (6):
        ('tmp2m', '2m_temperature', '2m_temperature', '2m_temperature', 'temp', 'tmp2m', 'temp', 't2m'),
        ("d2m", "2m_dewpoint_temperature", '2m_dewpoint_temperature', '2m_dewpoint_temperature', None, None, None, 'd2m'),
        # relative humidity at surface isn't natively supported in ERA5, derived from d2m and tmp2m
        ("rh2m", None, None, None, None, None, None, None),
        ('precip', 'total_precipitation', 'total_precipitation_6hr', 'total_precipitation_24hr',
         'precip', 'precip', 'precip', 'tp'),
        ("tcwv", "total_column_water_vapour", "total_column_water_vapour", None, None, None, None, None),
        ("vwind10m", "10m_v_component_of_wind", "10m_v_component_of_wind", None, None, None, None, 'v10'),
        ("uwind10m", "10m_u_component_of_wind", "10m_u_component_of_wind", None, None, None, None, 'u10'),
        ("msl", "mean_sea_level_pressure", "mean_sea_level_pressure", None, None, None, None, None),
        ("tisr", "toa_incident_solar_radiation", "toa_incident_solar_radiation", None, "tsi", None, None, 'ssr'),
        ("ssrd", "surface_solar_radiation_downwards", None, None, "tsi", None, None, 'ssrd'),

        # Atmospheric variables (6):
        ("tmp", "temperature", "temperature", None, None, None, None, None),
        ("uwind", "u_component_of_wind", "u_component_of_wind", None, None, None, None, None),
        ("vwind", "v_component_of_wind", "v_component_of_wind", None, None, None, None, None),
        ("hgt", "geopotential", "geopotential", None, None, None, None, None),
        ("w", "vertical_velocity", "vertical_velocity", None, None, None, None, None),
        ("q", "specific_humidity", "specific_humidity", None, None, None, None, None),
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
