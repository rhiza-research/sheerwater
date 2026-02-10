"""Coverage tables for station data."""
import xarray as xr

from sheerwater.utils import dask_remote
from nuthatch import cache
from sheerwater.metrics import coverage

@dask_remote
@cache(cache_args=['variable', 'time_grouping', 'space_grouping', 'grid', 'region', 'stations'],
       backend='sql', backend_kwargs={'hash_table_name': True})
def coverage_table(start_time, end_time, stations, agg_days, variable="precip",
                    time_grouping=None, space_grouping=None,
                    grid="global1_5", mask='lsm', region='global'):
       """Internal function to compute coverage table across multiple aggregation days.

       Results have format: time_group, space_group, agg_days, cells_count, periods_count, cells_covered, average_cell_periods
       """
       # The results will be stored in an x-array with time, region for time and space groupings
       results_ds = xr.Dataset(coords={'time': None, 'region': None})

       if time_grouping in ["month_of_year", "quarter_of_year"]:
              raise NotImplementedError("Coverage table does not support 'type' time groupings")

       # Make sure agg_days is a list
       if not isinstance(agg_days, list):
              agg_days = [agg_days]

       for agg in agg_days:
              print(f"Running coverage of {stations} for {variable} for {agg} days, "
              f"time grouping {time_grouping}, space grouping {space_grouping}, "
              f"grid {grid}, mask {mask}, region {region}")
              try:
                     ds = coverage(
                         start_time=start_time, end_time=end_time, variable=variable, agg_days=agg,
                         station_data=stations, time_grouping=time_grouping, space_grouping=space_grouping,
                         grid=grid, mask=mask, region=region
                     )
              except NotImplementedError:
                     ds = None
              if ds:
                     ds = ds.expand_dims(agg_days=[agg])
                     results_ds = results_ds.merge(ds)

       results_ds = results_ds.drop_vars(
           [var for var in results_ds.coords if var not in results_ds.dims], errors='ignore'
       )
       df = results_ds.to_dataframe().reset_index()

       order = [
           'time_grouping', 'region', 'agg_days', 'cells_count', 'periods_count',
           'cells_covered', 'average_cell_periods'
       ]

       if 'time' in df.columns:
              df = df.rename(columns={'time': 'time_grouping'})
       else:
              df['time_grouping'] = None

       if 'region' not in df.columns:
              df['region'] = None

       df = df[order]

       return df
