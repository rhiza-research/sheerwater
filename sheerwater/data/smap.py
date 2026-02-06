"""smap data product."""
import gcsfs
import xarray as xr
from dateutil import parser
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, regrid, roll_and_agg, get_grid_ds
from sheerwater.utils.secrets import earthaccess_password

from sheerwater.interfaces import data as sheerwater_data, spatial
import dask
import os
from .earthaccess_generic import earthaccess_dataset


@dask_remote
@cache(cache_args=[], backend_kwargs={'chunking': {'y': 300, 'x': 300, 'time': 365}})
def smap_l4_raw(start_time, end_time, delayed=False):

    def l4_preprocessor(dt):
        ds = dt['/'].to_dataset().merge(dt['/Geophysical_Data'])
        ds = ds[['sm_rootzone', 'sm_surface', 'time']]
        ds = ds.swap_dims({"phony_dim_0": "time"})
        ds = ds.drop_attrs()
        return ds

    ds = earthaccess_dataset(start_time, end_time, "SPL4SMGP", preprocessor=l4_preprocessor, delayed=delayed)

    def latlon_preprocessor(dt):
        ds = dt['/'].to_dataset()
        ds = ds.drop_attrs()
        return ds

    ds = earthaccess_dataset("2016-01-01 00:00:00", "2016-01-01 02:00:00", "SPL4SMGP", preprocessor=latlon_preprocessor, delayed=delayed)

    #results = earthaccess.search_data(short_name=shortname, cloud_hosted=True, temporal=("2016-01-01", "2016-01-01"))
    #single_ds = smap_single_file(results[0].data_links()[0].split('/')[-1])
    #ds = ds.assign_coords({'lat': single_ds.lat, 'lon': single_ds.lon})

    return ds


@dask_remote
@cache(cache_args=[], backend_kwargs={'chunking': {'y': 300, 'x': 300, 'time': 365}})
def smap_l3_raw(start_time, end_time, delayed=False):

    def l3_preprocessor(dt):
        ds = ds['/Geophysical_Data']
        ds = ds[['sm_rootzone', 'sm_surface', 'time']]
        ds = ds.swap_dims({"phony_dim_0": "time"})
        ds = ds.drop_attrs()
        return ds

    ds = earthaccess_dataset(start_time, endtime, "SPL3SMP_E", preprocessor=l3_preprocessor, delayed=delayed)

    return ds


@dask_remote
@cache(cache_args=['grid'], backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}},
       cache_disable_if={
           'grid': 'smap'
       })
def smap_gridded(start_time, end_time, grid='smap'):

    ds = smap_raw(start_time, end_time)

    # This must be run in a coiled run machine with 'package_sync_conda_extras' set to 'esmpy'
    if grid != 'smap':
        # Putting the import in the function prevents needing esmpy on your machine, which is hard on mac
        import xesmf as xe
        ds_out = get_grid_ds(grid)
        ds_out = ds_out.rename({'lat': 'latitude', 'lon': 'longitude'})
        ds = ds.rename({'lat': 'latitude', 'lon': 'longitude'})
        regridder = xe.Regridder(ds, ds_out, "conservative")
        ds = regridder(ds)
        ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})

    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid', 'agg_days'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap_rolled(start_time, end_time, agg_days, grid, mask=None, region='global'):
    """smap rolled and aggregated."""
    ds = smap_gridded(start_time, end_time, grid, mask=mask, region=region)

    if agg_days:
        ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')

    return ds

@dask_remote
@sheerwater_data()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap(start_time=None, end_time=None, variable='precip', agg_days=1,
          grid='global0_25', mask='lsm', region='global'):
    """Alias for smap final."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by smap.")
    return smap_rolled(start_time, end_time, agg_days=agg_days, grid=grid, mask=mask, region=region)
