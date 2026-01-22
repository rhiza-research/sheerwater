"""Test the region_utils module."""
import pytest
import geopandas as gpd

from sheerwater.utils.region_utils import (
    clean_name,
    reconcile_country_name,
    get_region_level,
    region_data,
)


def test_clean_name():
    """Test name cleaning including unicode and special cases."""
    assert clean_name("United States") == "united_states_of_america"
    assert clean_name("South Korea") == "south_korea"
    assert clean_name("United Kingdom") == "united_kingdom"
    assert clean_name("São Tomé") == "sao_tome"
    assert clean_name("Côte d'Ivoire") == "ivory_coast"
    assert clean_name(None) == "no_region"
    assert clean_name("") == "no_region"
    assert clean_name("_") == "no_region"


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
    """Test that region_data returns correct GeoDataFrame structure."""
    gdf = region_data("kenya")
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert 'region_name' in gdf.columns
    assert 'region_geometry' in gdf.columns
    assert gdf.crs == 'EPSG:4326'
    assert len(gdf) > 0


def test_region_data_admin_levels():
    """Test region_data for all admin levels and specific regions."""
    # Test all admin levels
    for level in ["admin_level_0", "admin_level_1", "admin_level_2"]:
        gdf = region_data(level)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) > 0
        assert gdf.crs == 'EPSG:4326'

    # Test specific country
    gdf = region_data("kenya")
    assert len(gdf) == 1
    assert gdf.iloc[0]['region_name'] == "kenya"
    assert gdf.crs == 'EPSG:4326'


def test_region_data_global_regions():
    """Test region_data for global regions (continents, subregions, UN, WB)."""
    # Test all levels
    for level in ["continent", "subregion", "region_un", "region_wb"]:
        gdf = region_data(level)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) > 0
        assert gdf.crs == 'EPSG:4326'

    # Test specific regions
    for region in ["africa", "asia", "eastern_africa"]:
        gdf = region_data(region)
        assert len(gdf) == 1
        assert gdf.iloc[0]['region_name'] == region
        assert gdf.crs == 'EPSG:4326'


def test_region_data_custom_regions():
    """Test region_data for custom regions."""
    # Test all custom region levels
    for level in ["sheerwater_region", "meteorological_zone"]:
        gdf = region_data(level)
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
        gdf = region_data(region)
        assert len(gdf) == 1
        assert gdf.iloc[0]['region_name'] == region
        assert gdf.crs == 'EPSG:4326'

    # Verify sheerwater_region contains expected regions
    gdf = region_data("sheerwater_region")
    region_names = gdf['region_name'].tolist()
    assert 'nimbus_east_africa' in region_names
    assert 'nimbus_west_africa' in region_names
    assert 'conus' in region_names


def test_region_data_invalid_region():
    """Test region_data raises error for invalid region."""
    with pytest.raises(ValueError, match="Invalid region"):
        region_data("nonexistent_region_xyz")
