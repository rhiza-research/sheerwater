"""Spatial grouping and masking functionality for Sheerwater."""
# ruff: noqa: E501 <- line too long, ignore for the long country list
import gcsfs
from functools import partial
import geopandas as gpd
import pandas as pd
import unicodedata
import logging
import numpy as np
import xarray as xr
import shapely
from shapely.geometry import box
import rioxarray  # noqa: F401 - needed to enable .rio attribute

from nuthatch import cache
from sheerwater.utils import get_grid_ds, regrid, check_bases, load_object

import warnings
from rasterio.errors import ShapeSkipWarning

warnings.filterwarnings(
    "ignore",
    category=ShapeSkipWarning,
)

# A global dictionary of spatial subdivisions, indexed by subdivision name
# defined at the bottom of this file
global spatial_subdivisions


logger = logging.getLogger(__name__)

##############################################################################
# Utility functions for spatial subdivisions
##############################################################################


def reconcile_country_name(country_name):
    """Maps a country name variant to its standardized name.

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
        'gambia': 'the_gambia',

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

        # Virgin Islands variants
        'virgin_islands,_u.s.': 'virgin_islands',

        # US variants
        'united_states': 'united_states_of_america',

        # Falkland Islands variants
        'falkland_islands_(uk)': 'falkland_islands',

        # Palestine variants
        'gaza_strip': 'palestine',
        'west_bank': 'palestine',
    }

    # First check if it has a standardization mapping
    if country_name in standardization_map:
        return standardization_map[country_name]
    else:
        return country_name


def clean_spatial_subdivision_name(name):
    """Clean a spatial subdivision name to make matching easier and replace non-English characters."""
    name = str(name)  # convert to string
    if name in [None, 'none', 'None', '', '_', '-', '-_', ' ']:
        return 'no_region'
    name = name.lower().replace(' ', '_').strip()
    name = name.replace('&', 'and')
    # Normalize unicode string to remove accents, e.g., 'são_tomé_and_príncipe' -> 'sao_tome_and_principe'
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')

    # If region is country data, reconcile the name
    name = reconcile_country_name(name)
    return name


@cache(cache_args=['admin_level'])
def admin_level_gdf_legacy(admin_level=2):
    """A datasoruce of administrative boundaries at a given level.

    Args:
        admin_level(int): The admin level to get the data for. Must be
            an admin level(e.g., 0, 1, 2).

    Returns:
        gdf(gpd.GeoDataFrame): A GeoDataFrame for the admin level, with columns:
            - 'admin_name': the name of the admin level,
            - 'geometry': its geometry as a shapely object.
    """
    # World geojson downloaded from https://www.geoboundaries.org/globalDownloads.html
    if admin_level not in [0, 1, 2]:
        raise ValueError(f"Invalid admin level: {admin_level}")
    filepath = f'gs://sheerwater-public-datalake/regions/geoBoundariesCGAZ_ADM{admin_level}.geojson'
    df = gpd.read_file(load_object(filepath))
    df['admin_name'] = df['shapeName'].apply(clean_spatial_subdivision_name)
    return df


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
    if admin_level not in [0, 1, 2]:
        raise ValueError(f"Invalid admin level: {admin_level}")

    if admin_level == 0:
        # This low res admin 0 does not contain cape verde, for example
        # path = 'gs://sheerwater-public-datalake/regions/low_res_admin_0.geojson'
        # Use this source instead for countries
        path = 'gs://sheerwater-public-datalake/regions/world_50m.geojson'
        df = gpd.read_file(load_object(path))
        df['admin_name'] = df['name_en'].apply(clean_spatial_subdivision_name)
        return df

    # Otherwise, read from the admin-boundaries/lo-res directory
    # Note that this data source does not contain cape verde, for example
    dir = {
        1: 'Admin1_simp10',
        2: 'Admin2_simp05',
    }
    path = f'gs://sheerwater-public-datalake/regions/admin-boundaries/lo-res/{dir[admin_level]}'

    fs = gcsfs.GCSFileSystem(project='sheerwater', token='google_default')
    files = fs.ls(path)
    dfs = []
    for file in files:
        sub = gpd.read_file(load_object(file))
        if 'Name' in sub:
            # There is an inconsistency in the original datasource where the column
            # is labeled 'Name' instead of 'NAME_0'
            sub = sub.rename(columns={'Name': 'NAME_0'})

        if 'GID_0' in sub and str((sub['GID_0'].iloc[0])) == 'MCO':
            # Fix an error in the origional datasource where MCO is labeled as Macao, instead of Monaco
            sub['NAME_0'] = 'Monaco'
        dfs.append(sub)
    # Concat geopandas dataframes
    df = gpd.GeoDataFrame(pd.concat(dfs, ignore_index=True))
    df = df.set_geometry('geometry')

    # Clean and construct 'admin_name' according to admin level
    df['clean0'] = df['NAME_0'].apply(clean_spatial_subdivision_name)
    if admin_level == 0:
        df['admin_name'] = df['clean0']
    if admin_level == 1:
        df['clean1'] = df['NAME_1'].apply(clean_spatial_subdivision_name)
        df['admin_name'] = df['clean0'] + '-' + df['clean1']
    elif admin_level == 2:
        df['clean1'] = df['NAME_1'].apply(clean_spatial_subdivision_name)
        df['clean2'] = df['NAME_2'].apply(clean_spatial_subdivision_name)
        df['admin_name'] = df['clean0'] + '-' + df['clean1'] + '-' + df['clean2']
    return df


@cache()
def multinational_gdf():
    """A datasource that maps countries to their global administrative regions."""
    # World geojson downloaded from https://geojson-maps.kyd.au
    filepath = 'gs://sheerwater-public-datalake/regions/world_50m.geojson'
    country_gdf = gpd.read_file(load_object(filepath))
    country_gdf = country_gdf[['name_en', 'continent', 'region_un', 'subregion', 'region_wb', 'geometry']]
    # Clean string columns for consistent, lowercase, and underscore-separated names
    for col in ["name_en", "continent", "region_un", "subregion", "region_wb"]:
        cleaned_col = "country" if col == "name_en" else col
        country_gdf[cleaned_col] = country_gdf[col].apply(clean_spatial_subdivision_name)
    return country_gdf


# Define the custom regions, allow the construction of custom regions by country list or lat / lon bounding box
custom_subdivisions_definitions = {
    'sheerwater_region': {
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


@cache(cache_args=['level'])
def polygon_subdivision_geodataframe(level):
    """Get the boundary geodatarame for a given subdivision level defined by a set of polygons.

    Supports the following levels:
    1. Multinational subdivisions: 'continent', 'subregion', 'region_un', 'region_wb'
        - Defined by multinational_gdf(), from the World Bank / UN datasources
        - Each region is composed of a set of coutries, which are selected and their geometry is unioned to form a region geometry
    2. Subnational subdivisions: 'country', 'admin_1', 'admin_2' - defined by the admin level
        - Defined by admin_level_gdf(), from the admin-boundaries/lo-res datasource
        - Each region is compsed of a single geometry, selected from the admin level dataframe
    3. Custom regions defined by polygon boundaries: 'sheerwater_region', 'meteorological_zone', 'hemisphere', 'global'
        - Defined in the dictionary custom_subdivisions_definitions
        - Each region is composed either of a set of countries, or a lat/lon bounding box. The countries are selected from
          source (2) above and unioned to form a region geometry, or the lat/lon bounding box is converted to a rectangular Polygon.

    Args:
        level(str): The level to get the data for . Must be
            a level(e.g., 'country', 'admin_1', 'continent', 'meteorological_zone')

    Returns:
        gdf(gpd.GeoDataFrame): A GeoDataFrame for the level, with columns:
            - 'region_name': the name of the region,
            - 'region_geometry': its geometry as a shapely object.
    """
    if level in ['country', 'admin_1', 'admin_2']:
        # Get all region objects in the regions list
        if level == 'country':
            admin_level = 0
        else:
            admin_level = int(level.split('_')[-1])
        gdf = admin_level_gdf(admin_level)
        gdf = gdf[['admin_name', 'geometry']]
        gdf = gdf.rename(columns={
            'admin_name': 'region_name',
            'geometry': 'region_geometry',
        })
    elif level in ['continent', 'subregion', 'region_un', 'region_wb']:
        # Need to merge the countries invovled in a global region into a single geometry
        # Need to use the global regions df here, otherwise there are gaps in the
        # geometry coverage.
        country_gdf = multinational_gdf()

        def multinational_subdivisions_to_countries(df, subdivision):
            """A local helper to map each multinational subdivision to a list of countries."""
            vals = {}
            multinational_regions = set(df[subdivision])
            for val in multinational_regions:
                countries = df[df[subdivision] == val]['country']
                countries = [x for x in countries if x != 'no_region']
                vals[val] = set(countries)
            return vals
        subdivision_to_countries = multinational_subdivisions_to_countries(country_gdf, level)
        region_names = []
        region_geometries = []
        regions = subdivision_to_countries.keys()
        for reg in regions:
            countries = subdivision_to_countries[reg]
            region_gdf = country_gdf[country_gdf['country'].isin(countries)]
            geometry = region_gdf.geometry.union_all()
            region_names.append(reg)
            region_geometries.append(geometry)
        gdf = gpd.GeoDataFrame({'region_name': region_names, 'region_geometry': region_geometries})
    elif level in custom_subdivisions_definitions.keys():
        # Custom regions are defined by a list of countries or a lat/lon bounding box
        # Need to merge the countries invovled in a custom region into a single geometry
        admin_0 = admin_level_gdf(admin_level=0)
        region_names = []
        region_geometries = []
        regions = custom_subdivisions_definitions[level].keys()
        for reg in regions:
            data = custom_subdivisions_definitions[level][reg]
            if 'lats' in data and 'lons' in data:
                # Create a shapefile (GeoDataFrame) from lat/lon boundaries as a rectangular Polygon
                tol = 0.005
                lons = data['lons']
                lats = data['lats']
                region_box = box(lons[0] - tol, lats[0] - tol, lons[1] + tol, lats[1] + tol)
                region_names.append(reg)
                region_geometries.append(region_box)
            elif 'countries' in data:
                countries = [clean_spatial_subdivision_name(country) for country in data['countries']]
                region_gdf = admin_0[admin_0['admin_name'].isin(countries)]
                if len(countries) != len(region_gdf):
                    raise ValueError(
                        f"Some countries were not found: {set(countries) - set(region_gdf['admin_name'])}")
                geometry = region_gdf.geometry.union_all()
                region_names.append(reg)
                region_geometries.append(geometry)
            else:
                raise ValueError(f"Poorly formatted custom region entry: {data}")
        gdf = gpd.GeoDataFrame({'region_name': region_names, 'region_geometry': region_geometries})
    else:
        raise ValueError(f"Invalid region level: {level}")

    # Set the geometry and CRS
    gdf = gdf.set_geometry("region_geometry")
    gdf = gdf.set_crs("EPSG:4326")
    return gdf

##############################################################################
# The fundamental functions that define gridded spatial subdivision datasets
##############################################################################


@cache(cache_args=['grid', 'level'],
       backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
def polygon_subdivision_labels(grid='global1_5', level='country'):
    """Generate a gridded dataset with a region coordinate at a specific polygon subdivision level.

    Args:
        grid(str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.
        level(str): A polygon subdivision level, one of the supported levels from
            polygon_subdivision_geodataframe() above

    Returns:
        xarray.Dataset: A gridded dataset with a region coordinate at the specified polygon subdivision level.
    """
    # Get a geopandas dataframe for the specific subnational level
    gdf = polygon_subdivision_geodataframe(level)

    # Get the grid dataframe
    ds = get_grid_ds(grid)
    # Assign a dummy region coordinate to all grid cells
    # Fixed data type of strings of length 40
    ds = ds.assign_coords(region=(('lat', 'lon'), xr.full_like(ds.lat * ds.lon, 'no_region', dtype='U40').data))

    # If admin group, construct the admin gridded dataframe
    # Loop through each region and label grid cells
    for i, rn in gdf.iterrows():
        print(i+1, '/', len(gdf.region_name), rn.region_name)
        # Clip the grid to the boundary of Shapefile
        world_ds = xr.full_like(ds.lat * ds.lon, 1.0, dtype=np.float32)
        #  Add geometry to the dataframe and clip
        world_ds = world_ds.rio.write_crs("EPSG:4326")
        world_ds = world_ds.rio.set_spatial_dims('lon', 'lat')
        region_ds = world_ds.rio.clip(rn, gdf.crs, drop=False)
        # Assign the region name to the region coordinate
        ds['region'] = xr.where(~region_ds.isnull(), rn.region_name, ds['region'])
    return ds


# zone labels from https://data.apps.fao.org/catalog/dataset/0bb7237a-6740-4ea3-b2a1-e26b1647e4e0
agroecological_zone_names = {
    0: "No region",
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


@cache(cache_args=['grid'], backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
def agroecological_subdivision_labels(grid='global1_5'):
    """Get the agroecological zones as an xarray dataset."""
    # Downloaded from https://data.apps.fao.org/catalog/iso/9a9ed6cf-83cc-4b42-b295-305184d3f0b8
    tif_path = 'gs://sheerwater-public-datalake/regions/agroecological_zones.tif'
    ds = xr.open_dataset(load_object(tif_path), engine='rasterio')
    ds = ds.rename({'x': 'lon', 'y': 'lat'})
    ds = ds.squeeze('band').drop(['band', 'spatial_ref'])
    ds = ds.rename_vars({'band_data': 'agroecological_zone'})

    # Fill Nas with mostly water label
    da = ds.agroecological_zone.fillna(33)
    da = da.astype(np.int32)

    # Sort latitude and longitude values in descending order
    # NEED TO DO THIS OR REGRIDDING WILL FAIL
    da = da.sortby('lat', ascending=True)
    da = da.sortby('lon', ascending=True)

    da = regrid(da, grid, base='base180', method='most_common', regridder_kwargs={
                'values': np.unique(da.values), 'fill_value': 33})
    ds = da.to_dataset(name='region')

    # Convert back to integer
    ds['region'] = ds['region'].astype(np.int32)

    def map_labels(x):
        """Convert the agroecological zone number to a name."""
        try:
            x = int(x)
        except ValueError:
            return "no_region"
        name = agroecological_zone_names.get(x, "no_region")
        name = name.replace('; ', '_').replace(', ', '_').replace(' ', '_').lower().strip()
        return name

    # Vectorized mapping function
    vectorized_map = np.vectorize(map_labels)

    # Apply to your DataArray
    ds['region'] = xr.apply_ufunc(
        vectorized_map,
        ds['region'],
        vectorize=True
    )

    # Convert variables to a coordinate
    ds = ds.set_coords('region')
    return ds


##############################################################################
# The final spatial subdivision interface
##############################################################################


@cache(memoize=True, cache_args=['grid'])
def spatial_subdivision_regions(grid='global0_25'):
    """A dictionary containing all the regions for each spatial subdivision for quick look up.

    # TODO: could divide by level and perhaps quieried in order of size to make as fast as possible?
    """
    vals = {}
    for subdivision in spatial_subdivisions.keys():
        if spatial_subdivisions[subdivision][1] is not None:
            # If the subdivision is a geometry region, get the regions from the geometry
            gdf = spatial_subdivisions[subdivision][1]()
            vals[subdivision] = np.unique(gdf['region_name'].values)
        else:
            # If the subdivision is a gridded region, get the regions from the grid
            try:
                df = spatial_subdivisions[subdivision][0](grid=grid)
                vals[subdivision] = np.unique(df['region'].values)
            except NotImplementedError:
                vals[subdivision] = []
                warnings.warn(f"No regions found for {subdivision} on grid {grid}")
    return vals


def get_spatial_subdivision_level(name, grid='global0_25'):
    """For a given spatial subdivision, return the level of that spatial subdivision.

    Args:
        name(str): The spatial subdivision to get the level of. Can either be a spatial subdivision name
            or a specific region within that spatial subdivision.
            e.g., both 'country' and 'indonesia' are valid region arguments.
        grid(str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.

    Returns:
        level(str): The level of the spatial subdivision.
        promoted(int): An indictor of whether the subdivision is promoted to a higher level.
            -1: for global, not promoted
            0: for already a subdivision, not promoted
            1: for a specific region, promoted to a higher level
    """
    if name is None or name == 'global':
        return 'global', -1

    name = clean_spatial_subdivision_name(name)

    # If name is already a high level spatial subdivision, just return that value
    if name in spatial_subdivisions.keys():
        return name, 0

    # First, check the polygon subdivisions
    vals = spatial_subdivision_regions(grid=grid)
    for subdivision, regions in vals.items():
        if name in regions:
            return subdivision, 1

    raise ValueError(f"Invalid spatial subdivision: {name}")


@cache(cache_args=['grid', 'space_grouping'], memoize=True,
       backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
def space_grouping_labels(grid='global1_5', space_grouping='country'):
    """Generate a gridded dataset with a region coordinate at a specific spatial subdivision.

    Args:
        grid(str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.
        space_grouping(str or list): Region grouping(s):
            - A string for a single grouping: 'country', 'continent', 'subregion', etc.
            - A list for multiple groupings: ['country'], ['admin_1', 'agroecological_zone'], etc.

    Returns:
        xarray.Dataset: Dataset with added region coordinate
    """
    # Convert single string to list (treat as single region, don't split by dashes)
    if space_grouping is None:
        space_grouping = 'global'

    if not isinstance(space_grouping, list):
        space_grouping = [space_grouping]

    for level in space_grouping:
        if level not in spatial_subdivisions.keys():
            raise ValueError(f"Invalid spatial subdivision: {level}")

    # Sort alphabetically to ensure consistent results regardless of input order
    space_grouping = sorted(space_grouping)

    # Compose a list of gridded datasets for each spatial subdivision
    ds_list = []
    ds_coords = []
    for level in space_grouping:
        labels_ds = spatial_subdivisions[level][0](grid=grid)
        labels_ds = labels_ds.rename({'region': f'{level}_region'})
        ds_list.append(labels_ds)
        ds_coords.append(f'{level}_region')

    # Create a a new dataset with the concatonation of all the layers
    ds = xr.merge(ds_list)
    # This pesky spatial_ref coordinate is not needed
    if 'spatial_ref' in ds.coords:
        ds = ds.drop_vars('spatial_ref')

    # Now combine the region coordinates into a single region coordinate
    coords_values = [ds[x].values.flatten() for x in ds_coords]
    combined_region_coords = np.array(['-'.join(vals) for vals in zip(*coords_values)], dtype='U40')
    ds = ds.assign_coords(region=(('lat', 'lon'), combined_region_coords.reshape(ds.lat.size, ds.lon.size)))
    return ds

##############################################################################
# Core clipping / masking utilities
##############################################################################


def clip_region(ds, region, grid, region_dim=None, drop=True, clip_coords=False):
    """Clip a dataset to a region.

    Args:
        ds(xr.Dataset): The dataset to clip to a specific region.
        region(str, list): The region to clip to. A str or list of strs.
        grid(str): The grid to clip to.
        region_dim(str): The name of the region dimension. If None, region data is fetched from the region registry.
        drop(bool): Whether to drop the original coordinates that are NaN'd by clipping.
        clip_coords(bool): Whether to clip the coordinates to the region. Coordinates outside set to NaN.
    """

    if region == 'global' or region is None or 'global' in region:
        return ds

    # get coordinates which contain 'region' in the name
    region_coords = [coord for coord in ds.coords if 'region' in coord]

    if isinstance(region, str) and region != 'global':
        # rename values of region coordinates from 'global' to the region name
        for coord in region_coords:
            ds[coord] = ds[coord].astype(str).str.replace('global', region)

    if ds.lat.size == 0 and ds.lon.size == 0:
        # If the dataset is empty / dimensionless, return it untouched
        return ds

    if not isinstance(region, list):
        region = [region]

    if region_dim is not None:
        # If we already have a region dimension, just select the region
        return ds.where(ds[region_dim] == '-'.join(region), drop=drop)

    # Clean the region names
    region = [clean_spatial_subdivision_name(x) for x in region]

    # Get the high level region for each region in the list
    promoted_levels = []
    for level in region:
        level, promoted = get_spatial_subdivision_level(level, grid=grid)
        if promoted == 0:
            raise ValueError("Must pass a single region into clip_region, not a subdivision.")
        promoted_levels.append(level)

    # Sort the region names by the promoted region levels alphabetically
    sort_idx = np.argsort(promoted_levels)
    promoted_levels = [promoted_levels[i] for i in sort_idx]
    region = [region[i] for i in sort_idx]

    if clip_coords:
        ds = ds.reset_coords(region_coords, drop=False)

    #########################################################
    # Clip to geometry regions
    #########################################################
    clipped_regions = [(i, x) for i, x in enumerate(promoted_levels) if spatial_subdivisions[x][1] is not None]
    if len(clipped_regions) > 1:
        raise ValueError(f"Cannot clip to multiple geometry regions at the same time: {clipped_regions}.")

    if len(clipped_regions) == 1:
        i, region_name = clipped_regions[0]
        region_idx = region[i]
        gdf = spatial_subdivisions[region_name][1]()
        sub = gdf[gdf['region_name'] == region_idx]
        ds = clip_by_geometry(ds, sub.geometry, drop=drop)

    #########################################################
    # Select gridded regions
    #########################################################
    gridded_regions = [(i, x) for i, x in enumerate(promoted_levels) if spatial_subdivisions[x][1] is None]
    if len(gridded_regions) > 0:
        # Prepare string for select of gridded regions
        region_str = '-'.join([region[i] for i, _ in gridded_regions])
        region_ds = space_grouping_labels(space_grouping=promoted_levels, grid=grid)
        region_ds = region_ds.rename({'region': '_clip_region'})
        ds = ds.where((region_ds._clip_region == region_str), drop=False)
        ds = ds.drop_vars('_clip_region')

    if clip_coords:
        ds = ds.set_coords(region_coords)

    return ds


def clip_by_geometry(ds, geometry=None, lon_dim='lon', lat_dim='lat', drop=True):
    """Clip a dataset to a passed geometry.

    This is not used in our pipelines, as it doesn't support regions that are not defined
    by geometries, such as the gridded agroecological zones.

    Args:
        ds (xr.Dataset): The dataset to clip to a specific region.
        geometry (shapely.geometry.Polygon): The geometry to clip to.
        lon_dim (str): The name of the longitude dimension.
        lat_dim (str): The name of the latitude dimension.
        drop (bool): Whether to drop the original coordinates that are NaN'd by clipping.
    """
    # No clipping needed
    if geometry is None:
        return ds

    if ds.lat.size == 0 and ds.lon.size == 0:
        # If the dataset is empty / dimensionless, return it untouched
        return ds

    # check if the dataset has data variables
    if len(ds.data_vars) == 0:
        # Must have a data variable to clip
        ds['mask'] = xr.ones_like(ds.lat * ds.lon, dtype=np.int32)

    if nonuniform_grid(ds):
        ds = clip_with_mask(ds, geometry, drop=drop)
    else:
        # Set up dataframe for clipping
        ds = ds.rio.write_crs("EPSG:4326")
        ds = ds.rio.set_spatial_dims(lon_dim, lat_dim)
        # swap region coordinate to a data variables
        # Clip the grid to the passed geometry
        ds = ds.rio.clip(geometry, geometry.crs, drop=drop)
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
    # No masking needed if mask is None or the dataset is empty / dimensionless
    if mask is None:
        return ds

    if ds.lat.size == 0 and ds.lon.size == 0:
        # If the dataset is empty / dimensionless, return it untouched
        return ds

    if isinstance(mask, str):
        from .masks import spatial_mask
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

    masking_ds = mask_ds['mask'] > val
    if isinstance(var, str):
        # Mask a single variable
        ds[var] = ds[var].where(masking_ds, drop=False)
    else:
        # Mask multiple variables
        ds = ds.where(masking_ds, drop=False)
    return ds


def clip_with_mask(ds, region_df, drop=True):
    """Clip a dataset to a region using a mask.

    Args:
        ds (xr.Dataset): Dataset to clip to a region.
        region_df (geopandas.GeoDataFrame): The region data to clip to.
        drop (bool): Whether to drop the original coordinates that are NaN'd by clipping.
    """
    # create a mask on the ds grid corresponding to the region
    lon2d, lat2d = xr.broadcast(ds.lon, ds.lat)
    mask = xr.zeros_like(lon2d, dtype=bool)

    polygon = region_df.geometry.union_all()
    # the mask can be large; two step filtering will be faster
    # first filter to the bounding box of the region
    lon_min, lat_min, lon_max, lat_max = polygon.bounds
    bmask = (lon2d >= lon_min) & (lon2d <= lon_max) & (lat2d >= lat_min) & (lat2d <= lat_max)
    # then filter to the precise polygon
    mask[bmask] = shapely.intersects_xy(polygon, lon2d[bmask], lat2d[bmask])
    # convert to xarray
    mask = xr.DataArray(mask, dims=("lon", "lat"), coords={"lon": ds.lon, "lat": ds.lat})
    # in a nonuniform grid, automatic dropping gets rid of interior slices in a way that leads
    # to visually strange results. By cropping to the bounding box, we have a better result.
    ds = ds.where(mask, drop=False)
    if drop:
        ds = ds.sel(lon=slice(lon_min, lon_max), lat=slice(lat_min, lat_max))
    return ds


def nonuniform_grid(ds, error_thresh=1e-4):
    """Check if a dataset has a nonuniform grid."""
    lat_deltas = np.diff(ds.lat.values) - np.mean(np.diff(ds.lat.values))
    lon_deltas = np.diff(ds.lon.values) - np.mean(np.diff(ds.lon.values))
    return not (np.allclose(lat_deltas, 0, atol=error_thresh) and np.allclose(lon_deltas, 0, atol=error_thresh))

##################################################################
# Spatial subdivision definitions, including custom regions
# Each spatial subdivision is defined by a tuple of a function that generates a
# gridded dataset with a region coordinate at a specific spatial subdivision,
# and a function that generates a geodataframe for the spatial subdivision. If the
# spatial subdivision is not defined by a set of polygons, the second function is None.
##################################################################
spatial_subdivisions = {
    # A set of standard regions that are above the nationional level - defined by the UN or WB
    'continent': [partial(polygon_subdivision_labels, level='continent'), partial(polygon_subdivision_geodataframe, level='continent')],
    'subregion': [partial(polygon_subdivision_labels, level='subregion'), partial(polygon_subdivision_geodataframe, level='subregion')],
    'region_un': [partial(polygon_subdivision_labels, level='region_un'), partial(polygon_subdivision_geodataframe, level='region_un')],
    'region_wb': [partial(polygon_subdivision_labels, level='region_wb'), partial(polygon_subdivision_geodataframe, level='region_wb')],
    # Custom regions defined by polygon boundaries
    'sheerwater_region': [partial(polygon_subdivision_labels, level='sheerwater_region'), partial(polygon_subdivision_geodataframe, level='sheerwater_region')],
    'meteorological_zone': [partial(polygon_subdivision_labels, level='meteorological_zone'), partial(polygon_subdivision_geodataframe, level='meteorological_zone')],
    'hemisphere': [partial(polygon_subdivision_labels, level='hemisphere'), partial(polygon_subdivision_geodataframe, level='hemisphere')],
    'global': [partial(polygon_subdivision_labels, level='global'), partial(polygon_subdivision_geodataframe, level='global')],
    # A set of standard regions that are below the nationional level - defined by the admin level
    # admin level 0 is the same as country, but we include it for consistency
    'country': [partial(polygon_subdivision_labels, level='country'), partial(polygon_subdivision_geodataframe, level='country')],
    'admin_1': [partial(polygon_subdivision_labels, level='admin_1'), partial(polygon_subdivision_geodataframe, level='admin_1')],
    'admin_2': [partial(polygon_subdivision_labels, level='admin_2'), partial(polygon_subdivision_geodataframe, level='admin_2')],
    # Custom agroecological zones
    'agroecological_zone': [agroecological_subdivision_labels, None]
}
