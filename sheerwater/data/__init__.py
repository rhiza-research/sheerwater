"""Data functions for all parts of the data pipeline."""
from .ghcn import ghcn, ghcn_avg
from .tahmo import tahmo, tahmo_avg
from .chirps import chirps, chirps_v3, chirp_v3, chirps_v2, chirp_v2
from .imerg import imerg, imerg_late, imerg_final
from .data_decorator import data

# Use __all__ to define what is part of the public API.
__all__ = [
    "data",
    "ghcn",
    "ghcn_avg",
    "chirps",
    "chirps_v3",
    "chirp_v3",
    "chirps_v2",
    "chirp_v2",
    "imerg",
    "imerg_late",
    "imerg_final",
    "tahmo",
    "tahmo_avg"
]
