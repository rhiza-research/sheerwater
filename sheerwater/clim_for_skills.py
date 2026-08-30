"""Simplified daily climatologies (mean + variance) for skills.
"""

import numpy as np
import xarray as xr
from nuthatch import cache

from sheerwater.interfaces import forecast as sheerwater_forecast, spatial, get_data, get_forecast
from sheerwater.utils import (
    add_dayofyear,
    dask_remote,
    get_dates,
    pad_with_leapdays,
)


@dask_remote
@spatial()
@cache(cache_args=['data_name', 'variable', 'first_year', 'last_year', 'grid', 'mask', 'region'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "dayofyear": 1000, "prediction_timedelta": 1},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, 'dayofyear': 30, 'prediction_timedelta': 1}
               }
           }
})
def clim_stats_raw(data_name, variable, first_year=1985, last_year=2014, is_forecast=False,
                    grid='global1_5', mask=None, region='global'):
    """Compute the per-day-of-year climatological mean and variance for a data source.

    Returns:
        xr.Dataset: Dataset with a `dayofyear` dimension (and `prediction_timedelta`,
            if `is_forecast=True`) containing `{variable}` (climatological mean) and
            `{variable}_variance` (climatological variance).
    """
    data_fn = get_forecast(data_name) if is_forecast else get_data(data_name)

    start_time = f"{first_year}-01-01"
    end_time = f"{last_year}-12-31"
    ds = data_fn(start_time, end_time, variable=variable, agg_days=1, grid=grid, mask=mask, region=region)
    ds = ds[[variable]]

    try:
        ds = add_dayofyear(ds)
        ds = pad_with_leapdays(ds)
    except KeyError:
        raise ValueError(f"Underlying data source {data_name} does not have full coverage "
                         f"of the climatology period {first_year}-{last_year}.")

    grouped = ds.groupby('dayofyear')
    mean_ds = grouped.mean(dim='time', skipna=True)
    var_ds = grouped.var(dim='time', skipna=True).rename({variable: f"{variable}_variance"})
    ds = xr.merge([mean_ds, var_ds])
    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache_args=['variable', 'data_name', 'first_year', 'last_year',
                   'forecast_lead_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'prediction_timedelta': 1}})
def clim_daily(start_time, end_time, variable, data_name, agg_days=1,  # noqa: ARG001
                first_year=1985, last_year=2014, is_forecast=False,
                forecast_lead_days=None, prob_type='deterministic',  # noqa: ARG001
                grid='global0_25', mask='lsm', region='global'):
    """Standard-format daily climatology forecast (mean + variance) for a given data source.
    """
    raw = clim_stats_raw(data_name, variable, first_year=first_year, last_year=last_year,
                         is_forecast=is_forecast, grid=grid, mask=mask, region=region)

    target_dates = get_dates(start_time, end_time, stride='day', return_string=False)
    time_ds = add_dayofyear(xr.Dataset({'time': target_dates}))

    ds = raw.sel(dayofyear=time_ds.dayofyear)
    ds = ds.drop_vars('dayofyear')
    ds = ds.assign_attrs(prob_type="deterministic")

    if is_forecast:
        # forecast already has leads.
        ds = ds.sel(time=slice(start_time, end_time))
    else:
        # climatology is lead independent, so create synthetic leads.
        leads = [np.timedelta64(x, "D").astype('timedelta64[ns]') for x in range(0, forecast_lead_days)]
        ds = ds.expand_dims({"prediction_timedelta": leads})
        ds = ds.sel(time=slice(start_time, end_time))

    ds = ds.chunk({'lat': 121, 'lon': 240, 'prediction_timedelta': 1})
    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'prediction_timedelta': 1}})
def clim_era5(variable, agg_days=1,  # noqa: ARG001
              prob_type='deterministic',  # noqa: ARG001
              grid='global0_25', mask='lsm', region='global'):
    """Daily ERA5 climatology (mean + variance), 1990-2019.
    """
    return clim_daily('1904-01-01', '1904-12-31', variable, data_name='era5',
                      first_year=1990, last_year=2019, is_forecast=False,
                      forecast_lead_days=46, grid=grid, mask=mask, region=region)


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'prediction_timedelta': 1}})
def clim_imerg(variable, agg_days=1,  # noqa: ARG001
               prob_type='deterministic',  # noqa: ARG001
               grid='global0_25', mask='lsm', region='global'):
    """Daily IMERG climatology (mean + variance), 1998-2024.
    """
    return clim_daily('1904-01-01', '1904-12-31', variable, data_name='imerg_final',
                      first_year=1998, last_year=2024, is_forecast=False,
                      forecast_lead_days=46, grid=grid, mask=mask, region=region)


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'prediction_timedelta': 1}})
def clim_chirps(variable, agg_days=1,  # noqa: ARG001
                prob_type='deterministic',  # noqa: ARG001
                grid='global0_25', mask='lsm', region='global'):
    """Daily CHIRPS v3 climatology (mean + variance), 1998-2024.
    """
    return clim_daily('1904-01-01', '1904-12-31', variable, data_name='chirps_v3',
                      first_year=1998, last_year=2024, is_forecast=False,
                      forecast_lead_days=46, grid=grid, mask=mask, region=region)


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'prediction_timedelta': 1}})
def clim_ecmwf_ifs_er(variable, agg_days=1,  # noqa: ARG001
                      prob_type='deterministic',  # noqa: ARG001
                      grid='global0_25', mask='lsm', region='global'):
    """Daily, per-lead ECMWF IFS extended-range climatology (mean + variance), 2018-2022.
    """
    return clim_daily('1904-01-01', '1904-12-31', variable, data_name='ecmwf_ifs_er',
                      first_year=2018, last_year=2022, is_forecast=True,
                      forecast_lead_days=None, grid=grid, mask=mask, region=region)
