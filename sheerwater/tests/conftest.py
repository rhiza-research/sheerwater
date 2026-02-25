"""This module contains pytest fixtures and configuration."""
import sys

import pytest
from nuthatch.nuthatch import get_cache_mode as _original_get_cache_mode
from nuthatch import clear_memoizer
_nuthatch_mod = sys.modules['nuthatch.nuthatch']

# Workaround: force all nuthatch cache operations to use 'local' mode so that
# data is written to the local filesystem cache (for CI persistence).
#
# Why monkeypatching set_global_cache_variables is not enough:
#   - Top-level @cacheable functions reset global_cache_mode (line 113-117)
#   - But then they use their OWN cache_mode from final_cache_config (line 599),
#     which is None, falling through to 'write' (line 647-648)
#   - global_cache_mode only propagates to NESTED functions (line 129-130)
#
# Why config alone doesn't work:
#   - sheerwater is in site-packages, so nuthatch drops its local section (line 307-327)
#   - A typo ('fileysstem') on config.py line 334 also overwrites any local config
#
# So we patch get_cache_mode to redirect 'write' → 'local', ensuring top-level
# functions write to the local cache.
#
# Proper fixes in nuthatch:
#   1. Fix the typo on config.py line 334 ('fileysstem' → 'filesystem')
#   2. Make set_global_cache_variables only override when explicitly non-None
# Once those land, remove this monkeypatch and use:
#     set_global_cache_variables(cache_mode="local")


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items):
    """Only use the nuthatch local override on tests that don't use remote."""
    for item in items:
        if 'remote_dask_cluster' not in item.fixturenames:
            item.fixturenames.append('use_local_cache')

@pytest.fixture
def use_local_cache(monkeypatch):
    """Fixutre to overwrite nuthatch and force the use of local caching."""
    def _patched_get_cache_mode(cache_mode):
        if cache_mode == 'write':
            cache_mode = 'local'
        return _original_get_cache_mode(cache_mode)

    print("Running the local cache fixture!")
    monkeypatch.setattr(_nuthatch_mod, "get_cache_mode", _patched_get_cache_mode)



# Scope to module so the memoizer is active throughout performance tests
@pytest.fixture(scope='module')
def remote_dask_cluster():
    """Start a remote Dask cluster for the test session (used by metric correctness and performance tests)."""
    from sheerwater.utils import start_remote

    client = start_remote(remote_config="xlarge_cluster")
    yield

    # Close the client so other tests don't have to use it
    # requires clearing the memoizer of remote objects
    clear_memoizer()
    client.close()


@pytest.fixture
def start_iri_ecmwf():
    """The start date for the IRI ECMWF data."""
    return "2015-05-14"


@pytest.fixture
def end_iri_ecmwf():
    """The end date for the IRI ECMWF data."""
    return "2023-06-16"


@pytest.fixture
def start_era5():
    """The start date for the ECMWF ERA5 data."""
    return "1979-01-01"


@pytest.fixture
def end_era5():
    """The end date for the ECMWF ERA5 data."""
    return "2024-10-01"


@pytest.fixture
def start_eval():
    """The start date for the SheerWater Benchmarking eval."""
    return "2016-01-01"


@pytest.fixture
def end_eval():
    """The end date for the SheerWater Benchmarking eval."""
    return "2022-12-31"
