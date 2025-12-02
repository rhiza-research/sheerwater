"""Verification metrics for forecasters and reanalyses."""
import xarray as xr
from inspect import signature
from nuthatch import cache
import numpy as np
from sheerwater.utils import dask_remote, get_datasource_fn
from sheerwater.metrics_library import metric_factory
from sheerwater.regions_and_masks import region_labels
from sheerwater.utils import get_mask, groupby_time, groupby_region


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'agg_days', 'forecast', 'truth',
                   'metric_name', 'time_grouping', 'spatial', 'grid', 'mask', 'region'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "time": 100, 'region': 300, 'prediction_timedelta': -1},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           }
})
def metric(start_time, end_time, variable, agg_days, forecast, truth,
           metric_name, time_grouping=None, spatial=False, grid="global1_5",
           mask='lsm', region='country-africa'):
    """Compute a grouped metric for a forecast at a specific lead."""
    # Use the metric registry to get the metric class
    if '-' in region:
        region_level, clip = region.split('-')
    else:
        region_level = region
        clip = 'global'
    metric_obj = metric_factory(metric_name, start_time=start_time, end_time=end_time, variable=variable,
                                agg_days=agg_days, forecast=forecast, truth=truth, time_grouping=time_grouping,
                                spatial=spatial, grid=grid, mask=mask, region=region_level, clip=clip)
    return metric_obj.compute()


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'agg_days', 'station_data',
                   'time_grouping', 'grid', 'mask', 'region', 'missing_thresh'])
def coverage(start_time, end_time, variable, agg_days, station_data,
             time_grouping=None, grid="global1_5", mask='lsm', region='country', missing_thresh=0.9):
    """Compute coverage of a dataset."""
    # Use the metric registry to get the metric class
    station_data_fn = get_datasource_fn(station_data)
    data = station_data_fn(start_time, end_time, variable, agg_days=agg_days,
                           grid=grid, mask=None, region='global')

    data['non_null'] = data[variable].notnull()
    data['indicator'] = xr.ones_like(data[variable])
    data = groupby_time(data, time_grouping=time_grouping, agg_fn='mean')

    region_ds = region_labels(grid=grid, region_level="country").compute()
    mask_ds = get_mask(mask=mask, grid=grid)
    data = groupby_region(data, region_ds, mask_ds, agg_fn='sum')

    data['coverage'] = data['non_null'] / data['indicator']

    data = data.drop_vars(variable)
    return data


__all__ = ['metric']
