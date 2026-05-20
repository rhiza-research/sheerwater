"""A decorator for event definitions."""
from functools import wraps
import numpy as np
import xarray as xr
from sheerwater.utils import roll_and_agg, groupby_time

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

            try:
                ds = fn(ds, *args, **kwargs)
            except TypeError as e:
                raise ValueError(f"Event {name} requires missing event_kwargs key. \n{e}") from e

            # Add an attribute to the dataset to indicate the event name
            ds = ds.assign_attrs({'event': name})
            return ds

        key = fn.__name__.lower()
        if callable(duration):
            wrapper.duration = wrap_duration(duration, key)
        else:
            wrapper.duration = duration
        wrapper.default_variable = default_variable
        wrapper.filter = filter
        EVENT_REGISTRY[key] = wrapper
        return wrapper

    return decorator


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=False)
def digitized(ds, agg_days, bins):
    """An event to digitize a dataset into bins."""
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')

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
def above_threshold(ds, agg_days, threshold):
    """An event to calculate the above threshold of a dataset."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ds = digitized(ds, agg_days=agg_days, bins=bins)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)
    ds = ds.astype(float) - 1.0
    return ds


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=False)
def accumulated_rain(ds, agg_days):
    """An event to calculate the accumulated rain over a sliding, right-aligned window."""
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", align='right', agg_fn='sum')
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


@event(default_variable="precip", duration=120, filter=False)
def seasonal_accumulation(ds, time_grouping='year', by_percent=False):
    """A function to calculate the seasonal accumulation of a dataset."""
    # Add the grouping coordinates but perform no aggregation
    ds = groupby_time(ds, time_grouping, agg_fn=None)
    nanmask = ds.isnull()

    # Set all times to zero where the group in the null mask (i.e., season was None)
    is_null_group = ds['group'].astype(str).str.contains('None')
    ds = ds.where(~is_null_group, np.nan)

    def seasonal_accumulation(x):
        cumsum = x.cumsum(dim="time")
        # There is a bug in xarray cumsum that causes the time coordinate to be lost
        # https://github.com/pydata/xarray/issues/6528
        cumsum = cumsum.assign_coords(time=x['time'])
        if by_percent:
            cumsum = cumsum / cumsum.max(dim="time")
        return cumsum

    # Ensure that the timedimension is sorted
    ds = ds.sortby("time")
    ret = ds.groupby("group").map(seasonal_accumulation)

    # Restore the null pattern and attributes, which are lost during the grouping
    ret = ret.where(~nanmask, other=np.nan)
    ret = ret.assign_attrs(ds.attrs)
    return ret


@event(default_variable="precip", duration=120, filter=True)
def start_of_season_by_accumulation(ds, time_grouping='year', accumulation_threshold=200.0, by_percent=False):
    """A function to calculate the start of season by accumulation of a dataset."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season by accumulation event requires a 'precip' variable.")

    ds = seasonal_accumulation(ds, time_grouping=time_grouping, by_percent=by_percent)
    null_mask = ds.isnull()
    ds_suitable = (ds >= accumulation_threshold)
    ds_suitable = ds_suitable.where(~null_mask, np.nan)

    attrs = ds.attrs.copy()
    return ds_suitable.assign_attrs(attrs)


@event(
    default_variable="precip",
    duration=lambda kwargs: np.sum(kwargs["agg_days"]) if 'agg_days' in kwargs else 30,
    filter=True
)
def start_of_season_by_spells(ds, onset_definition='chc',
                              spells=['wet', 'wet'], agg_days=[10, 20],
                              thresholds=[25.0, 20.0], agg_type=['mean', 'mean'], counts=[np.nan, np.nan],
                              start_of_season_index=0):
    """A function to calculate the planting suitability of a dataset."""
    if onset_definition == 'chc':
        spells = ['wet', 'not_dry']
        agg_days = [10, 20]
        thresholds = [25.0, 20.0]
        agg_type = ['mean', 'mean']
        counts = [np.nan, np.nan]
        start_of_season_index = 0
    elif onset_definition == 'icpac':
        spells = ['wet', 'not_dry']
        agg_days = [10, 20]
        thresholds = [25.0, 20.0]
        agg_type = ['mean', 'mean']
        counts = [np.nan, np.nan]
        start_of_season_index = 0
    elif onset_definition == 'moron-and-robertson':
        spells = ['wet', 'not_dry']
        agg_days = [5, 10]
        thresholds = [38.0, 5.0]
        agg_type = ['mean', 'mean']
        counts = [np.nan, np.nan]
        start_of_season_index = 0
    elif onset_definition == 'wet-not_dry-count':
        spells = ['wet', 'not_dry']
        agg_days = [10, 20]
        thresholds = [5.0, 5.0]
        agg_type = ['count', 'count']
        counts = [3, 2]
        start_of_season_index = 0
    elif onset_definition == 'dry-wet-not_dry-agg':
        spells = ['dry', 'wet', 'not_dry']
        agg_days = [20, 10, 20]
        thresholds = [20.0, 25.0, 20.0]
        agg_type = ['mean', 'mean', 'mean']
        counts = [np.nan, np.nan, np.nan]
        start_of_season_index = 1
    elif onset_definition is None:
        pass
    else:
        raise ValueError(f"Invalid event name: {onset_definition}")

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

    # We want to declare start of season around the trigger index event, and need to align dry spells before it
    # and wet spells after it with the trigger index event.
    shift_indices = [0]*len(spells)
    # Compute the shift indicies for each spell. We want everything to align around the trigger index
    event_indicies = list(zip(range(len(spells)), spells, agg_days))
    # Shift the events before the trigger index to the right (positive)
    shift_days = 0
    for index, event, agg in event_indicies[0:start_of_season_index][::-1]:
        shift_days += agg
        shift_indices[index] = shift_days
    # Shift the events after the trigger index to the left (negative)
    shift_days = -agg_days[start_of_season_index]
    for index, event, agg in event_indicies[start_of_season_index+1:]:
        shift_indices[index] = shift_days
        shift_days -= agg

    # Get the spell timeseries
    spell_timeseries = []
    for i, event in enumerate(spells):
        spell_event_threshold = thresholds[i]
        spell_agg_days = agg_days[i]
        if agg_type[i] == 'mean':
            spell = above_threshold(ds, agg_days=spell_agg_days, threshold=spell_event_threshold / spell_agg_days)
        elif agg_type[i] == 'sum':
            spell = above_threshold(ds, agg_days=spell_agg_days, threshold=spell_event_threshold)
        elif agg_type[i] == 'count':
            spell = has_days_above_threshold(ds, agg_days=spell_agg_days,
                                             threshold=spell_event_threshold, above_days=counts[i])

        if event == 'dry':
            # Looking for not above threshhold, so negate the event
            spell = 1.0 - spell

        # Shift the spell to be aligned with the trigger index
        if i != start_of_season_index:
            spell = spell.shift(time=shift_indices[i])
        spell_timeseries.append(spell)

    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    ret = xr.ones_like(ds['precip'])
    for spell in spell_timeseries:
        ret = ret * spell

    # Invalid at start
    invalid_at_start = int(np.sum(shift_indices[0:start_of_season_index]))
    invalid_at_end = int(np.sum(np.abs(shift_indices[start_of_season_index+1:])))
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
def start_of_season_by_accumulation_with_leaky_bucket(ds, time_grouping='year', accumulation_threshold=40.0,
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
