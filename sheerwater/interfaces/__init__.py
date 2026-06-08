"""Standard interfaces for Sheerwater data and forecasts."""
from .datasets import (forecast, data, DATA_REGISTRY, FORECAST_REGISTRY,
                       list_forecasts, get_forecast, list_data, get_data,
                       add_spatial_attrs, check_spatial_attr,
                       get_forecast_or_data)
from .events import EVENT_REGISTRY, get_event_fn
from .processors import PROCESSOR_REGISTRY, get_processor_fn
from .spatial import spatial

__all__ = [
    "forecast",
    "data",
    "spatial",
    "DATA_REGISTRY",
    "FORECAST_REGISTRY",
    "EVENT_REGISTRY",
    "PROCESSOR_REGISTRY",
    "get_event_fn",
    "get_processor_fn",
    "list_forecasts",
    "get_forecast",
    "list_data",
    "get_data",
    "add_spatial_attrs",
    "check_spatial_attr",
    "get_forecast_or_data",
]
