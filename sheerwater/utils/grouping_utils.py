"""Library of metrics implementations for verification."""
# flake8: noqa: D102

import numpy as np
import pandas as pd
import xarray as xr


def mean_or_sum(ds, agg_fn, dims=['lat', 'lon']):
    """A light wrapper around standard groupby aggregation functions."""
    # Note, for some reason:
    # ds.groupby('region').mean(['lat', 'lon'], skipna=True).compute()
    # raises:
    # *** AttributeError: 'bool' object has no attribute 'blockwise'
    # or
    # *** TypeError: reindex_intermediates() missing 1 required positional argument: 'array_type'
    # So we have to do it via apply
    if agg_fn == 'mean':
        return ds.mean(dims, skipna=True)
    else:
        return ds.sum(dims, skipna=True)


def groupby_time(ds, time_grouping, agg_fn='mean'):
    """Aggregate a statistic over time."""
    if time_grouping is not None:
        if time_grouping == 'month_of_year':
            coords = [f'M{x:02d}' for x in ds.time.dt.month.values]
        elif time_grouping == 'year':
            coords = [f'Y{x:04d}' for x in ds.time.dt.year.values]
        elif time_grouping == 'quarter_of_year':
            coords = [f'Q{x:02d}' for x in ds.time.dt.quarter.values]
        elif time_grouping == 'day_of_year':
            coords = [f'D{x:03d}' for x in ds.time.dt.dayofyear.values]
        elif time_grouping == 'month':
            coords = [f'{pd.to_datetime(x).year:04d}-{pd.to_datetime(x).month:02d}-01' for x in ds.time.values]
        else:
            raise ValueError("Invalid time grouping")
        ds = ds.assign_coords(group=("time", coords))

        if agg_fn == 'mean':
            ds = ds.groupby("group").mean(dim="time", skipna=True)
        else:
            ds = ds.groupby("group").sum(dim="time", skipna=True)
        ds = ds.rename({"group": "time"})
        ds = ds.assign_coords(time=ds['time'].astype('<U10'))
    else:
        # Average in time
        if agg_fn == 'mean':
            ds = ds.mean(dim="time")
        elif agg_fn == 'sum':
            ds = ds.sum(dim="time")
        else:
            raise ValueError(f"Invalid aggregation function {agg_fn}")
    return ds


def groupby_region(ds, region_ds, mask_ds, agg_fn='mean', weighted=False):
    """Aggregate a statistic over region."""
    if agg_fn not in ['mean', 'sum']:
        raise ValueError(f"Invalid aggregation function {agg_fn}")
    if weighted and agg_fn == 'sum':
        raise ValueError("Cannot aggregate by sum with weighted averaging")

    if 'region' not in ds.coords:
        ds = ds.assign_coords(region=region_ds.region)

    variable_names = list(ds.data_vars)

    # Aggregate in space
    if weighted:
        # Group by region and average in space, while applying weighting for mask
        weights = latitude_weights(ds.lat)
        # Expand weights to have a time dimension that matches ds
        if 'time' in ds.dims:  # Enable a time specific null pattern
            weights = weights.expand_dims(time=ds.time)

        # Ensure the weights null pattern matches the ds null pattern
        # Get all variable names in the dataset (excluding coords)
        weights = weights.where(ds[variable_names[0]].notnull(), np.nan, drop=False)

        # Mulitply by weights
        weights = weights * mask_ds.mask
    else:
        weights = mask_ds.mask

    ds['weights'] = weights
    for var in variable_names:
        ds[var] = ds[var] * ds['weights']

    ds = ds.groupby('region').sum(dim=['lat', 'lon'], skipna=True)

    if agg_fn == 'mean':
        for var in variable_names:
            ds[var] = ds[var] / ds['weights']

    ds = ds.drop_vars(['weights'])
    return ds


def latitude_weights(lats):
    """Return cosine latitude weights for any arbitrary collection of latitude values.

    Args:
        lats (array-like): Latitude values in degrees.

    Returns:
        xr.DataArray: Normalized weights proportional to cos(lat).
    """
    lats = xr.DataArray(lats, dims='lat') if not isinstance(lats, xr.DataArray) else lats
    weights = np.cos(np.deg2rad(lats))
    weights /= weights.mean()
    return weights
