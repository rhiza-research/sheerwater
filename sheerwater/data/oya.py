"""oya data product."""
import ee
import dask
from dask.distributed import get_client
import xarray as xr
import pandas as pd
import numpy as np
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.interfaces import data as sheerwater_data, spatial
from sheerwater.utils import dask_remote, regrid, roll_and_agg, run_in_parallel


class Plugin(dask.distributed.diagnostics.plugin.WorkerPlugin):
    """Plugin to setup dask distributed.

    We use this instead of the
    Init args in Xee because it has less chance of API overuse errors (429).
    """
    def __init__(self, *args, **kwargs): # noqa: D107
        pass  # the constructor is up to you
    def setup(self, worker: dask.distributed.Worker): # noqa: ARG002 D102
        ee.Initialize(project='sheerwater', opt_url='https://earthengine-highvolume.googleapis.com')
        pass
    def teardown(self, worker: dask.distributed.Worker): # noqa: ARG001 D102
        pass
    def transition(self, key: str, start: str, finish: str, **kwargs): # noqa: ARG001 D102
        pass
    def release_key(self, key: str, state: str, cause: str | None, reason: None, report: bool): # noqa: ARG001 D102
        pass


@dask_remote
@cache(cache_args=['day'],
       backend_kwargs={'chunking': {'lat': 4001, 'lon': 8000, 'time': 1}})
def oya_daily(day):
    """Get oya from earthengine and cache it."""
    # To use EE distributed we must register the worker plugin
    try:
        plugin = Plugin()
        client = get_client()
        client.register_plugin(plugin)
    except ValueError:
        print("No dask client in which to register a plugin.")

    ee.Initialize(project='sheerwater',
                  opt_url='https://earthengine-highvolume.googleapis.com')

    # This is how you get the data at its native projection
    day1 = pd.to_datetime(day) + pd.Timedelta(days=1)
    ic = ee.ImageCollection('projects/global-precipitation-nowcast/assets/global_estimation').filterDate(day,
                                                                                              day1.strftime('%Y-%m-%d'))
    ds = None
    if ic.size().getInfo() > 0:
        ds = xr.open_dataset(ic,
                             engine='ee', projection=ic.first().select(0).projection(),
                             chunks={'time': 48, 'lat': 512, 'lon': 512},
                             getitem_kwargs={'max_retries': 10, 'initial_delay': 20000})
    else:
        print(f"No data in collection for day {day}")
        return None

    # Note: we could use the Xee auto init functionality, but that makes a read call
    # to the earth engine API on every read
    # which triggers an error that doesn't get caught by the robust read functionality set above
    # so it's better to init via plugin

    # Roll the data up to the daily level. The data is mm/hour every 30 minutes, so the sum (to get it to daily)
    # must be divided by 2
    ds = ds.sel(time=slice(day, day))
    resampled_ds = xr.Dataset()
    resampled_ds['precip'] = ds['precipitation'].resample(time='1D').sum(skipna=True, min_count=48) * 0.5

    return resampled_ds



@dask_remote
@timeseries()
@cache(cache_args=[],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def oya_raw(start_time, end_time, delayed=False):
    """Get oya from earthengine and cache it."""
    days = pd.date_range(start_time, end_time)

    def run_day(day):
        ds = oya_daily(day.strftime("%Y-%m-%d"), filepath_only=True)
        return ds

    run_in_parallel(run_day, days, 20)

    datasets = []
    for day in days:
        if delayed:
            ds = dask.delayed(oya_daily)(day.strftime("%Y-%m-%d"), filepath_only=True)
        else:
            ds = oya_daily(day.strftime("%Y-%m-%d"), filepath_only=True)

        datasets.append(ds)

    if delayed:
        datasets = dask.compute(*datasets)

    datasets = [d for d in datasets if d is not None]

    ds = xr.open_mfdataset(datasets,
                           engine='zarr',
                           parallel=True,
                           chunks={})

    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}},
       cache_disable_if={
           'grid': 'source'
       })
def oya_gridded(start_time, end_time, grid, mask=None,  # noqa: ARG001
                  region='global'):
    """Regridded version of whole oya dataset."""
    ds = oya_raw(start_time, end_time)

    # There are both infs and really large numbers in the dataset
    ds = ds.where(ds != np.inf)
    ds = ds.where(ds < 1000)

    # Regrid if not on the native grid
    if grid != 'source':
        ds = regrid(ds, grid, base='base180', method='conservative', region=region)

    return ds


@dask_remote
@sheerwater_data()
def oya(start_time, end_time, variable, agg_days, grid, mask=None, region='global'):
    """A unified oya caller."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by oya.")
    ds = oya_gridded(start_time, end_time, grid, mask=mask, region=region)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')
    return ds
