"""Get GHCND data."""
import math

import dask
import dask.dataframe as dd
import numpy as np
import pandas as pd
import xarray as xr
from dateutil import parser
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, get_grid, get_grid_ds, get_variable, roll_and_agg, snap_point_to_grid

from .data_decorator import data


@cache(cache_args=[])
def ghcn_station_list():
    """Gets GHCN station metadata."""
    df = pd.read_table('https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt',
                       sep="\\s+", names=['ghcn_id', 'lat', 'lon', 'unknown', 'start_year', 'end_year'])

    df = df.drop(['unknown'], axis=1)
    df = df.groupby(by=['ghcn_id']).first().reset_index()

    return df


@dask_remote
@cache(cache_args=['year', 'grid', 'cell_aggregation'],
       backend_kwargs={
           'chunking': {
               'time': 365,
               'lat': 300,
               'lon': 300,
           }
})
def ghcnd_yearly(year, grid='global0_25', cell_aggregation='first'):
    """Get a by year station data and save it as a zarr."""
    obs = dd.read_csv(f"s3://noaa-ghcn-pds/csv/by_year/{year}.csv",
                      names=['ghcn_id', 'date', 'variable', 'value', 'mflag', 'qflag', 'sflag', 'otime'],
                      header=0,
                      blocksize="32MB",
                      dtype={'ghcn_id': str,
                             'date': str,
                             'variable': str,
                             'value': int,
                             'mflag': str,
                             'qflag': str,
                             'sflag': str,
                             'otime': str},
                      storage_options={'anon': True},
                      on_bad_lines="skip")

    # Drop rows we don't care about
    obs = obs[obs['variable'].isin(['TMAX', 'TMIN', 'TAVG', 'PRCP'])]

    # Drop flagged data
    obs = obs[obs['qflag'].isna()]

    # Rplace any invalid data
    INVALID_NUMBER = 9999
    obs = obs.replace(INVALID_NUMBER, pd.NA)

    # Divide by 10 because data is represented in 10ths
    obs['value'] = obs['value'] / 10.0

    # Assign to new column based on variable values
    obs['tmax'] = obs.apply(lambda x: x.value if x['variable'] == 'TMAX' else pd.NA,
                            axis=1, meta=('tmax', 'f8'))
    obs['tmin'] = obs.apply(lambda x: x.value if x['variable'] == 'TMIN' else pd.NA,
                            axis=1, meta=('tmin', 'f8'))
    obs['temp'] = obs.apply(lambda x: x.value if x['variable'] == 'TAVG' else pd.NA,
                            axis=1, meta=('temp', 'f8'))
    obs['precip'] = obs.apply(lambda x: x.value if x['variable'] == 'PRCP' else pd.NA,
                              axis=1, meta=('precip', 'f8'))

    obs = obs.drop(['variable', 'value', 'qflag', 'mflag', 'sflag', 'otime'], axis=1)

    # Group by date and merge columns
    obs = obs.groupby(by=['date', 'ghcn_id']).first()
    obs = obs.reset_index()

    # If temp is none avrage the two
    atemp = (obs['tmin'] + obs['tmax'])/2
    obs['temp'] = obs['temp'].astype(float).fillna(atemp.astype(float))

    # Convert date into a datetime
    obs["time"] = dd.to_datetime(obs["date"])
    obs = obs.drop(['date'], axis=1)

    # Round the coordinates to the nearest grid
    lats, lons, grid_size, offset = get_grid(grid)

    stat = ghcn_station_list()
    stat['lat'] = stat['lat'].apply(lambda x: snap_point_to_grid(x, grid_size, offset))
    stat['lon'] = stat['lon'].apply(lambda x: snap_point_to_grid(x, grid_size, offset))

    stat = stat.set_index('ghcn_id')

    if 'start_year' in stat.columns:
        stat = stat.drop('start_year', axis=1)
    if 'end_year' in stat.columns:
        stat = stat.drop('end_year', axis=1)

    obs = obs.join(stat, on='ghcn_id', how='inner')

    if cell_aggregation == 'first':
        stations_to_use = obs.groupby(['lat', 'lon']).agg(ghcn_id=('ghcn_id', 'first'))
        stations_to_use = stations_to_use['ghcn_id'].unique()

        obs = obs[obs['ghcn_id'].isin(stations_to_use)]
        obs = obs.drop(['ghcn_id'], axis=1)
    elif cell_aggregation == 'mean':
        # Group by lat/lon/time
        obs = obs.groupby(by=['lat', 'lon', 'time']).agg(temp=('temp', 'mean'),
                                                         precip=('precip', 'mean'),
                                                         tmin=('tmin', 'min'),
                                                         tmax=('tmax', 'max'))
        obs = obs.reset_index()

    obs.temp = obs.temp.astype(np.float32)
    obs.tmax = obs.tmax.astype(np.float32)
    obs.tmin = obs.tmin.astype(np.float32)
    obs.precip = obs.precip.astype(np.float32)

    # Convert to xarray - for this to succeed obs must be a pandas dataframe
    obs = xr.Dataset.from_dataframe(obs.compute().set_index(['time', 'lat', 'lon']))

    # Reindex to fill out the lat/lon
    grid_ds = get_grid_ds(grid)
    obs = obs.reindex_like(grid_ds, method='nearest', tolerance=0.005)

    # Return the xarray
    return obs


@dask_remote
@timeseries()
@cache(cache_args=['grid', 'cell_aggregation'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def ghcnd(start_time, end_time, grid="global0_25", cell_aggregation='first', delayed=True):
    """Final gridded station data before aggregation."""
    # Get years between start time and end time
    years = range(parser.parse(start_time).year, parser.parse(end_time).year + 1)

    datasets = []
    for year in years:
        if delayed:
            ds = dask.delayed(ghcnd_yearly)(year, grid, cell_aggregation, filepath_only=True)
            datasets.append(ds)
        else:
            ds = dask.delayed(ghcnd_yearly)(year, grid, cell_aggregation, filepath_only=True)
            datasets.append(dask.compute(ds)[0])

    if delayed:
        datasets = dask.compute(*datasets)

    x = xr.open_mfdataset(datasets,
                          engine='zarr',
                          parallel=True,
                          chunks={'lat': 300, 'lon': 300, 'time': 365})

    return x


@dask_remote
@timeseries()
@cache(cache_args=['grid', 'agg_days', 'missing_thresh', 'cell_aggregation'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def ghcnd_rolled(start_time, end_time, agg_days,
                 grid='global0_25', missing_thresh=0.9, cell_aggregation='first'):
    """GHCND rolled and aggregated."""
    # Get the data
    ds = ghcnd(start_time, end_time, grid, cell_aggregation)

    # Roll and agg
    agg_thresh = max(math.ceil(agg_days*missing_thresh), 1)

    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean', agg_thresh=agg_thresh)
    return ds


@dask_remote
def _ghcn_unified(start_time, end_time, variable, agg_days,
                  grid='global0_25', missing_thresh=0.9, cell_aggregation='first'):
    """Standard interface for ghcn data."""
    ds = ghcnd_rolled(start_time, end_time, agg_days=agg_days, grid=grid,
                      missing_thresh=missing_thresh, cell_aggregation=cell_aggregation)

    # Get the variable
    variable_ghcn = get_variable(variable, 'ghcn')
    variable_sheerwater = get_variable(variable, 'sheerwater')
    ds = ds[variable_ghcn].to_dataset()
    # Rename
    ds = ds.rename({variable_ghcn: variable_sheerwater})
    # Note that this is sparse
    ds = ds.assign_attrs(sparse=True)
    return ds


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region', 'missing_thresh'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def ghcn(start_time=None, end_time=None, variable='precip', agg_days=1,
         grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
         missing_thresh=0.9):
    """Standard interface for ghcn data."""
    return _ghcn_unified(start_time, end_time, variable, agg_days=agg_days,
                         grid=grid,
                         missing_thresh=missing_thresh, cell_aggregation='first')


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region', 'missing_thresh'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def ghcn_avg(start_time=None, end_time=None, variable='precip', agg_days=1,
             grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
             missing_thresh=0.9):
    """Standard interface for ghcn data."""
    return _ghcn_unified(start_time, end_time, variable, agg_days=agg_days,
                         grid=grid,
                         missing_thresh=missing_thresh, cell_aggregation='mean')
