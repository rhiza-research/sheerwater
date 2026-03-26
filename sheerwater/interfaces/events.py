"""A decorator for event definitions."""
import numpy as np
from abc import ABC, abstractmethod

from sheerwater.utils import roll_and_agg

EVENT_REGISTRY = {}


class Event(ABC):
    """Abstract base class for events."""
    def __init_subclass__(cls, **kwargs):
        """Automatically register derived Events classes with the event registry."""
        super().__init_subclass__(**kwargs)
        # Register this event class with the registry
        cls.name = cls.__name__.lower()
        EVENT_REGISTRY[cls.name] = cls

    def __call__(self, ds):
        """Apply the event to the dataset."""
        if self.valid_variables is not None and self.valid_variables != []:
            for v in ds.data_vars:
                if v not in self.valid_variables:
                    raise ValueError(f"Event {self.name} is not valid for variable {v}.")
        ds = self.apply(ds)
        # Add an attribute to the dataset to indicate the event name
        ds = ds.assign_attrs({'event': self.name})
        if 'member' in ds.dims:
            ds = ds.mean(dim='member')
        return ds

    @property
    @abstractmethod
    def duration(self) -> int:
        """The duration of the event."""
        pass

    @property
    @abstractmethod
    def valid_variables(self) -> list[str]:
        """What variables is the metric valid for?"""
        pass

    @property
    @abstractmethod
    def default_variable(self) -> str:
        """The default variable for the event."""
        pass


class above_threshold(Event):
    """An event to calculate the above threshold of a dataset."""
    valid_variables = None  # valid for any variable that can be averaged
    default_variable = "precip"

    def __init__(self, agg_days=10, threshold=10.0):
        """Initialize the event."""
        self.agg_days = agg_days
        self.threshold = threshold

    def apply(self, ds):
        """A function to calculate the above threshold of a dataset."""
        # Check agg days and roll if necessary
        if 'agg_days' in ds.attrs and ds.attrs['agg_days'] != 1:
            raise ValueError(f"Event {self.name} requires agg_days to be 1.")
        ds = roll_and_agg(ds, agg=self.agg_days, agg_col="time", agg_fn='mean')
        # Save and restore the null pattern, which is removed by the boolean operations
        null_mask = ds.isnull()
        ds = (ds >= self.threshold).astype(np.float32)
        ds = ds.where(~null_mask, np.nan)
        return ds

    @property
    def duration(self) -> int:
        """The duration of the event."""
        return self.agg_days


class planting_suitability(Event):
    """An event to calculate the above threshold of a dataset."""
    valid_variables = ["precip"]  # only valid for precipitation
    default_variable = "precip"

    def __init__(self,
                 wet_spell_agg_days=10, dry_spell_agg_days=20,
                 wet_spell_threshold=25.0, dry_spell_threshold=20.0):
        """Initialize the event."""
        self.wet_spell_agg_days = wet_spell_agg_days
        self.dry_spell_agg_days = dry_spell_agg_days
        self.wet_spell_threshold = wet_spell_threshold
        self.dry_spell_threshold = dry_spell_threshold

    def apply(self, ds):
        """A function to calculate the above threshold of a dataset."""
        wet_spell = above_threshold(ds, agg_days=self.wet_spell_agg_days,
                                    threshold=self.wet_spell_threshold / self.wet_spell_agg_days)
        dry_spell = above_threshold(ds, agg_days=self.dry_spell_agg_days,
                                    threshold=self.dry_spell_threshold / self.dry_spell_agg_days)
        # Shift to get wet spell followed by dry spell
        dry_spell = dry_spell.shift(time=self.wet_spell_agg_days)
        # Chop off the last  days for wet spell, which won't have a matching dry spell
        wet_spell = wet_spell.isel(time=slice(None, -self.wet_spell_agg_days))
        # Floatwise "and-ing" of the two spells together to get the planting suitability
        return (wet_spell * dry_spell)

    @property
    def duration(self) -> int:
        """The duration of the event."""
        return self.wet_spell_agg_days + self.dry_spell_agg_days


def get_event_fn(name):
    """Get an event function from the registry."""
    if name not in EVENT_REGISTRY:
        raise ValueError(f"Event {name!r} not found.")
    return EVENT_REGISTRY[name]
