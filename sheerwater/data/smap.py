"""smap data product."""
from nuthatch import cache
import pandas as pd
from nuthatch.processors import timeseries

from sheerwater.interfaces import data as sheerwater_data
from sheerwater.utils import dask_remote

from .earthaccess_generic import earthaccess_dataset


@dask_remote
@sheerwater_data(register=False)
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

    # L4 is on the curved EASE Grid, which is indexed by x/y, and therefore need coordinates for lat/lon
    # Because the lat/lon coordinates are stored in a different group, we get them separately and merge
    # them into the original dataset
    single_ds = earthaccess_dataset("2016-01-01 00:00:00", "2016-01-01 00:00:00", "SPL4SMGP",
                                    preprocessor=latlon_preprocessor, delayed=delayed, limit=1)
    ds = ds.assign_coords({'lat': single_ds.cell_lat, 'lon': single_ds.cell_lon})

    return ds


@dask_remote
@sheerwater_data(register=False)
@cache(cache_args=[], backend_kwargs={'chunking': {'y': 300, 'x': 300, 'time': 365}})
def smap_l3_raw(start_time, end_time, delayed=False):
    """L3 raw concatenated."""

    def l3_preprocessor(dt):
        # Soil moisture comes through at both AM and PM. AM is considered more reliable, but coalescing (and averaging)
        # them increases pass rate to at minimum once every 2 days. Get both for averaging later
        ds_am = dt['/Soil_Moisture_Retrieval_Data_AM'].to_dataset()
        ds_am = ds_am[['soil_moisture', 'tb_time_seconds']]
        ds_am = ds_am.rename_dims({'phony_dim_0': 'y', 'phony_dim_1': 'x'})

        # There is no daily timestamp, but a set of seconds since 2000 for the physical retrievals
        # Get that set and average them, then round to the nearest day
        try:
            time = pd.Timestamp(pd.to_datetime("2000-01-01") + ds_am['tb_time_seconds'].mean().values).round(freq='1d')
        except: #noqa: E722
            # On two files this process fails, just drop those files
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

    # Average AM and PM together
    ds['soil_moisture'] = ds[['soil_moisture', 'soil_moisture_pm']].to_array(dim='mdim').mean(dim='mdim', skipna=True)
    ds = ds.drop_vars(["soil_moisture_pm"])

    def latlon_preprocessor(dt):
        ds = dt['/'].to_dataset()
        ds = ds.drop_attrs()
        return ds

    # L3 is on the curved EASE Grid, which is indexed by x/y, and therefore need coordinates for lat/lon
    # Because the lat/lon coordinates are stored in a different group, we get them separately and merge
    # them into the original dataset. We actually pull the lat/lon from the L4 product because it's,
    # for some reason, not something I can find in the L3 product, but it's the same grid
    single_ds = earthaccess_dataset("2016-01-01 00:00:00", "2016-01-01 00:00:00", "SPL4SMGP",
                                    preprocessor=latlon_preprocessor, delayed=delayed, limit=1)
    ds = ds.assign_coords({'lat': single_ds.cell_lat, 'lon': single_ds.cell_lon})

    return ds


@dask_remote
@sheerwater_data()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap_l3(start_time=None, end_time=None, variable='soil_moisture', agg_days=1,
          grid='source', mask=None, region='global'): # noqa: ARG001
    """Alias for smap final."""
    if variable not in ['soil_moisture']:
        raise NotImplementedError("Only soil moisture and derived variables provided by smap.")

    return smap_l3_raw(start_time, end_time, agg_days=agg_days, grid=grid, mask=mask, region=region)


@dask_remote
@sheerwater_data()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def smap_l4(start_time=None, end_time=None, variable='soil_moisture', agg_days=1,
          grid='source', mask=None, region='global'): # noqa: ARG001
    """Alias for smap final."""
    if variable not in ['soil_moisture']:
        raise NotImplementedError("Only soil moisture and derived variables provided by smap.")

    return smap_l4_raw(start_time, end_time, agg_days=agg_days, grid=grid, mask=mask, region=region)
