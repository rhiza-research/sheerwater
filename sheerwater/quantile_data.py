"""Downscaling datasets."""
import numpy as np
import xarray as xr

from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.interfaces import get_data, get_forecast
from sheerwater.utils import (dask_remote, get_grid, groupby_time, regrid, add_dayofyear,
                              pad_with_leapdays, convert_init_time_to_pred_time)
from sheerwater.spatial_subdivisions import clip_to_region_envelope
from sheerwater.forecasts.ecmwf_er import ecmwf_ifs_er_reforecast


@dask_remote
@cache(cache_args=['variable', 'data', 'first_year', 'last_year', 'agg_days',
                   'time_grouping', 'margin_in_days', 'n_quantiles',
                   'grid', 'region'],
       backend_kwargs={
           'chunking': {"lat": 500, "lon": 500, "group": 15, 'quantile': 25},
           'chunk_by_arg': {
               'data': {
                   'ecmwf_ifs_er': {"lat": 500, "lon": 500, 'group': 15, 'prediction_timedelta': 1, 'quantile': 25}
               }
           }
})
def quantile_ranks(variable, data='era5', first_year=1985, last_year=2014, agg_days=1,
                   time_grouping="month_of_year", margin_in_days=None, n_quantiles=20,
                   grid="global1_5", region='global'):
    """Generates quantile ranks of a dataset."""
    if (margin_in_days is not None and time_grouping is not None):
        raise ValueError("margin_in_days and time_grouping cannot be used together. One must be passed as None.")

    start_time = f"{first_year}-01-01"
    end_time = f"{last_year}-12-31"
    try:
        # Try to get a dataset for remapping
        data_fn = get_data(data)
        ds = data_fn(start_time, end_time, variable=variable, agg_days=agg_days, grid=grid, mask=None, region='global')
    except ValueError:
        # If we fail, this is a forecast. We are only supporting ECMWF reforecasts for now.
        if data == 'ecmwf_ifs_er':
            # TODO: temporary fix for ECMWF reforecasts, make this a generic reforecast getter
            # TODO: need to handle the first year and last year challenge
            ds = ecmwf_ifs_er_reforecast(start_time=start_time, end_time=end_time,
                                         variable=variable, agg_days=agg_days,
                                         grid=grid, mask=None, region='global')
        else:
            raise ValueError(f"Unsupported data source: {data}")
    # Select only the variable of interest
    ds = ds[[variable]]

    # Clip to region envelope before computing ranks. This is important for efficiency.
    _, _, grid_res, _ = get_grid(grid)
    ds = clip_to_region_envelope(ds, region, padding=grid_res)

    is_forecast = 'prediction_timedelta' in ds.coords

    # Add one to account for the end point in the quantile calculation
    ranks = np.linspace(0, 1, n_quantiles+1, endpoint=True)  # Includes 1
    ranks = np.round(ranks, 5)  # round to 5 decimal places fori more stable merging

    if margin_in_days is None:
        qs = quantile_ranks_by_group(ds, ranks, time_grouping=time_grouping, is_forecast=is_forecast)
    else:
        qs = quantile_ranks_by_margin(ds, ranks, margin_in_days=margin_in_days, is_forecast=is_forecast)

    return qs


def quantile_ranks_by_group(ds, ranks, time_grouping=None, is_forecast=False):
    """Computes the quantile ranks by a time grouping."""
    if is_forecast:
        # Model issuance date determines the calendar grouping for reforecasts
        ds = groupby_time(ds, time_grouping, agg_fn=None, time_dim='model_issuance_date')
        # Time is uniquely determined by model issuance data and start year
        ds = ds.stack(time=("model_issuance_date", "start_year"))
        ds = ds.chunk({"time": -1})
    else:
        ds = groupby_time(ds, time_grouping, agg_fn=None, time_dim='time')
        ds = ds.chunk({"time": -1})
    if time_grouping is not None:
        qs = ds.groupby("group").quantile(q=ranks, dim="time", skipna=True)
    else:
        qs = ds.quantile(q=ranks, dim="time", skipna=True)
    return qs


def quantile_ranks_by_margin(ds, ranks, margin_in_days=None, is_forecast=False):
    """Computes the quantile ranks with a margin in days."""
    if is_forecast:
        time_dim = 'model_issuance_date'
        chunk_dims = {'dayofyear': -1, 'year': -1, 'start_year': -1, 'lat': 30, 'lon': 30}
    else:
        time_dim = 'time'
        chunk_dims = {'dayofyear': -1, 'year': -1, 'lat': 30, 'lon': 30}

    # Add day of year and pad with leap days
    ds = add_dayofyear(ds, time_dim=time_dim)
    try:
        ds = pad_with_leapdays(ds, time_dim=time_dim)
    except KeyError:
        # Note: pad with leapdays will fail if the time dim is not dense
        pass
    # We will group by day of year, with margin in days padding
    ds = ds.assign_coords(year=ds[time_dim].dt.year)
    # Day of year and year uniquely determine the time index, and enable us to roll in the dayofyear dimension
    ds = ds.chunk({time_dim: -1})
    ds = ds.set_index({time_dim: ['dayofyear', 'year']}).unstack(time_dim)

    # Make sure the days of year are sorted
    ds = ds.sortby('dayofyear')

    # Construct a concatted dataframe that rolls around the end of year
    half = margin_in_days // 2
    window = 2 * half + 1

    if half > 0:  # if we have a margin in days padding, we need to pad the dataset
        # Create a padded dataset with the missing days at the start and end
        ds_pad = xr.concat([
            ds.isel(dayofyear=slice(-half, None)),   # late December wraps to early January
            ds,
            ds.isel(dayofyear=slice(0, half)),
        ], dim='dayofyear')
        ds_pad = ds_pad.chunk(chunk_dims)
    else:
        ds_pad = ds

    # Next, roll over the margin in days and construct the window for quantiles
    windowed = ds_pad.rolling(dayofyear=window, center=True, min_periods=1).construct('dayofyear_window')
    # Finally, drop the padding
    windowed = windowed.isel(dayofyear=slice(half, -half))
    # Keep the window axis in one chunk so the downstream `sample` stack stays
    # in one chunk per worker (required for an efficient quantile reduction).
    windowed = windowed.chunk({'dayofyear_window': -1})

    # Apply the quantiles over the window
    if is_forecast:
        samples = windowed.stack(sample=('year', 'start_year', 'dayofyear_window'))
    else:
        samples = windowed.stack(sample=('year', 'dayofyear_window'))
    qs = samples.quantile(ranks, dim='sample', skipna=True)
    # Assign the day of year coordinates
    qs = qs.assign_coords(
        group=('dayofyear', [f'D{x:03d}' for x in qs.dayofyear.dt.dayofyear.values])
    )
    qs = qs.swap_dims({'dayofyear': 'group'}).drop_vars('dayofyear')

    return qs
