# ruff: noqa: E501 <- line too long
"""Region definitions for the Sheerwater Benchmarking project.

The regions are defined as follows:
- countries
    - 242 unique countries
- subregions:
  - 'central_america', 'caribbean', 'north_america',
  - 'south_eastern_asia', 'western_asia', 'south_asia',
  - 'eastern_asia', 'central_asia', 'seven_seas_open_ocean',
  - 'south_america', 'eastern_africa', 'north_africa',
  - 'middle_africa', 'southern_africa', 'western_africa',
  - 'western_europe', 'eastern_europe', 'north_europe',
  - 'south_europe', 'melanesia', 'australia_and_new_zealand',
  - 'polynesia', 'micronesia', 'antarctica'
- regions_un: United Nations regions
  - 'americas', 'asia', 'africa', 'europe', 'oceania', 'antarctica'
- regions_wb
  - 'latin_america_and_caribbean', 'north_america',
  - 'europe_and_central_asia', 'east_asia_and_pacific', 'south_asia',
  - 'middle_east_and_north_africa', 'sub_saharan_africa', 'antarctica'
- continents
    - 'north_america', 'asia', 'south_america', 'africa', 'europe',
    - 'oceania', 'antarctica', 'seven_seas_open_ocean'
- meteorological_zones
  - 'tropics', 'extratropics'
- hemispheres
  - 'northern_hemisphere', 'southern_hemisphere'
- global:
  - 'global'
"""
from shapely.geometry import box
import geopandas as gpd

from .general_utils import load_object


def clean_name(name):
    """Clean a name to make matching easier."""
    return name.lower().replace(' ', '_')


# Define the class of standard regions
standard_regions = ['country', 'continent', 'subregion', 'region_un', 'region_wb']

# Additionally, allow the construction of custom regions by country list or lat / lon bounding box
custom_regions = {
    'sheerwater_areas': {
        'nimbus_east_africa': {
            'countries': ['kenya', 'burundi', 'rwanda', 'tanzania', 'uganda'],
        },
        'nimbus_west_africa': {
            'countries': ['benin', 'burkina_faso', 'cape_verde', 'ivory_coast', 'the_gambia', 'ghana', 'guinea', 'guinea-bissau', 'liberia', 'mali', 'mauritania', 'niger', 'nigeria', 'senegal', 'sierra_leone', 'togo'],
        },
        'conus': {
            'countries': ['united_states_of_america'],
        }
    },
    'meteorological_zones': {
        'tropics': {
            'lons': [-180.0, 180.0],
            'lats': [-23.5, 23.5]
        },
        'extratropics_northern': {
            'lons': [-180.0, 180.0],
            'lats': [-90.0, -23.5],
        },
        'extratropics_southern': {
            'lons': [-180.0, 180.0],
            'lats': [23.5, 90.0],
        }
    },
    'hemispheres': {
        'northern_hemisphere': {
            'lons': [-180.0, 180.0],
            'lats': [0.0, 90.0]
        },
        'southern_hemisphere': {
            'lons': [-180.0, 180.0],
            'lats': [-90.0, 0.0]
        }
    },
    'global': {
        'global': {
            'lons': [-180.0, 180.0],
            'lats': [-90.0, 90.0]
        }
    }
}


def get_country_gdf():
    """Get the country GeoDataFrame."""
    # World geojson downloaded from https://geojson-maps.kyd.au
    filepath = 'gs://sheerwater-datalake/regions/world_50m.geojson'
    country_gdf = gpd.read_file(load_object(filepath))
    country_gdf = country_gdf[['name_en', 'continent', 'region_un', 'subregion', 'region_wb', 'geometry']]
    # Clean string columns for consistent, lowercase, and underscore-separated names
    for col in ["name_en", "continent", "region_un", "subregion", "region_wb"]:
        cleaned_col = "country" if col == "name_en" else col
        country_gdf[cleaned_col] = country_gdf[col].apply(clean_name)
    return country_gdf


def get_region_level(region):
    """Get the level of a region and the regions at that level."""
    country_gdf = get_country_gdf()

    # Find which region level the region is in, and get a list of regions at that level
    # If a region could possibly match several region levels, it will return the first
    found = False
    for level in standard_regions:
        if found:
            break
        if region == level:
            region_level = level
            regions = country_gdf[region_level].unique()
            found = True
        if region in country_gdf[level].unique():
            region_level = level
            regions = [region]
            found = True
    for level, data in custom_regions.items():
        if found:
            break
        if region == level:
            region_level = level
            regions = data.keys()
            found = True
        elif region in data.keys():
            region_level = level
            regions = [region]
            found = True
    if not found:
        raise ValueError(f"Region {region} not found")
    return region_level, regions


def get_region_data(region):
    """Get the boundary shapefile for a given region.

    Args:
        region (str): The region to get the data for. Can be either
            a region level or a specific region within that level. So, for example,
            both 'countries' and 'indonesia' are valid regions.

    Returns:
        gdf (gpd.GeoDataFrame): A GeoDataFrame for the region, with columns:
            - 'region_name': the name of the region,
            - 'region_geometry': its geometry as a shapely object.
    """
    # Standardize input region name
    region = clean_name(region)

    # Get the region data needed to form the GeoDataFrame
    country_gdf = get_country_gdf()
    region_level, regions = get_region_level(region)

    # Form the GeoDataFrame for the region
    region_names = []
    region_geometries = []
    for reg in regions:
        if region_level in standard_regions:
            # Handle standard regions
            region_names.append(reg)
            geometry = country_gdf[country_gdf[region_level] == reg].geometry.union_all()
            region_geometries.append(geometry)
        else:
            # Handle custom regions
            data = custom_regions[region_level][reg]
            if 'lats' in data and 'lons' in data:
                # Create a shapefile (GeoDataFrame) from lat/lon boundaries as a rectangular Polygon
                tol = 0.005
                lons = data['lons']
                lats = data['lats']
                region_box = box(lons[0] - tol, lats[0] - tol, lons[1] + tol, lats[1] + tol)
                region_names.append(reg)
                region_geometries.append(region_box)
            elif 'countries' in data:
                countries = [clean_name(country) for country in data['countries']]
                region_gdf = country_gdf[country_gdf['country'].isin(countries)]
                if len(countries) != len(region_gdf):
                    raise ValueError(f"Some countries were not found: {set(countries) - set(region_gdf['country'])}")
                geometry = region_gdf.geometry.union_all()
                region_names.append(reg)
                region_geometries.append(geometry)
            else:
                raise ValueError(f"Poorly formatted custom region entry: {data}")

    gdf = gpd.GeoDataFrame({'region_name': region_names, 'region_geometry': region_geometries})
    gdf = gdf.set_geometry("region_geometry")
    gdf = gdf.set_crs("EPSG:4326")
    return gdf
