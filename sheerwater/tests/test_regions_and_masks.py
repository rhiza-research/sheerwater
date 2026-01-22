"""Test the regions and masking functions."""
from sheerwater.regions_and_masks import land_sea_mask
from sheerwater.utils.region_utils import region_data, get_region_level
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
    assert abs(lons[-1] - (180.0 - 0.025)) < 1e-10
    assert lats[0] == -90.0 + 0.025
    assert abs(lats[-1] - (90.0 - 0.025)) < 1e-10
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
    gdf = region_data("indonesia")
    assert gdf.iloc[0]['region_name'] == "indonesia"

    gdf = region_data("country")
    assert len(gdf) == 242

    # Get for all continents
    gdf = region_data("continent")
    assert len(gdf) == 8

    gdf = region_data("eastern_africa")
    assert len(gdf) == 1

    gdf = region_data("meteorological_zone")
    assert len(gdf) == 3

    gdf = region_data("sheerwater_region")
    assert len(gdf) == 3


def test_admin_regions():
    """Test the admin level regions."""
    # Test getting all admin levels
    for admin_level in [1, 2]:
        level_name = f"admin_level_{admin_level}"
        gdf = region_data(level_name)
        if admin_level == 1:
            assert len(gdf) > 0
        elif admin_level == 2:
            assert len(gdf) == 290
        assert 'region_name' in gdf.columns
        assert 'region_geometry' in gdf.columns

        # Verify we get the correct region level
        region_level, regions = get_region_level(level_name)
        assert region_level == level_name
        assert len(regions) > 0


def test_specific_admin_region():
    """Test getting a specific admin region."""
    # First get all admin level 2 regions to find a valid one
    all_admin2 = region_data("admin_level_2")
    assert len(all_admin2) > 0

    # Test getting a specific admin level 2 region
    test_region = all_admin2.iloc[0]['region_name']
    specific_region = region_data(test_region)
    assert len(specific_region) == 1
    assert specific_region.iloc[0]['region_name'] == test_region

    # Verify we get the correct region level
    region_level, regions = get_region_level(test_region)
    assert region_level == "admin_level_2"
    assert len(regions) == 1
    assert regions[0] == test_region
