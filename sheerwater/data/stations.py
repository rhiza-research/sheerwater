"""One station datasource to rule them all."""
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
@cache(cache_args=['grid', 'missing_thresh', 'cell_aggregation', 'variable'],
       backend_kwargs={
           'chunking': {
               'time': 365,
               'lat': 300,
               'lon': 300,
           }
})
def stations_aggregated(start_time, end_time, variable,
                        grid='global0_25', missing_thresh=0.9, cell_aggregation='first', mask=None, region='global'):
    """Aggregate station data from all station sources into a single dataset."""
    if cell_aggregation == 'first':
        knust_ds = knust(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                         mask=mask, region=region)
        tahmo_ds = tahmo(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                         mask=mask, region=region)
        ghcn_ds = ghcn(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                       mask=mask, region=region)
    elif cell_aggregation == 'mean':
        knust_ds = knust_avg(start_time, end_time, variable=variable, grid=grid, agg_days=1,
                             missing_thresh=missing_thresh, mask=mask, region=region)
        tahmo_ds = tahmo_avg(start_time, end_time, variable=variable, grid=grid, agg_days=1,
                             missing_thresh=missing_thresh, mask=mask, region=region)
        ghcn_ds = ghcn_avg(start_time, end_time, variable=variable, grid=grid, agg_days=1, missing_thresh=missing_thresh,
                           mask=mask, region=region)

    knust_ds = knust_ds.expand_dims(dim={"source": ["knust"]})
    knust_ds = knust_ds.chunk({'time': 365, 'lat': 300, 'lon': 300})
    knust_ds['precip'] = knust_ds['precip'].astype('float32')
    tahmo_ds = tahmo_ds.expand_dims(dim={"source": ["tahmo"]})
    ghcn_ds = ghcn_ds.expand_dims(dim={"source": ["ghcn"]})

    # Concat the datasets
    ds = xr.concat([knust_ds, tahmo_ds, ghcn_ds], dim='source')

    if cell_aggregation == 'first':
        ds = ds.ffill(dim='source')
        ds = ds.bfill(dim='source')
        ds = ds.isel(source=0)
        ds = ds.reset_coords('source', drop=True)
    elif cell_aggregation == 'mean':
        # TODO: It would be better to use a weighted mean based on the number of stations in each source.
        # This is a simple mean for now.
        ds = ds.mean(dim='source')

    return ds


@dask_remote
def _stations_unified(start_time, end_time, variable, agg_days,
                      grid='global0_25', missing_thresh=0.9, cell_aggregation='first', mask=None, region='global'):
    """Standard interface for all station data."""
    ds = stations_aggregated(start_time, end_time, variable, grid=grid,
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
def stations(start_time=None, end_time=None, variable='precip', agg_days=1,
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
def stations_avg(start_time=None, end_time=None, variable='precip', agg_days=1,
              grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
              missing_thresh=0.9):
    """Standard interface for all station data."""
    return _stations_unified(start_time, end_time, variable, agg_days, grid=grid,
                             missing_thresh=missing_thresh, cell_aggregation='mean', mask=mask, region=region)
