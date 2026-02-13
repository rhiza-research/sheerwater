"""One station datasource to rule them all."""
import math
import numpy as np
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, roll_and_agg
from sheerwater.interfaces import data as sheerwater_data, spatial, get_data


@dask_remote
@timeseries()
@spatial()
@cache(cache_args=['grid', 'missing_thresh', 'cell_aggregation', 'variable'],
       backend_kwargs={'chunking': {'time': 365, 'lat': 300, 'lon': 300}})
def stations_aggregated(start_time, end_time, variable,
                        grid='global0_25', missing_thresh=0.9,
                        cell_aggregation='mean', mask=None, region='global'):
    """Aggregate station data from all station sources into a single dataset."""
    if cell_aggregation != 'mean':
        raise ValueError(f"Cell aggregation {cell_aggregation} not supported")

    sources = ['knust_avg', 'tahmo_avg', 'ghcn_avg']
    # Get all the datasets
    fns = [(source, get_data(source)) for source in sources]
    datasets = [fn(start_time, end_time, variable=variable, grid=grid, agg_days=1,
                   missing_thresh=missing_thresh,
                   mask=mask, region=region)
                .expand_dims(dim={"source": [source]})
                for source, fn in fns]
    ds = xr.concat(datasets, dim='source', data_vars="minimal", coords="minimal",
                   compat="override", join='outer', fill_value=np.nan)

    weight_sum = ds[f'{variable}_count'].sum(dim='source', min_count=1)
    ds['relative_weight'] = ds[f'{variable}_count'] / weight_sum
    ds[variable] = ds[variable] * ds['relative_weight']
    ds = ds.sum(dim='source', skipna=True, min_count=1)
    ds = ds.drop_vars(['relative_weight'])
    return ds


@dask_remote
@sheerwater_data()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region', 'missing_thresh'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365}})
def stations(start_time=None, end_time=None, variable='precip', agg_days=1,
              grid='global0_25', mask='lsm', region='global',  # noqa: ARG001
              missing_thresh=0.9):
    """Standard interface for all station data."""
    ds = stations_aggregated(start_time, end_time, variable, grid=grid,
                             missing_thresh=missing_thresh, cell_aggregation='mean',
                             mask=mask, region=region)

    agg_thresh = max(math.ceil(agg_days*missing_thresh), 1)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean', agg_thresh=agg_thresh)
    # Note that this is sparse
    ds = ds.assign_attrs(sparse=True)
    return ds
