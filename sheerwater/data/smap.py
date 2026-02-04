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
@cache(cache_args=['earthaccess_result'])
def smap_single_file(earthaccess_result):

    KeyboardInterrupt
    os.environ["EARTHDATA_USERNAME"] = "joshua_adkins"
    os.environ["EARTHDATA_PASSWORD"] = earthaccess_password()
    earthaccess.login(strategy="environment", persist=True)

    # Takes a single earthaccess result, fetches the file, opens it in xarray, the returns it to be cached
    uuid = earthaccess_result.uuid
    earthaccess.download([earthaccess_result], local_path="./" + uuid)

    ds = xr.open_datatree('./' + uuid + "/*.h5", engine='h5netcdf', phony_dims='access')
    ds = ds['/'].to_dataset().merge(ds['/Geophysical_Data'])
    ds = ds[['cell_lat', 'cell_lon', 'sm_rootzone', 'sm_surface']]
    ds = ds.rename({'cell_lat': 'lat', 'cell_lon': 'lon'})
    ds = ds.set_coords("lat")
    ds = ds.set_coords("lon")

    return ds


@dask_remote
@cache(cache_args=['grid'], backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap_gridded(start_time, end_time, grid='smap', delayed=False):
    """Fetch all the individual files and """
    os.environ["EARTHDATA_USERNAME"] = "joshua_adkins"
    os.environ["EARTHDATA_PASSWORD"] = earthaccess_password()
    earthaccess.login(strategy="environment", persist=True)

    results = earthaccess.search_data(short_name="SPL4SMGP", cloud_hosted=True, temporal=(start_time, end_time))

    files = []
    for result in results:
        if delayed:
            files.append(smap_single_file(result, filepath_only=True))
        else:
            files.append(dask.delayed(smap_single_file)(result, filepath_only=True))

    if delayed:
        files = files.compute()

    ds = xr.open_mfdataset(files,
                           engine='zarr',
                           parallel=True,
                           chunks={'lat': 300, 'lon': 300, 'time': 365})

    def regrid(ds):
        import xesmf as xe
        ds_out = get_grid_ds(grid)
        regridder = xe.Regridder(ds, ds_out, "bilinear")
        ds = regridder(ds)
        return ds

    if grid != 'smap':
        ds = dask.delayed(regrid)(ds)
        ds = ds.compute()

    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid', 'agg_days', 'version'],
       cache_disable_if={'agg_days': 1},
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap_rolled(start_time, end_time, agg_days, grid, version, mask=None, region='global'):
    """smap rolled and aggregated."""
    ds = smap_gridded(start_time, end_time, grid, version, mask=mask, region=region)
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
    return smap_rolled(start_time, end_time, agg_days=agg_days, grid=grid, version='final', mask=mask, region=region)
