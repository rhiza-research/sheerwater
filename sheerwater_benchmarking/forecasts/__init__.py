"""Forecasting models for the Sheerwater benchmarking project."""
from .salient import salient
from .ecmwf_er import ecmwf_ifs_er, ecmwf_ifs_er_debiased
from .fuxi import fuxi
from .graphcast import graphcast
from .gencast import gencast

# Use __all__ to define what is part of the public API.
__all__ = ["salient", "ecmwf_ifs_er_debiased", "ecmwf_ifs_er", "fuxi", "graphcast", "gencast"]

# Define which are proper forecasts to be benchmarked
__forecasts__ = ["salient", "ecmwf_ifs_er_debiased", "ecmwf_ifs_er", "fuxi", "graphcast", "gencast"]
