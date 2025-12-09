"""Verification metrics for forecasters and reanalyses."""
import xarray as xr
from nuthatch import cache

from sheerwater.data.data_decorator import get_data
from sheerwater.metrics_library import metric_factory
from sheerwater.regions_and_masks import region_labels
from sheerwater.utils import dask_remote, get_mask, groupby_region, groupby_time, clip_region


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'agg_days', 'forecast', 'truth',
                   'metric_name', 'time_grouping', 'space_grouping', 'spatial', 'grid', 'mask', 'region'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "time": 100, 'region': 300, 'prediction_timedelta': -1},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           }
})
def metric(start_time, end_time, variable, agg_days, forecast, truth,
           metric_name, time_grouping=None, space_grouping=None,
           spatial=False, grid="global1_5", mask='lsm', region='global'):
    """Compute a grouped metric for a forecast at a specific lead."""
    # Use the metric registry to get the metric class
    metric_obj = metric_factory(metric_name, start_time=start_time, end_time=end_time, variable=variable,
                                agg_days=agg_days, forecast=forecast, truth=truth, time_grouping=time_grouping,
                                space_grouping=space_grouping, spatial=spatial, grid=grid, mask=mask, region=region)
    return metric_obj.compute()


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'agg_days', 'station_data',
                   'time_grouping', 'grid', 'mask', 'region', 'missing_thresh'])
def coverage(start_time=None, end_time=None, variable='precip', agg_days=7, station_data='ghcn_avg',
             time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm',
             region='global', missing_thresh=0.9):  # noqa: ARG001
    """Compute coverage of a dataset."""
    # Use the metric registry to get the metric class
    station_data_fn = get_data(station_data)
    data = station_data_fn(start_time, end_time, variable, agg_days=agg_days,
                           grid=grid, mask=None, region=region)

    data['non_null'] = data[variable].notnull()
    data['indicator'] = xr.ones_like(data[variable])
    data = groupby_time(data, time_grouping=time_grouping, agg_fn='mean')

    region_ds = region_labels(grid=grid, space_grouping=space_grouping, region=region).compute()
    mask_ds = get_mask(mask=mask, grid=grid)
    if region != 'global':
        mask_ds = clip_region(mask_ds, region=region)
    data = groupby_region(data, region_ds, mask_ds, agg_fn='sum')

    data['coverage'] = data['non_null'] / data['indicator']

    data = data.drop_vars(variable)
    return data


__all__ = ['metric']
