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
from shapely.geometry import box, GeometryCollection
import rioxarray  # noqa: F401 - needed to enable .rio attribute

from .rainfall_regions import get_rainfall_regions
from nuthatch import cache
from sheerwater.utils import get_grid_ds, regrid, load_object

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
            'countries': ['kenya', 'ethiopia', 'tanzania', 'uganda', 'somalia', 'eritrea', 'south_sudan', 'rwanda', 'burundi', 'djibouti', 'somaliland'],
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


@cache(cache_args=['level', 'merged'])
def polygon_subdivision_geodataframe(level, merged=True):
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
        merged(bool): Whether to merge the countries into a single geometry.
            If True, the countries are merged into a single geometry.
            If False, the countries are kept as separate geometries. Default is True.

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
            if merged:
                geometry = region_gdf.geometry.union_all()
            else:
                geometry = GeometryCollection(list(region_gdf.geometry.values))
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
                if merged:
                    geometry = region_gdf.geometry.union_all()
                else:
                    geometry = GeometryCollection(list(region_gdf.geometry.values))
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

    # Create a copy of the region data for assignments
    region_data = ds['region'].copy()

    # Loop through each region and label grid cells
    for i, rn in gdf.iterrows():
        print(i + 1, '/', len(gdf.region_name), rn.region_name)
        # Clip the grid to the boundary of Shapefile
        world_ds = xr.full_like(ds.lat * ds.lon, 1.0, dtype=np.float32)
        world_ds = world_ds.rio.write_crs("EPSG:4326")
        world_ds = world_ds.rio.set_spatial_dims('lon', 'lat')
        region_ds = world_ds.rio.clip(rn, gdf.crs, drop=False)
        region_mask = ~region_ds.isnull()
        region_data = xr.where(region_mask, rn.region_name, region_data)

    ds['region'] = region_data
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


@cache(cache_args=['grid'], backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
def rainfall_region_labels(grid='global0_25'):
    """Gridded rainfall-regime labels for east and west Africa nimbus regions.

    Args:
        grid (str): spatial resolution of regions.

    Returns:
        xarray.Dataset: dataset with a string ``region`` coordinate per lat/lon.
    """
    from .utils import regrid_region_masks
    def masks_to_labels(masks, idx2names):
        labels = xr.DataArray(
            np.full((len(masks.lat), len(masks.lon)), "", dtype=object),
            coords={"lat": masks.lat, "lon": masks.lon},
            dims = ["lat", "lon"],
            name = "rainfall_region"
        )
        for region in masks.region.values:
            name = idx2names[region]
            labels = xr.where(masks.sel(region=region).masks.data, name, labels)
        labels = labels.where(labels != "", "no_region")
        labels = labels.to_dataset(name="region").set_coords("region")
        return labels

    rr_east = get_rainfall_regions(
            data_source="imerg_final",
            kregions=5,
            region="nimbus_east_africa",
            grid='global0_25',
            mask="lsm",
            agg_days=1,
            smooth_neighbors=50,
            spatial_coherence=5.0,
    )
    rr_west = get_rainfall_regions(
            data_source="imerg_final",
            kregions=4,
            region="nimbus_west_africa",
            grid='global0_25',
            mask="lsm",
            agg_days=1,
            smooth_neighbors=50,
            spatial_coherence=5.0,
    )
    rr_west = rr_west.assign_coords(region=rr_west.region + rr_east.region.size)
    rr_east_west = xr.concat([rr_east, rr_west], dim="region")
    if grid != 'global0_25':
        rr_east_west = regrid_region_masks(rr_east_west, output_grid=grid)


    rr_names = {# east africa
                0 : "east_africa_sudanian",
                1 : "east_africa_lake_victoria_basin",
                2 : "east_africa_coastal_savannah",
                3 : "east_africa_west_ethiopian_highlands",
                4 : "east_africa_coastal_horn",
                # west africa
                5 : "west_africa_western_sahel",
                6 : "west_africa_eastern_sahel",
                7 : "west_africa_sudanian",
                8 : "west_africa_coastal"
                }

    rr_labels = masks_to_labels(rr_east_west, rr_names)
    rr_labels['region'] = rr_labels['region'].astype('U40')
    return rr_labels


@cache(cache_args=['grid'], backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
def season_region_labels(grid='global0_25'):
    """Return space labels for each seasonal grouping."""
    ds = rainfall_region_labels(grid)
    season_regions = xr.where(ds.coords["region"].isin(['east_africa_coastal_horn',
                                                         'east_africa_west_ethiopian_highlands']),
                               'africa_bimodal_season', ds.coords["region"])

    ds = ds.assign_coords(region=season_regions)

    season_regions = xr.where(ds.coords["region"].isin(['east_africa_sudanian',
                                                          'west_africa_coastal',
                                                          'west_africa_western_sahel',
                                                          'west_africa_eastern_sahel',
                                                          'west_africa_sudanian']),
                              'africa_unimodal_season', ds.coords["region"])
    ds = ds.assign_coords(region=season_regions)

    season_regions = xr.where(ds.coords["region"].isin(['east_africa_coastal_savannah']),
                              'africa_unimodal_shifted_season', ds.coords["region"])
    ds = ds.assign_coords(region=season_regions)


    season_regions = xr.where(ds.coords["region"].isin(['africa_unimodal_season', 'africa_bimodal_season',
                                                        'africa_unimodal_shifted_season']),
                               ds.coords["region"], "no_region")

    ds = ds.assign_coords(region=season_regions)

    ds['region'] = ds['region'].astype('U40')
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
    'agroecological_zone': [agroecological_subdivision_labels, None],
    # Custom regions with similar rainy season patterns in nimbus regions of interest
    'rainfall_region': [rainfall_region_labels, None],
    'season_regions': [season_region_labels, None],
}
