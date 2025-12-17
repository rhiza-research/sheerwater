"""Standard interfaces for Sheerwater data and forecasts."""
from .datasets import (forecast, data, DATA_REGISTRY, FORECAST_REGISTRY,  \
                        list_forecasts, get_forecast, list_data, get_data)
from .spatial import spatial

__all__ = ["forecast", "data", "spatial", "DATA_REGISTRY", "FORECAST_REGISTRY",
           "list_forecasts", "get_forecast", "list_data", "get_data"]
