"""Get Tahmo data."""
import math

import dask
import dask.dataframe as dd
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, get_grid, get_grid_ds, roll_and_agg, snap_point_to_grid

from .data_decorator import data


@cache(cache_args=[])
def tahmo_deployment():
    """Stub function to get deployment cache."""
    raise RuntimeError("Processing not implemented for tahmo_deployment and wasn't found in the cache.")


@cache(cache_args=['station_id'])
def tahmo_station_cleaned(station_id):  # noqa: ARG001
    """Stub function to get data cache."""
    raise RuntimeError("Processing not implemented for tahmo_station_cleaned and wasn't found in the cache.")


@dask_remote
@cache(cache_args=[])
def tahmo_raw_daily():
    """Tahmo data combined and aggregated into days."""
    # Get the station list
    stations = tahmo_deployment().compute()

    datasets = []
    for station in stations.to_dict(orient='records'):
        ds = dask.delayed(tahmo_station_cleaned)(station['code'], filepath_only=True)
        datasets.append(ds)

    datasets = dask.compute(*datasets)
    datasets = [item for item in datasets if item is not None]
    obs = dd.read_parquet(datasets)

    # remove all data without quality_flag = 1
    obs = obs[obs['precip_quality_flag'] > 0.9]
    obs = obs.drop(['precip_quality_flag', 'precip_sensor_id'], axis=1)

    # For each station ID roll the data into a daily sum
    obs = obs.groupby([obs.time.dt.date, 'station_id']).agg({'precip_mm': 'sum'})
    obs = obs.rename(columns={'precip_mm': 'precip'})
    obs = obs.reset_index()

    # Convert what is now a date back to a datetime
    obs['time'] = dd.to_datetime(obs['time'])

    return obs


@dask_remote
@timeseries()
@cache(cache_args=['grid', 'cell_aggregation'],
       backend_kwargs={
           'chunking': {
               'time': 365,
               'lat': 300,
               'lon': 300,
           }
})
def tahmo_raw(start_time, end_time, grid='global0_25', cell_aggregation='first'):  # noqa: ARG001
    """Get tahmo data from the QC controlled stations."""
    # Get the station list
    stations = tahmo_deployment().compute()

    obs = tahmo_raw_daily().compute()

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
@cache(cache_args=['agg_days', 'grid', 'missing_thresh', 'cell_aggregation'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def tahmo_rolled(start_time, end_time, agg_days,
                 grid='global0_25',
                 missing_thresh=0.9, cell_aggregation='first'):
    """Tahmo rolled and aggregated."""
    # Get the data
    ds = tahmo_raw(start_time, end_time, grid, cell_aggregation)

    grid_ds = get_grid_ds(grid)
    ds = ds.reindex_like(grid_ds, method='nearest', tolerance=0.005)

    # Roll and agg
    agg_thresh = max(math.ceil(agg_days*missing_thresh), 1)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean', agg_thresh=agg_thresh)
    return ds


@dask_remote
def _tahmo_unified(start_time, end_time, variable, agg_days,
                   grid='global0_25', missing_thresh=0.9, cell_aggregation='first'):
    if variable != 'precip':
        raise ValueError("TAHMO only supports precip")

    ds = tahmo_rolled(start_time, end_time, agg_days, grid, missing_thresh, cell_aggregation)
    ds = ds[[variable]]

    # Note that this is sparse
    ds = ds.assign_attrs(sparse=True)
    return ds


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region', 'missing_thresh'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def tahmo(start_time=None, end_time=None, variable='precip', agg_days=1,
          grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
          missing_thresh=0.9):
    """Standard interface for TAHMO data."""
    return _tahmo_unified(start_time, end_time, variable, agg_days,
                          grid=grid,
                          missing_thresh=missing_thresh, cell_aggregation='first')


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region', 'missing_thresh'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def tahmo_avg(start_time=None, end_time=None, variable='precip', agg_days=1,
              grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
              missing_thresh=0.9):
    """Standard interface for TAHMO data."""
    return _tahmo_unified(start_time, end_time, variable, agg_days,
                          grid=grid,
                          missing_thresh=missing_thresh, cell_aggregation='mean')
