"""KMD WRF forecast."""

import os
import pandas as pd
import dask
import gcsfs
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries
from sheerwater.interfaces import forecast as sheerwater_forecast, spatial

from sheerwater.utils import dask_remote, get_dates, regrid, roll_and_agg, shift_by_days


@dask_remote
@cache(cache_args=['date', 'forecast_type'],
       backend_kwargs={'chunking': {'lat': 350, 'lon': 300, 'lead_time': 60, 'time': 1}})
def kmd_wrf_raw(date, forecast_type='weekly'):
    """KMD WRF forecast."""
    if forecast_type == 'weekly':
        days = 7
    elif forecast_type == 'daily':
        days = 1
    else:
        raise ValueError(f"Forecast type {forecast_type} not implemented.")

    time = pd.to_datetime(date)
    end_date = time + pd.Timedelta(days=days)
    filepath = f'gs://sheerwater-datalake/kmd-data/wrf/{time.strftime("%Y%m%d")}_to_{end_date.strftime("%Y%m%d")}_fcst.nc'

    # Clone the file locally to open
    # This is necessary because xarray doesn't support an engine that will open old netcdf4 file
    # on the cloud. Must be a local file.
    fs = gcsfs.GCSFileSystem(project='sheerwater', token='google_default')
    try:
        fs.get(filepath, '/tmp/kmd_wrf.nc')
    except FileNotFoundError:
        return None

    ds = xr.open_dataset('/tmp/kmd_wrf.nc', engine='netcdf4')

    # Remove 1-dimensional level dimension
    ds = ds.squeeze('lev').drop('lev')

    # Drop cumulus precipitation variable
    ds = ds.drop('rainc')

    # Rename variables to standard names
    ds = ds.rename({
        'rainnc': 'precip',
        't2': 'tmp2m',
        'time': 'lead_time',
    })

    # Convert variables
    K_const = 273.15
    ds['tmp2m'] = ds['tmp2m'] - K_const

    # Rain is accumulated in mm; return the difference between each subsequent time
    ds['precip'] = ds['precip'].diff('time')

    # Expand the dataset to add a time dimension corresponding to the first lead_time (lead_time==0)
    first_time_val = ds['lead_time'].values[0]
    ds = ds.expand_dims({'time': [first_time_val]})
    ds = ds.assign_coords({'time': [pd.to_datetime(date)]})

    # Ensure data is in memory and remove the temp file
    ds = ds.compute()
    os.remove('/tmp/kmd_wrf.nc')
    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['variable', 'grid', 'forecast_type'],
       backend_kwargs={'chunking': {'lat': 350, 'lon': 300, 'time': 60, 'prediction_timedelta': 60}})
def kmd_wrf_daily(start_time, end_time, variable, grid='kmd', forecast_type='weekly', mask=None, region='kenya'):  # noqa: ARG001
    """KMD WRF forecast aggregated into daily data."""
    # Read and combine all the data into an array
    target_dates = get_dates(start_time, end_time, stride="day", return_string=True)

    datasets = []
    for date in target_dates:
        ds = dask.delayed(kmd_wrf_raw)(date, forecast_type=forecast_type, filepath_only=True)
        datasets.append(ds)
    datasets = dask.compute(*datasets)
    data = [d for d in datasets if d is not None]
    if len(data) == 0:
        return None

    ds = xr.open_mfdataset(data,
                           engine='zarr',
                           combine="by_coords",
                           parallel=True,
                           chunks={'lat': 350, 'lon': 300, 'time': 60, 'prediction_timedelta': 60})
    ds = ds[[variable]]
    # Drop partial days before resampling
    samples = ds.lead_time.resample(lead_time='D').count(dim='lead_time')
    # daily forecasts are produced at a 3-hrly interval, so 8 samples per day
    # b/c forecasting starts at 06:00, we're always missing the first 2 samples of the day
    # so allow for 6 samples per day
    samples_per_day = 8
    allow_missing = 2

    if variable == 'tmp2m':
        ds = ds.resample(lead_time='D').mean(dim='lead_time')
    elif variable == 'precip':
        # Take the mean and mulitply by the number of samples per day to get the daily precip
        # this allows for days with missing samples to be filled in with the mean precip
        ds = ds.resample(lead_time='D').mean(dim='lead_time') * samples_per_day
        # Select days that have all the samples
        ds = ds.where(samples >= samples_per_day - allow_missing, drop=True)

        # Round the time coordinates to the nearest day
    else:
        raise ValueError(f"Variable {variable} not implemented.")

    # Compute prediction_timedelta as the offset in days for each lead_time entry relative to the first time (assumes time has only one entry)
    ds = ds.assign_coords(
        prediction_timedelta=(ds['lead_time'] - ds['lead_time'][0]).astype('timedelta64[D]')
    )
    ds = ds.swap_dims({'lead_time': 'prediction_timedelta'})
    ds = ds.drop_vars('lead_time')
    if 'spatial_ref' in ds.coords:
        ds = ds.drop_vars('spatial_ref')
    if 'number' in ds.coords:
        ds = ds.drop_vars('number')

    # Regrid the output
    if grid != 'kmd':
        ds = regrid(ds, grid, base='base180', method='conservative')
    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'lead_time': 1}})
def kmd_wrf(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic',
              grid='global1_5', mask='lsm', region="global"):  # noqa: ARG001
    """Final KMD WRF interface."""
    if prob_type != 'deterministic':
        raise NotImplementedError("Only deterministic forecast implemented for KMD WRF")

    # The KMD weekly forecast is 7 days long, so we shift to include all the forecasters who could
    forecast_start = shift_by_days(start_time, -7) if start_time is not None else None
    forecast_end = shift_by_days(end_time, 7) if end_time is not None else None

    ds = kmd_wrf_daily(forecast_start, forecast_end, variable, grid=grid,
                       forecast_type='weekly', mask=mask, region=region)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="prediction_timedelta", agg_fn="mean")
    ds = ds.assign_attrs(prob_type="deterministic")
    ds = ds.rename({'time': 'init_time'})
    return ds
