"""Get knust data."""
import math

import dask
import dask.dataframe as dd
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, get_grid, get_grid_ds, roll_and_agg, snap_point_to_grid
from sheerwater.interfaces import data as sheerwater_data, spatial

@cache(cache_args=[])
def knust_deployment():
    pass

@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid', 'cell_aggregation'],
       backend_kwargs={
           'chunking': {'time': 365, 'lat': 300, 'lon': 300}
})
def knust_raw(start_time, end_time, grid='global0_25', cell_aggregation='first', mask=None, region='global'):  # noqa: ARG001
    """Get knust data from the QC controlled stations."""

    # Open the netcdf datasets and standardize
    ashanti = xr.open_dataset('gs://sheerwater-datalake/knust_stations/ashanti.nc', engine='h5netcdf')
    ashanti = ashanti.reset_coords('lat')
    ashanti = ashanti.reset_coords('lon')
    ashanti = ashanti.swap_dims({'ncells':'station_id'})

    dacciwa = xr.open_mfdataset(['gs://sheerwater-datalake/knust_stations/dacciwa/dacciwa_rg_daily_2015-2017.nc',
                                 'gs://sheerwater-datalake/knust_stations/dacciwa/dacciwa_rg_daily_2018-2019.nc'], engine='h5netcdf')
    dacciwa = dacciwa.rename({'station': 'station_id', 'stat_lat': 'lat', 'stat_lon': 'lon'})
    dacciwa['station_id'] = dacciwa['station_id'].astype(str)

    furiflood = xr.open_dataset('gs://sheerwater-datalake/knust_stations/furiflood_kumasi_raingauge_data/furiflood_rg_01-D.nc', engine='h5netcdf')
    furiflood = furiflood.rename({'latitude': 'lat', 'longitude': 'lon'})
    furiflood['station_id'] = furiflood['station_id'].astype(str)

    # combine
    ds = xr.merge([ashanti, dacciwa, furiflood])

    # Round the coordinates to the nearest grid
    lats, lons, grid_size, offset = get_grid(grid)

    stat = stations.rename(columns={'location_latitude': 'lat', 'location_longitude': 'lon', 'code': 'station_id'})
    stat['lat'] = stat['lat'].apply(lambda x: snap_point_to_grid(x, grid_size, offset))
    stat['lon'] = stat['lon'].apply(lambda x: snap_point_to_grid(x, grid_size, offset))

    stat = stat[['station_id', 'lat', 'lon']]
    stat = stat.set_index('station_id')
    obs = obs.join(stat, on='station_id', how='inner')

    if cell_aggregation == 'first':
        stations_to_use = obs.groupby(['lat', 'lon']).agg(station_id=('station_id', 'first'))
        stations_to_use = stations_to_use['station_id'].unique()

        obs = obs[obs['station_id'].isin(stations_to_use)]
        obs = obs.drop(['station_id'], axis=1)
        obs = obs.reset_index()
        obs = obs.drop(['index'], axis=1)
    elif cell_aggregation == 'mean':
        obs = obs.groupby(by=['lat', 'lon', 'time']).agg(precip=('precip', 'mean'))
        obs = obs.reset_index()

    # Convert to xarray - for this to succeed obs must be a pandas dataframe
    obs = xr.Dataset.from_dataframe(obs.set_index(['time', 'lat', 'lon']))

    # Return the xarray
    return obs


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['agg_days', 'grid', 'missing_thresh', 'cell_aggregation'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def knust_rolled(start_time, end_time, agg_days,
                 grid='global0_25',
                 missing_thresh=0.9, cell_aggregation='first', mask=None, region='global'):
    """knust rolled and aggregated."""
    # Get the data
    ds = knust_raw(start_time, end_time, grid, cell_aggregation, mask=mask, region=region)

    grid_ds = get_grid_ds(grid)
    ds = ds.reindex_like(grid_ds, method='nearest', tolerance=0.005)

    # Roll and agg
    agg_thresh = max(math.ceil(agg_days*missing_thresh), 1)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean', agg_thresh=agg_thresh)
    return ds


@dask_remote
def _knust_unified(start_time, end_time, variable, agg_days,
                   grid='global0_25', missing_thresh=0.9, cell_aggregation='first', mask=None, region='global'):
    if variable != 'precip':
        raise ValueError("knust only supports precip")

    ds = knust_rolled(start_time, end_time, agg_days, grid, missing_thresh, cell_aggregation, mask=mask, region=region)
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
