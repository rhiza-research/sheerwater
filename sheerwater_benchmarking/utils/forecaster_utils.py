"""Variable-related utility functions for all parts of the data pipeline."""

from datetime import datetime
from functools import wraps
import dateparser
import pandas as pd
import numpy as np

# Global forecast registry
FORECAST_REGISTRY = {}


def forecast(func):
    """Decorator to mark a function as a forecast and concat the leads."""
    # Register the forecast in the global forecast registry when defined
    FORECAST_REGISTRY[func.__name__] = func

    @wraps(func)
    def forecast_wrapper(*args, **kwargs):
        ds = func(*args, **kwargs)
        ds = ds.assign_attrs(agg_days=float(kwargs['agg_days']))
        return ds
    return forecast_wrapper


def convert_lead_to_valid_time(ds, initialization_time_dim='initialization_time',
                               lead_time_dim='prediction_timedelta', valid_time_dim='valid_time'):
    """Convert the start_date and lead_time coordinates to a valid_time coordinate."""
    ds = ds.assign_coords({valid_time_dim: ds[initialization_time_dim] + ds[lead_time_dim]})
    tmp = ds.stack(z=(initialization_time_dim, lead_time_dim))
    tmp = tmp.set_index(z=(valid_time_dim, lead_time_dim))
    ds = tmp.unstack('z')
    ds = ds.rename({lead_time_dim: 'prediction_timedelta'})
    ds = ds.drop_vars(initialization_time_dim)
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


def get_lead_group(lead):
    """Get the lead group for a lead."""
    if lead in ['weekly', 'biweekly', 'monthly', 'quarterly'] or 'daily-' in lead:
        return lead
    elif 'day' in lead:
        return f'daily-{lead[3:]}'
    elif 'weeks' in lead:
        return 'biweekly'
    elif 'week' in lead and 'weeks' not in lead:
        return 'weekly'
    elif 'month' in lead:
        return 'monthly'
    elif 'quarter' in lead:
        return 'quarterly'
    else:
        raise ValueError(f"Lead {lead} not supported")


def get_lead_info(lead):
    """Get lead information.

    Support leads are
    - weekly
    - biweekly
    - monthly
    - quarterly
    - daily-n, where n is the number of days from day1 to dayn
    - week1, week2, week3, week4, week5, week6
    - weeks12, weeks23, weeks34, weeks45, weeks56
    - month1, month2, month3
    """
    if lead == 'weekly':
        return {
            'agg_period': np.timedelta64(7, 'D'),
            'agg_days': 7,
            'lead_offsets': [np.timedelta64(0, 'D'), np.timedelta64(7, 'D'), np.timedelta64(14, 'D'), np.timedelta64(21, 'D'), np.timedelta64(28, 'D'), np.timedelta64(35, 'D')],  # noqa: E501 <- line too long
            'labels': ['week1', 'week2', 'week3', 'week4', 'week5', 'week6'],
        }
    elif lead == 'biweekly':
        return {
            'agg_period': np.timedelta64(14, 'D'),
            'agg_days': 14,
            'lead_offsets': [np.timedelta64(0, 'D'), np.timedelta64(7, 'D'), np.timedelta64(14, 'D'), np.timedelta64(21, 'D'), np.timedelta64(28, 'D')],  # noqa: E501 <- line too long
            'labels': ['weeks12', 'weeks23', 'weeks34', 'weeks45', 'weeks56'],
        }
    elif lead == 'monthly':
        return {
            'agg_period': np.timedelta64(30, 'D'),
            'agg_days': 30,
            'lead_offsets': [np.timedelta64(0, 'D'), np.timedelta64(30, 'D'), np.timedelta64(60, 'D')],
            'labels': ['month1', 'month2', 'month3'],
        }
    elif lead == 'quarterly':
        return {
            'agg_period': np.timedelta64(90, 'D'),
            'agg_days': 90,
            'lead_offsets': [np.timedelta64(0, 'D'), np.timedelta64(90, 'D'), np.timedelta64(180, 'D'), np.timedelta64(270, 'D')],  # noqa: E501 <- line too long
            'labels': ['quarter1', 'quarter2', 'quarter3', 'quarter4'],
        }
    elif 'daily' in lead:
        if '-' not in lead:
            raise ValueError(f"Daily lead {lead} must be in the format 'daily-n', {lead} is not valid")
        days = int(lead.split('-')[1])
        if days < 1 or days > 366:
            raise ValueError(f"Daily lead {lead} must be between 1 and 366 days, got {days}")
        return {
            'agg_period': np.timedelta64(1, 'D'),
            'agg_days': 1,
            'lead_offsets': [np.timedelta64(i, 'D') for i in range(days)],
            'labels': [f'day{i}' for i in range(1, days + 1)],
        }
    elif 'day' in lead or 'week' in lead or 'month' in lead or 'quarter' in lead:
        if 'day' in lead:
            day_num = int(lead[3:])
            if day_num < 1 or day_num > 366:
                raise ValueError(f"Day lead {lead} must be between day1 and day366, got day{day_num}")
            ret = get_lead_info('daily')
        elif 'week' in lead and 'weeks' not in lead:
            week_num = int(lead[4:])
            if week_num < 1 or week_num > 52:
                raise ValueError(f"Week lead {lead} must be between week1 and week52, got week{week_num}")
            ret = get_lead_info('weekly')
        elif 'weeks' in lead:
            week_num = int(lead[5])
            second_week_num = int(lead[6])
            if second_week_num != week_num + 1:
                raise ValueError(
                    f"Biweekly lead {lead} must be be of the format weeks(n)(n+1), e.g., weeks56")
            if week_num < 1 or week_num > 52 or second_week_num < 1 or second_week_num > 52:
                raise ValueError(f"Biweekly lead {lead} must be between weeks12 and weeks52, got weeks{week_num}")
            ret = get_lead_info('biweekly')
        elif 'month' in lead:
            month_num = int(lead[5:])
            if month_num < 1 or month_num > 12:
                raise ValueError(f"Month lead {lead} must be between month1 and month12, got month{month_num}")
            ret = get_lead_info('monthly')
        elif 'quarter' in lead:
            quarter_num = int(lead[7:])
            if quarter_num < 1 or quarter_num > 4:
                raise ValueError(f"Quarter lead {lead} must be between quarter1 and quarter4, got quarter{quarter_num}")
            ret = get_lead_info('quarterly')
        # Now get specific lead information
        lead_index = ret['labels'].index(lead)
        lead_offset = ret['lead_offsets'][lead_index]
        data = ret.copy()
        data['lead_offsets'] = [lead_offset]
        data['labels'] = [lead]
        return data
    else:
        raise ValueError(f"Lead {lead} not supported")
