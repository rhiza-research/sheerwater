"""A decorator for event definitions."""
from functools import wraps
import numpy as np
import xarray as xr
from sheerwater.utils import roll_and_agg

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


def event(default_variable=None, duration=0):
    """Stub decorator for event definitions. Extend with registration or wrapping as needed.

    Args:
       default_variable: The default variable for the event.
       duration: The duration of the event. Can be a callable that takes in event kwargs or an integer.
            For exmaple, `11` and `lambda kwargs: kwargs['agg_days'] + 1` are both valid.
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
        EVENT_REGISTRY[key] = wrapper
        return wrapper

    return decorator


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"])
def above_threshold(ds, agg_days, threshold):
    """An event to calculate the above threshold of a dataset."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ds = digitized(ds, agg_days=agg_days, bins=bins)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)
    ds = ds.astype(float) - 1.0
    return ds


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"])
def days_above_threshold(ds, agg_days, threshold, above_days):
    """An event to calculate the above threshold of a dataset."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ret = digitized(ds, agg_days=None, bins=bins)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)
    ret = ret.astype(float) - 1.0
    ret = roll_and_agg(ret, agg=agg_days, agg_col="time", agg_fn='sum')
    null_mask = ret.isnull()
    ret = ret >= above_days

    plot = False
    if plot:
        import matplotlib.pyplot as plt
        lat = 1.75
        lon = 40.0
        year = 2023
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 5), sharex=True)

        orig = ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        ret_plot = ret.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip

        # Plot original precip on left axis
        p1 = ax1.plot(orig.time, orig.values, color='gray', alpha=0.45, label='Original Precip')
        ax1.set_ylabel('Precipitation', color='gray')
        ax1.tick_params(axis='y', labelcolor='gray')

        # Create a second y-axis
        ax2 = ax1.twinx()
        # Plot ret on right axis
        p2 = ax2.plot(ret_plot.time, ret_plot.values, color='b', label='Days Above Threshold', linewidth=2)
        ax2.set_ylabel('Days Above Threshold', color='b')
        ax2.tick_params(axis='y', labelcolor='b')

        # Combine all plotted lines for legend
        lines = p1 + p2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        plt.show()
    # Restore NaN values
    ret = ret.where(~null_mask, np.nan)
    return ret

@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"])
def count_days_above_threshold(ds, agg_days, threshold):
    """An event to calculate the above threshold of a dataset."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ret = digitized(ds, agg_days=None, bins=bins)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)
    ret = ret.astype(float) - 1.0
    ret = roll_and_agg(ret, agg=agg_days, agg_col="time", agg_fn='sum')
    null_mask = ret.isnull()

    plot = False
    if plot:
        import matplotlib.pyplot as plt
        lat = 1.75
        lon = 40.0
        year = 2023
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 5), sharex=True)

        orig = ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        ret_plot = ret.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip

        # Plot original precip on left axis
        p1 = ax1.plot(orig.time, orig.values, color='gray', alpha=0.45, label='Original Precip')
        ax1.set_ylabel('Precipitation', color='gray')
        ax1.tick_params(axis='y', labelcolor='gray')

        # Create a second y-axis
        ax2 = ax1.twinx()
        # Plot ret on right axis
        p2 = ax2.plot(ret_plot.time, ret_plot.values, color='b', label='Days Above Threshold', linewidth=2)
        ax2.set_ylabel('Days Above Threshold', color='b')
        ax2.tick_params(axis='y', labelcolor='b')

        # Combine all plotted lines for legend
        lines = p1 + p2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        plt.show()
    # Restore NaN values
    ret = ret.where(~null_mask, np.nan)
    return ret


@event(default_variable="precip", duration=lambda kwargs: kwargs["smoothing"]+kwargs["continuous_days"])
def continuous_days_above_threshold(ds, threshold, smoothing, continuous_days):
    """An event to calculate the above threshold of a dataset."""
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

    plot = False
    if plot:
        import matplotlib.pyplot as plt
        # lat = 1.75
        # lon = 40.0
        lat = -1.5
        lon = 38.0
        year = 2023
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 5), sharex=True)

        # orig = ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        # ret_plot = ret.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        orig = ds.sel(lat=lat, lon=lon).precip
        ret_plot = ret.sel(lat=lat, lon=lon).precip

        # Plot original precip on left axis
        p1 = ax1.plot(orig.time, orig.values, color='gray', alpha=0.45, label='Original Precip')
        ax1.set_ylabel('Precipitation', color='gray')
        ax1.tick_params(axis='y', labelcolor='gray')

        # Create a second y-axis
        ax2 = ax1.twinx()
        # Plot ret on right axis
        p2 = ax2.plot(ret_plot.time, ret_plot.values, color='b', label='Days Above Threshold', linewidth=2)
        ax2.set_ylabel('Days Above Threshold', color='b')
        ax2.tick_params(axis='y', labelcolor='b')

        # Combine all plotted lines for legend
        lines = p1 + p2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        plt.show()
    # Restore NaN values
    ret = ret.where(~null_mask, np.nan)
    return ret


@event(default_variable="precip", duration=lambda kwargs: kwargs["agg_days"])
def digitized(ds, agg_days, bins):
    """An event to digitize a dataset into bins."""  # Save and restore the null pattern, which is removed by the boolean operations
    if agg_days is not None:
        ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')

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


@event(
    default_variable="precip",
    duration=lambda kwargs: kwargs["wet_spell_agg_days"] + kwargs["dry_spell_agg_days"],
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
    return (wet_spell * dry_spell).assign_attrs(attrs)


@event(
    default_variable="precip",
    duration=lambda kwargs: kwargs["wet_spell_agg_days"] + kwargs["not_dry_spell_agg_days"],
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


@event(default_variable="precip", duration=30)
def start_of_season_by_accumulation(ds, accumulation_threshold=10.0):
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
    # lat = 1.75
    # lon = 40.0
    # lat = -1.5
    # lon = 37.0

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
                             kwargs["dry_spell_agg_days"] + kwargs["leading_dry_spell_agg_days"])
)
def start_of_season(ds,
                    leading_dry_spell_agg_days=20, leading_dry_spell_threshold=1.0,
                    wet_spell_agg_days=3, wet_spell_threshold=7.0,
                    dry_spell_agg_days=7, dry_spell_threshold=1.0):
    """A function to calculate the start of season of a dataset."""
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
    duration=lambda kwargs: (kwargs["wet_spell_agg_days"] + kwargs["dry_spell_agg_days"])
)
def nimbus_start_of_season(ds,
                           dry_spell_agg_days=10, dry_spell_threshold=4.0, dry_spell_count=1,
                           wet_spell_agg_days=10, wet_spell_threshold=4.0, wet_spell_count=3):
    """A function to calculate the start of season of a dataset."""
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
    plot = False
    if plot:
        import matplotlib.pyplot as plt
        # # # lat = -2.75
        # # # lon = 39.75
        # # lat = 1.25
        # # lat = 2.25
        # # lon = 37.25
        # # lat = 0.0
        # # lon = 34.25
        lat = 1.75
        lon = 40.0
        year = 2023
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 5), sharex=True)

        wet = wet_spell.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        dry = dry_spell.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        lagged_dry = lagged_dry_spell.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        orig = ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip

        # --- Wet and Dry Spells on One Subplot with Twin Y-Axis ---
        ax2 = ax1.twinx()

        # Plot original precip on left axis
        p1 = ax1.plot(orig.time, orig.values, color='gray', alpha=0.45, label='Original Precip')
        ax1.set_ylabel('Precipitation', color='gray')
        ax1.tick_params(axis='y', labelcolor='gray')
        precip_min = min(orig.values.min(), 0)
        precip_max = max(orig.values.max(), 1.5)
        ax1.set_ylim(precip_min, precip_max)

        # Plot wet spell (binary) on right axis
        p2 = ax2.plot(wet.time, wet.values, color='b', label='Wet Spell', linewidth=2)
        # Plot dry spell (binary, lagged) on right axis as well
        p3 = ax2.plot(lagged_dry.time, 0.5*lagged_dry.values, color='r', label='Lagged Dry Spell', linewidth=2)
        p4 = ax2.plot(lagged_dry.time, 0.1*dry.values, color='g', label='Dry Spell', linewidth=2)
        # Optionally plot dry (not lagged) for debugging
        # p4 = ax2.plot(dry.time, dry.values, color='g', label='Dry Spell', linewidth=2)

        ax2.set_ylabel('Spell Indicator', color='k')
        ax2.tick_params(axis='y', labelcolor='k')
        ax2.set_ylim(-0.2, 1.2)

        ax1.set_title('Wet & Dry Spells (with Original Precip)')

        # Combine all plotted lines for legend
        lines = p1 + p2 + p3 + p4
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        plt.show()

    return (lagged_dry_spell * wet_spell).assign_attrs(attrs)


@event(
    default_variable="precip",
    duration=lambda kwargs: (kwargs["wet_spell_agg_days"] + kwargs["dry_spell_agg_days"])
)
def nimbus_start_of_season_not_dry(ds,
                                   threshold=1.0,
                                   dry_spell_agg_days=10,
                                   dry_spell_count=1,
                                   wet_spell_agg_days=10,
                                   wet_spell_count=3):
    """A function to calculate the start of season of a dataset."""
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

    plot = False
    if plot:
        print(
            f"Plotting nimbus_start_of_season_not_dry with wet spell count {wet_spell_count} and dry spell count {dry_spell_count}, wet spell agg days {wet_spell_agg_days} and dry spell agg days {dry_spell_agg_days}")
        import matplotlib.pyplot as plt
        # # lat = -2.75
        # # lon = 39.75
        # lat = 1.25
        # lat = 2.25
        # lon = 37.25
        # lat = 0.0
        # lon = 34.25
        # lat = 1.75
        # lon = 40.0
        lat = 12.5
        lon = -8.0
        year = 2020
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 5), sharex=True)

        wet = wet_spell.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        dry = dry_spell.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        lagged_dry = lagged_dry_spell.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        orig = ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip

        # --- Wet and Dry Spells on One Subplot with Twin Y-Axis ---
        ax2 = ax1.twinx()

        # Plot original precip on left axis
        p1 = ax1.plot(orig.time, orig.values, color='gray', alpha=0.45, label='Original Precip')
        ax1.set_ylabel('Precipitation', color='gray')
        ax1.tick_params(axis='y', labelcolor='gray')
        import numpy as np
        precip_min = min(np.nanmin(orig.values), 0)
        precip_max = max(np.nanmax(orig.values), 1.5)
        ax1.set_ylim(precip_min, precip_max)

        # Plot wet spell (binary) on right axis
        p2 = ax2.plot(wet.time, wet.values, color='b', label='Wet Spell', linewidth=2)
        # Plot dry spell (binary, lagged) on right axis as well
        p3 = ax2.plot(lagged_dry.time, 0.5*lagged_dry.values, color='r', label='Lagged Dry Spell', linewidth=2)
        p4 = ax2.plot(lagged_dry.time, 0.1*dry.values, color='g', label='Dry Spell', linewidth=2)
        # Optionally plot dry (not lagged) for debugging
        # p4 = ax2.plot(dry.time, dry.values, color='g', label='Dry Spell', linewidth=2)

        ax2.set_ylabel('Spell Indicator', color='k')
        ax2.tick_params(axis='y', labelcolor='k')
        ax2.set_ylim(-0.2, 1.2)

        ax1.set_title('Wet & Dry Spells (with Original Precip)')

        # Combine all plotted lines for legend
        lines = p1 + p2 + p3 + p4
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        plt.show()

    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    return (lagged_dry_spell * wet_spell).assign_attrs(attrs)

@event(
    default_variable="precip",
    duration=lambda kwargs: (kwargs["wet_spell_agg_days"] + kwargs["dry_spell_agg_days"])
)
def wet_day_regime(ds, wet_threshold=4.0, dry_threshold=1.0, agg_days=30, fraction = 0.01):
    """A function to calculate the regime change of a dataset."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Start of season event requires a 'precip' variable.")

    wet_days = above_threshold(ds, agg_days=1, threshold=wet_threshold)
    not_dry_days = above_threshold(ds, agg_days=1, threshold=dry_threshold)
    dry_days = 1.0 - not_dry_days

    wet_regime = roll_and_agg(wet_days, agg=agg_days, agg_col="time", agg_fn='mean')
    dry_regime = roll_and_agg(dry_days, agg=agg_days, agg_col="time", agg_fn='mean')

    # Detect a change in regime step by step
    wet_change = wet_regime.diff(dim="time")
    dry_change = dry_regime.diff(dim="time")

    # Find the indices of the changes









    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    plot = False
    if plot:
        import matplotlib.pyplot as plt
        # # # lat = -2.75
        # # # lon = 39.75
        # # lat = 1.25
        # # lat = 2.25
        # # lon = 37.25
        # # lat = 0.0
        # # lon = 34.25
        lat = 1.75
        lon = 40.0
        year = 2023
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 5), sharex=True)

        wet = wet_spell.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        dry = dry_spell.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        lagged_dry = lagged_dry_spell.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip
        orig = ds.sel(time=slice(f"{year}-01-01", f"{year}-12-31")).sel(lat=lat, lon=lon).precip

        # --- Wet and Dry Spells on One Subplot with Twin Y-Axis ---
        ax2 = ax1.twinx()

        # Plot original precip on left axis
        p1 = ax1.plot(orig.time, orig.values, color='gray', alpha=0.45, label='Original Precip')
        ax1.set_ylabel('Precipitation', color='gray')
        ax1.tick_params(axis='y', labelcolor='gray')
        precip_min = min(orig.values.min(), 0)
        precip_max = max(orig.values.max(), 1.5)
        ax1.set_ylim(precip_min, precip_max)

        # Plot wet spell (binary) on right axis
        p2 = ax2.plot(wet.time, wet.values, color='b', label='Wet Spell', linewidth=2)
        # Plot dry spell (binary, lagged) on right axis as well
        p3 = ax2.plot(lagged_dry.time, 0.5*lagged_dry.values, color='r', label='Lagged Dry Spell', linewidth=2)
        p4 = ax2.plot(lagged_dry.time, 0.1*dry.values, color='g', label='Dry Spell', linewidth=2)
        # Optionally plot dry (not lagged) for debugging
        # p4 = ax2.plot(dry.time, dry.values, color='g', label='Dry Spell', linewidth=2)

        ax2.set_ylabel('Spell Indicator', color='k')
        ax2.tick_params(axis='y', labelcolor='k')
        ax2.set_ylim(-0.2, 1.2)

        ax1.set_title('Wet & Dry Spells (with Original Precip)')

        # Combine all plotted lines for legend
        lines = p1 + p2 + p3 + p4
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        plt.show()

    return (lagged_dry_spell * wet_spell).assign_attrs(attrs)


def get_event_fn(name):
    """Get an event function from the registry."""
    if name is None:
        return None
    if name not in EVENT_REGISTRY:
        raise ValueError(f"Event {name!r} not found.")
    return EVENT_REGISTRY[name]
