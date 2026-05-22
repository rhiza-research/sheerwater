"""Functions to fetch and process data from the ECMWF WeatherBench dataset."""
import numpy as np
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, get_variable, lon_base_change, regrid, shift_by_days
from sheerwater.interfaces import forecast as sheerwater_forecast, spatial


@dask_remote
@spatial()
@timeseries(timeseries=['init_time'])
@cache(cache=True,
       cache_args=['variable', 'prob_type', 'grid'],
       backend_kwargs={'chunking': {"lat": 300, "lon": 300, "prediction_timedelta": 10, "init_time": 25}})
def hres_raw(start_time, end_time, variable='precip', prob_type='deterministic', # noqa: ARG001
                grid="global0_25", mask=None, region='global'): # noqa: ARG001
    """Fetches IFS ENS from the weatherbench bucket."""
    filepath = 'gs://weatherbench2/datasets/hres/2016-2022-0012-1440x721.zarr/'

    # Pull the google dataset
    ds = xr.open_zarr(filepath, decode_timedelta=True, chunks={})
    ds = ds.rename({'latitude': 'lat', 'longitude': 'lon', 'time': 'init_time'})

    # Resample time to 1 day
    ds = ds.where(ds.init_time.dt.hour == 0, drop=True)

    # Convert to base180 longitude
    ds = lon_base_change(ds, to_base="base180")

    # Select the right variable
    var = get_variable(variable, 'ecmwf_ifs_er')
    ds = ds[[var]]

    variable = get_variable(var, 'sheerwater')
    ds = ds.rename_vars(name_dict={var: variable})

    # Perform unit conversions if a specific variable is requested
    if variable in ['tmp2m', 'tmax2m', 'tmin2m']:
        ds[variable] = ds[variable] - 273.15
        ds[variable].attrs.update(units='C')
        ds = ds.resample(prediction_timedelta='1D').mean(dim='prediction_timedelta')
    elif variable == 'precip':
        ds[variable] = ds[variable] * 1000.0
        ds[variable].attrs.update(units='mm')
        ds[variable] = np.maximum(ds[variable], 0)
        # Sicne we are getting the 24 hr precip variable
        # Resample time to 1 day
        ds = ds.where(ds.prediction_timedelta.dt.hour == 0, drop=True)
    elif variable == 'ssrd':
        ds[variable].attrs.update(units='Joules/m^2')
        ds = np.maximum(ds, 0)
        ds = ds.resample(prediction_timedelta='1D').mean(dim='prediction_timedelta')
    else:
        # Just do a daily average for variables we don't know
        ds = ds.resample(prediction_timedelta='1D').mean(dim='prediction_timedelta')


    # Shift lead time to the right by 1 day
    ds['prediction_timedelta'] = ds['prediction_timedelta'] - np.timedelta64(24, 'h')
    ds = ds.isel(prediction_timedelta=slice(1,None))

    # Average the member if necessary
    if prob_type != 'deterministic':
        raise ValueError("Only deterministic hres is supported.")

    # Regrid if necessary
    if grid == 'global0_25':
        pass
    else:
        ds = regrid(ds, grid, base='base180', method='conservative')

    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'event', 'event_kwargs', 'lookback_source', 'densify',
                   'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'lead_time': 1, 'member': 1}})
def ecmwf_hres(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic', # noqa: ARG001
                event=None, event_kwargs=None,  # noqa: ARG001
                lookback_source=None, densify=False,  # noqa: ARG001
                 grid='global0_25', mask='lsm', region="global"):
    """Standard format forecast data for ECMWF forecasts."""
    forecast_start = shift_by_days(start_time, -10) if start_time is not None else None
    forecast_end = shift_by_days(end_time, 10) if end_time is not None else None

    return hres_raw(start_time=forecast_start, end_time=forecast_end, variable=variable,
                       prob_type=prob_type,
                       grid=grid, mask=mask, region=region)
