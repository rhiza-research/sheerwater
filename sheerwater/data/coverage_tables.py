import pandas as pd
import xarray as xr

from sheerwater.utils import dask_remote
from nuthatch import cache
from sheerwater.metrics import coverage

def _coverage_table(start_time, end_time, stations, agg_days, variable="precip",
                    time_grouping=None, space_grouping=None, 
                    grid="global1_5", mask='lsm', region='global'):
       """Internal function to compute coverage table across multiple aggregation days."""
       # The results will be stored in an x-array with time, region for time and space groupings
       results_ds = xr.Dataset(coords={'time': None, 'region': None})

       # Make sure agg_days is a list
       if not isinstance(agg_days, list):
              agg_days = [agg_days]

       for station_data in stations:
              for agg in agg_days:
                     print(f"Running coverage of {station_data} for {variable} for {agg} days, "
                     f"time grouping {time_grouping}, space grouping {space_grouping}, "
                     f"grid {grid}, mask {mask}, region {region}")
                     try:
                            ds = coverage(start_time=start_time, end_time=end_time, variable=variable, agg_days=agg, 
                                          station_data=station_data, time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask=mask, region=region)
                     except NotImplementedError:
                            ds = None
                     if ds:
                            ds = ds.rename({'coverage': agg})
                            ds = ds.expand_dims({'station': [station_data]}, axis=0)
                            results_ds = results_ds.merge(ds[[agg]])

       if not time_grouping:
              results_ds = results_ds.reset_coords('time', drop=True)
       if not space_grouping:
              results_ds = results_ds.reset_coords('region', drop=True)
       
       results_ds = results_ds.drop_vars([var for var in results_ds.coords if var not in results_ds.dims], errors='ignore')
       df = results_ds.to_dataframe().reset_index()
       
       order = ['station', 'time_grouping', 'region'] + agg_days

       if 'time' in df.columns:
              df = df.rename(columns={'time': 'time_grouping'})
              df['time_grouping'] = df['time_grouping'].map({'M01': 'January',
                                                        'M02': 'February',
                                                        'M03': 'March',
                                                        'M04': 'April',
                                                        'M05': 'May',
                                                        'M06': 'June',
                                                        'M07': 'July',
                                                        'M08': 'August',
                                                        'M09': 'September',
                                                        'M10': 'October',
                                                        'M11': 'November',
                                                        'M12': 'December'})
       else:
              df['time_grouping'] = None

       if 'region' not in df.columns:
              df['region'] = None

       df = df[order]

       return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'time_grouping', 'space_grouping', 'grid', 'region'],
       backend='sql', backend_kwargs={'hash_table_name': True})
def coverage_table_stations_aggdays(start_time, end_time, variable='precip',
                 time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm', region='global'):
    """Generate coverage data."""
    agg_days = [3, 5, 7, 10, 11, 20]
    stations = ["ghcn_avg", "tahmo_avg"]
    df = _coverage_table(start_time=start_time, end_time=end_time, variable=variable, stations=stations,
                         time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, region=region,
                         agg_days=agg_days)
    print(df)
    return df