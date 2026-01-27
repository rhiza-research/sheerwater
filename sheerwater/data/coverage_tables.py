import pandas as pd

from sheerwater.utils import dask_remote
from nuthatch import cache
from sheerwater.metrics import coverage

@dask_remote
@cache(cache_args=["station_data", "time_grouping", "space_grouping"],
       backend='sql', backend_kwargs={'hash_table_name': True})
def coverage_table(start_time, end_time, variable='precip', station_data='ghcn_avg',
                 time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm', region='global'):
    """Generate coverage data."""
    # concatenate dataframes for each agg_days
    results = []
    for agg_days in [3, 5, 7, 10, 11, 20]:
       ds = coverage(start_time=start_time, end_time=end_time, variable=variable, agg_days=agg_days, 
       station_data=station_data, time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask=mask, region=region)
       df = ds.to_dataframe()
       # drop rows where coverage is nan
       df = df.dropna(subset=['coverage'])
       df["agg_days"] = agg_days
       results.append(df.reset_index())
    df = pd.concat(results)
    return df