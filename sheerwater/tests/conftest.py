"""This module contains pytest fixtures and configuration."""
import pytest


def pytest_addoption(parser):
    """Add command line option for skipping remote tests."""
    parser.addoption(
        "--skip-remote",
        action="store_true",
        default=False,
        help="Skip tests that require the remote Dask cluster",
    )


def pytest_configure(config):
    """Register the 'remote' marker."""
    config.addinivalue_line(
        "markers", "remote: mark test as requiring remote Dask cluster"
    )


def pytest_collection_modifyitems(config, items):
    """Skip remote tests if --skip-remote is passed."""
    if not config.getoption("--skip-remote"):
        return
    skip_remote = pytest.mark.skip(reason="Skipped with --skip-remote option")
    for item in items:
        if "remote" in item.keywords:
            item.add_marker(skip_remote)


@pytest.fixture(scope="session")
def dask_cluster():
    """Session-scoped fixture that starts the remote Dask cluster once."""
    from sheerwater.utils import start_remote
    start_remote(remote_config='large_cluster')
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
