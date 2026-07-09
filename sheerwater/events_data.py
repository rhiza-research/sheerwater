import pandas as pd
import numpy as np
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries
from sheerwater.interfaces import spatial, get_data
from sheerwater.utils import get_dates, groupby_time, roll_and_agg


def remove_partial_time_groups(ds, time_grouping='year', coverage_threshold=0.95):
    """Remove time groups that don't have enough coverage."""
    years = pd.to_datetime(ds.time.values).year
    min_year = years.min()
    max_year = years.max()
    # Pad the dataset with lagging and leading time to ensure that all partial seasons
    # are dropped properly, even those that are misaligned with the start and end
    # of the year
    start_time = pd.Timestamp(f"{min_year-1}-09-01")
    end_time = pd.Timestamp(f"{max_year+1}-02-28")
    daily_timeseries = get_dates(start_time, end_time, stride='day', return_string=False)
    ds = ds.reindex(time=daily_timeseries, fill_value=np.nan)

    # Add the grouping coordinates but perform no aggregation
    ds = groupby_time(ds, time_grouping, agg_fn=None)

    # Add indicator and non-null variables to the dataset
    var = list(ds.data_vars)[0]
    ds['indicator'] = xr.ones_like(ds[var])
    ds['non_null'] = ds[var].notnull()

    # Coverage per group: fraction of timesteps with non-null data
    group_sums = ds[['indicator', 'non_null']].groupby('group').sum(dim="time", min_count=1)
    group_coverage = group_sums['non_null'] / group_sums['indicator']

    # Set all times to zero where the group in the null mask (i.e., season was None)
    is_null_group = ds['group'].astype(str).str.contains('None')
    ds = ds.where(~is_null_group, other=np.nan)

    # Remove groups that don't have enough coverage
    coverage_at_time = group_coverage.sel(group=ds['group'])
    ds = ds.where(coverage_at_time >= coverage_threshold, other=np.nan)
    ds = ds.drop_vars(['indicator', 'non_null'])

    return ds


@spatial()
@timeseries()
@cache(cache=True, cache_args=['data_source', 'variable', 'time_grouping', 'early_season_accumulation_by_percent',
                               'mid_season_accumulation_by_percent', 'season_accumulation_minimum_mm',
                               'first_rain_threshold_mm', 'pre_period_in_days', 'coverage_threshold', 'grid'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "time": 1000, "prediction_timedelta": 1},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30, "prediction_timedelta": 1}
               },
           }
})
def initial_growing_period_data(
        start_time, end_time, data_source, variable,
        time_grouping='year',
        early_season_accumulation_by_percent=0.10,
        mid_season_accumulation_by_percent=0.30,
        season_accumulation_minimum_mm=300.0,
        first_rain_threshold_mm=5.0,
        pre_period_in_days=30,
        coverage_threshold=0.95,
        grid='global1_5', mask='lsm', region='global'):  # noqa: ARG001
    """A function to calculate the initial growing period of a dataset."""
    ds = get_data(data_source)(start_time=start_time, end_time=end_time,
                               variable=variable, grid=grid,
                               mask=None, region='global')

    # Add the grouping coordinates but perform no aggregation
    ds = groupby_time(ds, time_grouping, agg_fn=None)
    ds = remove_partial_time_groups(ds, time_grouping=time_grouping, coverage_threshold=coverage_threshold)
    null_mask = ds.isnull()

    # Set all times to NaN where time group is None
    is_null_group = ds['group'].astype(str).str.contains('None')
    ds = ds.where(~is_null_group, np.nan)

    def in_season(x):
        cumsum = x.cumsum(dim="time")
        # There is a bug in xarray cumsum that causes the time coordinate to be lost
        # https://github.com/pydata/xarray/issues/6528
        cumsum = cumsum.assign_coords(time=x['time'])

        low_season_rain = (cumsum.max(dim="time") < season_accumulation_minimum_mm).astype(int)
        cumsum = cumsum / cumsum.max(dim="time")
        season = (cumsum >= early_season_accumulation_by_percent) & (cumsum <= mid_season_accumulation_by_percent)
        season = season & ~low_season_rain
        season = season.astype(int)
        return season

    # Ensure that the time dimension is sorted
    ds = ds.sortby("time")
    season = ds.groupby("group").map(in_season)
    season = season.persist()

    # Expand the season by detection period in days
    pre_season = roll_and_agg(season, agg=pre_period_in_days, agg_col="time", align="left", agg_fn='max')
    has_rain = (ds > first_rain_threshold_mm).astype(int)

    # Find the first time where the precipitation is greater than the first rain threshold and the season is active.
    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    pre_season_rain = pre_season * has_rain
    # Continue forward from first rain through the initial growing period
    # Okay to fill past the first date, becuase we're going to
    # or this with the pre-season afterwards.
    first_rain_period = roll_and_agg(pre_season_rain, agg=pre_period_in_days,
                                     agg_col="time", align="right", agg_fn='max')

    # Clip the first rain period back down to the pre-season + season
    full_period = first_rain_period * pre_season

    # Some times have been lost in the rollings, so we will update the null mask to valid times
    null_mask = null_mask.sel(time=full_period.time.values)
    full_period = full_period.where(~null_mask, np.nan)

    attrs = ds.attrs.copy()
    return full_period.assign_attrs(attrs)

