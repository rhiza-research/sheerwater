import numpy as np
import xarray as xr

from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.interfaces import spatial, get_data, get_forecast
from sheerwater.utils import (dask_remote, get_grid, groupby_time, regrid, add_dayofyear,
                              pad_with_leapdays, convert_init_time_to_pred_time)
from sheerwater.spatial_subdivisions import clip_to_region_envelope
from sheerwater.forecasts.ecmwf_er import ifs_extended_range


@dask_remote
@cache(cache_args=['variable', 'data', 'first_year', 'last_year',
                   'time_grouping', 'margin_in_days',
                   'agg_days', 'grid', 'region'],
       backend_kwargs={
           'chunking': {"lat": 500, "lon": 500, "group": 12, 'quantile': 11},
           'chunk_by_arg': {
               'data': {
                   'ecmwf_ifs_er': {"lat": 100, "lon": 100, 'group': 12, 'prediction_timedelta': 50, 'quantile': 11}
               }
           }
})
def quantile_ranks(variable, data='era5', first_year=1985, last_year=2014,
                   time_grouping="month_of_year", margin_in_days=None,
                   agg_days=7, grid="global1_5", region='global'):
    """Generates quantile ranks of a dataset."""
    if (margin_in_days is not None and time_grouping is not None) or (margin_in_days is None and time_grouping is None):
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
            ds = ifs_extended_range(None, None, variable, forecast_type='reforecast',
                                    run_type='average', time_group='daily', grid=grid, mask=None, region='global')
            ds = ds.rename({'lead_time': 'prediction_timedelta'})
            # Nan out all timestamps that are outside of the start and end time.
            # start_year is a year offset from model_issuance_date (see ifs_er_reforecast_lead_bias).
            init_times = ds.model_issuance_date + ds.start_year.astype('timedelta64[Y]')
            valid_times = init_times + ds.prediction_timedelta
            in_range = (valid_times >= np.datetime64(start_time)) & (valid_times <= np.datetime64(end_time))
            ds = ds.where(in_range, other=np.nan)
        else:
            raise ValueError(f"Unsupported data source: {data}")
    # Select only the variable of interest
    ds = ds[[variable]]

    # Clip to region envelope before computing ranks. This is important for efficiency.
    _, _, grid_res, _ = get_grid(grid)
    ds = clip_to_region_envelope(ds, region, padding=grid_res)

    is_forecast = 'prediction_timedelta' in ds.coords

    ranks = np.arange(0, 1.1, 0.1)
    # round ranks to 1 decimal place
    ranks = np.round(ranks, 1)

    if time_grouping is not None:
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
    qs = ds.groupby("group").quantile(q=ranks, dim="time", skipna=True)
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


@dask_remote
@timeseries()
@cache(cache=True,
       cache_args=['data', 'variable', 'prob_type', 'time_grouping', 'margin_in_days', 'source_grid', 'grid', 'region'],
       backend_kwargs={
           'chunking': {"lat": 500, "lon": 500, "time": 120},
       })
def data_quantile_regridded(start_time=None, end_time=None, data='era5',
                            variable='precip',
                            prob_type='deterministic',
                            time_grouping=None, margin_in_days=6,
                            source_grid="global1_5", grid="global1_5", region='global'):
    """Computes the quantile regridded unerlying data sources."""
    try:
        data_fn = get_data(data)
        ds = data_fn(start_time, end_time, variable=variable,
                     agg_days=1, grid=source_grid, mask=None, region='global')
    except ValueError:
        forecast_fn = get_forecast(data)
        ds = forecast_fn(start_time, end_time, variable=variable, prob_type=prob_type,
                         agg_days=1, grid=source_grid, mask=None, region='global')

    _, _, grid_res, _ = get_grid(source_grid)
    ds = clip_to_region_envelope(ds, region, padding=grid_res)

    # The forecast outputs will have been converted
    if 'init_time' in ds.coords:
        ds = convert_init_time_to_pred_time(ds)
    # add time group
    if margin_in_days is not None:
        ds = groupby_time(ds, 'day_of_year', agg_fn=None)
    else:
        ds = groupby_time(ds, time_grouping, agg_fn=None)

    # Call the quantiles with the passed region to get already clipped to envelope
    source_q = quantile_ranks(variable=variable, data=data, time_grouping=time_grouping, recompute=False,
                              margin_in_days=margin_in_days, agg_days=1, grid=source_grid, region=region)


    """Step 1: Convert precip values to quantiles based on source distribution"""
    # For each cell, find the source-quantile bin closest to the data value and
    # return the corresponding quantile probability. xarray broadcasts by dim
    # name, so subtracting along `quantile` is automatic.
    src_vals = source_q[variable].sel(group=ds.group)  # has dim 'quantile'
    diff = abs(src_vals - ds[variable]).fillna(np.inf)
    source_dsq = diff.idxmin(dim='quantile')

    # Restore NaNs where the input or the entire quantile row was NaN.
    valid = ds[variable].notnull() & src_vals.notnull().any(dim='quantile')
    source_dsq = source_dsq.where(valid)

    """Step 2: Regrid source quantiles to target grid"""
    source_dsq = source_dsq.sortby('lat')
    # Drop grouping coordinate - it's causing problems with the caching
    source_dsq = source_dsq.drop_vars('group')
    # Must pass region into here otherwise the regrid will be slow
    source_dsq_regrid = regrid(source_dsq, grid, method="linear", region=region)
    source_dsq_regrid = source_dsq_regrid.to_dataset(name=variable)

    return source_dsq_regrid
