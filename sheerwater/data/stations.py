"""One station datasource to rule them all."""
import math
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, roll_and_agg
from sheerwater.data import knust, knust_avg, tahmo, tahmo_avg, ghcn, ghcn_avg
from sheerwater.interfaces import data as sheerwater_data, spatial, get_data


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid', 'missing_thresh', 'cell_aggregation', 'variable'],
       backend_kwargs={'chunking': {'time': 365, 'lat': 300, 'lon': 300, }})
def stations_aggregated(start_time, end_time, variable,
                        grid='global0_25', missing_thresh=0.9,
                        cell_aggregation='mean', mask=None, region='global'):
    """Aggregate station data from all station sources into a single dataset."""
    suffix = '_avg' if cell_aggregation == 'mean' else ''
    sources = ['knust', 'tahmo', 'ghcn']

    # Get all the datasets
    fns = [(source, get_data(source + suffix)) for source in sources]
    datasets = [fn(start_time, end_time, variable=variable, grid=grid, agg_days=1,
                   missing_thresh=missing_thresh,
                   mask=mask, region=region)
                .chunk({'time': 365, 'lat': 300, 'lon': 300})
                .expand_dims(dim={"source": [source]})
                for source, fn in fns]

    import pdb
    pdb.set_trace()

    ds = xr.conct(datasets, dim='source')

    if cell_aggregation != 'mean':
        raise ValueError(f"Cell aggregation {cell_aggregation} not supported")

    # Compute the mean, weighted by the number of stations in each source
    weight_sum = ds[f'{variable}_count'].sum(dim='source')
    # weight_sum = ds[[f'{source}_count' for source in sources]].to_array(dim='source').sum(dim='source')
    ds[f'{variable}_count'] = ds[f'{variable}_count'] / weight_sum
    import pdb
    pdb.set_trace()
    out = (ds[variable] * ds[f'{variable}_count']).sum(dim='source')
    return out.to_dataset(name=variable)


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
