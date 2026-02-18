"""This module contains pytest fixtures and configuration."""
import os
from pathlib import Path

import numpy as np
import polars as pl
import pytest
import xarray as xr

# Test cache directory - stored in the repo for reproducible tests
TEST_CACHE_DIR = Path(__file__).parent / "test_cache"


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


def get_cache_key(forecast: str, truth: str, metric_name: str, region: str) -> str:
    """Generate the nuthatch cache key for a metric call.

    Cache args are sorted alphabetically, then values joined with underscore.
    """
    cache_arg_values = {
        "agg_days": 7,
        "end_time": "2020-12-31",
        "forecast": forecast,
        "grid": "global1_5",
        "mask": "lsm",
        "metric_name": metric_name,
        "region": region,
        "space_grouping": None,
        "spatial": False,
        "start_time": "2020-01-01",
        "time_grouping": None,
        "truth": truth,
        "variable": "precip",
    }
    sorted_keys = sorted(cache_arg_values.keys())
    flat_values = [str(cache_arg_values[k]) for k in sorted_keys]
    return "metric/" + "_".join(flat_values)


def create_fake_metric_result(metric_name: str, forecast: str) -> xr.Dataset:
    """Create a fake xarray Dataset that looks like a metric result.

    The structure matches what sheerwater.metrics.metric returns.
    """
    lead_times_days = [1, 7, 14, 21, 28]
    lead_times_ns = [d * 86400 * 1e9 for d in lead_times_days]

    np.random.seed(hash(forecast) % 2**32)
    base_value = 2.0 + np.random.random()
    values = base_value + np.random.random(len(lead_times_days)) * 0.5

    ds = xr.Dataset(
        {metric_name.lower(): (["prediction_timedelta"], values)},
        coords={"prediction_timedelta": lead_times_ns},
    )
    return ds


def create_metadata(cache_key: str, base_path: Path) -> None:
    """Create the nuthatch metadata parquet file."""
    metadata_dir = base_path / "nuthatch_metadata.nut" / cache_key
    metadata_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "cache_key": cache_key,
        "namespace": None,
        "version": None,
        "backend": "zarr",
        "state": "confirmed",
        "last_modified": 1700000000000000.0,
        "commit_hash": "test_fixture",
        "user": "test",
        "path": str(base_path / f"{cache_key}.zarr"),
    }
    df = pl.DataFrame(metadata)
    df.write_parquet(metadata_dir / "zarr.parquet")

    (base_path / "nuthatch_metadata.nut" / "exists.nut").touch()


def populate_test_cache() -> None:
    """Populate the test cache with fake data for common test queries."""
    TEST_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    test_configs = [
        ("ecmwf_ifs_er", "chirps_v3", "mae", "Kenya"),
        ("fuxi", "chirps_v3", "mae", "Kenya"),
        ("graphcast", "chirps_v3", "mae", "Kenya"),
        ("ecmwf_ifs_er", "chirps_v3", "rmse", "Kenya"),
        ("fuxi", "chirps_v3", "rmse", "Kenya"),
    ]

    for forecast, truth, metric, region in test_configs:
        cache_key = get_cache_key(forecast, truth, metric, region)
        zarr_path = TEST_CACHE_DIR / f"{cache_key}.zarr"

        if not zarr_path.exists():
            ds = create_fake_metric_result(metric, forecast)
            ds.to_zarr(zarr_path, mode="w", consolidated=True)
            create_metadata(cache_key, TEST_CACHE_DIR)


@pytest.fixture(scope="session", autouse=True)
def configure_nuthatch_for_testing():
    """Configure Nuthatch to use local test cache instead of production GCS.

    This sets environment variables before any Sheerwater imports happen,
    pointing Nuthatch to our local test cache directory.
    """
    os.environ["NUTHATCH_ROOT_FILESYSTEM"] = str(TEST_CACHE_DIR)
    os.environ["NUTHATCH_LOCAL_FILESYSTEM"] = str(TEST_CACHE_DIR)

    populate_test_cache()

    yield
