"""Verification metrics for forecasters and reanalyses."""
from sheerwater.utils import cacheable, dask_remote
from sheerwater.metrics_library import metric_factory


@dask_remote
@cacheable(data_type='array',
           cache_args=['start_time', 'end_time', 'variable', 'agg_days', 'forecast', 'truth',
                       'metric_name', 'time_grouping', 'spatial', 'grid', 'mask', 'region'],
           chunking={"lat": 121, "lon": 240, "time": 30, 'region': 300, 'prediction_timedelta': -1},
           chunk_by_arg={
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           },
           cache=True)
def metric(start_time, end_time, variable, agg_days, forecast, truth,
           metric_name, time_grouping=None, spatial=False, grid="global1_5",
           mask='lsm', region='countries'):
    """Compute a grouped metric for a forecast at a specific lead."""
    # Use the metric registry to get the metric class
    metric_obj = metric_factory(metric_name, start_time=start_time, end_time=end_time, variable=variable,
                                agg_days=agg_days, forecast=forecast, truth=truth, time_grouping=time_grouping,
                                spatial=spatial, grid=grid, mask=mask, region=region)
    return metric_obj.compute()


__all__ = ['metric']
