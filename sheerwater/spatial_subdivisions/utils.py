"""Utility functions for spatial subdivisions."""
import geopandas as gpd
import numpy as np
import xarray as xr
import shapely
import logging
from shapely.geometry import Polygon
from shapely.ops import unary_union
from affine import Affine
from rasterio import features
import rioxarray  # noqa: F401 - needed to enable .rio attribute

from sheerwater.utils import get_grid, check_bases, is_station_grid

import warnings
from rasterio.errors import ShapeSkipWarning

from .spatial_subdivisions import (polygon_subdivision_geodataframe, spatial_subdivisions,
                                   get_spatial_subdivision_level,
                                   clean_spatial_subdivision_name, space_grouping_labels)


logger = logging.getLogger(__name__)

warnings.filterwarnings(
    "ignore",
    category=ShapeSkipWarning,
)

##############################################################################
# Core clipping / masking utilities
##############################################################################


def clip_region(ds, region, grid, coords_to_clip=None, drop=True, drop_gridded_regions=False):
    """Clip a dataset to a region.

    Args:
        ds(xr.Dataset): The dataset to clip to a specific region.
        region(str, list): The region to clip to. A str or list of strs.
        grid(str): The grid to clip to.
        coords_to_clip(list): The coordinates to clip to the region. Coordinates outside set to 'nan'.
        drop(bool): Whether to drop the original coordinates that are NaN'd by clipping.
    """
    if region == 'global' or region is None or 'global' in region:
        return ds

    if ds.lat.size == 0 and ds.lon.size == 0:
        # If the dataset is empty / dimensionless, return it untouched
        return ds

    if not isinstance(region, list):
        region = [region]

    # if coords_to_clip is not None or a list, convert to a list.
    if coords_to_clip is not None and not isinstance(coords_to_clip, list):
        coords_to_clip = [coords_to_clip]
        for coord in coords_to_clip:
            if ["lat", "lon"] not in ds[coord].dims:
                raise ValueError(f"Coordinates to clip must be indexed by lat and lon: {coord}")

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

    # setting coordinates to variables allows them to be clipped to the region.
    # these are then reset to coordinates so those outside the region are 'nan'.
    if coords_to_clip is not None:
        ds = ds.reset_coords(coords_to_clip, drop=False)

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
        if drop_gridded_regions:
            ds = ds.where((region_ds._clip_region.compute() == region_str), drop=True)
        else:
            ds = ds.where((region_ds._clip_region == region_str), drop=False)
        ds = ds.drop_vars('_clip_region')

    # restore coordinate variables to coordinates.
    if coords_to_clip is not None:
        ds = ds.set_coords(coords_to_clip)

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
    if is_station_grid(ds):
        ds = clip_station_grid(ds, geometry=geometry, drop=drop)
    elif nonuniform_grid(ds):
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

    # If the grid doesn't exist throw a warning and return
    try:
        get_grid(grid)
    except NotImplementedError:
        logger.warning(f"Cannot apply mask for undefinied grid {grid}.")
        return ds

    if isinstance(mask, str):
        from sheerwater.masks import spatial_mask
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
    # broadcasting gives us an explicit lat/lon for each grid cell
    lon2d, lat2d = xr.broadcast(ds.lon, ds.lat)
    mask = xr.zeros_like(lon2d, dtype=bool)

    polygon = region_df.geometry.union_all()

    # the mask can be large; two step filtering will be faster
    # first filter to the bounding box of the region
    lon_min, lat_min, lon_max, lat_max = polygon.bounds
    bmask = (lon2d >= lon_min) & (lon2d <= lon_max) & (lat2d >= lat_min) & (lat2d <= lat_max)

    # then filter to the precise polygon
    # use NumPy; lazy xarray breaks Shapely and needs tricky re-alignment
    mask.values[bmask.values] = shapely.intersects_xy(polygon, lon2d.values[bmask.values], lat2d.values[bmask.values])

    # in a nonuniform grid, automatic dropping gets rid of interior slices in a way that leads
    # to visually strange results. By cropping to the bounding box, we have a better result.
    ds = ds.where(mask, drop=False)
    if drop:
        if "lat" in ds.dims and "lon" in ds.dims:
            # regular rectilinear grid
            ds = ds.sel(
                lon=slice(lon_min, lon_max),
                lat=slice(lat_min, lat_max)
            )
        else:
            # curvilinear grid (lat/lon are coordinates, e.g. (y, x))
            mask = (
                (ds.lon >= lon_min) &
                (ds.lon <= lon_max) &
                (ds.lat >= lat_min) &
                (ds.lat <= lat_max)
            )

            ds = ds.where(mask)
    return ds


def clip_station_grid(ds, geometry=None, drop=True):
    """Clip a station grid to a geometry.

    A station grid is indexed by station_id and has lat/lon coordinates corresponding to
    individual station locations. Each lat/lon point needs to be checked against the geometry to
    determine if it is within the geometry.
    """
    if geometry is None:
        return ds

    def station_within(station_lons, station_lats):
        buffer = 1e-5
        return shapely.contains_xy(geometry.iloc[0].buffer(buffer), station_lons, station_lats)

    mask = xr.apply_ufunc(station_within, ds["lon"], ds["lat"], dask="parallelized", output_dtypes=[bool])
    ds = ds.where(mask.compute(), drop=drop)

    return ds


def regrid_region_masks(masks, output_grid, base="base180"):
    """Regrid boolean region masks using most_common.

    Collapses (lat, lon, region) bool masks to an integer label map, regrids with
    most_common, then expands back to bool masks. Region indices are shifted up by
    one during regridding so that 0 unambiguously represents background.

    Args:
        masks: xr.DataArray or xr.Dataset with ``masks`` of shape (lat, lon, region).
        output_grid: Target grid name, e.g. ``"global1_5"``.
        base: Longitude convention (``"base180"`` or ``"base360"``).
        region: Region to clip to during regridding.

    Returns:
        Regridded masks in the same type as the input (DataArray or Dataset).
    """
    from sheerwater.utils.data_utils import regrid

    # incremement regions by 1 - 0 becomes background
    masks['region'] = masks['region'] + 1
    region_coords = masks.region.values
    label_map = (masks.astype(np.int8) * masks.region).sum("region")

    label_map_comm = regrid(label_map.masks, output_grid, base=base, method="most_common",
                            regridder_kwargs={"values": np.append(0, masks.region.values), "fill_value": 0},
                            )
    label_map_fill = regrid(label_map.masks, output_grid, base=base, method="stat",
                            regridder_kwargs={"method": "max"})
    # if a cell has a label but is mostly background, comm=0, but fill!=0
    fillin = (label_map_fill != 0) & (label_map_comm == 0)
    label_map = label_map_comm.where(~fillin, label_map_fill)

    regridded = label_map == xr.DataArray(region_coords, dims="region")
    regridded = (
        regridded.transpose("lat", "lon", "region")
        .assign_coords(region=region_coords)
        .astype(bool)
    )

    # decrement regions by 1
    regridded['region'] = regridded['region'] - 1
    regridded = regridded.to_dataset(name="masks")

    return regridded


def masks_to_polygons(masks, crs="EPSG:4326"):
    """Convert lat/lon mask into a multipolygon geodataframe."""
    nregions = len(masks.region.values)
    gdfs = []
    for region in range(nregions):
        mask = masks.sel(region=region).astype(np.int8)
        lat, lon = mask.lat.values, mask.lon.values
        # grid spacings
        dlat, dlon = np.abs(np.mean(np.diff(lat))), np.abs(np.mean(np.diff(lon)))
        # upper-left corner transform
        tf = Affine.translation(
            lon.min() - dlon / 2,
            lat.min() - dlat / 2,
        ) * Affine.scale(dlon, dlat)
        polygons = []
        for geom, values in features.shapes(mask, transform=tf):
            # if polygon corresponds to masked area, keep it.
            if values == 1:
                polygons.append(Polygon(geom['coordinates'][0]))
        if len(polygons) == 0:
            gdf = gpd.GeoDataFrame(geometry=[], crs=crs)
        else:
            # dissolve
            merged = unary_union(polygons)
            gdf = gpd.GeoDataFrame(geometry=[merged], crs=crs)
        gdf['region'] = region
        gdfs.append(gdf)
    return gdfs


def nonuniform_grid(ds, error_thresh=1e-5):
    """Check if a dataset has a nonuniform grid.

    Threshold value has been chosen based on inconsistency in chirps source grid.
    """
    # if lat or lon are not 1d arrays this must be a nonuniform grid, like smap
    if len(ds.lat.shape) > 1 or len(ds.lon.shape) > 1:
        return True

    lat_deltas = np.diff(ds.lat.values) - np.mean(np.diff(ds.lat.values))
    lon_deltas = np.diff(ds.lon.values) - np.mean(np.diff(ds.lon.values))
    return not (np.allclose(lat_deltas, 0, atol=error_thresh) and np.allclose(lon_deltas, 0, atol=error_thresh))


def get_region_envelope(region, padding=1e-6):
    """Get the envelope of a region, padded with a small epsilon."""
    level, _ = get_spatial_subdivision_level(region)
    gdf = polygon_subdivision_geodataframe(level=level)
    gdf = gdf[gdf['region_name'] == region]
    bounds = gdf.geometry.bounds
    # pad minx, miny, maxx, maxy
    bounds['minx'] -= padding
    bounds['miny'] -= padding
    bounds['maxx'] += padding
    bounds['maxy'] += padding
    return bounds


def clip_to_region_envelope(ds, region, padding=1e-6):
    """Clip a dataset to a region envelope."""
    min_lon, min_lat, max_lon, max_lat = get_region_envelope(region, padding=padding).iloc[0]
    ds = ds.sel(lon=slice(min_lon, max_lon), lat=slice(min_lat, max_lat))
    return ds
