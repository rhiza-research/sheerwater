"""CHIRPS data product."""
import datetime

import fsspec
import pandas as pd
import xarray as xr
from dateutil import parser
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, regrid, roll_and_agg

from .data_decorator import data


@dask_remote
@cache(cache_args=['year', 'grid', 'stations', 'version'],
       backend_kwargs={
           'chunking': {'lat': 300, 'lon': 300, 'time': 365}
})
def chirps_raw(year, grid, stations=True, version=2):  # noqa: ARG001
    """CHIRPS raw by year."""
    # Open the datastore
    if not stations and version == 3:
        base_url = f'https://data.chc.ucsb.edu/products/CHIRP-v3.0/daily/global/tifs/{year}/chirp-v3.0.'
        urls = []
        if year < 2000:
            print("Chirp v3 not valid before 2000. Returning none.")
            return None
        elif year == 2000:
            for date in pd.date_range(f"{year}-06-01", f"{year}-12-31"):
                date = date.date()
                full_url = base_url + f"{year}.{date.month:02}.{date.day:02}.tif"
                urls.append(full_url)
        else:
            fs = fsspec.filesystem("https")
            for date in pd.date_range(f"{year}-01-01", f"{year}-12-31"):
                date = date.date()
                full_url = base_url + f"{year}.{date.month:02}.{date.day:02}.tif"
                if fs.exists(full_url):
                    urls.append(full_url)

        def preprocess(ds):
            """Preprocess the dataset to add the member dimension."""
            ff = ds.encoding["source"]
            date = pd.to_datetime('-'.join(ff.split('/')[-1].split('.')[2:-1]))
            ds = ds.assign_coords(time=date)
            ds = ds.expand_dims(dim='time')
            ds = ds.squeeze('band')
            ds = ds.reset_coords('band', drop=True)
            return ds

        ds = xr.open_mfdataset(
            urls, engine='rasterio', preprocess=preprocess,
            chunks={'y': 1200, 'x': 1200, 'time': 365},
            concat_dim=["time"], compat="override", coords="minimal", combine="nested")
        ds = ds.rename({'y': 'lat', 'x': 'lon', 'band_data': 'precip'})
    elif stations and version == 2:
        if year == datetime.datetime.now().year:
            prelim_url = f'https://data.chc.ucsb.edu/products/CHIRPS-2.0/prelim/global_daily/netcdf/p05/chirps-v2.0.{year}.days_p05.nc'
            url = f'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/netcdf/p05/chirps-v2.0.{year}.days_p05.nc'

            fs = fsspec.filesystem("https", timeout=7200)
            fobj = fs.open(url)
            fprelim = fs.open(prelim_url)
            ds = xr.open_dataset(fobj, chunks={'lat': 300, 'lon': 300, 'time': 365})
            ds_prelim = xr.open_dataset(fprelim, chunks={'lat': 300, 'lon': 300, 'time': 365})

            ds = ds.combine_first(ds_prelim)

            # Rename to lat/lon
            ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})
        else:
            url = f'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/netcdf/p05/chirps-v2.0.{year}.days_p05.nc'

            fs = fsspec.filesystem("https", timeout=7200)
            fobj = fs.open(url)
            ds = xr.open_dataset(fobj, chunks={'lat': 300, 'lon': 300, 'time': 365})

            # Rename to lat/lon
            ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})
    elif stations and version == 3:
        base_url = f"https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/final/sat/netcdf/byMonth/chirps-v3.0.{year}"
        urls = []
        if year < 2000:
            print("Chirps v3 not valid before 2000. Returning none.")
            return None
        elif year == 2000:
            for month in range(6, 13):
                full_url = base_url + f".{month:02}.days_p05.nc"
                urls.append(full_url)
        else:
            for month in range(1, 13):
                full_url = base_url + f".{month:02}.days_p05.nc"
                urls.append(full_url)

        fs = fsspec.filesystem("https", timeout=7200, block_size=10*10*1024*1024)
        files = []
        for url in urls:
            try:
                f = fs.open(url)
                files.append(f)
            except FileNotFoundError:
                pass

        ds = xr.open_mfdataset(files, chunks={'lat': 300, 'lon': 300, 'time': 365})

        # Rename to lat/lon
        ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})
    else:
        if not stations and version == 2:
            url = f'https://data.chc.ucsb.edu/products/CHIRP/daily/netcdf/chirp.{year}.days_p05.nc'
        else:
            raise ValueError(f"No chirps dataset found for stations:{stations}, version:{version}")

        fs = fsspec.filesystem("https", timeout=7200, block_size=10*10*1024*1024)
        fobj = fs.open(url, block_size=10*10*1024*1024)
        ds = xr.open_dataset(fobj, chunks={'lat': 300, 'lon': 300, 'time': 365})

        # Rename to lat/lon
        ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})

    # clip to the year
    start_time = str(year) + '-01-01'
    end_time = str(year) + '-12-31'

    ds = ds.sel({'time': slice(start_time, end_time)})

    return ds


@dask_remote
@timeseries()
@cache(cache_args=['grid', 'stations', 'version'],
       backend_kwargs={
           'chunking': {'lat': 300, 'lon': 300, 'time': 365}
})
def chirps_gridded(start_time, end_time, grid, stations=True, version=2):
    """CHIRPS regridded by year."""
    years = range(parser.parse(start_time).year, parser.parse(end_time).year + 1)

    datasets = []
    for year in years:
        ds = chirps_raw(year, 'chirps', stations=stations, version=version, filepath_only=True)
        if ds is not None:
            datasets.append(ds)

    ds = xr.open_mfdataset(datasets,
                           engine='zarr',
                           parallel=True,
                           chunks={'lat': 300, 'lon': 300, 'time': 365})

    if "spatial_ref" in ds:
        ds = ds.drop_vars(["spatial_ref"])

    # Regrid if not on the native grid
    if grid != 'chirps':
        ds = regrid(ds, grid, base='base180', method='conservative')

    return ds


@timeseries()
@cache(cache_args=['grid', 'agg_days', 'stations', 'version'],
       cache_disable_if={'agg_days': 1},
       backend_kwargs={
           'chunking': {'lat': 300, 'lon': 300, 'time': 365}
})
def chirps_rolled(start_time, end_time, agg_days, grid, stations=True, version=2):
    """CHIRPS rolled and aggregated."""
    ds = chirps_gridded(start_time, end_time, grid, stations=stations, version=version)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')
    return ds


def _chirps_unified(start_time, end_time, variable, agg_days, grid='global0_25',
                    stations=True, version=2):
    """A unified chirps caller."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by CHIRP/S.")
    ds = chirps_rolled(start_time, end_time, agg_days, grid, stations=stations, version=version)
    ds = ds.assign_attrs(sparse=True)
    return ds


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def chirp_v2(start_time=None, end_time=None, variable='precip', agg_days=5,
             grid='global0_25', mask='lsm', region='global'):  # noqa: ARG001
    """A chirps interface for CHIRP2."""
    return _chirps_unified(start_time, end_time, variable, agg_days, grid=grid,
                           stations=False, version=2)


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def chirp_v3(start_time=None, end_time=None, variable='precip', agg_days=5,
             grid='global0_25', mask='lsm', region='global'):  # noqa: ARG001
    """A chirps interface for CHIRP3."""
    return _chirps_unified(start_time, end_time, variable, agg_days, grid=grid,
                           stations=False, version=3)


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def chirps_v2(start_time=None, end_time=None, variable='precip', agg_days=5,
              grid='global0_25', mask='lsm', region='global'):  # noqa: ARG001
    """A chirps interface for CHIRPS2."""
    return _chirps_unified(start_time, end_time, variable, agg_days, grid=grid,
                           stations=True, version=2)


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def chirps_v3(start_time=None, end_time=None, variable='precip', agg_days=5,
              grid='global0_25', mask='lsm', region='global'):  # noqa: ARG001
    """A chirps interface for CHIRPS3."""
    return _chirps_unified(start_time, end_time, variable, agg_days, grid=grid,
                           stations=True, version=3)


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def chirps(start_time=None, end_time=None, variable='precip', agg_days=5,
           grid='global0_25', mask='lsm', region='global'):  # noqa: ARG001
    """Final access function for chirps."""
    ds = _chirps_unified(start_time, end_time, variable, agg_days, grid=grid,
                         stations=True, version=3)

    return ds
