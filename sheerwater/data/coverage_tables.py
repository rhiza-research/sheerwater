from sheerwater.utils import dask_remote
from nuthatch import cache
from sheerwater.metrics import coverage

@dask_remote
@cache(cache_args=["station_data", "time_grouping", "space_grouping"],
       backend='sql', backend_kwargs={'hash_table_name': True})
def get_coverage(start_time, end_time, variable='precip', agg_days=7, station_data='ghcn_avg',
                 time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm', region='global'):
    """Generate coverage data."""
    ds = coverage(start_time=start_time, end_time=end_time, variable=variable, agg_days=agg_days, 
    station_data=station_data, time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask=mask, region=region)
    df = ds.to_dataframe()
    # turn the index into columns
    df = df.reset_index()
    import pdb; pdb.set_trace()
    return df