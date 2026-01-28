"""Test the regions and masking functions."""
import pytest
import geopandas as gpd

from sheerwater.masks import land_sea_mask
from sheerwater.metrics import metric
from sheerwater.spatial_subdivisions import (
    clean_region_name,
    reconcile_country_name,
    get_region_level,
    admin_region_data,
    admin_region_labels,
    region_labels,
)
from sheerwater.utils import get_grid


def test_clean_region_name():
    """Test name cleaning including unicode and special cases."""
    assert clean_region_name("United States") == "united_states_of_america"
    assert clean_region_name("South Korea") == "south_korea"
    assert clean_region_name("United Kingdom") == "united_kingdom"
    assert clean_region_name("São Tomé") == "sao_tome"
    assert clean_region_name("Côte d'Ivoire") == "ivory_coast"
    assert clean_region_name(None) == "no_region"
    assert clean_region_name("") == "no_region"
    assert clean_region_name("_") == "no_region"


def test_reconcile_country_name():
    """Test country name variants."""
    assert reconcile_country_name("ch-in") == "china"
    assert reconcile_country_name("cabo_verde") == "cape_verde"
    assert reconcile_country_name("united_states") == "united_states_of_america"
    assert reconcile_country_name("kenya") == "kenya"


def test_get_region_level():
    """Test get_region_level for various inputs."""
    level, regions = get_region_level(None)
    assert level == 'global'
    assert regions == ['global']

    level, regions = get_region_level('continent')
    assert level == 'continent'
    assert len(regions) > 0

    level, regions = get_region_level('africa')
    assert level == 'continent'
    assert regions == ['africa']

    level, regions = get_region_level('nimbus_east_africa')
    assert level == 'sheerwater_region'
    assert regions == ['nimbus_east_africa']


def test_region_data_structure():
    """Test that admin_region_data returns correct GeoDataFrame structure."""
    gdf = admin_region_data("kenya")
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert 'region_name' in gdf.columns
    assert 'region_geometry' in gdf.columns
    assert gdf.crs == 'EPSG:4326'
    assert len(gdf) > 0


def test_region_data_admin_levels():
    """Test admin_region_data for all admin levels and specific regions."""
    # Test all admin levels
    for level in ["admin_level_0", "admin_level_1", "admin_level_2"]:
        gdf = admin_region_data(level)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) > 0
        assert gdf.crs == 'EPSG:4326'
        assert 'region_name' in gdf.columns
        assert 'region_geometry' in gdf.columns

        # Verify we get the correct region level
        region_level, regions = get_region_level(level)
        assert region_level == level
        assert len(regions) > 0

    # Test specific country
    gdf = admin_region_data("kenya")
    assert len(gdf) == 1
    assert gdf.iloc[0]['region_name'] == "kenya"
    assert gdf.crs == 'EPSG:4326'

    # Test getting a specific admin level 2 region
    all_admin2 = admin_region_data("admin_level_2")
    assert len(all_admin2) > 0
    test_region = all_admin2.iloc[0]['region_name']
    specific_region = admin_region_data(test_region)
    assert len(specific_region) == 1
    assert specific_region.iloc[0]['region_name'] == test_region
    region_level, regions = get_region_level(test_region)
    assert region_level == "admin_level_2"
    assert len(regions) == 1
    assert regions[0] == test_region


def test_region_data_global_regions():
    """Test admin_region_data for global regions (continents, subregions, UN, WB)."""
    # Test all levels
    for level in ["continent", "subregion", "region_un", "region_wb"]:
        gdf = admin_region_data(level)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) > 0
        assert gdf.crs == 'EPSG:4326'

    # Test specific regions
    for region in ["africa", "asia", "eastern_africa", "indonesia"]:
        gdf = admin_region_data(region)
        assert len(gdf) == 1
        assert gdf.iloc[0]['region_name'] == region
        assert gdf.crs == 'EPSG:4326'


def test_region_data_custom_regions():
    """Test admin_region_data for custom regions."""
    # Test all custom region levels
    for level in ["sheerwater_region", "meteorological_zone"]:
        gdf = admin_region_data(level)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) > 0
        assert gdf.crs == 'EPSG:4326'

    # Test specific custom regions
    test_regions = [
        "nimbus_east_africa",  # countries-based
        "tropics",  # lat/lon-based
        "northern_hemisphere",  # hemisphere
        "global",  # global
    ]
    for region in test_regions:
        gdf = admin_region_data(region)
        assert len(gdf) == 1
        assert gdf.iloc[0]['region_name'] == region
        assert gdf.crs == 'EPSG:4326'

    # Verify sheerwater_region contains expected regions
    gdf = admin_region_data("sheerwater_region")
    region_names = gdf['region_name'].tolist()
    assert 'nimbus_east_africa' in region_names
    assert 'nimbus_west_africa' in region_names
    assert 'conus' in region_names


def test_region_data_invalid_region():
    """Test admin_region_data raises error for invalid region."""
    with pytest.raises(ValueError, match="Invalid region"):
        admin_region_data("nonexistent_region_xyz")


def test_country_alias():
    """Test that 'country' works as an alias for 'admin_level_0' everywhere."""
    # Test in admin_region_data
    gdf_country = admin_region_data("country")
    gdf_admin0 = admin_region_data("admin_level_0")
    assert len(gdf_country) == len(gdf_admin0)
    assert set(gdf_country['region_name']) == set(gdf_admin0['region_name'])

    # Test in admin_region_labels (spatial_subdivisions uses 'region' coord)
    ds_country = admin_region_labels(grid='global1_5', admin_level='country')
    ds_admin0 = admin_region_labels(grid='global1_5', admin_level='admin_level_0')
    assert set(ds_country.region.values.flatten()) == set(ds_admin0.region.values.flatten())

    # Test in region_labels (string and list)
    ds_country_str = region_labels(grid='global1_5', space_grouping='country')
    ds_country_list = region_labels(grid='global1_5', space_grouping=['country'])
    ds_admin0 = region_labels(grid='global1_5', space_grouping='admin_level_0')
    assert set(ds_country_str.region.values.flatten()) == set(ds_admin0.region.values.flatten())
    assert set(ds_country_list.region.values.flatten()) == set(ds_admin0.region.values.flatten())


def test_region_labels_input_formats():
    """Test region_labels with string and list inputs."""
    ds_str = region_labels(grid='global1_5', space_grouping='country', region='global')
    ds_list = region_labels(grid='global1_5', space_grouping=['country'], region='global')

    assert 'region' in ds_str.coords
    assert 'region' in ds_list.coords
    assert len(ds_str.lat) > 0
    assert len(ds_list.lat) > 0
    # String and list should produce same results
    assert set(ds_str.region.values.flatten()) == set(ds_list.region.values.flatten())


def test_region_labels_list_ordering():
    """Test that list ordering doesn't matter for region_labels."""
    ds1 = region_labels(grid='global1_5', space_grouping=['admin_level_1', 'agroecological_zone'])
    ds2 = region_labels(grid='global1_5', space_grouping=['agroecological_zone', 'admin_level_1'])

    regions1 = set(ds1.region.values.flatten())
    regions2 = set(ds2.region.values.flatten())

    # They should have the same region names (order-independent)
    assert regions1 == regions2


def test_region_labels_multiple_admin_regions_error():
    """Test that passing multiple admin regions raises an error."""
    with pytest.raises(ValueError, match="Only one admin region can be specified"):
        region_labels(grid='global1_5', space_grouping=['admin_level_1', 'admin_level_2'])

    with pytest.raises(ValueError, match="Only one admin region can be specified"):
        region_labels(grid='global1_5', space_grouping=['country', 'admin_level_1'])

    with pytest.raises(ValueError, match="Only one admin region can be specified"):
        region_labels(grid='global1_5', space_grouping=['admin_level_0', 'admin_level_1', 'agroecological_zone'])


def test_metric_with_list_grouping():
    """Test that metric function accepts list space_grouping."""
    # Test with a simple metric call using list grouping
    result = metric(
        start_time="2016-01-01",
        end_time="2016-01-08",
        variable="precip",
        agg_days=7,
        forecast="chirps",
        truth="chirps",
        metric_name="mae",
        space_grouping=['country', 'agroecological_zone'],
        grid="global1_5",
        region=['africa', 'land_with_ample_irrigated_soils'],
        recompute=True,
        cache_mode='overwrite'
    )
    # Verify the result has a region coordinate
    assert 'space_grouping' in result.coords or 'space_grouping' in result.dims
    assert len(result) > 0


def test_land_sea_mask():
    """Test the land sea mask function."""
    grids = ["global0_25", "global1_5"]
    for grid in grids:
        lsm = land_sea_mask(grid=grid)
        assert len(lsm.lat.values) > 0


def test_get_grid():
    """Test the get_grid function."""
    # Test global0_25 grid
    lons, lats, grid_size, _ = get_grid("global0_25")
    assert lons[0] == -180.0
    assert lons[-1] == 180.0 - 0.25
    assert lats[0] == -90.0
    assert lats[-1] == 90.0
    assert grid_size == 0.25
    assert len(lons) == 1440
    assert len(lats) == 721

    # Test global1_5 grid
    lons, lats, grid_size, _ = get_grid("global1_5")
    assert lons[0] == -180.0
    assert lons[-1] == 180.0 - 1.5
    assert lats[0] == -90.0
    assert lats[-1] == 90.0
    assert grid_size == 1.5
    assert len(lons) == 240
    assert len(lats) == 121

    # Test salient0_25 grid
    lons, lats, grid_size, _ = get_grid("salient0_25")
    assert lons[0] == -180.0 + 0.125
    assert lons[-1] == 180.0 - 0.125
    assert lats[0] == -90.0 + 0.125
    assert lats[-1] == 90.0 - 0.125
    assert grid_size == 0.25
    assert len(lons) == 1440
    assert len(lats) == 720

    # Test chirps grid
    lons, lats, grid_size, _ = get_grid("chirps")
    assert pytest.approx(lons[0], abs=1e-10) == -180.0 + 0.025
    assert pytest.approx(lons[-1], abs=1e-10) == 180.0 - 0.025
    assert pytest.approx(lats[0], abs=1e-10) == -90.0 + 0.025
    assert pytest.approx(lats[-1], abs=1e-10) == 90.0 - 0.025
    assert pytest.approx(grid_size, abs=1e-10) == 0.05
    assert len(lons) == 7200
    assert len(lats) == 3600

    # Test imerg grid
    lons, lats, grid_size, _ = get_grid("imerg")
    assert pytest.approx(lons[0], abs=1e-10) == -180.0 + 0.05
    assert pytest.approx(lons[-1], abs=1e-10) == 180.0 - 0.05
    assert pytest.approx(lats[0], abs=1e-10) == -90.0 + 0.05
    assert pytest.approx(lats[-1], abs=1e-10) == 90.0 - 0.05
    assert pytest.approx(grid_size, abs=1e-10) == 0.1
    assert len(lons) == 3600
    assert len(lats) == 1800
