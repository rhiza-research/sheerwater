"""Sheerwater Benchmarking package."""

# Top level config for nuthatch
# Must be in a python file to work with coiled
from nuthatch import config_parameter

@config_parameter('filesystem', location='root')
def set_root_for_coiled():
    """Dynamically set cache root to work on coiled."""
    return "gs://sheerwater-datalake/caches"
