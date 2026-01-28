"""Space utility functions for all parts of the data pipeline."""
import numpy as np
import xarray as xr
import logging
logger = logging.getLogger(__name__)


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


def snap_point_to_grid(point, grid_size, offset):
    """Snap a point to a provided grid and offset."""
    return round(float(point+offset)/grid_size) * grid_size - offset


def get_grid_ds(grid_id, base="base180"):
    """Get a dataset equal to ones for a given region."""
    lons, lats, _, _ = get_grid(grid_id, base=base)
    data = np.ones((len(lons), len(lats)))
    ds = xr.Dataset(
        {"mask": (['lon', 'lat'], data)},
        coords={"lon": lons, "lat": lats}
    )
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
    if ds.lat.size == 0 and ds.lon.size == 0:
        # If the dataset is empty / dimensionless, return it untouched
        return 0
    if dsp.lat.size == 0 and dsp.lon.size == 0:
        # If the dataset is empty / dimensionless, return it untouched
        return 0

    import pdb; pdb.set_trace()
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
