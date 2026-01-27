"""Get knust data."""
import math
from functools import partial

import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, get_grid, get_grid_ds, roll_and_agg, snap_point_to_grid
from sheerwater.interfaces import data as sheerwater_data, spatial


@cache(cache_args=[])
def knust_ashanti():
    # Open the netcdf datasets and standardize
    ashanti = xr.open_dataset('gs://sheerwater-datalake/knust_stations/ashanti.nc',
                              engine='h5netcdf')
    ashanti = ashanti.swap_dims({'ncells':'station_id'})
    ashanti = ashanti.dropna(dim='time')
    ashanti = ashanti.reset_coords('lat')
    ashanti = ashanti.reset_coords('lon')
    return ashanti


@cache(cache_args=[])
def knust_dacciwa():
    dacciwa = xr.open_mfdataset(['gs://sheerwater-datalake/knust_stations/dacciwa/dacciwa_rg_daily_2015-2017.nc',
                                 'gs://sheerwater-datalake/knust_stations/dacciwa/dacciwa_rg_daily_2018-2019.nc'],
                                engine='h5netcdf')
    dacciwa = dacciwa.rename({'station': 'station_id', 'stat_lat': 'lat', 'stat_lon': 'lon'})
    dacciwa['station_id'] = dacciwa['station_id'].astype(str)
    dacciwa['lat'] = dacciwa.lat.isel(time=0)
    dacciwa['lon'] = dacciwa.lon.isel(time=0)
    return dacciwa


@cache(cache_args=[])
def knust_furiflood():
    furiflood = xr.open_dataset('gs://sheerwater-datalake/knust_stations/furiflood_kumasi_raingauge_data/furiflood_rg_01-D.nc',
                                engine='h5netcdf')
    furiflood = furiflood.rename({'latitude': 'lat', 'longitude': 'lon'})
    furiflood['station_id'] = furiflood['station_id'].astype(str)
    return furiflood


@dask_remote
@timeseries()
@cache(cache_args=['grid', 'cell_aggregation'],
       backend_kwargs={
           'chunking': {'time': 365, 'lat': 300, 'lon': 300}
})
def knust_raw(start_time, end_time, grid='global0_25', cell_aggregation='first', mask=None, region='global'):  # noqa: ARG001
    """Get knust data from the QC controlled stations."""
    ashanti = knust_ashanti()

    # Extra reset coords necessary for an unkown reason. Zarr wasn't updating coords vs vars appropriately
    ashanti = ashanti.reset_coords('lat')
    ashanti = ashanti.reset_coords('lon')

    dacciwa = knust_dacciwa()
    furiflood = knust_furiflood()

    # combine
    ds = xr.merge([ashanti, dacciwa, furiflood])

    # Snap the lat/lon values to our requested grid
    _, _, grid_size, offset = get_grid(grid)

    partial_func = partial(snap_point_to_grid, grid_size=grid_size, offset=offset)
    ds['lat'] = xr.apply_ufunc(partial_func, ds['lat'].compute(), vectorize=True)
    ds['lon'] = xr.apply_ufunc(partial_func, ds['lon'].compute(), vectorize=True)
    ds = ds.set_coords("lat")
    ds = ds.set_coords("lon")


    if cell_aggregation == 'mean':
        ds = ds.groupby(['lat','lon']).mean()
    elif cell_aggregation == 'first':
        ds = ds.groupby(['lat','lon']).first()
    else:
        raise ValueError("Cell aggregation must be 'first' or 'mean'")

    # Return the xarray
    ds = ds.chunk({'time':365, 'lat': 300, 'lon': 300})
    return ds


@dask_remote
@timeseries()
@spatial()
def _knust_unified(start_time, end_time, variable, agg_days,
                   grid='global0_25', missing_thresh=0.9, cell_aggregation='first', mask=None, region='global'):

    ds = knust_raw(start_time, end_time, grid, cell_aggregation, mask=mask, region=region)
    ds = ds.rename({'precipitation_amount': 'precip'})

    # Apply grid to fill out lat/lon
    grid_ds = get_grid_ds(grid)
    ds = ds.reindex_like(grid_ds, method='nearest', tolerance=0.005)

    agg_thresh = max(math.ceil(agg_days*missing_thresh), 1)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean', agg_thresh=agg_thresh)

    if variable != 'precip':
        raise ValueError("knust only supports precip")

    ds = ds[[variable]]

    # Note that this is sparse
    ds = ds.assign_attrs(sparse=True)
    return ds


@dask_remote
@sheerwater_data()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region', 'missing_thresh'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def knust(start_time=None, end_time=None, variable='precip', agg_days=1,
          grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
          missing_thresh=0.9):
    """Standard interface for knust data."""
    return _knust_unified(start_time, end_time, variable, agg_days,
                          grid=grid,
                          missing_thresh=missing_thresh, cell_aggregation='first', mask=mask, region=region)


@dask_remote
@sheerwater_data()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region', 'missing_thresh'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def knust_avg(start_time=None, end_time=None, variable='precip', agg_days=1,
              grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
              missing_thresh=0.9):
    """Standard interface for knust data."""
    return _knust_unified(start_time, end_time, variable, agg_days,
                          grid=grid,
                          missing_thresh=missing_thresh, cell_aggregation='mean', mask=mask, region=region)
