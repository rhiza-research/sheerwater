"""KMD WRF forecast."""

import pandas as pd
import dask
import gcsfs
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries
from sheerwater.interfaces import forecast as sheerwater_forecast, spatial

from sheerwater.utils import dask_remote, get_dates, regrid


@dask_remote
@cache(cache_args=['date', 'days'], backend_kwargs={'chunking': {'lat': 350, 'lon': 300, 'time': 60}})
def kmd_wrf_raw(date, days=7):
    """KMD WRF forecast."""
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

    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['variable', 'grid', 'lead_days'], backend_kwargs={'chunking': {'lat': 350, 'lon': 300, 'time': 60}})
def kmd_wrf_daily(start_time, end_time, variable, grid='kmd', lead_days=7, mask=None, region='global'):  # noqa: ARG001
    """KMD WRF forecast aggregated into daily data."""
    # Read and combine all the data into an array
    target_dates = get_dates(start_time, end_time, stride="day", return_string=True)

    datasets = []
    for date in target_dates:
        ds = dask.delayed(kmd_wrf_raw)(date, days=lead_days, filepath_only=True)
        datasets.append(ds)
    datasets = dask.compute(*datasets)
    data = [d for d in datasets if d is not None]
    if len(data) == 0:
        return None

    ds = xr.open_mfdataset(data,
                           engine='zarr',
                           combine="by_coords",
                           parallel=True,
                           chunks={'lat': 350, 'lon': 300, 'time': 60})
    ds = ds[[variable]]
    if variable == 'tmp2m':
        ds = ds.resample(lead_time='D').mean(dim='lead_time')
    elif variable == 'precip':
        ds = ds.resample(lead_time='D').sum(dim='lead_time')
        # Round the time coordinates to the nearest day
    else:
        raise ValueError(f"Variable {variable} not implemented.")

    # Regrid the output
    if grid != 'kmd':
        ds = regrid(ds, grid, base='base180', method='conservative', region=region)
    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['variable', 'agg_days', 'grid'],
       cache_disable_if={'agg_days': 1},
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "lead_time": 10, "time": 100},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, 'lead_time': 1, 'time': 30}
               },
           }
})
def graphcast_wb_rolled(start_time, end_time, variable, agg_days, grid='global0_25', mask=None, region='global'):
    """A rolled and aggregated Graphcast forecast."""
    # Grab the init 0 forecast; don't need to regrid
    ds = graphcast_daily_wb(start_time, end_time, variable, init_hour=0, grid=grid, mask=mask, region=region)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="lead_time", agg_fn="mean")
    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'lead_time': 1}})
def graphcast(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic',
              grid='global1_5', mask='lsm', region="global"):  # noqa: ARG001
    """Final Graphcast interface."""
    if prob_type != 'deterministic':
        raise NotImplementedError("Only deterministic forecast implemented for graphcast")

    # Get the data with the right days
    forecast_start = shift_by_days(start_time, -15) if start_time is not None else None
    forecast_end = shift_by_days(end_time, 15) if end_time is not None else None

    # Get the data with the right days
    ds = graphcast_wb_rolled(forecast_start, forecast_end, variable,
                             agg_days=agg_days, grid=grid, mask=mask,
                             region=region)
    ds = ds.assign_attrs(prob_type="deterministic")

    # Rename to standard naming
    ds = ds.rename({'time': 'init_time', 'lead_time': 'prediction_timedelta'})

    return ds
