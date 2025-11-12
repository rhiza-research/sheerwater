"""Verification metrics for forecasters and reanalyses."""
from sheerwater_benchmarking.utils import cacheable, dask_remote
from sheerwater_benchmarking.metrics_library import metric_factory


@dask_remote
@cacheable(data_type='array',
           cache_args=['start_time', 'end_time', 'variable', 'lead', 'forecast',
                       'truth', 'metric', 'time_grouping', 'spatial', 'grid', 'mask', 'region'],
           chunking={"lat": 121, "lon": 240, "time": -1},
           chunk_by_arg={
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           },
           cache=True)
def grouped_metric(start_time, end_time, variable, lead, forecast, truth,
                   metric, time_grouping=None, spatial=False, grid="global1_5",
                   mask='lsm', region='africa'):
    """Compute a grouped metric for a forecast at a specific lead."""
    # TODO: Delete, keeping around for cachable function atm
    pass


@dask_remote
@cacheable(data_type='array',
           cache_args=['start_time', 'end_time', 'variable', 'agg_days', 'forecast', 'truth',
                       'metric', 'time_grouping', 'spatial', 'grid', 'mask', 'region'],
           chunking={"lat": 121, "lon": 240, "time": 30, 'region': 300, 'lead_time': -1},
           chunk_by_arg={
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           },
           cache=True)
def grouped_metric_new(start_time, end_time, variable, agg_days, forecast, truth,
                       metric, time_grouping=None, spatial=False, grid="global1_5",
                       mask='lsm', region='countries'):
    """Compute a grouped metric for a forecast at a specific lead."""
    # Use the metric registry to get the metric class
    cache_kwargs = {
        'start_time': start_time,
        'end_time': end_time,
        'variable': variable,
        'agg_days': agg_days,
        'forecast': forecast,
        'truth': truth,
        'time_grouping': time_grouping,
        'spatial': spatial,
        'grid': grid,
        'mask': mask,
        'region': region,
    }
    metric_obj = metric_factory(metric, **cache_kwargs)
    m_ds = metric_obj.compute()
    return m_ds


__all__ = ['grouped_metric']
