"""A decorator for event definitions."""
import numpy as np

from sheerwater.utils import roll_and_agg

EVENTS_REGISTRY = {}


def event(name, variable=None):
    """Register an event. Default `variable` can be overridden when calling the event."""
    def decorator(func):
        def wrapped(ds, *args, **kwargs):
            ds = func(ds, *args, **kwargs)
            # Average over ensemble members to get a single value
            if 'member' in ds.dims:
                ds = ds.mean(dim='member')
            return ds
        wrapped.__wrapped__ = func
        wrapped.variable = variable
        EVENTS_REGISTRY[name] = wrapped
        return wrapped
    return decorator


@event('above_threshold', variable='precip')
def above_threshold(ds, agg_days=10, threshold=10.0):
    """A function to calculate the above threshold of a dataset."""
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')
    # Save and restore the null pattern, which is removed by the boolean operations
    null_mask = ds.isnull()
    ds = (ds >= threshold).astype(np.float32)
    ds = ds.where(~null_mask, np.nan)
    return ds


@event('planting_suitability', variable='precip')
def planting_suitability(ds, wet_spell_agg_days=10, dry_spell_agg_days=20,
                         wet_spell_threshold=25.0, dry_spell_threshold=20.0):
    """A function to calculate the planting suitability of a dataset."""
    if 'precip' not in ds.variables:
        raise ValueError("Dataset must have a 'precip' variable.")
    wet_spell = above_threshold(ds, agg_days=wet_spell_agg_days, threshold=wet_spell_threshold / wet_spell_agg_days)
    not_dry_spell = above_threshold(ds, agg_days=dry_spell_agg_days, threshold=dry_spell_threshold / dry_spell_agg_days)
    # Shift to get wet spell followed by dry spell
    not_dry_spell = not_dry_spell.shift(time=wet_spell_agg_days)
    # Chop off the last  days for wet spell, which won't have a matching dry spell
    wet_spell = wet_spell.isel(time=slice(None, -wet_spell_agg_days))
    # Floatwise "and-ing" of the two spells together to get the planting suitability
    import matplotlib.pyplot as plt
    import pdb; pdb.set_trace()
    return (wet_spell * not_dry_spell)


def get_event_fn(name):
    """Get an event function from the registry."""
    if name not in EVENTS_REGISTRY:
        raise ValueError(f"Event {name!r} not found.")
    return EVENTS_REGISTRY[name]
