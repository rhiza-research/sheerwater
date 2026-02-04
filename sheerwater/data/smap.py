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
import earthaccess


@dask_remote
@cache(cache_args=['filename'])
def smap_single_file(filename, earthaccess_result):

    KeyboardInterrupt
    os.environ["EARTHDATA_USERNAME"] = "joshua_adkins"
    os.environ["EARTHDATA_PASSWORD"] = earthaccess_password()
    earthaccess.login(strategy="environment", persist=True)

    # Takes a single earthaccess result, fetches the file, opens it in xarray, the returns it to be cached
    earthaccess.download([earthaccess_result], local_path="./smap")

    ds = xr.open_datatree('./smap/' + filename, engine='h5netcdf', phony_dims='access')
    ds = ds['/'].to_dataset().merge(ds['/Geophysical_Data'])
    ds = ds[['cell_lat', 'cell_lon', 'sm_rootzone', 'sm_surface', 'time']]
    ds = ds.rename({'cell_lat': 'lat', 'cell_lon': 'lon'})
    ds = ds.set_coords("lat")
    ds = ds.set_coords("lon")
    ds = ds.swap_dims({"phony_dim_0": "time"})
    ds = ds.drop_attrs()

    ds = ds.compute()
    print(ds)

    # Necessary to not fill up on-cluster disk
    os.remove('./smap/' + filename)

    return ds


@dask_remote
@cache(cache_args=[], backend_kwargs={'chunking': {'y': 300, 'x': 300, 'time': 365}})
def smap_raw(start_time, end_time, delayed=False):
    """Fetch all the individual files and """
    os.environ["EARTHDATA_USERNAME"] = "joshua_adkins"
    os.environ["EARTHDATA_PASSWORD"] = earthaccess_password()
    earthaccess.login(strategy="environment", persist=True)

    results = earthaccess.search_data(short_name="SPL4SMGP", cloud_hosted=True, temporal=(start_time, end_time))

    files = []
    for result in results:
        fname = result.data_links()[0].split('/')[-1]
        if delayed:
            files.append(dask.delayed(smap_single_file)(fname, result, filepath_only=True))
        else:
            files.append(smap_single_file(fname, result, filepath_only=True))

    if delayed:
        files = dask.compute(*files)

    ds = xr.open_mfdataset(files,
                           engine='zarr',
                           parallel=True,
                           chunks={'y': 300, 'x': 300, 'time': 365})

    return ds

@dask_remote
@cache(cache_args=['grid'], backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}},
       cache_disable_if={
           'grid': 'smap'
       })
def smap_gridded(start_time, end_time, grid='smap'):

    ds = smap_raw(start_time, end_time)

    def regrid(ds):
        import xesmf as xe
        ds_out = get_grid_ds(grid)
        regridder = xe.Regridder(ds, ds_out, "bilinear")
        ds = regridder(ds)
        return ds

    # This must be run in delayed with 'package_sync_conda_extras' set to 'esmpy'
    if grid != 'smap':
        ds = dask.delayed(regrid)(ds)
        ds = ds.compute()

    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid', 'agg_days'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap_rolled(start_time, end_time, agg_days=None, grid, mask=None, region='global'):
    """smap rolled and aggregated."""
    ds = smap_gridded(start_time, end_time, grid, mask=mask, region=region)

    if agg_days:
        ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')

    return ds

@dask_remote
@sheerwater_data()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap(start_time=None, end_time=None, variable='precip', agg_days=None,
          grid='global0_25', mask='lsm', region='global'):
    """Alias for smap final."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by smap.")
    return smap_rolled(start_time, end_time, agg_days=agg_days, grid=grid, mask=mask, region=region)
