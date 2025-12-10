from .forecast_data_decorator import forecast, data, DATA_REGISTRY, FORECAST_REGISTRY, list_forecasts, get_forecast, list_data, get_data
from .spatial_decorator import spatial

__all__ = ["forecast", "data", "spatial", "DATA_REGISTRY", "FORECAST_REGISTRY",
           "list_forecasts", "get_forecast", "list_data", "get_data"]
