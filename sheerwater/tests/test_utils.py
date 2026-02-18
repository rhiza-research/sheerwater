"""Test the utility functions in the utils module."""
import numpy as np
import xarray as xr
import pandas as pd
import pytest

from sheerwater.utils import base180_to_base360, base360_to_base180, get_grid
from sheerwater.utils.data_utils import regrid


def test_get_grid():
    """Test the get_grid function."""
    grids = ["global1_5", "global0_25", "global0_05"]
    for grid in grids:
        lons, lats, size, _ = get_grid(grid)
        diffs_lon = np.diff(lons)
        diffs_lat = np.diff(lats)
        # Use allclose (default tol 1e-8) instead of exact equality because
        # np.arange accumulates floating point error over many steps (e.g. 7200 for global0_05)
        assert np.allclose(diffs_lon, size)
        assert np.allclose(diffs_lat, size)


def test_no_unknown_grid():
    """Test that we can not regrid to an unknown grid."""
    ds = xr.Dataset(
        {"precip": (["time", "lat", "lon"], np.random.rand(10, 10, 10))},
        coords={
            "time": pd.date_range("2000-01-01", periods=10),
            "lat": np.linspace(-90, 90, 10),
            "lon": np.linspace(-180, 180, 10)
        }
    )
    with pytest.raises(NotImplementedError):
        regrid(ds, "nonexistent_grid")


def test_lon_convert():
    """Test the get_grid function."""
    # On the boundary of the wrap point in the 360 base
    hard_wrap_180 = np.arange(-10, 10, 1.0)
    # On the boundary of the wrap point in the 180 base
    hard_wrap_360 = np.arange(170, 190, 1.0)

    # Convert bases
    out_360 = base180_to_base360(hard_wrap_180)
    out_180 = base360_to_base180(hard_wrap_360)

    # Check that the output contains a discontinuity
    assert (sorted(out_360) != out_360).all()
    assert (sorted(out_180) != out_180).all()

    # Convert back
    rev_180 = base360_to_base180(out_360)
    rev_360 = base180_to_base360(out_180)
    assert (rev_180 == hard_wrap_180).all()
    assert (rev_360 == hard_wrap_360).all()

    # Convert a single point
    assert base180_to_base360(-179.0) == 181.0
    assert base360_to_base180(0.0) == 0.0
    assert base360_to_base180(359.0) == -1.0
