"""A decorator for event definitions."""
from functools import wraps
import numpy as np
import xarray as xr
from sheerwater.utils import roll_and_agg

EVENT_REGISTRY = {}


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

            ds = fn(ds, *args, **kwargs)
            # Add an attribute to the dataset to indicate the event name
            ds = ds.assign_attrs({'event': name})
            return ds

        wrapper.duration = duration
        wrapper.default_variable = default_variable
        key = fn.__name__.lower()
        EVENT_REGISTRY[key] = wrapper
        return wrapper

    return decorator


@event(default_variable="precip", duration=lambda kwargs: kwargs['agg_days'])
def above_threshold(ds, agg_days, threshold):
    """An event to calculate the above threshold of a dataset."""
    # Bins will be in the format [-inf, threshold, inf]
    bins = [-np.inf, threshold, np.inf]
    ds = digitized(ds, agg_days=agg_days, bins=bins)
    # Convert from the outptut of digitized (1,2) to floating (0, 1)
    ds = ds.astype(float) - 1.0
    return ds


@event(default_variable="precip", duration=lambda kwargs: kwargs['agg_days'])
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


@event(default_variable="precip", duration=lambda kwargs: kwargs['wet_spell_agg_days'] + kwargs['dry_spell_agg_days'])
def planting_suitability(ds, wet_spell_agg_days=10, dry_spell_agg_days=20,
                         wet_spell_threshold=25.0, dry_spell_threshold=20.0):
    """A function to calculate the above threshold of a dataset."""
    if 'precip' not in ds.data_vars:
        raise ValueError("Planting suitability event requires a 'precip' variable.")

    wet_spell = above_threshold(ds, agg_days=wet_spell_agg_days, threshold=wet_spell_threshold / wet_spell_agg_days)
    dry_spell = above_threshold(ds, agg_days=dry_spell_agg_days, threshold=dry_spell_threshold / dry_spell_agg_days)

    # Shift to get wet spell followed by dry spell
    dry_spell = dry_spell.shift(time=-wet_spell_agg_days)

    # Chop off the last  days for wet spell, which won't have a matching dry spell
    wet_spell = wet_spell.isel(time=slice(None, -wet_spell_agg_days))

    # Floatwise "and-ing" of the two spells together to get the planting suitability
    # Ensure that attributes pass through
    attrs = ds.attrs.copy()
    return (wet_spell * dry_spell).assign_attrs(attrs)


def get_event_fn(name):
    """Get an event function from the registry."""
    if name is None:
        return None
    if name not in EVENT_REGISTRY:
        raise ValueError(f"Event {name!r} not found.")
    return EVENT_REGISTRY[name]
