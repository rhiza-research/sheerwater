"""Rain over Africa data product."""
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, regrid, roll_and_agg, get_grid
from sheerwater.interfaces import data as sheerwater_data, spatial


@dask_remote
@cache(cache_args=[],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def tamsat_raw():
    """Access raw tamsat data."""
    ds = xr.open_dataset("http://gws-access.jasmin.ac.uk/public/tamsat/rfe/data_degraded/v3.1/daily/0.25/rfe1983-present_daily_0.25.v3.1.nc",
                         engine="h5netcdf")
    return ds


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def tamsat_gridded(start_time, end_time, grid, mask=None, region='global'):  # noqa: ARG001
    """Regridded version of whole TAMSAT dataset."""
    ds = tamsat_raw()

    # Rename variable and select precip
    ds = ds.rename({'rfe': 'precip'})
    ds = ds[['precip']]

    _, _, grid_size, _ = get_grid(grid)

    # Regrid if not on the native grid
    if grid == 'tamsat':
        pass
    elif grid_size < 0.25:
        raise ValueError("The sheerwater TAMSAT datasource does not support grids smaller than 0.25")
    else:
        ds = regrid(ds, grid, base='base180', method='conservative', region=region)

    return ds


@dask_remote
@sheerwater_data(
    description="TAMSAT - Tropical Applications of Meteorology using SATellite data",
    variables=["precip"],
    coverage="Africa",
    data_type="gridded",
)
@cache(cache=False, cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def tamsat(start_time=None, end_time=None, variable='precip', agg_days=1,
           grid='global0_25', mask='lsm', region='global'):
    """Standard data interface for TAMSAT data."""
    if variable not in ['precip']:
        raise NotImplementedError("Only precip and derived variables provided by TAMSAT.")

    ds = tamsat_gridded(start_time, end_time, grid, mask=mask, region=region)
    return roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')
