"""This module contains pytest fixtures and configuration."""
import re

import pytest


def pytest_addoption(parser):
    """Add --metric-test-numbers for test_metric_correctness (run by case number 1-26)."""
    parser.addoption(
        "--metric-test-numbers",
        action="store",
        default=None,
        help="Run only these metric correctness case numbers (e.g. 5, 3,5,10, or 3-7). Default: all.",
    )


def _parse_metric_test_numbers(raw):
    """Parse a comma/range string into set of 1-based indices. None or empty -> None (run all)."""
    if not raw or not str(raw).strip():
        return None
    raw = str(raw).strip()
    out = set()
    for part in re.split(r"[\s,]+", raw):
        part = part.strip()
        if not part:
            continue
        if "-" in part and not part.startswith("-"):
            a, b = part.split("-", 1)
            try:
                lo, hi = int(a.strip()), int(b.strip())
                out.update(range(lo, hi + 1))
            except ValueError:
                pass
            continue
        try:
            out.add(int(part))
        except ValueError:
            pass
    return out if out else None


@pytest.fixture
def metric_test_numbers(request):
    """Parsed --metric-test-numbers (set of 1-based indices or None for all)."""
    raw = request.config.getoption("--metric-test-numbers", default=None)
    return _parse_metric_test_numbers(raw)


@pytest.fixture(scope="session")
def remote_dask_cluster():
    """Start a remote Dask cluster for the test session (used by metric correctness and performance tests)."""
    from sheerwater.utils import start_remote

    start_remote(remote_config="xlarge_cluster")
    yield


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
