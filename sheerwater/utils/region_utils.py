# ruff: noqa: E501 <- line too long
"""Region definitions for the Sheerwater Benchmarking project.

The regions are defined as follows:
- admin_level_x: Administrative level x boundaries
    - Available admin levels: 1 (region), 2 (county)
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
import os

import geopandas as gpd
from shapely.geometry import box

from nuthatch import cache

from .general_utils import load_object


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


def clean_name(name):
    """Clean a name to make matching easier and replace non-English characters."""
    import unicodedata

    # unsupported region names
    if name in [None, '', '_', '-', '-_', ' ']:
        return 'no_region'
    name = name.lower().replace(' ', '_').strip()
    name = name.replace('&', 'and')
    # Normalize unicode string to remove accents, e.g., 'são_tomé_and_príncipe' -> 'sao_tome_and_principe'
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
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
    # elif country_name in unsupported_regions:
        # return 'no_region'
    # Otherwise keep as-is (assumed to be a recognized country)
    else:
        return country_name


@cache()
def global_regions_gdf():
    """Get the country GeoDataFrame."""
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
    """A dictionary mapping global regions to countries.

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
    """Get the admin level GeoDataFrame."""
    filepath = f'gs://sheerwater-public-datalake/regions/geoBoundariesCGAZ_ADM{admin_level}.geojson'
    df = gpd.read_file(load_object(filepath))
    df['admin_name'] = df['shapeName'].apply(clean_name)
    return df


@cache()
def region_levels_and_labels():
    """A dictionary of region levels and their labels, as small as possible to enable fast lookup."""
    labels_dict = {}
    # Populate all admin level regions
    for region in admin_level_regions:
        sub = admin_level_gdf(admin_level=int(region.split('_')[-1]), recompute=True, cache_mode='overwrite')
        labels_dict[region] = sorted(set(sub['admin_name']))

    # Add all the global regions
    df = global_regions_gdf(recompute=True, cache_mode='overwrite')
    for region in global_regions:
        labels_dict[region] = sorted(set(df[region]))
    return labels_dict


def get_region_level(region):
    """For a given region, return which level that region is at and all regions at that level.

    If the region is a specific instance of a region level, return the level and only
        that region instance.

    Args:
        region (str): The region to get the level of.

    Returns:
        level (str): The level of the region.
        regions (list): All regions at that level.
    """
    if region is None:
        return 'global', ['global']

    # Iterate through the standard regions dicts
    # Will return the first level that the region is found at
    labels_dict = region_levels_and_labels()
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
        return 'agroecological_zone', ['agroecological_zone']
    else:
        raise ValueError(f"Invalid region: {region}")


@cache(cache_args=['region_level'])
def full_region_data(region_level):
    """Get the boundary shapefile for a given region level.

    Args:
        region_level (str): The region level to get the data for. Must be
            a region level (e.g., 'countries', 'admin_level_1')

    Returns:
        gdf (gpd.GeoDataFrame): A GeoDataFrame for the region, with columns:
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
        # Need to use the global regions df here, otherwise there are gaps in the
        # geometry coverage.
        country_gdf = global_regions_gdf()
        global_mapping = global_regions_to_country()
        region_names = []
        region_geometries = []
        regions = region_levels_and_labels()[region_level]
        for reg in regions:
            countries = global_mapping[region_level][reg]
            region_gdf = country_gdf[country_gdf['country'].isin(countries)]
            geometry = region_gdf.geometry.union_all()
            region_names.append(reg)
            region_geometries.append(geometry)
        gdf = gpd.GeoDataFrame({'region_name': region_names, 'region_geometry': region_geometries})
    elif region_level in custom_regions:
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


def region_data(region):
    """Get geopandas GeoDataFrame with the geometry for a given region.

    Args:
        region (str): The region to get the data for. Must be
            a region level (e.g., 'countries', 'admin_level_1') or a specific region within that level (e.g., 'indonesia', 'kenya').
            For example, both 'countries' and 'indonesia' are valid region arguments.

    Returns:
        gdf (geopandas.GeoDataFrame): A GeoDataFrame for the region, with columns:
            - 'region_name': the name of the region,
            - 'region_geometry': its geometry as a shapely object.
    """
    region_level, regions = get_region_level(region)
    full_data = full_region_data(region_level)
    return full_data[full_data['region_name'].isin(regions)]


def to_name(name):
    """Convert a name to a more readable format."""
    if name == 'mae':
        return 'Mean Absolute Error'
    elif name == 'mse':
        return 'Mean Squared Error'
    elif name == 'rmse':
        return 'Root Mean Squared Error'
    elif name == 'bias':
        return 'Bias'
    elif name == 'crps':
        return 'Continuous Ranked Probability Score'
    elif name == 'brier':
        return 'Brier Score'
    elif name == 'smape':
        return 'Symmetric Mean Absolute Percentage Error'
    elif name == 'mape':
        return 'Mean Absolute Percentage Error'
    elif name == 'seeps':
        return 'Spatial Error in Ensemble Prediction Scale'
    elif 'heidke' in name:
        return f'Heidke Skill Score at {", ".join([mm.split("-")[-1] for mm in name.split("-")[:-1]])} mm'
    elif 'pod' in name:
        return f'Probability of Detection at {name.split("-")[-1]} mm'
    elif 'far' in name:
        return f'False Alarm Rate at {name.split("-")[-1]} mm'
    elif 'ets' in name:
        return f'Equitable Threat Score at {name.split("-")[-1]} mm'
    elif 'csi' in name:
        return f'Critical Success Index at {name.split("-")[-1]} mm'
    elif 'frequency_bias' in name:
        return f'Frequency Bias at {name.split("-")[-1]} mm'
    elif name == 'acc':
        return 'Anomaly Correlation Coefficient'
    elif name == 'pearson':
        return 'Pearson Correlation'
    else:
        return name


def bounds(variable):
    """Get the bounds for a variable."""
    if variable == 'mae':
        return (0.0, None)
    elif variable == 'mse':
        return (0.0, None)
    elif variable == 'rmse':
        return (0.0, None)
    elif variable == 'bias':
        return (None, None)
    elif variable == 'crps':
        return (0.0, None)
    elif variable == 'brier':
        return (0.0, None)
    elif variable == 'smape':
        return (0.0, None)
    elif variable == 'mape':
        return (0.0, None)
    elif variable == 'seeps':
        return (0.0, 3.0)
    elif 'heidke' in variable:
        return (0.0, 1.0)
    elif 'pod' in variable:
        return (0.0, 1.0)
    elif 'far' in variable:
        return (0.0, 1.0)
    elif 'ets' in variable:
        return (0.0, 1.0)
    elif 'csi' in variable:
        return (0.0, 1.0)
    elif 'frequency_bias' in variable:
        return (None, None)
    elif variable == 'acc':
        return (-1.0, 1.0)
    elif variable == 'pearson':
        return (-1.0, 1.0)
    elif variable == 'coverage':
        return (0.0, None)
    else:
        return (None, None)


def plot_by_region(ds, region, variable, file_string='none', title='Regional Map'):
    """Plot a variable from an xarray dataset by region.

    Args:
        ds: xarray DataArray or Dataset with a 'region' coordinate
        region: Region level or specific region name to plot
        variable: Variable name if ds is a Dataset (optional)
        file_string: File path string for saving the plot
        title: Title for the plot

    Returns:
        matplotlib axes object
    """
    import matplotlib.pyplot as plt
    import numpy as np

    # Get the region GeoDataFrame and metric bounds
    gdf = region_data(region)
    # Extract the data values
    try:
        data = ds[variable]
    except KeyError:
        data = ds

    # Convert to numpy array if it's a dask array
    if hasattr(data, 'compute'):
        data = data.compute()

    # Extract values for each region in the GeoDataFrame
    values = []
    for region_name in gdf.region_name:
        try:
            # Select the region and extract the scalar value
            region_value = data.sel(region=region_name)
            # Handle case where selection might still have dimensions
            if region_value.size > 1:
                # If there are multiple values, take the first or mean
                region_value = float(region_value.values.flatten()[0])
            else:
                region_value = float(region_value.values)
            values.append(region_value)
        except (KeyError, ValueError):
            # Region not found in dataset, use NaN
            values.append(np.nan)

    # Add values to GeoDataFrame
    gdf['value'] = values

    # Calculate 95th percentile for vmax (excluding NaNs)
    vmin, vmax = bounds(variable)
    values_array = np.array(values)
    valid_values = values_array[~np.isnan(values_array)]
    if vmin is None:
        vmin = np.percentile(valid_values, 5)
    if vmax is None:
        vmax = np.percentile(valid_values, 95)

    # Reproject to a better projection for world maps (Robinson projection)
    # Robinson is good for world maps, preserves area relationships well
    gdf_projected = gdf.to_crs('ESRI:54030')  # Robinson projection

    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))

    # Plot the choropleth map (without legend, we'll add it manually)
    gdf_projected.plot(column='value', ax=ax, legend=False,
                       cmap='viridis', edgecolor='black', linewidth=0.5,
                       vmin=vmin,
                       vmax=vmax,
                       missing_kwds={'color': 'red', 'edgecolor': 'black'})

    # Create colorbar with same height as plot and larger tick labels
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.1)
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis,
                               norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cax)
    cbar.ax.tick_params(labelsize=12)

    # Remove axis labels (not meaningful in projected coordinates)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Set title
    ax.set_title(title, fontsize=14, pad=10)

    plt.tight_layout()

    # Ensure colorbar height matches plot height exactly
    ax_pos = ax.get_position()
    cax_pos = cax.get_position()
    cax.set_position([cax_pos.x0, ax_pos.y0, cax_pos.width, ax_pos.height])
    # Save
    if not os.path.exists('metric_maps'):
        os.makedirs('metric_maps')
    plt.savefig(f'metric_maps/{variable}_{region}_{file_string}_map.png')
    return ax
