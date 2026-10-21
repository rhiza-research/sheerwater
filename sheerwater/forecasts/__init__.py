"""Forecasting models for the Sheerwater benchmarking project."""
from .ecmwf_er import ecmwf_ifs_er, ecmwf_ifs_er_debiased
from .ecmwf_ifs_ens import ecmwf_ifs_ens
from .ecmwf_hres import ecmwf_hres
from .ecmwf_aifs import ecmwf_aifs
from .gfs import gfs, gefs_chc
from .fuxi import fuxi
from .gencast import gencast
from .graphcast import graphcast
from .salient import salient, salient_gem
from .cumulus_ai import cumulus_ai
from .ecmwf_ifs_planette_reforecast import ecmwf_ifs_planette_reforecast

__all__ = ["salient", "ecmwf_ifs_er_debiased", "ecmwf_ifs_er", "fuxi", "graphcast", "gencast",
           "ecmwf_ifs_ens", "ecmwf_hres", "ecmwf_aifs", "gfs", "gefs_chc", "salient_gem", "cumulus_ai",
           "ecmwf_ifs_planette_reforecast"]
