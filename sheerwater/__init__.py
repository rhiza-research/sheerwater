"""Sheerwater Benchmarking package."""

# Top level config for nuthatch
# Must be in a python file to work with coiled
from nuthatch import set_parameter

set_parameter({
    'filesystem': "gs://sheerwater-datalake/caches",
    'driver': "postgresql",
    'host': "postgres.sheerwater.rhizaresearch.org",
    'port': 5432,
    'username': "write",
    'database': "postgres"
}, location='root')
