"""Mask data objects."""
import os
import cdsapi
import xarray as xr
import numpy as np
import rioxarray  # noqa: F401 - needed to enable .rio attribute

from sheerwater_benchmarking.utils import (cacheable, cdsapi_secret, get_grid,
                                           lon_base_change, get_region_data, get_grid_ds)


@cacheable(data_type='array', cache_args=['grid'])
def land_sea_mask(grid="global1_5"):
    """Get the ECMWF global land sea mask for the given grid.

    Args:
        grid (str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.
    """
    _, _, grid_size = get_grid(grid, base="base360")

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


@cacheable(data_type='array',
           cache_args=['grid', 'region_level'],
           chunking={'lat': 1000, 'lon': 1000})
def region_labels(grid='global1_5', region_level='countries'):
    """Generate a dataset with a region coordinate at a specific region level.

    Available region levels are
     - 'countries', 'continents', 'subregions', 'region_un', 'region_wb', 'meteorological_zones',
        'hemispheres', 'global', and 'sheerwater_areas'.

    # NOTE: this is a slow function. Doesn't really matter, b/c we
    compute it once and cache, but could parallelize better.

    Args:
        grid (str): The grid to fetch the data at.  Note that only
            the resolution of the specified grid is used.
        region_level (str): The region level to add to the dataset

    Returns:
        xarray.Dataset: Dataset with added region coordinate
    """
    # Get the list of regions for the specified admin level
    region_data = get_region_data(region_level)

    # Get the grid dataframe
    ds = get_grid_ds(grid)
    # Assign a dummy region coordinate to all grid cells
    # Fixed data type of strings of length 100
    ds = ds.assign_coords(region=(('lat', 'lon'), xr.full_like(ds.lat * ds.lon, 'no_region', dtype='U100').data))

    # Loop through each region and label grid cells
    for i, rn in region_data.iterrows():
        print(i+1, '/', len(region_data.region_name), rn.region_name)
        # Clip the grid to the boundary of Shapefile
        world_ds = xr.full_like(ds.lat * ds.lon, 1.0, dtype=np.float32)
        #  Add geometry to the dataframe and clip
        world_ds = world_ds.rio.write_crs("EPSG:4326")
        world_ds = world_ds.rio.set_spatial_dims('lon', 'lat')
        region_ds = world_ds.rio.clip(rn, region_data.crs, drop=False)
        # Assign the region name to the region coordinate
        ds['region'] = xr.where(~region_ds.isnull(), rn.region_name, ds['region'])
    return ds


__all__ = ['land_sea_mask', 'region_labels']
