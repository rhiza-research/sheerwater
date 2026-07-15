"""A decorator for event definitions.

A TODO note: this module defines several events and their corresponding boolean filters,
e.g., days_above_threshold and has_days_above_threshold, where days_above_threshold returns
an integer count of days and has_days_above_threshold takes an additional argument of the number of days
and returns a boolean mask. This pattern is repeated several times and could be consolidated and
supported in a more general way.
"""
from functools import wraps
import numpy as np
import pandas as pd
import xarray as xr
from sheerwater.utils import (roll_and_agg, groupby_time, get_dates,
                              convert_init_time_to_pred_time, convert_pred_time_to_init_time)

EVENT_REGISTRY = {}


def wrap_duration(duration_fn, event_name):
    """Call ``duration_fn(event_kwargs)``, turning missing keys into a clear ``ValueError``."""

    def wrapped(event_kwargs):
        try:
            return duration_fn(event_kwargs)
        except KeyError as e:
            key = e.args[0] if e.args else None
            raise ValueError(f"Event {event_name} requires key {key} in event_kwargs") from e
    return wrapped


def event(default_variable=None, duration=0, filter=False):
    """Stub decorator for event definitions. Extend with registration or wrapping as needed.

    Args:
        default_variable: The default variable for the event.
        duration: The duration of the event. Can be a callable that takes in event kwargs or an integer.
            For example, `11` and `lambda kwargs: kwargs['agg_days'] + 1` are both valid.
        filter: Whether the event returns a 0 to 1 mask that can be used to filter the data.
            TODO: could add error checking to enforce this. Atm, is only a soft check.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(ds, *args, **kwargs):
            name = fn.__name__.lower()

            if 'agg_days' in ds.attrs and ds.attrs['agg_days'] != 1:
                raise ValueError(f"Event {name} requires agg_days to be 1.")

            if callable(duration):
                dur = duration(kwargs)
            else:
                dur = duration
            if len(ds.time) < dur:
                raise ValueError(f"Event {name} requires at least {dur} lead days.")

            try:
                ds = fn(ds, *args, **kwargs)
            except TypeError as e:
                raise ValueError(f"Event {name} requires missing event_kwargs key. \n{e}") from e

            # Add an attribute to the dataset to indicate the event name
            ds = ds.assign_attrs({'event': name})
            return ds

        event_name = fn.__name__.lower()
        if callable(duration):
            wrapper.duration = wrap_duration(duration, event_name)
        else:
            wrapper.duration = duration
        wrapper.default_variable = default_variable
        wrapper.filter = filter
        EVENT_REGISTRY[event_name] = wrapper
        return wrapper

    return decorator


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=False)
def digitized(ds, agg_days, bins, align='left'):
    """An event to digitize a dataset into bins."""
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean', align=align)

    # Save and restore the null pattern, which is removed by the boolean operations
    null_mask = ds.isnull()
    attrs = ds.attrs.copy()

    # Bins are right aligned, so we want to detect below and up to the theshold, and strictly greater
    ds = xr.apply_ufunc(
        np.digitize,
        ds,
        kwargs={'bins': bins, 'right': True},
        dask='parallelized',
        output_dtypes=[int],
    )
    # Restore NaN values
    ds = ds.where(~null_mask, np.nan).assign_attrs(attrs)
    return ds


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=True)
def above_threshold(ds, agg_days, threshold, align='left', margin_in_days=0, margin_align='center'):
    """An event to calculate the above threshold of a dataset."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ds = digitized(ds, agg_days=agg_days, bins=bins, align=align)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)

    ds = ds.astype(float) - 1.0
    if margin_in_days > 0:
        # Soften the detections by margin in days
        ds = roll_and_agg(ds, agg=margin_in_days, agg_col="time", align=margin_align, agg_fn='max')
    return ds


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=True)
def below_threshold(ds, agg_days, threshold, align='left', margin_in_days=0, margin_align='center'):
    """An event to calculate the above threshold of a dataset."""
    above = above_threshold(ds, agg_days=agg_days, threshold=threshold, align=align,
                            margin_in_days=margin_in_days, margin_align=margin_align)
    return 1.0 - above


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=False)
def accumulated_rain(ds, agg_days, align='right'):
    """An event to calculate the accumulated rain over a sliding, aligned window."""
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", align=align, agg_fn='sum')
    return ds


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=False)
def days_above_threshold(ds, agg_days, threshold):
    """An event to calculate the number of days above a threshold."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ret = digitized(ds, agg_days=1, bins=bins)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)
    ret = ret.astype(float) - 1.0
    ret = roll_and_agg(ret, agg=agg_days, agg_col="time", agg_fn='sum')
    null_mask = ret.isnull()
    # Restore NaN values
    ret = ret.where(~null_mask, np.nan)
    return ret


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=True)
def has_days_above_threshold(ds, agg_days, threshold, above_days):
    """An event to calculate whether a forecast spends sufficient time above a threshold."""
    ds = days_above_threshold(ds, agg_days=agg_days, threshold=threshold)
    null_mask = ds.isnull()
    ds = (ds >= above_days)
    # Restore NaN values
    ds = ds.where(~null_mask, np.nan)
    return ds


@event(default_variable="precip", duration=lambda kwargs: kwargs["smoothing"]+kwargs["continuous_days"], filter=True)
def has_continuous_days_above_threshold(ds, threshold, smoothing, continuous_days):
    """An event to calculate whether a forecast spends consecutive days above a threshold."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ret = digitized(ds, agg_days=1, bins=bins)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)
    ret = ret.astype(float) - 1.0

    # Smooth detected above periods with a center-aligned max window
    ret = roll_and_agg(ret, agg=smoothing, agg_col="time", align="center", agg_fn='max')

    # Now count the number of consecutive days above the threshold
    ret = roll_and_agg(ret, agg=continuous_days, agg_col="time", agg_fn='sum')
    null_mask = ret.isnull()
    ret = (ret == continuous_days)

    # Restore NaN values
    ret = ret.where(~null_mask, np.nan)
    return ret


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


@event(default_variable="precip", duration=120, filter=False)
def seasonal_accumulation(ds, time_grouping='year', by_percent=False, minimum_accumulation_mm=0.0):
    """A function to calculate the seasonal accumulation of a dataset."""
    # Add the grouping coordinates but perform no aggregation
    ds = groupby_time(ds, time_grouping, agg_fn=None)
    ds = remove_partial_time_groups(ds, time_grouping=time_grouping, coverage_threshold=0.95)

    nanmask = ds.isnull()

    # Set all times to zero where the group in the null mask (i.e., season was None)
    is_null_group = ds['group'].astype(str).str.contains('None')
    ds = ds.where(~is_null_group, np.nan)

    def seasonal_accumulation_runner(x):
        cumsum = x.cumsum(dim="time")
        # There is a bug in xarray cumsum that causes the time coordinate to be lost
        # https://github.com/pydata/xarray/issues/6528
        cumsum = cumsum.assign_coords(time=x['time'])
        low_season_rain = (cumsum.max(dim="time") < minimum_accumulation_mm).astype(int)
        if by_percent:
            cumsum = cumsum / cumsum.max(dim="time")
        # Remove low rain seasons
        cumsum = xr.where(low_season_rain == 1, 0, cumsum)
        cumsum = cumsum.astype(int)
        return cumsum

    # Ensure that the timedimension is sorted
    ds = ds.sortby("time")
    ret = ds.groupby("group").map(seasonal_accumulation_runner)

    # Restore the null pattern and attributes, which are lost during the grouping
    ret = ret.where(~nanmask, other=np.nan)
    ret = ret.assign_attrs(ds.attrs)
    return ret


@event(default_variable="precip", duration=120, filter=True)
def has_seasonal_accumulation(ds, time_grouping='year', accumulation_threshold=200.0, by_percent=False):
    """A function to calculate the start of season by accumulation of a dataset."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season by accumulation event requires a 'precip' variable.")

    ds = seasonal_accumulation(ds, time_grouping=time_grouping, by_percent=by_percent)
    null_mask = ds.isnull()
    ds_suitable = (ds >= accumulation_threshold)
    ds_suitable = ds_suitable.where(~null_mask, np.nan)

    attrs = ds.attrs.copy()
    return ds_suitable.assign_attrs(attrs)


@event(default_variable="precip", duration=120, filter=True)
def in_season(ds, time_grouping='year',
              start_season_accumulation=0.2,
              end_season_accumulation=0.8,
              by_percent=True,
              minimum_accumulation_mm=0.0):
    """Calculate the in season period of a dataset.

    Marks all times where the cumulative sum is between the start and end season accumulation thresholds with 1.

    Args:
        ds: The input xarray.Dataset
        time_grouping: How to group time ("year" by default)
        start_season_accumulation: Threshold (value) in the cumsum to start the season
        end_season_accumulation: Threshold (value) in the cumsum to end the season
        by_percent: Whether to compute cumsum as percent of max in season
        minimum_accumulation_mm: Minimum accumulation value to use if using by percent accumulation.
    """
    # Add the grouping coordinates but perform no aggregation
    ds = groupby_time(ds, time_grouping, agg_fn=None)
    ds = remove_partial_time_groups(ds, time_grouping=time_grouping, coverage_threshold=0.95)
    nanmask = ds.isnull()

    # Set all times to NaN where season/group is None
    is_null_group = ds['group'].astype(str).str.contains('None')
    ds = ds.where(~is_null_group, np.nan)

    def in_season(x):
        cumsum = x.cumsum(dim="time")
        # There is a bug in xarray cumsum that causes the time coordinate to be lost
        # https://github.com/pydata/xarray/issues/6528
        cumsum = cumsum.assign_coords(time=x['time'])

        low_season_rain = (cumsum.max(dim="time") < minimum_accumulation_mm).astype(int)
        if by_percent:
            cumsum = cumsum / cumsum.max(dim="time")
        season = (cumsum >= start_season_accumulation) & (cumsum <= end_season_accumulation)
        season = season & ~low_season_rain
        season = season.astype(int)
        return season

    # Ensure that the time dimension is sorted
    ds = ds.sortby("time")
    ret = ds.groupby("group").map(in_season)

    # Restore the null pattern and attributes, which are lost during the grouping
    ret = ret.where(~nanmask, other=np.nan)
    ret = ret.assign_attrs(ds.attrs)
    return ret


@event(default_variable="precip", duration=120, filter=True)
def first_seasonal_accumulation(ds, time_grouping='year', by_percent=False,
                                accumulation_threshold=200.0):
    """Calculate the first time(s) a seasonal accumulation threshholds(s) is crossed.

    Marks all times where the cumulative sum crosses any of the specified accumulation thresholds with a 1.

    Args:
        ds: The input xarray.Dataset
        time_grouping: How to group time ("year" by default)
        by_percent: Whether to compute cumsum as percent of max in season
        accumulation_threshold: Threshold (value) in the cumsum to flag.
        by_percent_minimum_accumulation: Minimum accumulation value to use if using by percent accumulation.
    """
    if not isinstance(accumulation_threshold, list):
        accumulation_threshold = [accumulation_threshold]

    # Add the grouping coordinates but perform no aggregation
    ds = groupby_time(ds, time_grouping, agg_fn=None)
    ds = remove_partial_time_groups(ds, time_grouping=time_grouping, coverage_threshold=0.95)
    nanmask = ds.isnull()

    # Set all times to NaN where season/group is None
    is_null_group = ds['group'].astype(str).str.contains('None')
    ds = ds.where(~is_null_group, np.nan)

    def multi_point_accumulation(x):
        cumsum = x.cumsum(dim="time")
        # There is a bug in xarray cumsum that causes the time coordinate to be lost
        # https://github.com/pydata/xarray/issues/6528
        cumsum = cumsum.assign_coords(time=x['time'])
        if by_percent:
            cumsum = cumsum / cumsum.max(dim="time")

        # For each threshold, flag all times the cumsum crosses the threshold; then "or" them together
        result = None
        for thresh in accumulation_threshold:
            above = (cumsum >= thresh)
            # Mark the first crossing with 1, and 0 elsewhere for this threshold
            above_int = above.astype(int)
            # Only want the first crossing: same logic as before, cumsum and equals 1
            crossing = ((above_int == 1) & (above_int.cumsum(dim="time") == 1)).astype(int)
            # Accumulate all such cross-points (logical OR)
            if result is None:
                result = crossing
            else:
                result = result + crossing  # sum is fine; values will be >=0
        # Convert to 1s, but not double count if multiple hits happen at once
        result = (result >= 1).astype(int)
        return result

    # Ensure that the time dimension is sorted
    ds = ds.sortby("time")
    ret = ds.groupby("group").map(multi_point_accumulation)

    # Restore the null pattern and attributes, which are lost during the grouping
    ret = ret.where(~nanmask, other=np.nan)
    ret = ret.assign_attrs(ds.attrs)
    return ret


@event(default_variable="precip", duration=lambda kwargs: kwargs["drying_day_agg_in_days"], filter=True)
def drying_spells(ds, drying_day_threshold_mm=2.0, drying_day_agg_in_days=5):
    """A function to calculate the drying spells of a dataset."""
    # Find drying spells
    total_rain = accumulated_rain(ds, agg_days=drying_day_agg_in_days, align='right')
    null_mask = total_rain.isnull()
    drying_spells = (total_rain < drying_day_threshold_mm).astype(int)
    drying_spells = drying_spells.where(~null_mask, np.nan)
    attrs = ds.attrs.copy()
    return drying_spells.assign_attrs(attrs)


@event(default_variable="precip", duration=120, filter=True)
def initial_growing_period(
        ds,
        time_grouping='year',
        early_season_accumulation_by_percent=0.10,
        mid_season_accumulation_by_percent=0.30,
        season_accumulation_minimum_mm=300.0,
        first_rain_threshold_mm=5.0,
        pre_period_in_days=30):
    """A function to calculate the initial growing period of a dataset."""
    null_mask = ds.isnull()

    # Add the grouping coordinates but perform no aggregation
    ds = groupby_time(ds, time_grouping, agg_fn=None)
    ds = remove_partial_time_groups(ds, time_grouping=time_grouping, coverage_threshold=0.95)
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


@event(default_variable="precip", duration=10, filter=True)
def icpac_onset(ds):
    """An event to calculate the ICPAC onset conditions."""
    spells = ['above', 'above']
    agg_days = [3, 7]
    thresholds = [21.0, 10.5]
    agg_type = ['sum', 'sum']
    counts = [None, None]
    onset_spell_index = 0
    return has_onset_conditions(ds, spells=spells, agg_days=agg_days, thresholds=thresholds,
                                agg_type=agg_type, counts=counts, onset_spell_index=onset_spell_index)


@event(default_variable="precip", duration=30, filter=True)
def chc_onset(ds):
    """An event to calculate the CHC onset conditions."""
    spells = ['above', 'above']
    agg_days = [10, 20]
    thresholds = [25.0, 20.0]
    agg_type = ['sum', 'sum']
    counts = [None, None]
    onset_spell_index = 0
    return has_onset_conditions(ds, spells=spells, agg_days=agg_days, thresholds=thresholds,
                                agg_type=agg_type, counts=counts, onset_spell_index=onset_spell_index)


@event(default_variable="precip", duration=15, filter=True)
def moron_and_robertson_onset(ds):
    """An event to calculate the Moron and Robertson onset conditions."""
    spells = ['above', 'above']
    agg_days = [5, 10]
    thresholds = [38.0, 5.0]
    agg_type = ['sum', 'sum']
    counts = [None, None]
    onset_spell_index = 0
    return has_onset_conditions(ds, spells=spells, agg_days=agg_days, thresholds=thresholds,
                                agg_type=agg_type, counts=counts, onset_spell_index=onset_spell_index)


@event(default_variable="precip", duration=30, filter=True)
def wet_not_dry_count_onset(ds):
    """An event to calculate the wer,  not dry count onset conditions."""
    spells = ['above', 'above']
    agg_days = [10, 20]
    thresholds = [5.0, 5.0]
    agg_type = ['count', 'count']
    counts = [3, 1]
    onset_spell_index = 0
    return has_onset_conditions(ds, spells=spells, agg_days=agg_days, thresholds=thresholds,
                                agg_type=agg_type, counts=counts, onset_spell_index=onset_spell_index)


@event(default_variable="precip", duration=40, filter=True)
def dry_wet_not_dry_onset(ds):
    """An event to calculate the dry wet not dry onset conditions."""
    spells = ['below', 'above', 'above']
    agg_days = [20, 10, 10]
    thresholds = [1.0, 2.5, 2.0]
    agg_type = ['mean', 'mean', 'mean']
    counts = [None, None, None]
    onset_spell_index = 1
    return has_onset_conditions(ds, spells=spells, agg_days=agg_days, thresholds=thresholds,
                                agg_type=agg_type, counts=counts, onset_spell_index=onset_spell_index)


@event(default_variable="precip", duration=lambda kwargs: np.sum(kwargs["agg_days"]), filter=True)
def has_onset_conditions(ds, spells=['below', 'above', 'above'], agg_days=[20, 10, 20],
                         thresholds=[10.0, 25.0, 20.0], agg_type=['sum', 'sum', 'sum'],
                         counts=[None, None, None],
                         onset_spell_index=1):
    """A function to calculate the planting suitability of a dataset.

    Args:
        ds (xr.Dataset): The input dataset.
        onset_definition (str): The onset definition to use, from a set of predefined definitions.
            If this is not None, the other arguments are ignored.
        spells (list[str]): The wet, not dry, and dry spells to use in the onset definition.
            Options are 'wet', 'not_dry', and 'dry'.
        agg_days (list[int]): The aggregation days to use for each spell. Should correspond to the spells list.
        thresholds (list[float]): The thresholds to use for each spell. Should correspond to the spells list.
        agg_type (list[str]): The aggregation type to use for each spell. Should correspond to the spells list.
            Options are 'mean', 'sum', and 'count'.
        counts (list[int]): The counts to use for each spell. Should correspond to the spells list.
            This is ignored if the agg_type is not 'count'.
        onset_spell_index (int): The start of season index to use, within the spells list. For example, if
            the spells list is ['wet', 'not_dry', 'dry'], and the start of season spell is [1], then the returned
            dataframe will have a 1 centered around the start of the not_dry spell.
    """
    # Input error checking
    if len(spells) != len(agg_days) or len(spells) != len(thresholds) or \
            len(spells) != len(agg_type) or len(spells) != len(counts):
        raise ValueError("The number of spells, agg days, thresholds, agg types, and counts must be the same.")
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season by spells event requires a 'precip' variable.")
    for i, a_type in enumerate(agg_type):
        if a_type not in ['mean', 'sum', 'count']:
            raise ValueError(f"Invalid aggregation type: {a_type}")
        if a_type == 'count' and not isinstance(counts[i], int):
            raise ValueError(f"Count type requires an integer count, got {counts[i]}")
    if not all(x in ['above', 'below'] for x in spells):
        raise ValueError(f"Invalid spells: {spells}")

    # We want to declare start of season around the trigger index event, and need to align dry spells before it
    # and wet spells after it with the trigger index event.
    shift_indices = [0]*len(spells)
    # Compute the shift indicies for each spell. We want everything to align around the trigger index
    event_indicies = list(zip(range(len(spells)), spells, agg_days))
    # Shift the events before the trigger index to the right (positive)
    shift_days = 0
    for index, event, agg in event_indicies[0:onset_spell_index][::-1]:
        shift_days += agg
        shift_indices[index] = shift_days
    # Shift the events after the trigger index to the left (negative)
    shift_days = -agg_days[onset_spell_index]
    for index, event, agg in event_indicies[onset_spell_index+1:]:
        shift_indices[index] = shift_days
        shift_days -= agg

    # Get the spell timeseries
    spell_timeseries = []
    for i, event in enumerate(spells):
        spell_event_threshold = thresholds[i]
        spell_agg_days = agg_days[i]
        if agg_type[i] == 'mean':
            spell = above_threshold(ds, agg_days=spell_agg_days, threshold=spell_event_threshold)
        elif agg_type[i] == 'sum':
            spell = above_threshold(ds, agg_days=spell_agg_days, threshold=spell_event_threshold / spell_agg_days)
        elif agg_type[i] == 'count':
            spell = has_days_above_threshold(ds, agg_days=spell_agg_days,
                                             threshold=spell_event_threshold, above_days=counts[i])

        if event == 'below':
            # Looking for not above threshhold, so negate the event
            spell = 1.0 - spell

        # Shift the spell to be aligned with the trigger index
        if i != onset_spell_index:
            spell = spell.shift(time=shift_indices[i])
        spell_timeseries.append(spell)

    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    ret = xr.ones_like(ds['precip'])
    for spell in spell_timeseries:
        ret = ret * spell

    # Invalid at start
    invalid_at_start = int(np.sum(shift_indices[0:onset_spell_index]))
    invalid_at_end = int(np.sum(np.abs(shift_indices[onset_spell_index+1:])))
    ret = ret.isel(time=slice(invalid_at_start, -invalid_at_end))
    return ret.assign_attrs(attrs)


@event(default_variable="precip", duration=30, filter=True)
def seasonal_accumulation_with_leaky_bucket(ds, time_grouping='year', leak_rate=4, runoff_rate=20, max_bucket=120.0):
    """A function to calculate the seasonal accumulation of a dataset with a leaky bucket."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season by accumulation event requires a 'precip' variable.")

    # Add the grouping coordinates but perform no aggregation
    ds = groupby_time(ds, time_grouping, agg_fn=None)
    nanmask = ds.isnull()
    attrs = ds.attrs.copy()

    # Set all times to zero where the group in the null mask (i.e., season was None)
    is_null_group = ds['group'].astype(str).str.contains('None')
    ds = ds.where(~is_null_group, np.nan)

    def leaky_bucket(precip, leak_rate, runoff_rate):
        """Simple leaky bucket model to calculate accumulated precipitation.

        Args:
            precip: 1D numpy array of precipitation values
            leak_rate: amount bucket drains per timestep (mm/day)
            runoff_rate: above this amount, rainfall runs off (mm/day)
        """
        result = np.empty_like(precip, dtype=float)
        bucket = 0.0
        for i, p in enumerate(precip):
            bucket = max(0.0, bucket + min(p, runoff_rate) - leak_rate)
            # Bucket overflows beyond max_bucket
            bucket = min(bucket, max_bucket)
            result[i] = bucket
        return result

    def func(x):
        ret = xr.apply_ufunc(
            leaky_bucket,
            x,
            input_core_dims=[["time"]],
            output_core_dims=[["time"]],
            kwargs={"leak_rate": leak_rate, "runoff_rate": runoff_rate, "max_bucket": max_bucket},
            dask="parallelized",
            vectorize=True,
            output_dtypes=[float],
        )
        return ret

    # Ensure that the timedimension is sorted
    ds = ds.sortby("time")
    ds = ds.chunk({'time': -1})  # must
    ret = ds.groupby("group").map(func)

    # Restore the null pattern and attributes, which are lost during the grouping
    ret = ret.where(~nanmask, other=np.nan)
    ret = ret.assign_attrs(attrs)
    return ret


@event(default_variable="precip", duration=30, filter=True)
def has_seasonal_accumulation_with_leaky_bucket(ds, time_grouping='year', accumulation_threshold=40.0,
                                                leak_rate=4, runoff_rate=20, max_bucket=120.0):
    """A function to calculate the start of season by accumulation of a dataset with a leaky bucket."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season by accumulation with leaky bucket event requires a 'precip' variable.")

    ds = seasonal_accumulation_with_leaky_bucket(
        ds, time_grouping=time_grouping, leak_rate=leak_rate, runoff_rate=runoff_rate, max_bucket=max_bucket)
    null_mask = ds.isnull()
    ds_suitable = (ds >= accumulation_threshold)
    ds_suitable = ds_suitable.where(~null_mask, np.nan)
    attrs = ds.attrs.copy()
    return ds_suitable.assign_attrs(attrs)


def get_event_fn(name):
    """Get an event function from the registry."""
    if name is None:
        return None
    if name not in EVENT_REGISTRY:
        raise ValueError(f"Event {name!r} not found.")
    return EVENT_REGISTRY[name]
