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
    if agg_days is not None:
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
    """An event to calculate the accumulated rain over a sliding agg days window."""
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='sum')
    return ds


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=True)
def days_above_threshold(ds, agg_days, threshold, above_days):
    """An event to calculate whether a forecast spends sufficient time above a threshold."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ret = digitized(ds, agg_days=None, bins=bins)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)
    ret = ret.astype(float) - 1.0
    ret = roll_and_agg(ret, agg=agg_days, agg_col="time", agg_fn='sum')
    null_mask = ret.isnull()
    ret = (ret >= above_days)
    # Restore NaN values
    ret = ret.where(~null_mask, np.nan)
    return ret


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"], filter=False)
def count_days_above_threshold(ds, agg_days, threshold):
    """An event to calculate the number of days above a threshold."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ret = digitized(ds, agg_days=None, bins=bins)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)
    ret = ret.astype(float) - 1.0
    ret = roll_and_agg(ret, agg=agg_days, agg_col="time", agg_fn='sum')
    null_mask = ret.isnull()
    # Restore NaN values
    ret = ret.where(~null_mask, np.nan)
    return ret


@event(default_variable="precip", duration=lambda kwargs: kwargs["smoothing"]+kwargs["continuous_days"], filter=True)
def continuous_days_above_threshold(ds, threshold, smoothing, continuous_days):
    """An event to calculate whether a forecast spends consecutive days above a threshold."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ret = digitized(ds, agg_days=None, bins=bins)
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


@event(
    default_variable="precip",
    duration=lambda kwargs: kwargs["wet_spell_agg_days"] + kwargs["dry_spell_agg_days"],
    filter=True,
)
def planting_suitability(ds, wet_spell_agg_days=10, dry_spell_agg_days=20,
                         wet_spell_threshold=25.0, dry_spell_threshold=20.0):
    """A function to calculate the planting suitability of a dataset."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Planting suitability event requires a 'precip' variable.")

    wet_spell = above_threshold(ds, agg_days=wet_spell_agg_days, threshold=wet_spell_threshold / wet_spell_agg_days)
    dry_spell = above_threshold(ds, agg_days=dry_spell_agg_days, threshold=dry_spell_threshold / dry_spell_agg_days)

    # Shift to get wet spell followed by not dry spell
    dry_spell = dry_spell.shift(time=-wet_spell_agg_days)
    # Chop off the last NaNs introduced by the shift
    dry_spell = dry_spell.isel(time=slice(None, -wet_spell_agg_days))

    # Chop off the last  days for wet spell, which won't have a matching dry spell
    wet_spell = wet_spell.isel(time=slice(None, -wet_spell_agg_days))

    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    ret = (wet_spell * dry_spell).assign_attrs(attrs)
    return ret


@event(
    default_variable="precip",
    duration=lambda kwargs: kwargs["wet_spell_agg_days"] + kwargs["not_dry_spell_agg_days"],
    filter=True,
)
def planting_suitability_by_count(ds,
                                  wet_spell_agg_days=5, wet_spell_threshold=4.0, wet_spell_count=3,
                                  not_dry_spell_agg_days=10, not_dry_spell_threshold=1.0, not_dry_spell_count=2):
    """A function to calculate the planting suitability based on wet day counts."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Planting suitability event requires a 'precip' variable.")

    wet_spell = days_above_threshold(ds,
                                     agg_days=wet_spell_agg_days,
                                     threshold=wet_spell_threshold,
                                     above_days=wet_spell_count)
    not_dry_spell = days_above_threshold(ds,
                                         agg_days=not_dry_spell_agg_days,
                                         threshold=not_dry_spell_threshold,
                                         above_days=not_dry_spell_count)

    # Shift to get wet spell followed by not dry spell
    not_dry_spell = not_dry_spell.shift(time=-wet_spell_agg_days)

    # Chop off the last  days for wet spell, which won't have a matching not dry spell
    wet_spell = wet_spell.isel(time=slice(None, -wet_spell_agg_days))

    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    return (wet_spell * not_dry_spell).assign_attrs(attrs)


@event(default_variable="precip", duration=30, filter=False)
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


@event(default_variable="precip", duration=30, filter=True)
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


@event(default_variable="precip", duration=30, filter=True)
def start_of_season_by_leaky_bucket(ds, accumulation_threshold=10.0):
    """A function to calculate the start of season by accumulation of a dataset."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season by accumulation event requires a 'precip' variable.")

    null_mask = ds.isnull()
    attrs = ds.attrs.copy()

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
            # Bucket overflows beyond 120.0
            bucket = min(bucket, 120.0)
            result[i] = bucket
        return result

    ds = ds.chunk({'time': -1})  # must
    ds = xr.apply_ufunc(
        leaky_bucket,
        ds,
        input_core_dims=[["time"]],
        output_core_dims=[["time"]],
        kwargs={"leak_rate": 4, "runoff_rate": 20},
        dask="parallelized",
        vectorize=True,
        output_dtypes=[float],
    )

    ds_suitable = ds >= accumulation_threshold
    ds_suitable = ds_suitable.where(~null_mask, np.nan)

    attrs = ds.attrs.copy()
    return ds_suitable.assign_attrs(attrs)


@event(
    default_variable="precip",
    duration=lambda kwargs: (kwargs["wet_spell_agg_days"] +
                             kwargs["dry_spell_agg_days"] + kwargs["leading_dry_spell_agg_days"]),
    filter=True,
)
def start_of_season(ds,
                    leading_dry_spell_agg_days=20, leading_dry_spell_threshold=1.0,
                    wet_spell_agg_days=3, wet_spell_threshold=7.0,
                    dry_spell_agg_days=7, dry_spell_threshold=1.0):
    """Start of season of a dataset with a leading dry spell, a wet spell, and a not dry spell."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season event requires a 'precip' variable.")

    leading_dry_spell = 1.0 - above_threshold(ds, agg_days=leading_dry_spell_agg_days,
                                              threshold=leading_dry_spell_threshold)
    wet_spell = above_threshold(ds, agg_days=wet_spell_agg_days, threshold=wet_spell_threshold)
    dry_spell = above_threshold(ds, agg_days=dry_spell_agg_days, threshold=dry_spell_threshold)

    # Shift to get wet spell followed by dry spell
    wet_spell = wet_spell.shift(time=leading_dry_spell_agg_days)
    dry_spell = dry_spell.shift(time=(wet_spell_agg_days + leading_dry_spell_agg_days))

    # Chop off the last days for wet spell, which won't have a matching dry spell
    # TODO: figure out if this is right
    leading_dry_spell = leading_dry_spell.isel(time=slice(None, -(leading_dry_spell_agg_days + wet_spell_agg_days)))
    wet_spell = wet_spell.isel(time=slice(None, -(leading_dry_spell_agg_days)))

    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    return (leading_dry_spell * wet_spell * dry_spell).assign_attrs(attrs)


@event(
    default_variable="precip",
    duration=lambda kwargs: (kwargs["wet_spell_agg_days"] + kwargs["dry_spell_agg_days"]),
    filter=True,
)
def nimbus_start_of_season(ds,
                           dry_spell_agg_days=10, dry_spell_threshold=4.0, dry_spell_count=1,
                           wet_spell_agg_days=10, wet_spell_threshold=4.0, wet_spell_count=3):
    """State of season with a dry spell, by count, buffered, and followed by a wet spell by count."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season event requires a 'precip' variable.")

    not_dry_spell = days_above_threshold(
        ds,
        agg_days=dry_spell_agg_days,
        threshold=dry_spell_threshold,
        above_days=dry_spell_count)
    dry_spell = 1.0 - not_dry_spell

    wet_spell = days_above_threshold(
        ds,
        agg_days=wet_spell_agg_days,
        threshold=wet_spell_threshold,
        above_days=wet_spell_count)

    # Shift to get wet spell followed by dry spell
    buffer_days = 7
    lagged_dry_spell = dry_spell.shift(time=wet_spell_agg_days)
    # Remove the NaNs that were introduced by the shift
    lagged_dry_spell = lagged_dry_spell.isel(time=slice(wet_spell_agg_days, None))
    lagged_dry_spell = roll_and_agg(lagged_dry_spell, agg=buffer_days, agg_col="time", align='right', agg_fn='max')

    # Chop off the first days for wet spell, which won't have a matching dry spell
    wet_spell = wet_spell.isel(time=slice(wet_spell_agg_days, -(buffer_days-1)))

    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    return (lagged_dry_spell * wet_spell).assign_attrs(attrs)


@event(
    default_variable="precip",
    duration=lambda kwargs: (kwargs["wet_spell_agg_days"] + kwargs["dry_spell_agg_days"]),
    filter=True,
)
def nimbus_start_of_season_not_dry(ds,
                                   threshold=1.0,
                                   dry_spell_agg_days=10,
                                   dry_spell_count=1,
                                   wet_spell_agg_days=10,
                                   wet_spell_count=3):
    """State of season with a dry spell, by count, followed by a not dry spell by count."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season event requires a 'precip' variable.")

    not_dry_spell = days_above_threshold(
        ds,
        agg_days=dry_spell_agg_days,
        threshold=threshold,
        above_days=dry_spell_count)
    dry_spell = 1.0 - not_dry_spell

    wet_spell = days_above_threshold(
        ds,
        agg_days=wet_spell_agg_days,
        threshold=threshold,
        above_days=wet_spell_count)

    # Shift to get dry spell followed by wet spell
    lagged_dry_spell = dry_spell.shift(time=dry_spell_agg_days)
    # Remove the NaNs that were introduced by the shift
    lagged_dry_spell = lagged_dry_spell.isel(time=slice(dry_spell_agg_days, None))

    # Chop off the first days for wet spell, which won't have a matching dry spell
    wet_spell = wet_spell.isel(time=slice(dry_spell_agg_days, None))

    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    return (lagged_dry_spell * wet_spell).assign_attrs(attrs)


def get_event_fn(name):
    """Get an event function from the registry."""
    if name is None:
        return None
    if name not in EVENT_REGISTRY:
        raise ValueError(f"Event {name!r} not found.")
    return EVENT_REGISTRY[name]
