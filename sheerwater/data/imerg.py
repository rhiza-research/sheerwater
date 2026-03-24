"""Imerg data product."""
import gcsfs
import xarray as xr
from dateutil import parser
from nuthatch import cache

from sheerwater.utils import dask_remote
from sheerwater.interfaces import data as sheerwater_data

from .earthaccess_generic import earthaccess_dataset


@dask_remote
@spatial()
@timeseries()
@cache(cache=False, cache_args=["version"], backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_raw_live(start_time, end_time, version='late', delayed=False, grid='source', mask=None, region='global'): # noqa: ARG001
    """GPM IMERG Final / Late Precipitation L3 1 day 0.1 degree x 0.1 degree V07 (GPM_3IMERGDF / GPM_3IMERGDL)."""
    def imerg_preprocessor(dt):
        ds = dt['precipitation'].to_dataset()
        ds = ds.drop_attrs()
        return ds

    if version == 'late':
        shortname = "GPM_3IMERGDL"
    elif version == 'final':
        shortname = "GPM_3IMERGDF"
    else:
        raise ValueError(f"Invalid version: {version}")

    ds = earthaccess_dataset(start_time, end_time, shortname, preprocessor=imerg_preprocessor, delayed=delayed)
    return ds


@dask_remote
@cache(cache_args=['year', 'version'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_year(year, version='final'):
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
@sheerwater_data(register=False)
@cache(cache_args=['version'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_raw(start_time, end_time, version):
    """IMERG combined into years"""
    years = range(parser.parse(start_time).year, parser.parse(end_time).year + 1)

    datasets = []
    for year in years:
        ds = imerg_year(year, version, filepath_only=True)
        datasets.append(ds)

    ds = xr.open_mfdataset(datasets,
                           engine='zarr',
                           parallel=True,
                           chunks={'lat': 300, 'lon': 300, 'time': 365})

    ds = ds['precipitation'].to_dataset()
    ds = ds.rename({'precipitation': 'precip'})

    ds.attrs.update(source_grid='global0_1')

    return ds


@dask_remote
@sheerwater_data()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_final(start_time=None, end_time=None, variable='precip', agg_days=1,
                grid='global0_25', mask='lsm', region='global'):
    """IMERG Final."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by IMERG.")

    return imerg_raw(start_time, end_time, agg_days=agg_days, grid=grid, version='final', mask=mask, region=region)


@dask_remote
@sheerwater_data()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_late(start_time=None, end_time=None, variable='precip', agg_days=1,
               grid='global0_25', mask='lsm', region='global'):
    """IMERG late."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by IMERG.")

    return imerge_raw(start_time, end_time, agg_days=agg_days, grid=grid, version='late', mask=mask, region=region)


@dask_remote
@sheerwater_data()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg(start_time=None, end_time=None, variable='precip', agg_days=1,
          grid='global0_25', mask='lsm', region='global'):
    """Alias for IMERG final."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by IMERG.")

    return imerg_raw(start_time, end_time, agg_days=agg_days, grid=grid, version='final', mask=mask, region=region)
