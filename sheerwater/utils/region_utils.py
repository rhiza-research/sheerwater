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
import numpy as np
import xarray as xr
import logging
import unicodedata
import geopandas as gpd
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


def agroecological_zones_name_dict():
    """Human-readable labels for the agroecological zones."""
    # zone labels from https://data.apps.fao.org/catalog/dataset/0bb7237a-6740-4ea3-b2a1-e26b1647e4e0
    zone_labels = {
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
    return zone_labels


##################################################################
# Region utilities
##################################################################


def clean_name(name):
    """Clean a name to make matching easier and replace non-English characters."""
    # unsupported region names
    if name in [None, '', '_', '-', '-_', ' ']:
        return 'no_region'
    name = name.lower().replace(' ', '_').strip()
    name = name.replace('&', 'and')
    # Normalize unicode string to remove accents, e.g., 'são_tomé_and_príncipe' -> 'sao_tome_and_principe'
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')

    # If region is country data, reconcile the name
    name = reconcile_country_name(name)
    return name


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
        country_gdf[cleaned_col] = country_gdf[col].apply(clean_name)
    return country_gdf


def global_regions_to_country():
    """A helful mapping of global administrative regions to a list of their constituent countries.

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
    """A datasoruce of administrative boundaries at a given level."""
    filepath = f'gs://sheerwater-public-datalake/regions/geoBoundariesCGAZ_ADM{admin_level}.geojson'
    df = gpd.read_file(load_object(filepath))
    df['admin_name'] = df['shapeName'].apply(clean_name)
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

    region = clean_name(region)
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
        return 'agroecological_zone', [clean_name(x) for x in agroecological_zones_name_dict().values()]
    elif region in [clean_name(x) for x in agroecological_zones_name_dict().values()]:
        return 'agroecological_zone', [region]
    else:
        raise ValueError(f"Invalid region: {region}")


@cache(cache_args=['region_level'])
def full_admin_data(region_level):
    """Get the boundary shapefile for a given region level.

    Args:
        region_level(str): The region level to get the data for . Must be
            a region level(e.g., 'country', 'admin_level_1')

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
                countries = [clean_name(country) for country in data['countries']]
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


@cache(cache_args=['grid', 'admin_level'],
       backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
def admin_region_labels(grid='global1_5', admin_level='country'):
    """Generate a dataset with a region coordinate at a specific space grouping.

    Available space groupings are
     - 'country', 'continent', 'subregion', 'region_un', 'region_wb', 'meteorological_zone',
        'hemisphere', 'global', and 'sheerwater_region'. The admin level region is also available.

    Args:
        grid(str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.
        admin_level(str): A single admin level:
            - country, continent, subregion, region_un, region_wb, meteorological_zone,
              hemisphere, sheerwater_region, or admin_level_0, admin_level_1, admin_level_2

    Returns:
        xarray.Dataset: Dataset with added region coordinate
    """
    # Normalize 'country' to 'admin_level_0'
    if admin_level == 'country':
        admin_level = 'admin_level_0'

    # Get the list of regions for the specified admin level
    admin_df = admin_region_data(admin_level)

    # Get the grid dataframe
    ds = get_grid_ds(grid)
    # Assign a dummy region coordinate to all grid cells
    # Fixed data type of strings of length 40
    ds = ds.assign_coords(admin_region=(('lat', 'lon'), xr.full_like(ds.lat * ds.lon, 'no_admin', dtype='U40').data))

    # If admin group, construct the admin gridded dataframe
    # Loop through each region and label grid cells
    for i, rn in admin_df.iterrows():
        print(i+1, '/', len(admin_df.region_name), rn.region_name)
        # Clip the grid to the boundary of Shapefile
        world_ds = xr.full_like(ds.lat * ds.lon, 1.0, dtype=np.float32)
        #  Add geometry to the dataframe and clip
        world_ds = world_ds.rio.write_crs("EPSG:4326")
        world_ds = world_ds.rio.set_spatial_dims('lon', 'lat')
        region_ds = world_ds.rio.clip(rn, admin_df.crs, drop=False)
        # Assign the region name to the region coordinate
        ds['admin_region'] = xr.where(~region_ds.isnull(), rn.region_name, ds['admin_region'])
    return ds


def get_combined_region_name(region):
    """Get the standard name of a combined region."""
    if isinstance(region, str):
        return region
    return '-'.join([clean_name(x) for x in region])


@cache(cache_args=['grid', 'space_grouping'], memoize=True,
       backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
def region_labels(grid='global1_5', space_grouping=None):
    """Generate a dataset with a region coordinate at a specific space grouping.

    Args:
        grid(str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.
        space_grouping(str or list): Region grouping(s):
            - A string for a single grouping: 'country', 'continent', 'subregion', etc.
            - A list for multiple groupings: ['country'], ['admin_level_1', 'agroecological_zone'], etc.

    Returns:
        xarray.Dataset: Dataset with added region coordinate
    """
    if space_grouping is None:
        space_grouping = ['country']

    # Convert single string to list (treat as single region, don't split by dashes)
    if isinstance(space_grouping, str):
        layers = [space_grouping]
    elif isinstance(space_grouping, list):
        layers = space_grouping
    else:
        raise TypeError(f"space_grouping must be a str or list, got {type(space_grouping)}")

    # Normalize 'country' to 'admin_level_0' in all layers
    layers = ['admin_level_0' if layer == 'country' else layer for layer in layers]

    # Sort alphabetically to ensure consistent results regardless of input order
    layers = sorted(layers)

    # Validate that only one admin region is specified
    labels_dict = admin_levels_and_labels()
    admin_regions_in_list = [layer for layer in layers if layer in labels_dict.keys()]
    if len(admin_regions_in_list) > 1:
        raise ValueError(
            f"Only one admin region can be specified in space_grouping. "
            f"Found {len(admin_regions_in_list)}: {admin_regions_in_list}"
        )

    layer_grids = []
    for layer in layers:
        if layer in labels_dict:
            # One of the standard admin levels
            layer_df = admin_region_labels(admin_level=layer, grid=grid)
        else:
            if layer == 'agroecological_zone':
                layer_df = agroecological_zone_labels(grid=grid)
            else:
                raise ValueError(f"Invalid layer: {layer}")
        layer_grids.append(layer_df)

    # Create a a new dataset with the concatonation of all the layers
    ds = xr.merge(layer_grids)
    # This pesky spatial_ref coordinate is not needed
    if 'spatial_ref' in ds.coords:
        ds = ds.drop_vars('spatial_ref')

    # Find all the region coordinates
    region_coords = [x for x in ds.coords if x not in ds.dims]

    coords_values = [ds[x].values.flatten() for x in region_coords]
    combined_region_coords = np.array([get_combined_region_name(vals) for vals in zip(*coords_values)], dtype='U40')
    ds = ds.assign_coords(region=(('lat', 'lon'), combined_region_coords.reshape(ds.lat.size, ds.lon.size)))
    return ds


@cache(cache_args=['grid'])
def agroecological_zone_labels(grid='global1_5'):
    """Get the agroecological zones as an xarray dataset."""
    # Downloaded from https://data.apps.fao.org/catalog/iso/9a9ed6cf-83cc-4b42-b295-305184d3f0b8
    tif_path = 'gs://sheerwater-public-datalake/regions/agroecological_zones.tif'
    ds = xr.open_dataset(load_object(tif_path), engine='rasterio')
    ds = ds.rename({'x': 'lon', 'y': 'lat'})
    ds = ds.squeeze('band').drop(['band', 'spatial_ref'])
    ds = ds.rename_vars({'band_data': 'agroecological_zone'})

    da = ds.agroecological_zone.fillna(0)
    da = da.astype(np.int32)

    # Import here to avoid circular imports
    from .data_utils import regrid
    da = regrid(da, grid, base='base180', method='conservative')
    # Should use most common here, but is failing with error
    # *** ValueError: zero-size array to reduction operation fmax which has no identity
    # in the flox call. Can debug another day...
    # da = regrid(da, grid, base='base180', method='most_common', regridder_kwargs={'values': np.unique(da.values)})
    ds = da.to_dataset(name='agroecological_zone')

    # Convert back to integer
    ds['agroecological_zone'] = ds['agroecological_zone'].astype(np.int32)

    def map_labels(x):
        try:
            x = int(x)
        except ValueError:
            return "Unknown"
        name = agroecological_zones_name_dict().get(x, "Unknown")
        name = name.replace('; ', '_').replace(', ', '_').replace(' ', '_').lower().strip()
        return name

    # Vectorized mapping function
    vectorized_map = np.vectorize(map_labels)

    # Apply to your DataArray
    ds['agroecological_zone'] = xr.apply_ufunc(
        vectorized_map,
        ds['agroecological_zone'],
        vectorize=True
    )

    # Convert variables to a coordinate
    ds = ds.set_coords('agroecological_zone')
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
    region = [clean_name(x) for x in region]
    region_str = get_combined_region_name(region)
    region_ds = region_labels(space_grouping=promoted_regions, grid=grid)
    region_ds = region_ds.rename({region_ds.region.name: '_clip_region'})
    ds = ds.where((region_ds._clip_region == region_str).compute(), drop=drop)
    ds = ds.drop_vars('_clip_region')
    # Assign the region coordinate to the dataset
    return ds


def get_globe_slice(ds, lon_slice, lat_slice, lon_dim='lon', lat_dim='lat', base="base180"):
    """Get a slice of the globe from the dataset.

    Handle the wrapping of the globe when slicing.

    Args:
        ds (xr.Dataset): Dataset to slice.
        lon_slice (np.ndarray): The longitude slice.
        lat_slice (np.ndarray): The latitude slice.
        lon_dim (str): The longitude column name.
        lat_dim (str): The latitude column name.
        base (str): The base of the longitudes. One of:
            - base180, base360
    """
    if base == "base360" and (lon_slice < 0.0).any():
        raise ValueError("Longitude slice not in base 360 format.")
    if base == "base180" and (lon_slice > 180.0).any():
        raise ValueError("Longitude slice not in base 180 format.")

    # Ensure that latitude is sorted before slicing
    ds = ds.sortby(lat_dim)

    wrapped = is_wrapped(lon_slice)
    if not wrapped:
        return ds.sel(**{lon_dim: slice(lon_slice[0], lon_slice[-1]),
                         lat_dim: slice(lat_slice[0], lat_slice[-1])})
    # A single wrapping discontinuity
    if base == "base360":
        slices = [[lon_slice[0], 360.0], [0.0, lon_slice[-1]]]
    else:
        slices = [[lon_slice[0], 180.0], [-180.0, lon_slice[-1]]]
    ds_subs = []
    for s in slices:
        ds_subs.append(ds.sel(**{
            lon_dim: slice(s[0], s[-1]),
            lat_dim: slice(lat_slice[0], lat_slice[-1])
        }))
    return xr.concat(ds_subs, dim=lon_dim)


def lon_base_change(ds, to_base="base180", lon_dim='lon'):
    """Change the base of the dataset from base 360 to base 180 or vice versa.

    Args:
        ds (xr.Dataset): Dataset to change.
        to_base (str): The base to change to. One of:
            - base180
            - base360
        lon_dim (str): The longitude column name.
    """
    if to_base == "base180":
        if (ds[lon_dim] < 0.0).any():
            print("Longitude already in base 180 format.")
            return ds
        lons = base360_to_base180(ds[lon_dim].values)
    elif to_base == "base360":
        if (ds[lon_dim] > 180.0).any():
            print("Longitude already in base 360 format.")
            return ds
        lons = base180_to_base360(ds[lon_dim].values)
    else:
        raise ValueError(f"Invalid base {to_base}.")

    # Check if original data is wrapped
    wrapped = is_wrapped(ds.lon.values)

    # Then assign new coordinates
    ds = ds.assign_coords({lon_dim: lons})

    # Sort the lons after conversion, unless the slice
    # you're considering wraps around the meridian
    # in the resultant base.
    if not wrapped:
        ds = ds.sortby('lon')
    return ds


def apply_mask(ds, mask, var=None, val=0.0, grid='global1_5'):
    """Apply a mask to a dataset.

    Args:
        ds (xr.Dataset): Dataset to apply mask to.
        mask (str): The mask to apply. One of: 'lsm', None
        var (str): Variable to mask. If None, applies to apply to all variables.
        val (int): Value to mask below (any value that is
            strictly less than this value will be masked).
        grid (str): The grid resolution of the dataset.
    """
    # No masking needed
    if mask is None:
        return ds

    if isinstance(mask, str):
        from sheerwater.regions_and_masks import spatial_mask
        mask_ds = spatial_mask(mask, grid)
    else:
        mask_ds = mask

    # Check that the mask and dataset have the same dimensions
    if not all([dim in ds.dims for dim in mask_ds.dims]):
        raise ValueError("Mask and dataset must have the same dimensions.")

    if check_bases(ds, mask_ds) == -1:
        raise ValueError("Datasets have different longitude bases. Cannot mask.")

    # Ensure that the mask and the dataset don't have different precision
    # This MUST be np.float32 as of 4/28/25...unsure why?
    # Otherwise the mask doesn't match and lat/lons get dropped
    mask_ds['lon'] = np.round(mask_ds.lon, 5).astype(np.float32)
    mask_ds['lat'] = np.round(mask_ds.lat, 5).astype(np.float32)
    ds['lon'] = np.round(ds.lon, 5).astype(np.float32)
    ds['lat'] = np.round(ds.lat, 5).astype(np.float32)

    if isinstance(var, str):
        # Mask a single variable
        ds[var] = ds[var].where(mask_ds['mask'] > val, drop=False)
    else:
        # Mask multiple variables
        ds = ds.where(mask_ds['mask'] > val, drop=False)
    return ds


def snap_point_to_grid(point, grid_size, offset):
    """Snap a point to a provided grid and offset."""
    return round(float(point+offset)/grid_size) * grid_size - offset


def get_grid_ds(grid_id, base="base180", region='global'):
    """Get a dataset equal to ones for a given region."""
    lons, lats, _, _ = get_grid(grid_id, base=base)
    data = np.ones((len(lons), len(lats)))
    ds = xr.Dataset(
        {"mask": (['lon', 'lat'], data)},
        coords={"lon": lons, "lat": lats}
    )
    if region != 'global':
        ds = clip_region(ds, grid=grid_id, region=region)
    return ds


def get_grid(grid, base="base180"):
    """Get the longitudes, latitudes and grid size for a given global grid.

    Args:
        grid (str): The resolution to get the grid for. One of:
            - global1_5: 1.5 degree global grid
            - global0_25: 0.25 degree global grid
            - salient0_25: 0.25 degree Salient global grid
        base (str): The base grid to use. One of:
            - base360: 360 degree base longitude grid
            - base180: 180 degree base longitude grid
    """
    if grid == "global1_5":
        grid_size = 1.5
        offset = 0.0
    elif grid == "chirps":
        grid_size = 0.05
        offset = 0.025
    elif grid == "imerg":
        grid_size = 0.1
        offset = 0.05
    elif grid == "global0_25":
        grid_size = 0.25
        offset = 0.0
    elif grid == "global0_1":
        grid_size = 0.1
        offset = 0.0
    elif grid == "salient0_25":
        grid_size = 0.25
        offset = 0.125
    else:
        raise NotImplementedError(
            f"Grid {grid} has not been implemented.")

    # Instantiate the grid
    lons = np.arange(-180.0+offset, 180.0, grid_size)
    eps = 1e-6  # add a small epsilon to the end of the grid to enable poles for lat
    lats = np.arange(-90.0+offset, 90.0+eps, grid_size)
    if base == "base360":
        lons = base180_to_base360(lons)
        lons = np.sort(lons)

    # Round the longitudes and latitudes to the nearest 1e-5 to avoid floating point precision issues
    return lons, lats, grid_size, offset


def base360_to_base180(lons):
    """Converts a list of longitudes from base 360 to base 180.

    Args:
        lons (list, float): A list of longitudes, or a single longitude
    """
    if not isinstance(lons, np.ndarray) and not isinstance(lons, list):
        lons = [lons]
    val = [x - 360.0 if x >= 180.0 else x for x in lons]
    if len(val) == 1:
        return val[0]
    return np.array(val)


def base180_to_base360(lons):
    """Converts a list of longitudes from base 180 to base 360.

    Args:
        lons (list, float): A list of longitudes, or a single longitude
    """
    if not isinstance(lons, np.ndarray) and not isinstance(lons, list):
        lons = [lons]
    val = [x + 360.0 if x < 0.0 else x for x in lons]
    if len(val) == 1:
        return val[0]
    return np.array(val)


def is_wrapped(lons):
    """Check if the longitudes are wrapped.

    Works for both base180 and base360 longitudes. Requires that
    longitudes are in increasing order, outside of a wrap point.
    """
    wraps = (np.diff(lons) < 0.0).sum()
    if wraps > 1:
        raise ValueError("Only one wrapping discontinuity allowed.")
    elif wraps == 1:
        return True
    return False


def check_bases(ds, dsp, lon_col='lon', lon_colp='lon'):
    """Check if the bases of two datasets are the same."""
    if ds[lon_col].max() > 180.0:
        base = "base360"
    elif ds[lon_col].min() < 0.0:
        base = "base180"
    else:
        # Dataset base is ambiguous
        logger.info('Performing spatial data on a subset of data. Cannot check if longitude convention matches.'
                    'Please ensure that your dataframes are using the same longitude convention.')
        return 0

    if dsp[lon_colp].max() > 180.0:
        basep = "base360"
    elif dsp[lon_colp].min() < 0.0:
        basep = "base180"
    else:
        logger.info('Performing spatial data on a subset of data. Cannot check if longitude convention matches.'
                    'Please ensure that your dataframes are using the same longitude convention.')
        return 0

    # If bases are identifiable and unequal
    if base != basep:
        return -1
    return 0
