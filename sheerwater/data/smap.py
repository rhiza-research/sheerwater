"""smap data product."""
from nuthatch import cache
import pandas as pd
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, roll_and_agg

from .earthaccess_generic import earthaccess_dataset


@dask_remote
@timeseries()
@cache(cache_args=[], backend_kwargs={'chunking': {'y': 300, 'x': 300, 'time': 365}})
def smap_l4_raw(start_time, end_time, delayed=False):
    """Lr raw concatenated."""

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

    single_ds = earthaccess_dataset("2016-01-01 00:00:00", "2016-01-01 00:00:00", "SPL4SMGP",
                                    preprocessor=latlon_preprocessor, delayed=delayed, limit=1)
    ds = ds.assign_coords({'lat': single_ds.cell_lat, 'lon': single_ds.cell_lon})

    return ds


@dask_remote
@timeseries()
@cache(cache_args=[], backend_kwargs={'chunking': {'y': 300, 'x': 300, 'time': 365}})
def smap_l3_raw(start_time, end_time, delayed=False):
    """L3 raw concatenated."""

    def l3_preprocessor(dt):
        ds_am = dt['/Soil_Moisture_Retrieval_Data_AM'].to_dataset()
        ds_am = ds_am[['soil_moisture', 'tb_time_seconds']]
        ds_am = ds_am.rename_dims({'phony_dim_0': 'y', 'phony_dim_1': 'x'})

        try:
            time = pd.Timestamp(pd.to_datetime("2000-01-01") + ds_am['tb_time_seconds'].mean().values).round(freq='1d')
        except: #noqa: E722
            return None

        ds_am = ds_am.drop_vars("tb_time_seconds")

        ds_pm = dt['/Soil_Moisture_Retrieval_Data_PM'].to_dataset()
        ds_pm = ds_pm[['soil_moisture_pm']]
        ds_pm = ds_pm.rename_dims({'phony_dim_2': 'y', 'phony_dim_3': 'x'})

        ds = ds_am.merge(ds_pm)
        ds = ds.expand_dims({'time': [time]})
        ds = ds.drop_attrs()

        return ds

    ds = earthaccess_dataset(start_time, end_time, "SPL3SMP_E", preprocessor=l3_preprocessor, delayed=delayed)

    ds['soil_moisture'] = ds[['soil_moisture', 'soil_moisture_pm']].to_array(dim='mdim').mean(dim='mdim', skipna=True)
    ds = ds.drop_vars(["soil_moisture_pm"])

    def latlon_preprocessor(dt):
        ds = dt['/'].to_dataset()
        ds = ds.drop_attrs()
        return ds

    single_ds = earthaccess_dataset("2016-01-01 00:00:00", "2016-01-01 00:00:00", "SPL4SMGP",
                                    preprocessor=latlon_preprocessor, delayed=delayed, limit=1)
    ds = ds.assign_coords({'lat': single_ds.cell_lat, 'lon': single_ds.cell_lon})

    return ds


@dask_remote
@timeseries()
@cache(cache_args=['grid', 'version'], backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}},
       cache_disable_if={
           'grid': 'smap'
       })
def smap_gridded(start_time, end_time, grid='smap', version='L3'):
    """SMAP Gridded product."""
    if version == 'L3':
        ds = smap_l3_raw(start_time, end_time)
    elif version == 'L4':
        ds = smap_l4_raw(start_time, end_time)
    else:
        raise ValueError("Invalid smap version")

    # This must be run in a coiled run machine with 'package_sync_conda_extras' set to 'esmpy'
    if grid != 'smap':
        # Putting the import in the function prevents needing esmpy on your machine, which is hard on mac
        raise ValueError("Currently SMAP only supports the SMAP grid")
        #import xesmf as xe
        #ds_out = get_grid_ds(grid)
        #ds_out = ds_out.rename({'lat': 'latitude', 'lon': 'longitude'})
        #ds = ds.rename({'lat': 'latitude', 'lon': 'longitude'})
        #regridder = xe.Regridder(ds, ds_out, "conservative")
        #ds = regridder(ds)
        #ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})

    return ds


@dask_remote
@timeseries()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap_l3(start_time=None, end_time=None, variable='soil_moisture', agg_days=1,
          grid='smap'): # noqa: ARG001
    """Alias for smap final."""
    if variable not in ['soil_moisture']:
        raise NotImplementedError("Only soil moisture and derived variables provided by smap.")

    ds = smap_gridded(start_time, end_time, grid=grid, version="L3")

    if agg_days:
        ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')

    return ds


@dask_remote
@timeseries()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap_l4(start_time=None, end_time=None, variable='soil_moisture', agg_days=1,
          grid='smap'): # noqa: ARG001
    """Alias for smap final."""
    if variable not in ['soil_moisture']:
        raise NotImplementedError("Only soil moisture and derived variables provided by smap.")

    ds = smap_gridded(start_time, end_time, grid=grid, version="L4")

    if agg_days:
        ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')

    return ds
