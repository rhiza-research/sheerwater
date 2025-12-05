"""Test the regions and masking functions."""
from sheerwater.regions_and_masks import land_sea_mask
from sheerwater.utils.region_utils import get_region_data
from sheerwater.utils.space_utils import get_grid


def test_masks():
    """Test the land sea mask function."""
    grids = ["global0_25", "global1_5"]

    for grid in grids:
        lsm = land_sea_mask(grid=grid)
        assert len(lsm.lat.values) > 0


def test_get_grid():
    """Test the get grid function."""
    lons, lats, grid_size, _ = get_grid("global0_25")
    assert lons[0] == -180.0
    assert lons[-1] == 180.0 - 0.25
    assert lats[0] == -90.0
    assert lats[-1] == 90.0
    assert grid_size == 0.25
    assert len(lons) == 1440
    assert len(lats) == 721

    lons, lats, grid_size, _ = get_grid("global1_5")
    assert lons[0] == -180.0
    assert lons[-1] == 180.0 - 1.5
    assert lats[0] == -90.0
    assert lats[-1] == 90.0
    assert grid_size == 1.5
    assert len(lons) == 240
    assert len(lats) == 121

    lons, lats, grid_size, _ = get_grid("salient0_25")
    assert lons[0] == -180.0 + 0.125
    assert lons[-1] == 180.0 - 0.125
    assert lats[0] == -90.0 + 0.125
    assert lats[-1] == 90.0 - 0.125
    assert grid_size == 0.25
    assert len(lons) == 1440
    assert len(lats) == 720

    lons, lats, grid_size, _ = get_grid("chirps")
    assert lons[0] == -180.0 + 0.025
    assert lons[-1] == 180.0 - 0.025
    assert lats[0] == -90.0 + 0.025
    assert lats[-1] == 90.0 - 0.025
    assert grid_size == 0.05
    assert len(lons) == 7200
    assert len(lats) == 3600

    lons, lats, grid_size, _ = get_grid("imerg")
    assert lons[0] == -180.0 + 0.05
    assert lons[-1] == 180.0 - 0.05
    assert lats[0] == -90.0 + 0.05
    assert lats[-1] == 90.0 - 0.05
    assert grid_size == 0.1
    assert len(lons) == 3600
    assert len(lats) == 1800


def test_region_labels():
    """Test the region labels function."""
    # Get region data for a single country
    region_data = get_region_data("indonesia")
    assert region_data.iloc[0]['region_name'] == "indonesia"

    region_data = get_region_data("country")
    assert len(region_data) == 242

    # Get for all continents
    region_data = get_region_data("continent")
    assert len(region_data) == 8

    region_data = get_region_data("eastern_africa")
    assert len(region_data) == 1

    region_data = get_region_data("meteorological_zones")
    assert len(region_data) == 3

    region_data = get_region_data("sheerwater_region")
    assert len(region_data) == 3
