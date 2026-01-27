"""Standard interfaces for Sheerwater data, forecasts, and region layers."""
from .datasets import (forecast, data, region_layer, DATA_REGISTRY, FORECAST_REGISTRY, REGION_LAYER_REGISTRY,
                       list_forecasts, get_forecast, list_data, get_data, list_region_layers, get_region_layer)
from .spatial import spatial

__all__ = [
    "forecast",
    "data",
    "spatial",
    "DATA_REGISTRY",
    "FORECAST_REGISTRY",
    "list_forecasts",
    "get_forecast",
    "list_data",
    "get_data",
    "region_layer",
    "REGION_LAYER_REGISTRY",
    "list_region_layers",
    "get_region_layer",
]
