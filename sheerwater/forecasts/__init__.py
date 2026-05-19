"""Forecasting models for the Sheerwater benchmarking project."""
from .ecmwf_er import ecmwf_ifs_er, ecmwf_ifs_er_debiased
from .ecmwf_ifs_ens import ecmwf_ifs_ens
from .ecmwf_hres import ecmwf_hres
from .fuxi import fuxi
from .gencast import gencast
from .graphcast import graphcast
from .salient import salient

__all__ = ["salient", "ecmwf_ifs_er_debiased", "ecmwf_ifs_er", "fuxi", "graphcast", "gencast", "ecmwf_ifs_ens", "ecmwf_hres"]
