# ruff: noqa: E501 <- line too long
"""Region definitions for the Sheerwater Benchmarking project.

The regions are defined as follows:
- admin_level_x: Administrative level x boundaries
    - Available admin levels: 0 (national), 1 (region), 2 (county), 3 (subcounty)
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


def clean_name(name):
    """Clean a name to make matching easier."""
    return name.lower().replace(' ', '_')


# A set of standard regions that are above the nationional level - defined by the UN or WB
super_national_regions = ['country', 'continent', 'subregion', 'region_un', 'region_wb']
# A set of standard regions that are below the nationional level - defined by the admin level
sub_national_regions = ['admin_level_1', 'admin_level_2']

# Additionally, allow the construction of custom regions by country list or lat / lon bounding box
custom_regions = {
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


# By enabling caching this can be cached locally
@cache()
def country_gdf():
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

# By enabling caching this can be cached locally


@cache(cache_args=['admin_level'])
def admin_level_gdf(admin_level=2):
    """Get the admin level GeoDataFrame."""
    # World geojson downloaded from https://geojson-maps.kyd.au
    filepath = f'gs://sheerwater-public-datalake/regions/ken_admin{admin_level}.geojson'
    admin_level_gdf = gpd.read_file(load_object(filepath))
    admin_level_gdf['admin_name'] = admin_level_gdf[f'adm{admin_level}_name'].apply(clean_name)
    return admin_level_gdf


def get_region_level(region):
    """Get the level of a region and the regions at that level."""
    if region is None:
        region = 'global'

    country_data = country_gdf(memoize=True)  # country data and all super national regions
    admin_data = {x: admin_level_gdf(admin_level=x, memoize=True) for x in [1, 2]}

    # First, check if region is one of our conglomerate regions
    for level in super_national_regions:
        if region == level:
            regions = country_data[level].unique()
            return level, regions
    for i, level in enumerate(sub_national_regions):
        if region == level:
            regions = admin_data[i+1]['admin_name'].unique()
            return level, regions
    for level, data in custom_regions.items():
        if region == level:
            regions = data.keys()
            return level, regions

    # If region is a specific instance, we must check within each datasource
    for level in super_national_regions:
        if region in country_data[level].unique():
            return level, [region]
    for i, level in enumerate(sub_national_regions):
        if region in admin_data[i+1]['admin_name'].unique():
            return level, [region]
    for level, data in custom_regions.items():
        if region in data.keys():
            return level, [region]

    # If we still haven't found the region, it's not a valid region
    raise ValueError(f"Region {region} not found")


def region_data(region):
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
    country_data = country_gdf(memoize=True)
    admin_data = {x: admin_level_gdf(admin_level=x, memoize=True) for x in [1, 2]}
    region_level, regions = get_region_level(region)

    # Form the GeoDataFrame for the region
    region_names = []
    region_geometries = []
    for reg in regions:
        if region_level in super_national_regions:
            # Handle standard regions
            region_names.append(reg)
            geometry = country_data[country_data[region_level] == reg].geometry.union_all()
            region_geometries.append(geometry)
        elif region_level in sub_national_regions:
            # Handle admin level regions
            region_names.append(reg)
            admin_level = int(region_level.split('_')[-1])
            geometry = admin_data[admin_level][admin_data[admin_level]['admin_name'] == reg].geometry.values[0]
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
                region_gdf = country_data[country_data['country'].isin(countries)]
                if len(countries) != len(region_gdf):
                    raise ValueError(
                        f"Some countries were not found: {set(countries) - set(region_gdf['country'])}")
                geometry = region_gdf.geometry.union_all()
                region_names.append(reg)
                region_geometries.append(geometry)
            else:
                raise ValueError(f"Poorly formatted custom region entry: {data}")

    import pdb; pdb.set_trace()
    gdf = gpd.GeoDataFrame({'region_name': region_names, 'region_geometry': region_geometries})
    gdf = gdf.set_geometry("region_geometry")
    gdf = gdf.set_crs("EPSG:4326")
    return gdf


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
