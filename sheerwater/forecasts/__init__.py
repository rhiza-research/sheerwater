"""Forecasting models for the Sheerwater benchmarking project."""
from .ecmwf_er import ecmwf_ifs_er, ecmwf_ifs_er_debiased
from .forecast_decorator import forecast
from .fuxi import fuxi
from .gencast import gencast
from .graphcast import graphcast
from .salient import salient

# Use __all__ to define what is part of the public API.
__all__ = ["forecast", "salient", "ecmwf_ifs_er_debiased", "ecmwf_ifs_er", "fuxi", "graphcast", "gencast"]
