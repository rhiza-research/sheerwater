"""Imerg data product."""
import gcsfs
import xarray as xr
from dateutil import parser
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, regrid, roll_and_agg

from .data_decorator import data


@dask_remote
@cache(cache_args=['year', 'version'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_raw(year, version='final'):
    """Concatenated IMERG netcdf files by year.

    We manually download the IMERG netcdfs by going to this website
    https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDL_07/summary?keywords=%22IMERG%20late%22
    logging in, downloading the filelist, then following the curl fetch instructions
    here https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20Access%20GES%20DISC%20Data%20Using%20wget%20and%20curl,
    then finally uploading them to our datalake with tools/copy_imerg.py.
    """
    # Open the datastore
    fs = gcsfs.GCSFileSystem(project='sheerwater', token='google_default')

    if version == 'final':
        gsf = [fs.open(x) for x in fs.glob(f'gs://sheerwater-datalake/imerg/{year}*.nc')]
    elif version == 'late':
        gsf = [fs.open(x) for x in fs.glob(f'gs://sheerwater-datalake/imerg_late/{year}*.nc')]

    ds = xr.open_mfdataset(gsf, engine='h5netcdf', parallel=True)

    return ds


@dask_remote
@cache(cache_args=['grid', 'version'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_gridded(start_time, end_time, grid, version):
    """Regridded version of whole imerg dataset."""
    years = range(parser.parse(start_time).year, parser.parse(end_time).year + 1)

    datasets = []
    for year in years:
        ds = imerg_raw(year, version, filepath_only=True)
        datasets.append(ds)

    ds = xr.open_mfdataset(datasets,
                           engine='zarr',
                           parallel=True,
                           chunks={'lat': 300, 'lon': 300, 'time': 365})

    ds = ds['precipitation'].to_dataset()
    ds = ds.rename({'precipitation': 'precip'})

    # Regrid if not on the native grid
    if grid != 'imerg' and grid != 'global0_1':
        ds = regrid(ds, grid, base='base180', method='conservative')

    return ds


@dask_remote
@timeseries()
@cache(cache_args=['grid', 'agg_days', 'version'],
       cache_disable_if={'agg_days': 1},
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_rolled(start_time, end_time, agg_days, grid, version):
    """IMERG rolled and aggregated."""
    ds = imerg_gridded(start_time, end_time, grid, version)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')
    return ds


def _imerg_unified(start_time, end_time, variable, agg_days, grid='global0_25',
                   version='final'):
    """Unified IMERG accessor."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by IMERG.")
    ds = imerg_rolled(start_time, end_time, agg_days=agg_days, grid=grid, version=version)
    return ds


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def imerg_final(start_time=None, end_time=None, variable='precip', agg_days=1,
                grid='global0_25', mask='lsm', region='global'):  # noqa: ARG001
    """IMERG Final."""
    return _imerg_unified(start_time, end_time, variable, agg_days, grid=grid, version='final')


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def imerg_late(start_time=None, end_time=None, variable='precip', agg_days=1,
               grid='global0_25', mask='lsm', region='global'):  # noqa: ARG001
    """IMERG late."""
    return _imerg_unified(start_time, end_time, variable, agg_days, grid=grid, version='late')


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def imerg(start_time=None, end_time=None, variable='precip', agg_days=1,
          grid='global0_25', mask='lsm', region='global'):  # noqa: ARG001
    """Alias for IMERG final."""
    return _imerg_unified(start_time, end_time, variable, agg_days, grid=grid, version='final')
