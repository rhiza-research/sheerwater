"""A decorator for event definitions."""
import numpy as np

from sheerwater.utils import roll_and_agg

EVENTS_REGISTRY = {}


def event(name, variable=None):
    """Register an event. Default `variable` can be overridden when calling the event."""
    def decorator(func):
        def wrapped(ds, *args, **kwargs):
            return func(ds, *args, **kwargs)
        wrapped.variable = variable
        wrapped.__wrapped__ = func
        EVENTS_REGISTRY[name] = wrapped
        return wrapped
    return decorator


@event('above_threshold', variable='precip')
def above_threshold(ds, agg_days=10, threshold=10.0):
    """A function to calculate the above threshold of a dataset."""
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')
    return (ds >= threshold).astype(np.float32)


def get_event_fn(name):
    """Get an event function from the registry."""
    if name not in EVENTS_REGISTRY:
        raise ValueError(f"Event {name!r} not found.")
    return EVENTS_REGISTRY[name]
