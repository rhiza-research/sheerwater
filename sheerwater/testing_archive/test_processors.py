"""Test the processors."""

import xarray as xr


from sheerwater.interfaces import spatial
from nuthatch import cache


def test_spatial():
    """Test the spatial decorator."""
    spatial_data(grid="global0_25", region="kenya", cache_mode="local", recompute="_all")


@spatial()
@cache(cache_args=["grid"])
def spatial_data(grid="global0_25", region="kenya"):  # noqa: ARG001
    """Test the spatial decorator."""
    import numpy as np

    lats = np.arange(-90, 91, 1.5)
    lons = np.arange(0, 360, 1.5)
    data = np.zeros((lats.shape[0], lons.shape[0]))
    return xr.Dataset(
        {"zeros": (["lat", "lon"], data)},
        coords={"lat": lats, "lon": lons},
    )


if __name__ == "__main__":
    test_spatial()
