"""Rain over Africa data product."""
import gcsfs
import xarray as xr
import pandas as pd
from dateutil import parser
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, regrid, roll_and_agg

from sheerwater.interfaces import data as sheerwater_data, spatial

@dask_remote
@spatial()
@cache(cache_args=['date'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def roa_raw(date):
    """ROA Data share opening"""
    # Open the datastore
    fs = gcsfs.GCSFileSystem(project='sheerwater', token='google_default')
    dt = pd.to_datetime(date)

    gsf = [fs.open(x) for x in fs.glob(f'gs://sheerwater-datalake/rain_over_africa/{dt.year}/{dt.month:02}/MSG*{dt.year}{dt.month:02}{dt.day:02}-*.nc')]

    def preprocess(ds):
        """Preprocess the dataset to add the member dimension."""
        time = pd.to_datetime(ds.attrs['start_time'])
        ds = ds.assign_coords(time=time)
        ds = ds.expand_dims(dim='time')
        print(ds)
        return ds

    ds = xr.open_mfdataset(gsf, engine='h5netcdf', parallel=True, combine_attrs="drop_conflicts", preprocess=preprocess)
    ds = ds.rename({'latitude': 'lat'})
    ds = ds.rename({'longitude': 'lon'})

    # Aggregate up to daily data
    resampled_ds = xr.Dataset()
    resampled_ds['precip'] = ds['posterior_mean'].resample(time='1D').sum() * 0.25
    resampled_ds['max_probability_precip'] = ds['probability_precip'].resample(time='1D').max()

    return resampled_ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def roa_gridded(start_time, end_time, grid, mask=None, region='global'): # noqa: ARG001
    """Regridded version of whole roa dataset."""
    years = range(parser.parse(start_time).year, parser.parse(end_time).year + 1)

    datasets = []
    for year in years:
        ds = roa_raw(year, filepath_only=True)
        datasets.append(ds)

    ds = xr.open_mfdataset(datasets,
                           engine='zarr',
                           parallel=True,
                           chunks={'lat': 300, 'lon': 300, 'time': 365})

    # Regrid if not on the native grid
    if grid != 'roa':
        ds = regrid(ds, grid, base='base180', method='conservative', region=region)

    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid', 'agg_days'],
       cache_disable_if={'agg_days': 1},
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def roa_rolled(start_time, end_time, agg_days, grid, mask=None, region='global'):
    """rolled and aggregated."""
    ds = roa_gridded(start_time, end_time, grid, mask=mask, region=region)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')
    return ds


@dask_remote
@sheerwater_data()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def rain_over_africa(start_time=None, end_time=None, variable='precip', agg_days=1,
                grid='global0_25', mask='lsm', region='global'):
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by ROA.")
    return roa_rolled(start_time, end_time, agg_days=agg_days, grid=grid, mask=mask, region=region)
