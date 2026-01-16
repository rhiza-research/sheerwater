"""Imerg data product."""
import gcsfs
import xarray as xr
from dateutil import parser
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, regrid, roll_and_agg

from sheerwater.interfaces import data as sheerwater_data, spatial

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
@timeseries()
@spatial()
@cache(cache_args=['grid', 'version'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_gridded(start_time, end_time, grid, version, mask=None,  # noqa: ARG001
                  region='global'):
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
        ds = regrid(ds, grid, base='base180', method='conservative', region=region)

    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid', 'agg_days', 'version'],
       cache_disable_if={'agg_days': 1},
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_rolled(start_time, end_time, agg_days, grid, version, mask=None, region='global'):
    """IMERG rolled and aggregated."""
    ds = imerg_gridded(start_time, end_time, grid, version, mask=mask, region=region)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')
    return ds


@dask_remote
@sheerwater_data(
    description="IMERG Final - NASA GPM satellite precipitation",
    variables=["precip"],
    coverage="Global (60S-60N)",
    data_type="gridded",
)
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_final(start_time=None, end_time=None, variable='precip', agg_days=1,
                grid='global0_25', mask='lsm', region='global'):
    """IMERG Final."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by IMERG.")
    return imerg_rolled(start_time, end_time, agg_days=agg_days, grid=grid, version='final', mask=mask, region=region)


@dask_remote
@sheerwater_data(
    description="IMERG Late - NASA GPM near-real-time satellite precipitation",
    variables=["precip"],
    coverage="Global (60S-60N)",
    data_type="gridded",
)
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg_late(start_time=None, end_time=None, variable='precip', agg_days=1,
               grid='global0_25', mask='lsm', region='global'):
    """IMERG late."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by IMERG.")
    return imerg_rolled(start_time, end_time, agg_days=agg_days, grid=grid, version='late', mask=mask, region=region)


@dask_remote
@sheerwater_data(
    description="IMERG Final - NASA GPM satellite precipitation (alias)",
    variables=["precip"],
    coverage="Global (60S-60N)",
    data_type="gridded",
)
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def imerg(start_time=None, end_time=None, variable='precip', agg_days=1,
          grid='global0_25', mask='lsm', region='global'):
    """Alias for IMERG final."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by IMERG.")
    return imerg_rolled(start_time, end_time, agg_days=agg_days, grid=grid, version='final', mask=mask, region=region)
