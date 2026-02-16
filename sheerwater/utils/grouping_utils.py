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


def groupby_time(ds, time_grouping, agg_fn='mean', bins=None):
    """
    Aggregate a statistic over time, including optional histogram aggregation.

    Parameters
    ----------
    ds : xarray.Dataset or DataArray
        Input data with 'time' dimension.
    time_grouping : str or None
        Time grouping type: 'month_of_year', 'year', etc.
    agg_fn : str
        Aggregation function: 'mean', 'sum', or 'hist'.
    bins : array-like, optional
        Bin edges for histogram. Required if agg_fn='hist'.

    Returns
    -------
    ds_out : xarray.Dataset or DataArray
        Aggregated data.
    """

    # --- Histogram function, defined once ---
    def hist_time(values, bins):
        values = values[~np.isnan(values)]
        hist, _ = np.histogram(values, bins=bins)
        return hist

    # --- 1. Define time groups if requested ---
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
            coords = [f'{pd.to_datetime(x).year:04d}-{pd.to_datetime(x).month:02d}-01'
                      for x in ds.time.values]
        elif time_grouping == 'daily':
            coords = [f'{pd.to_datetime(x).year:04d}-{pd.to_datetime(x).month:02d}-{pd.to_datetime(x).day:02d}'
                      for x in ds.time.values]
        else:
            raise ValueError("Invalid time grouping")

        ds = ds.assign_coords(group=("time", coords))

        # --- 2. Histogram aggregation ---
        if agg_fn == 'hist':
            if bins is None:
                raise ValueError("bins must be provided for histogram aggregation")

            groups = np.unique(ds['group'].values)
            hist_list = []

            for g in groups:
                ds_group = ds.sel(time=ds['group'] == g)
                #ds_group = ds_group.chunk({"time": -1})  # Dask-friendly

                # apply histogram along time
                hist_group = xr.apply_ufunc(
                    hist_time,
                    ds_group,
                    input_core_dims=[["time"]],
                    output_core_dims=[["bin"]],
                    vectorize=True,
                    dask="parallelized",
                    output_dtypes=[int],
                    dask_gufunc_kwargs={"allow_rechunk": True},
                    output_sizes={"bin": len(bins)-1},
                    kwargs={"bins": bins},
                )

                hist_group = hist_group.expand_dims(group=[g])
                hist_list.append(hist_group)

            ds_out = xr.concat(hist_list, dim="group")
            ds_out = ds_out.assign_coords(bin=bins[:-1])

            return ds_out

        # --- 3. Mean or sum over time groups ---
        elif agg_fn == 'mean':
            ds_out = ds.groupby("group").mean(dim="time", skipna=True)
        elif agg_fn == 'sum':
            ds_out = ds.groupby("group").sum(dim="time", skipna=True, min_count=1)
        else:
            raise ValueError(f"Invalid aggregation function {agg_fn}")

        ds_out = ds_out.rename({"group": "time"})
        ds_out = ds_out.assign_coords(time=ds_out['time'].astype('<U10'))

        return ds_out

    # --- 4. No time grouping ---
    else:
        if agg_fn == 'mean':
            ds_out = ds.mean(dim="time", skipna=True)
        elif agg_fn == 'sum':
            ds_out = ds.sum(dim="time", skipna=True, min_count=1)
        elif agg_fn == 'hist':
            if bins is None:
                raise ValueError("bins must be provided for histogram aggregation")

            ds_chunked = ds.chunk({"time": -1})

            ds_out = xr.apply_ufunc(
                hist_time,
                ds_chunked,
                input_core_dims=[["time"]],
                output_core_dims=[["bin"]],
                vectorize=True,
                dask="parallelized",
                output_dtypes=[int],
                dask_gufunc_kwargs={"allow_rechunk": True},
                output_sizes={"bin": len(bins)-1},
                kwargs={"bins": bins},
            )
            ds_out = ds_out.assign_coords(bin=bins[:-1])
        else:
            raise ValueError(f"Invalid aggregation function {agg_fn}")

        return ds_out


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
        weights = latitude_weights(ds, lat_dim='lat', lon_dim='lon')
        # Expand weights to have a time dimension that matches ds
        if 'time' in ds.dims:  # Enable a time specific null pattern
            weights = weights.expand_dims(time=ds.time)

        # Ensure the weights null pattern matches the ds null pattern
        # Get all variable names in the dataset (excluding coords)
        weights = weights.where(ds[variable_names[0]].notnull(), np.nan, drop=False)
    else:
        weights = xr.ones_like(ds[variable_names[0]])
    # set weights to nan outside the mask - this is robust to boolean masks
    weights = weights.where(mask_ds.mask)
    if 'number' in weights.coords:
        weights = weights.reset_coords('number', drop=True)
    ds['weights'] = weights

    for var in variable_names:
        ds[var] = ds[var] * ds['weights']

    ds = ds.groupby('region').sum(dim=['lat', 'lon'], skipna=True, min_count=1)

    if agg_fn == 'mean':
        for var in variable_names:
            ds[var] = ds[var] / ds['weights']

    ds = ds.drop_vars(['weights'])
    return ds


def latitude_weights(ds, lat_dim='lat', lon_dim='lon'):
    """Return latitude weights as an xarray DataArray.

    This function weights each latitude band by the actual cell area,
    which accounts for the fact that grid cells near the poles are smaller
    in area than those near the equator.
    """
    if ds[lat_dim].size == 0:
        # Handle empty / dimensionless dataset
        return xr.DataArray(np.array([]), coords=[ds[lat_dim]], dims=[lat_dim]).expand_dims({lon_dim: ds[lon_dim]})
    # Calculate latitude cell bounds
    lat_rad = np.deg2rad(ds[lat_dim].values)
    pi_over_2 = np.array([np.pi / 2], dtype=ds[lat_dim].dtype)

    if lat_rad.min() == -pi_over_2 and lat_rad.max() == pi_over_2:
        # Dealing with the full globe
        lower_bound = -pi_over_2
        upper_bound = pi_over_2
    else:
        # Compute the difference in between cells
        diff = np.diff(lat_rad)
        if diff.std() > 0.5:
            raise ValueError(
                "Nonuniform grid! Need to think about spatial averaging more carefully.")
        diff = diff.mean()
        lower_bound = np.array([lat_rad[0] - diff / 2.0], dtype=lat_rad.dtype)
        upper_bound = np.array([lat_rad[-1] + diff / 2.0], dtype=lat_rad.dtype)

    bounds = np.concatenate([lower_bound, (lat_rad[:-1] + lat_rad[1:]) / 2, upper_bound])

    # Calculate cell areas from latitude bounds
    upper = bounds[1:]
    lower = bounds[:-1]
    # normalized cell area: integral from lower to upper of cos(latitude)
    weights = np.sin(upper) - np.sin(lower)

    # Normalize weights
    weights /= np.mean(weights)
    # Return an xarray DataArray with dimensions lat
    weights = xr.DataArray(weights, coords=[ds[lat_dim]], dims=[lat_dim])
    weights = weights.expand_dims({lon_dim: ds[lon_dim]})
    return weights
