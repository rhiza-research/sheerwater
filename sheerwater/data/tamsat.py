"""TAMSAT data product."""
import xarray as xr
from nuthatch import cache

from sheerwater.utils import dask_remote
from sheerwater.interfaces import data as sheerwater_data


@dask_remote
@sheerwater_data(register=False)
@cache(cache_args=[],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def tamsat_raw(start_time, end_time):
    """Access raw tamsat data."""
    ds = xr.open_dataset("http://gws-access.jasmin.ac.uk/public/tamsat/rfe/data_degraded/v3.1/daily/0.25/rfe1983-present_daily_0.25.v3.1.nc",
                         engine="h5netcdf")

    # Rename variable and select precip
    ds = ds.rename({'rfe': 'precip'})
    ds = ds[['precip']]

    # Note this an 0.25 grid so the source doesn't get regridded
    ds.attrs.update(source_grid='global0_25')

    return ds


@dask_remote
@sheerwater_data()
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def tamsat(start_time=None, end_time=None, variable='precip', agg_days=1,
           grid='global0_25', mask='lsm', region='global'):
    """Standard data interface for TAMSAT data."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by TAMSAT.")

    ds = tamsat_raw(start_time, end_time, agg_days=agg_days, grid=grid, mask=mask, region=region)
    return ds
