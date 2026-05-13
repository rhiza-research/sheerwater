"""A decorator for processors definitions."""
from functools import wraps
from sheerwater.utils import regrid as regrid_util

PROCESSOR_REGISTRY = {}

def processor():
    """Stub decorator for processor definitions."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            name = fn.__name__.lower()

            try:
                ds = fn(*args, **kwargs)
            except TypeError as e:
                raise ValueError(f"Processor {name} requires missing processor_kwargs key. \n{e}") from e

            # Add an attribute to the dataset to indicate the event name
            ds = ds.assign_attrs({'processor': name})
            return ds

        key = fn.__name__.lower()
        PROCESSOR_REGISTRY[key] = wrapper
        return wrapper

    return decorator


def get_processor_fn(name):
    """Get a processor function from the registry."""
    if name is None:
        return None
    if name not in PROCESSOR_REGISTRY:
        raise ValueError(f"Processor {name!r} not found.")
    return PROCESSOR_REGISTRY[name]


@processor()
def regrid(ds, target_grid, method='conservative', **kwargs):
    return regrid_util(ds, target_grid, method=method)
