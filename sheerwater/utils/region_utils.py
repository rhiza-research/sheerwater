# ruff: noqa: E501 <- line too long
"""Space and geography utility functions for all parts of the data pipeline.

The administrative regions are defined as follows:
- admin_level_x: Administrative level x boundaries
    - Available admin levels: 0 (national level), 1 (region level), 2 (county level)
- country
    - 242 unique countries, an alias for admin_level_0
- subregion:
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
- regions_wb:
  - 'latin_america_and_caribbean', 'north_america',
  - 'europe_and_central_asia', 'east_asia_and_pacific', 'south_asia',
  - 'middle_east_and_north_africa', 'sub_saharan_africa', 'antarctica'
- continent
    - 'north_america', 'asia', 'south_america', 'africa', 'europe',
    - 'oceania', 'antarctica', 'seven_seas_open_ocean'
- meteorological_zone
  - 'tropics', 'extratropics'
- hemisphere
  - 'northern_hemisphere', 'southern_hemisphere'
- global:
  - 'global'
"""
import logging
import unicodedata
import numpy as np
import pandas as pd
import geopandas as gpd
import gcsfs
from shapely.geometry import box
from nuthatch import cache
from .general_utils import load_object
import rioxarray  # noqa: F401 - needed to enable .rio attribute


logger = logging.getLogger(__name__)

##################################################################
# Administrative region definitions, including custom regions
##################################################################

# A set of standard regions that are above the nationional level - defined by the UN or WB
global_regions = ['continent', 'subregion', 'region_un', 'region_wb']
# A set of standard regions that are below the nationional level - defined by the admin level
# admin level 0 is the same as country, but we include it for consistency
admin_level_regions = ['admin_level_0', 'admin_level_1', 'admin_level_2']

# Additionally, allow the construction of custom regions by country list or lat / lon bounding box
custom_regions = {
    'sheerwater_region': {
        'nimbus_east_africa': {
            'countries': ['kenya', 'burundi', 'rwanda', 'tanzania', 'uganda'],
        },
        'nimbus_west_africa': {
            'countries': ['benin', 'burkina_faso', 'cabo_verde', 'ivory_coast', 'the_gambia', 'ghana', 'guinea', 'guinea-bissau', 'liberia', 'mali', 'mauritania', 'niger', 'nigeria', 'senegal', 'sierra_leone', 'togo'],
        },
        'conus': {
            'countries': ['united_states_of_america'],
        }
    },
    'meteorological_zone': {
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
    'hemisphere': {
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

# zone labels from https://data.apps.fao.org/catalog/dataset/0bb7237a-6740-4ea3-b2a1-e26b1647e4e0
agroecological_zone_names = {
    0: "No data",
    1: "Tropics, lowland; semi-arid",
    2: "Tropics, lowland; sub-humid",
    3: "Tropics, lowland; humid",
    4: "Tropics, highland; semi-arid",
    5: "Tropics, highland; sub-humid",
    6: "Tropics, highland; humid",
    7: "Sub-tropics, warm; semi-arid",
    8: "Sub-tropics, warm; sub-humid",
    9: "Sub-tropics, warm; humid",
    10: "Sub-tropics, moderately cool; semi-arid",
    11: "Sub-tropics, moderately cool; sub-humid",
    12: "Sub-tropics, moderately cool; humid",
    13: "Sub-tropics, cool; semi-arid",
    14: "Sub-tropics, cool; sub-humid",
    15: "Sub-tropics, cool; humid",
    16: "Temperate, moderate; dry",
    17: "Temperate, moderate; moist",
    18: "Temperate, moderate; wet",
    19: "Temperate, cool; dry",
    20: "Temperate, cool; moist",
    21: "Temperate, cool; wet",
    22: "Cold, no permafrost; dry",
    23: "Cold, no permafrost; moist",
    24: "Cold, no permafrost; wet",
    25: "Dominantly very steep terrain",
    26: "Land with severe soil/terrain limitations",
    27: "Land with ample irrigated soils",
    28: "Dominantly hydromorphic soils",
    29: "Desert/Arid climate",
    30: "Boreal/Cold climate",
    31: "Arctic/Very cold climate",
    32: "Dominantly built-up land",
    33: "Dominantly water"
}


##################################################################
# Region utilities
##################################################################


def clean_region_name(name):
    """Clean a name to make matching easier and replace non-English characters."""
    # unsupported region names
    name = str(name)  # convert to string
    if name in [None, '', '_', '-', '-_', ' ']:
        return 'no_region'
    name = name.lower().replace(' ', '_').strip()
    name = name.replace('&', 'and')
    # Normalize unicode string to remove accents, e.g., 'são_tomé_and_príncipe' -> 'sao_tome_and_principe'
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')

    # If region is country data, reconcile the name
    name = reconcile_country_name(name)
    return name


def get_combined_region_name(region):
    """Get the standard name of a combined region (e.g., 'country-agroecological_zone').

    Assumes that regions are passed in as a list of strings.
    """
    if isinstance(region, str):
        return region
    return '-'.join([clean_region_name(x) for x in region])


def reconcile_country_name(country_name):
    """Maps a country name variant to its standardized name.

    Unsupported territories/regions are mapped to 'no_region'.

    Args:
        country_name: String with a country name variant

    Returns:
        str: Standardized country name or 'no_region'
    """
    # Define standardized mappings for recognized countries
    standardization_map = {
        # China variants
        'ch-in': 'china',
        "people's_republic_of_china": 'china',

        # Cape Verde variants
        'cabo_verde': 'cape_verde',

        # Central African Republic variants
        'central_african_rep': 'central_african_republic',

        # Congo variants
        'congo,_dem_rep_of_the': 'democratic_republic_of_the_congo',
        'congo,_rep_of_the': 'republic_of_the_congo',

        # Czech Republic variants
        'czech_republic': 'czechia',

        # Ivory Coast variants
        "cote_d'ivoire": 'ivory_coast',

        # Timor-Leste variants
        'east_timor': 'timor-leste',

        # Eswatini variants
        'swaziland': 'eswatini',

        # The Bahamas variants
        'bahamas,_the': 'the_bahamas',

        # The Gambia variants
        'gambia,_the': 'the_gambia',

        # Korea variants
        'korea,_north': 'north_korea',
        'korea,_south': 'south_korea',

        # Macedonia variants
        'macedonia': 'north_macedonia',

        # Marshall Islands variants
        'marshall_is': 'marshall_islands',

        # Micronesia variants
        'micronesia,_fed_states_of': 'federated_states_of_micronesia',

        # Myanmar variants
        'burma': 'myanmar',

        # Solomon Islands variants
        'solomon_is': 'solomon_islands',

        # Saint variants (abbreviated)
        'st_kitts_and_nevis': 'saint_kitts_and_nevis',
        'st_lucia': 'saint_lucia',
        'st_vincent_and_the_grenadines': 'saint_vincent_and_the_grenadines',

        # US variants
        'united_states': 'united_states_of_america',

        # Falkland Islands variants
        'falkland_islands_(uk)': 'falkland_islands',

        # Palestine variants
        'gaza_strip': 'palestine',
        'west_bank': 'palestine',
    }

    # # Disputed territories and dependent territories to map to 'no_region'
    # unsupported_regions = [
    #     # Disputed territories
    #     'abyei', 'aksai_chin', 'ashmore_and_cartier_islands', 'demchok',
    #     'dragonja', 'dramana-shakatoe', 'isla_brasilera', 'kalapani',
    #     'koualou', 'liancourt_rocks', "no_man's_land", 'paracel_is',
    #     'senkakus', 'siachen-saltoro', 'siachen_glacier', 'somaliland',
    #     'spratly_is', 'turkish_republic_of_northern_cyprus',
    #     'sanafir_and_tiran_is.',
    #     # Dependent territories - for now, we will leave territories as they are
    #     'american_samoa', 'anguilla', 'aruba', 'bermuda',
    #     'british_virgin_islands', 'cayman_islands', 'cook_islands', 'curacao',
    #     'faroe_islands', 'french_polynesia', 'french_southern_and_antarctic_lands',
    #     'guam', 'guernsey', 'hong_kong', 'isle_of_man', 'jersey',
    #     'macau', 'montserrat', 'new_caledonia', 'niue', 'norfolk_island',
    #     'northern_mariana_islands', 'pitcairn_islands', 'puerto_rico',
    #     'saint_barthelemy', 'saint_helena', 'saint_martin', 'saint_pierre_and_miquelon',
    #     'sint_maarten', 'turks_and_caicos_islands', 'united_states_virgin_islands',
    #     'wallis_and_futuna', 'aland', 'british_indian_ocean_territory',
    #     'heard_island_and_mcdonald_islands', 'australian_indian_ocean_territories',
    #     'south_georgia_and_the_south_sandwich_islands'
    # }

    # First check if it has a standardization mapping
    if country_name in standardization_map:
        return standardization_map[country_name]
    # Then check if it's explicitly unsupported
    # For now, we will leave territories as they are
    # elif country_name in unsupported_regions:
        # return 'no_region'
    # Otherwise keep as-is (assumed to be a recognized country)
    else:
        return country_name


@cache()
def global_regions_gdf():
    """A datasource that maps countries to their global administrative regions."""
    # World geojson downloaded from https://geojson-maps.kyd.au
    filepath = 'gs://sheerwater-public-datalake/regions/world_50m.geojson'
    country_gdf = gpd.read_file(load_object(filepath))
    country_gdf = country_gdf[['name_en', 'continent', 'region_un', 'subregion', 'region_wb', 'geometry']]
    # Clean string columns for consistent, lowercase, and underscore-separated names
    for col in ["name_en", "continent", "region_un", "subregion", "region_wb"]:
        cleaned_col = "country" if col == "name_en" else col
        country_gdf[cleaned_col] = country_gdf[col].apply(clean_region_name)
    return country_gdf


def global_regions_to_country():
    """A helful mapping of global administrative regions to a list of their constituent countries.

    Derived from the global_regions_gdf.

    For example,
    {
        'continent': {
            'asia': ['china', 'india', 'japan'],
            'europe': ['france', 'germany', 'italy'],
        },
        'region_un': {
            'americas': ['united_states', 'canada'],
        },
    }
    """
    df = global_regions_gdf()
    global_regions_to_country = {}
    for region in global_regions:
        global_regions_to_country[region] = {}
        values = set(df[region])
        for val in values:
            countries = df[df[region] == val]['country']
            countries = [x for x in countries if x != 'no_region']
            global_regions_to_country[region][val] = set(countries)
    return global_regions_to_country


@cache(cache_args=['admin_level'])
def admin_level_gdf(admin_level=2):
    """A datasoruce of administrative boundaries at a given level.

    Args:
        admin_level(int): The admin level to get the data for. Must be
            an admin level(e.g., 0, 1, 2).

    Returns:
        gdf(gpd.GeoDataFrame): A GeoDataFrame for the admin level, with columns:
            - 'admin_name': the name of the admin level,
            - 'geometry': its geometry as a shapely object.
    """
    # World lo-res admin boundaries at the county level downloaded from https://github.com/stephanietuerk/admin-boundaries
    dir = {
        0: 'Admin0_simp50',
        1: 'Admin1_simp10',
        2: 'Admin2_simp05',
    }
    path = f'gs://sheerwater-public-datalake/regions/admin-boundaries/lo-res/{dir[admin_level]}'

    fs = gcsfs.GCSFileSystem(project='sheerwater', token='google_default')
    files = fs.ls(path)
    dfs = []
    for file in files:
        sub = gpd.read_file(load_object(file))
        dfs.append(sub)
    # Concat geopandas dataframes
    df = gpd.GeoDataFrame(pd.concat(dfs, ignore_index=True))
    df = df.set_geometry('geometry')

    if admin_level not in [0, 1, 2]:
        raise ValueError(f"Invalid admin level: {admin_level}")

    # Clean and construct 'admin_name' according to admin level
    df['clean0'] = df['NAME_0'].apply(clean_region_name)
    if admin_level == 0:
        df['admin_name'] = df['clean0']
    elif admin_level == 1:
        df['clean1'] = df['NAME_1'].apply(clean_region_name)
        df['admin_name'] = df['clean0'] + '-' + df['clean1']
    elif admin_level == 2:
        df['clean1'] = df['NAME_1'].apply(clean_region_name)
        df['clean2'] = df['NAME_2'].apply(clean_region_name)
        df['admin_name'] = df['clean0'] + '-' + df['clean1'] + '-' + df['clean2']
    return df


@cache(memoize=True)
def admin_levels_and_labels():
    """A dictionary of region levels and their labels, as small as possible to enable fast lookup."""
    labels_dict = {}
    # Populate all admin level regions
    for region in admin_level_regions:
        sub = admin_level_gdf(admin_level=int(region.split('_')[-1]))
        labels_dict[region] = sorted(set(sub['admin_name']))

    # Add all the global regions
    df = global_regions_gdf()
    for region in global_regions:
        labels_dict[region] = sorted(set(df[region]))
    return labels_dict


def get_region_level(region):
    """For a given region, return which level that region is at and all regions at that level.

    If the region is a specific instance of a region level, return the level and only
        that region instance.

    Args:
        region(str): The region to get the level of. 'country' is accepted as an alias for 'admin_level_0'.

    Returns:
        level(str): The level of the region.
        regions(list): All regions at that level.
    """
    if region is None:
        return 'global', ['global']

    region = clean_region_name(region)
    # Normalize 'country' to 'admin_level_0'
    if region == 'country':
        region = 'admin_level_0'

    # Iterate through the standard regions dicts
    # Will return the first level that the region is found at
    labels_dict = admin_levels_and_labels()
    for level, locations in labels_dict.items():
        if region == level:
            return level, locations
        elif region in locations:
            return level, [region]

    for level, data in custom_regions.items():
        if region == level:
            return level, data.keys()
        elif region in data.keys():
            return level, [region]

    # Now check the custom region layers
    if region == 'agroecological_zone':
        return 'agroecological_zone', [clean_region_name(x) for x in agroecological_zone_names.values()]
    elif region in [clean_region_name(x) for x in agroecological_zone_names.values()]:
        return 'agroecological_zone', [region]
    else:
        raise ValueError(f"Invalid region: {region}")


@cache(cache_args=['region_level'])
def full_admin_data(region_level):
    """Get the boundary shapefile for a given region level.

    Args:
        region_level(str): The region level to get the data for . Must be
            a region level(e.g., 'country', 'admin_level_1', 'continent', 'meteorological_zone')

    Returns:
        gdf(gpd.GeoDataFrame): A GeoDataFrame for the region, with columns:
            - 'region_name': the name of the region,
            - 'region_geometry': its geometry as a shapely object.
    """
    if region_level in admin_level_regions:
        # Get all region objects in the regions list
        gdf = admin_level_gdf(int(region_level.split('_')[-1]))
        gdf = gdf[['admin_name', 'geometry']]
        gdf = gdf.rename(columns={
            'admin_name': 'region_name',
            'geometry': 'region_geometry',
        })
    elif region_level in global_regions:
        # Need to merge the countries invovled in a global region into a single geometry
        # Need to use the global regions df here, otherwise there are gaps in the
        # geometry coverage.
        country_gdf = global_regions_gdf()
        global_mapping = global_regions_to_country()
        region_names = []
        region_geometries = []
        regions = admin_levels_and_labels()[region_level]
        for reg in regions:
            countries = global_mapping[region_level][reg]
            region_gdf = country_gdf[country_gdf['country'].isin(countries)]
            geometry = region_gdf.geometry.union_all()
            region_names.append(reg)
            region_geometries.append(geometry)
        gdf = gpd.GeoDataFrame({'region_name': region_names, 'region_geometry': region_geometries})
    elif region_level in custom_regions:
        # Custom regions are defined by a list of countries or a lat/lon bounding box
        # Need to merge the countries invovled in a custom region into a single geometry
        admin_0 = admin_level_gdf(admin_level=0)
        region_names = []
        region_geometries = []
        regions = custom_regions[region_level].keys()
        for reg in regions:
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
                countries = [clean_region_name(country) for country in data['countries']]
                region_gdf = admin_0[admin_0['admin_name'].isin(countries)]
                if len(countries) != len(region_gdf):
                    raise ValueError(
                        f"Some countries were not found: {set(countries) - set(region_gdf['country'])}")
                geometry = region_gdf.geometry.union_all()
                region_names.append(reg)
                region_geometries.append(geometry)
            else:
                raise ValueError(f"Poorly formatted custom region entry: {data}")
        gdf = gpd.GeoDataFrame({'region_name': region_names, 'region_geometry': region_geometries})
    else:
        raise ValueError(f"Invalid region level: {region_level}")

    # Set the geometry and CRS
    gdf = gdf.set_geometry("region_geometry")
    gdf = gdf.set_crs("EPSG:4326")
    return gdf


def admin_region_data(region):
    """Get geopandas GeoDataFrame with the geometry for a given admin region.

    A lightweight wrapper around full_admin_data that enables a user to pass either a
    high level region level or a specific region within that level.
    For example, both 'country' and 'indonesia' are valid region arguments.

    Args:
        region(str): The region to get the data for . Must be
            a region level(e.g., 'country', 'admin_level_1') or a specific region within that level(e.g., 'indonesia', 'kenya').
            'country' is accepted as an alias for 'admin_level_0'.
            For example, both 'country' and 'indonesia' are valid region arguments.

    Returns:
        gdf(geopandas.GeoDataFrame): A GeoDataFrame for the region, with columns:
            - 'region_name': the name of the region,
            - 'region_geometry': its geometry as a shapely object.
    """
    region_level, regions = get_region_level(region)
    full_data = full_admin_data(region_level)
    return full_data[full_data['region_name'].isin(regions)]


def clip_admin_region(ds, admin_region, region_dim=None, lon_dim='lon', lat_dim='lat', drop=True):
    """Clip a dataset to a region.

    Args:
        ds (xr.Dataset): The dataset to clip to a specific region.
        admin_region (str): The admin region to clip to, e.g., 'kenya', 'michigan'
        region_dim (str): The name of the region dimension. If None, region data is fetched from the region registry.
        lon_dim (str): The name of the longitude dimension.
        lat_dim (str): The name of the latitude dimension.
        drop (bool): Whether to drop the original coordinates that are NaN'd by clipping.
    """
    # No clipping needed
    if admin_region == 'global':
        return ds

    if region_dim is not None:
        # If we already have a region dimension, just select the region
        ds = ds.sel(**{region_dim: admin_region})
    else:
        region_df = admin_region_data(region=admin_region)

        if len(region_df) != 1:
            raise ValueError(f"Region {admin_region} has multiple geometries. Cannot clip.")
        # Set up dataframe for clipping
        ds = ds.rio.write_crs("EPSG:4326")
        ds = ds.rio.set_spatial_dims(lon_dim, lat_dim)
        # Clip the grid to the boundary of Shapefile
        ds = ds.rio.clip(region_df.geometry, region_df.crs, drop=drop)
    return ds


def clip_region(ds, region, grid, region_dim=None, drop=True):
    """Clip a dataset to a region.

    Args:
        ds(xr.Dataset): The dataset to clip to a specific region.
        region(str, list): The region to clip to. A str or list of strs.
        grid(str): The grid to clip to.
        region_dim(str): The name of the region dimension. If None, region data is fetched from the region registry.
        drop(bool): Whether to drop the original coordinates that are NaN'd by clipping.
    """
    if not isinstance(region, list):
        region = [region]
    # No clipping needed
    if region == ['global']:
        return ds

    if region_dim is not None:
        # If we already have a region dimension, just select the region
        return ds.where(ds[region_dim] == get_combined_region_name(region), drop=drop)

    # Get the high level region for each region in the list
    promoted_regions = [get_region_level(level)[0] for level in region]
    if any(x == y for x, y in zip(promoted_regions, region)):
        raise ValueError(f"Region {region} has multiple geometries. Cannot clip.")

    # Sort the region names by the promoted region levels alphabetically
    sort_idx = np.argsort(promoted_regions)
    promoted_regions = [promoted_regions[i] for i in sort_idx]
    region = [region[i] for i in sort_idx]

    # Form concatonated region string
    region = [clean_region_name(x) for x in region]
    region_str = get_combined_region_name(region)
    from sheerwater.regions_layers import region_labels
    region_ds = region_labels(space_grouping=promoted_regions, grid=grid)

    # Rename region to a dummy name to avoid conflicts while clipping
    region_ds = region_ds.rename({region_ds.region.name: '_clip_region'})
    ds = ds.where((region_ds._clip_region == region_str).compute(), drop=drop)
    ds = ds.drop_vars('_clip_region')
    return ds
