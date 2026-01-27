"""Definitions of region layers and labels for Sheerwater."""
import numpy as np
import xarray as xr
from nuthatch import cache
from sheerwater.utils import (
    get_grid_ds, load_object, regrid,
    admin_region_data, agroecological_zone_names,
    admin_levels_and_labels, get_combined_region_name)
from sheerwater.interfaces import region_layer, spatial

@spatial()
@region_layer(region_layer='admin_region')
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


@spatial()
@region_layer(region_layer='agroecological_zone')
@cache(cache_args=['grid'], backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
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

    # Sort latitude and longitude values in descending order
    # NEED TO DO THIS OR REGRIDDING WILL FAIL
    da = da.sortby('lat', ascending=True)
    da = da.sortby('lon', ascending=True)

    da = regrid(da, grid, base='base180', method='most_common', regridder_kwargs={'values': np.unique(da.values)})
    ds = da.to_dataset(name='agroecological_zone')

    # Convert back to integer
    ds['agroecological_zone'] = ds['agroecological_zone'].astype(np.int32)

    def map_labels(x):
        try:
            x = int(x)
        except ValueError:
            return "Unknown"
        name = agroecological_zone_names.get(x, "Unknown")
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


@spatial()
@region_layer(region_layer='region')
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
    layer_coords = []
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
        layer_coords.append(layer_df.region_layer)

    # Create a a new dataset with the concatonation of all the layers
    ds = xr.merge(layer_grids)
    # This pesky spatial_ref coordinate is not needed
    if 'spatial_ref' in ds.coords:
        ds = ds.drop_vars('spatial_ref')

    coords_values = [ds[x].values.flatten() for x in layer_coords]
    combined_region_coords = np.array([get_combined_region_name(vals) for vals in zip(*coords_values)], dtype='U40')
    ds = ds.assign_coords(region=(('lat', 'lon'), combined_region_coords.reshape(ds.lat.size, ds.lon.size)))
    return ds
