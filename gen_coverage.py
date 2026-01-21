from sheerwater.metrics import coverage
from sheerwater.utils import dask_remote
from nuthatch import cache
from sheerwater.utils import start_remote

@dask_remote
@cache(cache_args=["station_data", "time_grouping", "space_grouping"],
       backend='sql')
def get_coverage(start_time, end_time, variable='precip', agg_days=7, station_data='ghcn_avg',
                 time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm', region='global'):
    """Generate coverage data."""
    ds = coverage(start_time=start_time, end_time=end_time, variable=variable, agg_days=agg_days, 
    station_data=station_data, time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask=mask, region=region)
    df = ds.to_dataframe()
    return df

if __name__ == "__main__":
    start_time = "2020-01-01"
    end_time = "2020-03-01"
    variable = "precip"
    agg_days = 7
    station_data = "ghcn_avg"
    time_grouping = "month"
    space_grouping = "country"
    grid = "global1_5"
    mask = "lsm"
    region = "global"
    start_remote(remote_config='large_cluster')
    df = get_coverage(start_time, end_time, variable=variable, agg_days=agg_days, station_data=station_data,
                      time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask=mask, region=region,
                      backend='sql')