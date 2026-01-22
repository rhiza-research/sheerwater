"""Mask data objects."""
import os

import cdsapi
import numpy as np
import rioxarray  # noqa: F401 - needed to enable .rio attribute
import xarray as xr
from nuthatch import cache

from sheerwater.utils import (cdsapi_secret, clip_region, get_grid, get_grid_ds, admin_levels_and_labels,
                              region_data, lon_base_change, load_object)


@cache(cache_args=['grid'])
def land_sea_mask(grid="global1_5"):
    """Get the ECMWF global land sea mask for the given grid.

    Args:
        grid (str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.
    """
    _, _, grid_size, _ = get_grid(grid, base="base360")

    # Get data from the CDS API
    times = ['00:00']
    days = ['01']
    months = ['01']

    # Make sure the temp folder exists
    os.makedirs('./temp', exist_ok=True)
    path = "./temp/lsm.nc"

    # Create a file path in the temp folder
    url, key = cdsapi_secret()
    c = cdsapi.Client(url=url, key=key)
    c.retrieve('reanalysis-era5-single-levels',
               {
                   'product_type': 'reanalysis',
                   'variable': "land_sea_mask",
                   'year': 2022,
                   'month': months,
                   'day': days,
                   'time': times,
                   'format': 'netcdf',
                   'grid': [str(grid_size), str(grid_size)],
               },
               path)

    # Some transformations
    ds = xr.open_dataset(path)

    ds = ds.rename({'latitude': 'lat', 'longitude': 'lon', 'lsm': 'mask'})

    if 'valid_time' in ds.coords:
        time_var = 'valid_time'
    elif 'time' in ds.coords:
        time_var = 'time'
    else:
        raise ValueError("Could not find time variable in dataset.")
    ds = ds.sel(**{time_var: ds[time_var].values[0]})
    ds = ds.drop(time_var)

    if 'expver' in ds.coords:
        ds = ds.drop('expver')

    # Convert to our standard base 180 format
    ds = lon_base_change(ds, to_base="base180")

    # Sort and select a subset of the data
    ds = ds.sortby(['lon', 'lat'])  # CDS API returns lat data in descending order, breaks slicing

    ds = ds.compute()
    os.remove(path)
    return ds


@cache(cache_args=['mask', 'grid'], memoize=True)
def spatial_mask(mask, grid='global1_5', region='global'):
    """Get a mask dataset.

    Args:
        mask (str): The mask to apply. One of: 'lsm', None
            To get different land-sea masks, use 'lsm-<value>'. For example, 'lsm-0.5' will return a mask
            where the mask is greater than 0.5. Defaults to 0.0.
        grid (str): The grid resolution of the dataset.
        region (str): The region to clip to. A specific instance of a space group

    Returns:
        xr.Dataset: Mask dataset.
    """
    if mask is None:
        return get_grid_ds(grid)
    elif 'lsm' in mask:
        if grid == 'global1_5' or grid == 'global0_25':
            mask_ds = land_sea_mask(grid=grid).compute()
        else:
            # Import here to avoid circular imports
            # TODO: Should implement a more resolved land-sea mask for the other grids
            from sheerwater.utils.data_utils import regrid
            mask_ds = land_sea_mask(grid='global0_25')
            mask_ds = regrid(mask_ds, grid, method='nearest', region=region).compute()

        val = 0.0
        if '-' in mask:
            # Convert to boolean mask
            val = float(mask.split('-')[1])
        mask_ds['mask'] = mask_ds['mask'] > val
        return mask_ds
    else:
        raise NotImplementedError("Only land-sea or None mask is implemented.")


@cache(cache_args=['grid', 'admin_level', 'region'],
       backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
def admin_region_labels(grid='global1_5', admin_level='country', region='global'):
    """Generate a dataset with a region coordinate at a specific space grouping.

    Available space groupings are
     - 'country', 'continent', 'subregion', 'region_un', 'region_wb', 'meteorological_zone',
        'hemisphere', 'global', and 'sheerwater_region'. The admin level region is also available.

    Args:
        grid (str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.
        admin_level (str): A single admin level:
            - country, continent, subregion, region_un, region_wb, meteorological_zone,
              hemisphere, sheerwater_region, or admin_level_0, admin_level_1, admin_level_2
        region (str): The region to clip to. A specific instance of a space group
            -global, or any specific instance of the space groupings above, e.g., africa


    Returns:
        xarray.Dataset: Dataset with added region coordinate
    """
    # Normalize 'country' to 'admin_level_0'
    if admin_level == 'country':
        admin_level = 'admin_level_0'

    # Get the list of regions for the specified admin level
    admin_df = region_data(admin_level)

    # Get the grid dataframe
    ds = get_grid_ds(grid)
    # Assign a dummy region coordinate to all grid cells
    # Fixed data type of strings of length 40
    ds = ds.assign_coords(admin_region=(('lat', 'lon'), xr.full_like(ds.lat * ds.lon, 'no_admin', dtype='U40').data))
    if region != 'global':
        # Clip here for efficiency
        ds = clip_region(ds, region=region)

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


@cache(cache_args=['grid', 'space_grouping', 'region'],
       backend_kwargs={'chunking': {'lat': 1800, 'lon': 3600}})
def region_labels(grid='global1_5', space_grouping=None, region='global'):
    """Generate a dataset with a region coordinate at a specific space grouping.

    Args:
        grid (str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.
        space_grouping (str or list): Region grouping(s):
            - A string for a single grouping: 'country', 'continent', 'subregion', etc.
            - A list for multiple groupings: ['country'], ['admin_level_1', 'agroecological_zone'], etc.
        region (str): The region to clip to. A specific instance of a space group
            -global, or any specific instance of the space groupings above, e.g., africa


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
            layer_df = admin_region_labels(space_grouping=layer, grid=grid, region=region)
        else:
            if layer == 'agroecological_zone':
                layer_df = agroecological_zone_labels(grid=grid, recompute=True)
            else:
                raise ValueError(f"Invalid layer: {layer}")
            layer_df = clip_region(layer_df, region=region)
        layer_grids.append(layer_df)

    # Create a a new dataset with the concatonation of all the layers
    ds = xr.merge(layer_grids)
    # This pesky spatial_ref coordinate is not needed
    if 'spatial_ref' in ds.coords:
        ds = ds.drop_vars('spatial_ref')

    # Find all the region coordinates
    region_coords = [x for x in ds.coords if x not in ds.dims]

    coords_values = [ds[x].values.flatten() for x in region_coords]
    combined_region_coords = np.array(['_'.join(map(str, vals)) for vals in zip(*coords_values)], dtype='U40')
    ds = ds.assign_coords(region=(('lat', 'lon'), combined_region_coords.reshape(ds.lat.size, ds.lon.size)))
    return ds


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
    from sheerwater.utils.data_utils import regrid
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


__all__ = ['land_sea_mask', 'region_labels', 'agroecological_zone_labels']
