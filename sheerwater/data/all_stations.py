"""A Datasource to combine all other station datasources."""
import math
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, roll_and_agg
from sheerwater.data import knust, knust_avg, tahmo, tahmo_avg, ghcn, ghcn_avg
from sheerwater.interfaces import data as sheerwater_data, spatial

@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid', 'missing_thresh', 'cell_aggregation'])
def _stations_aggregated(start_time, end_time, variable,
                         grid='global0_25', missing_thresh=0.9, cell_aggregation='first', mask=None, region='global'):

    if cell_aggregation == 'first':
       knust = knust(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                     mask=mask, region=region)
       tahmo = tahmo(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                     mask=mask, region=region)
       ghcn = ghcn(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                   mask=mask, region=region)
    elif cell_aggregation == 'mean':
       knust = knust_avg(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                         mask=mask, region=region)
       tahmo = tahmo_avg(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                         mask=mask, region=region)
       ghcn = ghcn_avg(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                       mask=mask, region=region)

    knust = knust.expand_dims(dim={"source": ["knust"]})
    knust = knust.chunk({'time': 365, 'lat': 300, 'lon': 300})
    tahmo = tahmo.expand_dims(dim={"source": ["tahmo"]})
    ghcn = ghcn.expand_dims(dim={"source": ["ghcn"]})

    # Concat the datasets
    ds = xr.merge([knust, tahmo, ghcn])

    # Aggregate them depending on the cell aggregation preserving a variable for the source
    if cell_aggregation == 'first':
        ds = ds.groupby(['time', 'lat', 'lon']).first()
    elif cell_aggregation == 'mean':
        ds = ds.groupby(['time', 'lat', 'lon']).mean()

    return ds


@dask_remote
def _stations_unified(start_time, end_time, variable, agg_days,
                  grid='global0_25', missing_thresh=0.9, cell_aggregation='first', mask=None, region='global'):
    """Standard interface for all station data."""
    ds = _stations_aggregated(start_time, end_time, variable, grid=grid,
                              missing_thresh=missing_thresh, cell_aggregation=cell_aggregation,
                              mask=mask, region=region)

    agg_thresh = max(math.ceil(agg_days*missing_thresh), 1)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean', agg_thresh=agg_thresh)
    # Note that this is sparse
    ds = ds.assign_attrs(sparse=True)
    return ds


@dask_remote
@sheerwater_data()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region', 'missing_thresh'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def all_stations(start_time=None, end_time=None, variable='precip', agg_days=1,
          grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
          missing_thresh=0.9):
    """Standard interface for all data."""
    return _stations_unified(start_time, end_time, variable, agg_days, grid=grid,
                          missing_thresh=missing_thresh, cell_aggregation='first', mask=mask, region=region)


@dask_remote
@sheerwater_data()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region', 'missing_thresh'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def all_stations_avg(start_time=None, end_time=None, variable='precip', agg_days=1,
              grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
              missing_thresh=0.9):
    """Standard interface for all data."""
    return _stations_unified(start_time, end_time, variable, agg_days, grid=grid,
                                missing_thresh=missing_thresh, cell_aggregation='mean', mask=mask, region=region)
