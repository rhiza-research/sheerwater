"""Test the regions and masking functions."""
import pytest
import geopandas as gpd
import numpy as np
import xarray as xr

from sheerwater.masks import land_sea_mask
from sheerwater.metrics import metric
from sheerwater.spatial_subdivisions import (
    clean_spatial_subdivision_name,
    reconcile_country_name,
    get_spatial_subdivision_level,
    polygon_subdivision_geodataframe,
    polygon_subdivision_labels,
    space_grouping_labels,
    nonuniform_grid,
    clip_region,
)
from sheerwater.utils import get_grid


def test_clean_spatial_subdivision_name():
    """Test name cleaning including unicode and special cases."""
    assert clean_spatial_subdivision_name("United States") == "united_states_of_america"
    assert clean_spatial_subdivision_name("South Korea") == "south_korea"
    assert clean_spatial_subdivision_name("United Kingdom") == "united_kingdom"
    assert clean_spatial_subdivision_name("São Tomé") == "sao_tome"
    assert clean_spatial_subdivision_name("Côte d'Ivoire") == "ivory_coast"
    assert clean_spatial_subdivision_name(None) == "no_region"
    assert clean_spatial_subdivision_name("") == "no_region"
    assert clean_spatial_subdivision_name("_") == "no_region"


def test_reconcile_country_name():
    """Test country name variants."""
    assert reconcile_country_name("ch-in") == "china"
    assert reconcile_country_name("cabo_verde") == "cape_verde"
    assert reconcile_country_name("united_states") == "united_states_of_america"
    assert reconcile_country_name("kenya") == "kenya"


def test_get_spatial_subdivision_level():
    """Test get_spatial_subdivision_level for various inputs. Returns (level, promoted)."""
    level, promoted = get_spatial_subdivision_level(None)
    assert level == "global"
    assert promoted == -1

    level, promoted = get_spatial_subdivision_level("continent")
    assert level == "continent"
    assert promoted == 0

    level, promoted = get_spatial_subdivision_level("africa")
    assert level == "continent"
    assert promoted == 1

    level, promoted = get_spatial_subdivision_level("nimbus_east_africa")
    assert level == "sheerwater_region"
    assert promoted == 1


def _region_gdf(region, grid="global1_5"):
    """Helper: GeoDataFrame for a level or a specific region using spatial_subdivisions API."""
    level, promoted = get_spatial_subdivision_level(region, grid=grid)
    gdf = polygon_subdivision_geodataframe(level)
    if promoted == 1:
        name = clean_spatial_subdivision_name(region)
        gdf = gdf[gdf["region_name"] == name]
    return gdf


def test_region_data_structure():
    """Test that polygon_subdivision_geodataframe returns correct GeoDataFrame structure."""
    gdf = _region_gdf("kenya")
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert "region_name" in gdf.columns
    assert "region_geometry" in gdf.columns
    assert gdf.crs == "EPSG:4326"
    assert len(gdf) > 0


def test_region_data_admin_levels():
    """Test polygon_subdivision_geodataframe for admin levels and specific regions."""
    # spatial_subdivisions uses 'country', 'admin_1', 'admin_2' (no admin_level_0)
    for level in ["country", "admin_1", "admin_2"]:
        gdf = polygon_subdivision_geodataframe(level)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) > 0
        assert gdf.crs == "EPSG:4326"
        assert "region_name" in gdf.columns
        assert "region_geometry" in gdf.columns

        level_out, promoted = get_spatial_subdivision_level(level)
        assert level_out == level
        assert promoted == 0
        assert len(polygon_subdivision_geodataframe(level)) > 0

    # Specific country
    gdf = _region_gdf("kenya")
    assert len(gdf) == 1
    assert gdf.iloc[0]["region_name"] == "kenya"
    assert gdf.crs == "EPSG:4326"

    # Specific admin level 2 region
    all_admin2 = polygon_subdivision_geodataframe("admin_2")
    assert len(all_admin2) > 0
    test_region = all_admin2.iloc[0]["region_name"]
    specific_region = _region_gdf(test_region)
    assert len(specific_region) == 1
    assert specific_region.iloc[0]["region_name"] == test_region
    level_out, promoted = get_spatial_subdivision_level(test_region)
    assert level_out == "admin_2"
    assert promoted == 1


def test_region_data_global_regions():
    """Test polygon_subdivision_geodataframe for global regions (continents, subregions, UN, WB)."""
    for level in ["continent", "subregion", "region_un", "region_wb"]:
        gdf = polygon_subdivision_geodataframe(level)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) > 0
        assert gdf.crs == "EPSG:4326"

    for region in ["africa", "asia", "eastern_africa", "indonesia"]:
        gdf = _region_gdf(region)
        assert len(gdf) == 1
        assert gdf.iloc[0]["region_name"] == region
        assert gdf.crs == "EPSG:4326"


def test_region_data_custom_regions():
    """Test polygon_subdivision_geodataframe for custom regions."""
    for level in ["sheerwater_region", "meteorological_zone"]:
        gdf = polygon_subdivision_geodataframe(level)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) > 0
        assert gdf.crs == "EPSG:4326"

    test_regions = [
        "nimbus_east_africa",
        "tropics",
        "northern_hemisphere",
        "global",
    ]
    for region in test_regions:
        gdf = _region_gdf(region)
        assert len(gdf) == 1
        assert gdf.iloc[0]["region_name"] == region
        assert gdf.crs == "EPSG:4326"

    gdf = polygon_subdivision_geodataframe("sheerwater_region")
    region_names = gdf["region_name"].tolist()
    assert "nimbus_east_africa" in region_names
    assert "nimbus_west_africa" in region_names
    assert "conus" in region_names


def test_region_data_invalid_region():
    """Test that invalid region raises ValueError."""
    with pytest.raises(ValueError, match="Invalid spatial subdivision"):
        get_spatial_subdivision_level("nonexistent_region_xyz")
    with pytest.raises(ValueError, match="Invalid region level"):
        polygon_subdivision_geodataframe("nonexistent_region_xyz")


def test_polygon_subdivision_labels_country():
    """Test polygon_subdivision_labels with level='country' returns dataset with region coord."""
    ds = polygon_subdivision_labels(grid="global1_5", level="country")
    assert "region" in ds.coords
    assert len(ds.lat) > 0


def test_space_grouping_labels_input_formats():
    """Test space_grouping_labels with string and list inputs."""
    ds_str = space_grouping_labels(grid="global1_5", space_grouping="country")
    ds_list = space_grouping_labels(grid="global1_5", space_grouping=["country"])

    assert "region" in ds_str.coords
    assert "region" in ds_list.coords
    assert len(ds_str.lat) > 0
    assert len(ds_list.lat) > 0
    assert set(ds_str.region.values.flatten()) == set(ds_list.region.values.flatten())


def test_space_grouping_labels_list_ordering():
    """Test that list ordering doesn't matter for space_grouping_labels."""
    ds1 = space_grouping_labels(
        grid="global1_5", space_grouping=["admin_1", "agroecological_zone"]
    )
    ds2 = space_grouping_labels(
        grid="global1_5", space_grouping=["agroecological_zone", "admin_1"]
    )
    regions1 = set(ds1.region.values.flatten())
    regions2 = set(ds2.region.values.flatten())
    assert regions1 == regions2


def test_metric_with_list_grouping():
    """Test that metric function accepts list space_grouping."""
    result = metric(
        start_time="2016-01-01",
        end_time="2016-01-08",
        variable="precip",
        agg_days=7,
        forecast="chirps",
        truth="chirps",
        metric_name="mae",
        space_grouping=["country", "agroecological_zone"],
        grid="global1_5",
        region=["africa", "land_with_ample_irrigated_soils"],
        recompute=True,
        cache_mode="overwrite",
    )
    assert "space_grouping" in result.coords or "space_grouping" in result.dims
    assert len(result) > 0


def test_land_sea_mask():
    """Test the land sea mask function."""
    grids = ["global0_25", "global1_5"]
    for grid in grids:
        lsm = land_sea_mask(grid=grid)
        assert len(lsm.lat.values) > 0


def test_nonuniform_clip():
    """Test the nonuniform clip function."""
    # create a grid with randomized lat / lon steps
    lat_start = -90.0
    lon_start = -180.0
    lat_steps = np.random.uniform(1, 5, 1000)
    lon_steps = np.random.uniform(1, 5, 1000)
    lons = lon_start + np.cumsum(lon_steps)
    lats = lat_start + np.cumsum(lat_steps)
    # drop points above lat / lon limits (90 and 180 respectively)
    lons = lons[lons <= 180.0]
    lats = lats[lats <= 90.0]

    # create a dataset with random precip values
    ds = xr.Dataset(coords={'lon': lons, 'lat': lats}, data_vars={'precip': (('lat', 'lon'), np.random.rand(len(lats), len(lons)))})
    # check that grid is nonuniform
    assert nonuniform_grid(ds)
    # clip to africa
    ds_africa = clip_region(ds, "africa", grid="nonuniform")
    # check that values outside africa bounding box are nan
    mask_outside = ((ds_africa.lat < -40) | (ds_africa.lat > 40) | (ds_africa.lon < -20) | (ds_africa.lon > 55))
    assert ds_africa['precip'].where(mask_outside).isnull().all()

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
