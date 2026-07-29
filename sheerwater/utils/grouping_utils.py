"""Library of metrics implementations for verification."""
# flake8: noqa: D102

import numpy as np
import pandas as pd
import xarray as xr

from .time_utils import get_dates


def groupby_time(ds, time_grouping, agg_fn='mean', time_dim='time'):
    """Aggregate a statistic over time. If agg_fn is None, add the grouping coordinates but perform no aggregation."""
    # Implement MAM, JJA, SON, DJF seasons
    season_mapping = {
        1: 'DJF', 2: 'DJF', 3: 'MAM', 4: 'MAM', 5: 'MAM', 6: 'JJA', 7: 'JJA', 8: 'JJA',
        9: 'SON', 10: 'SON', 11: 'SON', 12: 'DJF',
    }
    kenya_rainy_season_mapping = {
        1: 'None',
        2: 'MAM', 3: 'MAM', 4: 'MAM', 5: 'MAM',
        6: 'None', 7: 'None', 8: 'None',
        9: 'OND', 10: 'OND', 11: 'OND', 12: 'OND',
    }
    two_seasons_mapping = {
        1: 'first',
        2: 'first',
        3: 'first',
        4: 'first',
        5: 'first',
        6: 'first',
        7: 'second',
        8: 'second',
        9: 'second',
        10: 'second',
        11: 'second',
        12: 'second',

    }
    if time_grouping is not None:
        if time_grouping == 'month_of_year':
            coords = [f'M{x:02d}' for x in ds[time_dim].dt.month.values]
        elif time_grouping == 'dekad_of_year':
            coords = [f'D{x:02d}' for x in ds[time_dim].dt.dayofyear.values // 10]
        elif time_grouping == 'week_of_year':
            coords = [f'W{x:02d}' for x in ds[time_dim].dt.weekofyear.values]
        elif time_grouping == 'year':
            coords = [f'Y{x:04d}' for x in ds[time_dim].dt.year.values]
        elif time_grouping == 'quarter_of_year':
            coords = [f'Q{x:02d}' for x in ds[time_dim].dt.quarter.values]
        elif time_grouping == 'day_of_year':
            coords = [f'D{x:03d}' for x in ds[time_dim].dt.dayofyear.values]
        elif time_grouping == 'month':
            coords = [f'{pd.to_datetime(x).year:04d}-{pd.to_datetime(x).month:02d}-01' for x in ds[time_dim].values]
        elif time_grouping == 'daily':
            coords = [pd.to_datetime(x).date() for x in ds[time_dim].values]
            raise ValueError("Invalid time grouping")
        elif time_grouping == 'season_of_year':
            coords = [f"{season_mapping.get(pd.to_datetime(x).month, None)}" for x in ds[time_dim].values]
        elif time_grouping == 'season':
            # Implement MAM, JJA, SON, DJF seasons
            coords = [f"{season_mapping.get(pd.to_datetime(x).month, None)}-{pd.to_datetime(x).year:04d}"
                      for x in ds[time_dim].values]
        elif time_grouping == 'kenya_rainy_season_of_year':
            coords = [f"{kenya_rainy_season_mapping.get(pd.to_datetime(x).month, None)}" for x in ds[time_dim].values]
        elif time_grouping == 'kenya_rainy_season':
            # Implement MAM, JJA, SON, DJF seasons
            coords = [
                f"{kenya_rainy_season_mapping.get(pd.to_datetime(x).month, None)}-{pd.to_datetime(x).year:04d}"
                for x in ds[time_dim].values]
        elif time_grouping == 'two_seasons_of_year':
            coords = [f"{two_seasons_mapping.get(pd.to_datetime(x).month, None)}" for x in ds[time_dim].values]
        elif time_grouping == 'two_seasons':
            coords = [
                f"{two_seasons_mapping.get(pd.to_datetime(x).month, None)}-{pd.to_datetime(x).year:04d}"
                for x in ds.time.values]
        elif time_grouping == 'shifted_season':
            coords = []
            for x in ds.time.values:
                if pd.to_datetime(x).month in [1, 2, 3, 4, 5, 6, 7]:
                    coords.append(f'{pd.to_datetime(x).year - 1}-season')
                else:
                    coords.append(f'{pd.to_datetime(x).year}-season')
        else:
            raise ValueError(f"Invalid time groupingi {time_grouping}")

        ds = ds.assign_coords(group=(time_dim, coords))

        # If no aggregation is requested, return the dataset augmented by the grouping coordinates
        if agg_fn is None:
            return ds

        if agg_fn == 'mean':
            ds = ds.groupby("group").mean(dim=time_dim, skipna=True)
        elif agg_fn == 'sum':
            # min_count ensures that all nan groups return nan
            ds = ds.groupby("group").sum(dim=time_dim, skipna=True, min_count=1)
        else:
            raise ValueError(f"Invalid aggregation function {agg_fn}")
        ds = ds.rename({"group": time_dim})
        ds = ds.assign_coords({time_dim: ds[time_dim].astype('<U15')})
    else:
        # Average in time
        if agg_fn == 'mean':
            ds = ds.mean(dim=time_dim, skipna=True)
        elif agg_fn == 'sum':
            # min_count ensures that all nan groups return nan
            ds = ds.sum(dim=time_dim, skipna=True, min_count=1)
        elif agg_fn is None:
            return ds
        else:
            raise ValueError(f"Invalid aggregation function {agg_fn}")

    return ds


def detect_in_time(ds, time_grouping=None, detect='first', coverage_threshold=0.95,
                   criteria='greater', criteria_kwargs={'threshold': 0.5}):
    """Detect the first or last time in a time grouping that satisfies a criteria."""
    if criteria == 'greater':
        def criteria(x): return x >= criteria_kwargs['threshold']
    elif criteria == 'less':
        def criteria(x): return x <= criteria_kwargs['threshold']
    else:
        raise ValueError(f"Invalid criteria {criteria}")

    # Pad the dataset with lagging and leading time to ensure that all partial seasons
    # are dropped properly, even those that are misaligned with the start and end
    # of the year
    years = pd.to_datetime(ds.time.values).year
    min_year = years.min()
    max_year = years.max()
    start_time = pd.Timestamp(f"{min_year-1}-09-01")
    end_time = pd.Timestamp(f"{max_year+1}-02-28")
    daily_timeseries = get_dates(start_time, end_time, stride='day', return_string=False)
    ds = ds.reindex(time=daily_timeseries, fill_value=np.nan)

    # Add the grouping coordinates but perform no aggregation
    ds = groupby_time(ds, time_grouping, agg_fn=None)
    nanmask = ds.isnull()

    var = list(ds.data_vars)[0]
    ds['indicator'] = xr.ones_like(ds[var])
    ds['non_null'] = ds[var].notnull()
    # Coverage per group: fraction of timesteps with non-null data
    group_sums = ds[['indicator', 'non_null']].groupby('group').sum(dim="time", min_count=1)
    group_coverage = group_sums['non_null'] / group_sums['indicator']

    # Apply the criteria to the dataset, converting to boolean
    ds = criteria(ds)

    # Set all times to zero where the group in the null mask (i.e., season was None)
    is_null_group = ds['group'].astype(str).str.contains('None')
    ds = ds.where(~is_null_group, other=np.nan)

    def first_hit(x):
        cumsum = x.cumsum(dim="time")
        # There is a bug in xarray cumsum that causes the time coordinate to be lost
        # https://github.com/pydata/xarray/issues/6528
        cumsum = cumsum.assign_coords(time=x['time'])
        return ((cumsum == 1.0) & (x == 1.0)).astype(int)

    def last_hit(x):
        # Reverse in time and run first hit
        x = x.isel(time=slice(None, None, -1))
        ret = first_hit(x)
        ret = ret.isel(time=slice(None, None, -1))
        return ret

    def last_time(x):
        # Produce a one-hot timeseries with 1 at the final (last) time, 0 elsewhere (same for every lat/lon)
        out = xr.zeros_like(x)
        out.loc[{'time': x.time[-1]}] = 1.0
        return out

    # Ensure that the timedimension is sorted
    ds = ds.sortby("time")
    if detect == 'first':
        func = first_hit
    elif detect == 'last':
        func = last_hit
    elif detect == 'last_time':
        func = last_time
    else:
        raise ValueError(f"Invalid detection type {detect}")

    # Apply the detection function to the dataset
    detected = ds.groupby("group").map(func)

    # Remove groups that don't have enough coverage
    coverage_at_time = group_coverage.sel(group=detected['group'])
    detected = detected.where(coverage_at_time >= coverage_threshold, other=np.nan)
    detected = detected.drop_vars(['indicator', 'non_null'])

    # Remove groups that don't have a detection
    has_detection = detected.groupby("group").sum(dim="time", skipna=True, min_count=1)
    has_detection_at_time = has_detection.sel(group=detected['group'])
    detected = detected.where(has_detection_at_time >= 1.00, other=np.nan)

    # Restore the null pattern and attributes, which are lost during the grouping
    detected = detected.where(~nanmask, other=np.nan)
    detected = detected.assign_attrs(ds.attrs)

    return detected


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
