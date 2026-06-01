import numpy as np
import xarray as xr

from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.interfaces import spatial, get_data, get_forecast
from sheerwater.utils import (dask_remote, get_grid, groupby_time, regrid, add_dayofyear, pad_with_leapdays, convert_init_time_to_pred_time)
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

    def compute_quantiles(x, ranks):
        # Define a lambda to compute the quantile ranks in each group.
        return x.groupby("group").quantile(q=ranks, dim="time", skipna=True)

    ranks = np.arange(0, 1.1, 0.1)
    # round ranks to 1 decimal place
    ranks = np.round(ranks, 1)

    if time_grouping is not None:  # a time_grouping style group is passed, versus a margin in days
        if is_forecast:
            # Model issuance date determines the calendar grouping for reforecasts
            ds = groupby_time(ds, time_grouping, agg_fn=None, time_dim='model_issuance_date')
            # Time is uniquely determined by model issuance data and start year
            ds = ds.stack(time=("model_issuance_date", "start_year"))
            ds = ds.chunk({"time": -1})
            qs = ds.groupby("prediction_timedelta").map(compute_quantiles, ranks=ranks)
        else:
            ds = groupby_time(ds, time_grouping, agg_fn=None, time_dim='time')
            ds = ds.chunk({"time": -1})
            qs = ds.groupby("group").quantile(q=ranks, dim="time", skipna=True)
    else:  # a margin in days is passed, versus a time_grouping style group
        if is_forecast:
            time_dim = 'model_issuance_date'
            chunk_dims = {'dayofyear': -1, 'year': -1, 'start_year': -1}
        else:
            time_dim = 'time'
            chunk_dims = {'dayofyear': -1, 'year': -1}

        # Add day of year and pad with leap days
        ds = add_dayofyear(ds, time_dim=time_dim)
        ds = pad_with_leapdays(ds, time_dim=time_dim)
        # We will group by day of year, with margin in days padding
        ds = ds.assign_coords(year=ds[time_dim].dt.year)
        # Day of year and year uniquely determine the time index, and enable us to roll in the dayofyear dimension
        ds = ds.set_index(time_dim=['dayofyear', 'year']).unstack(time_dim)

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

        # Apply the quantiles over the window
        if is_forecast:
            samples = windowed.stack(sample=('year', 'start_year', 'dayofyear_window'))
            # Handle the forecast case, where we need to compute the quantiles for each prediction timedelta
            qs = samples.groupby("prediction_timedelta").map(compute_quantiles, ranks=ranks)
        else:
            samples = windowed.stack(sample=('year', 'dayofyear_window'))
            qs = samples.quantile(ranks, dim='sample', skipna=True)
        # Assign the day of year coordinates
        qs = qs.assign_coords(group=('dayofyear', [f'D{d.dt.dayofyear:03d}' for d in qs.dayofyear]))

    return qs


@dask_remote
@timeseries()
@spatial()
@cache(cache=False,
       cache_args=['variable', 'data', 'time_grouping', 'margin_in_days', 'prob_type', 'grid'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "time": 1000},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, 'time': 30}
               }
           }
       })
def data_quantile_regridded(start_time, end_time, variable,
                            data='era5',
                            time_grouping=None, margin_in_days=6,
                            prob_type='deterministic', grid="global1_5",
                            mask=None, region='global'):
    """Computes the quantile regridded unerlying data sources"""
    try:
        ds = get_data(data)
        is_forecast = False
    except ValueError:
        ds = get_forecast(data)
        is_forecast = True

    _, _, grid_res, _ = get_grid(grid)
    ds = clip_to_region_envelope(ds, region, padding=grid_res)

    
    if is_forecast:
        ds = convert_init_time_to_pred_time(ds)

    source_q = quantile_ranks(variable=variable, data=data, time_grouping=time_grouping, recompute=True,
                              margin_in_days=margin_in_days, agg_days=1, grid=grid, region=region)
    

    # add time group
    ds = groupby_time(ds, time_grouping, agg_fn=None)

    """Step 1: Convert precip values to quantiles based on source distribution"""
    qvalues = source_q['quantile'].values

    def value_to_quantile(x, values):
        if np.all(np.isnan(values)) or np.isnan(x):
            return np.nan
        idx = np.argmin(np.abs(values - x))
        return qvalues[idx]

    source_dsq = xr.apply_ufunc(value_to_quantile,
                                ds[variable], source_q[variable].sel(group=ds.group),
                                input_core_dims=input_core_dims, output_core_dims=[[]],
                                vectorize=True, dask="parallelized", output_dtypes=[float])

    """Step 2: Regrid source quantiles to target grid"""
    source_dsq = source_dsq.sortby('lat')
    import pdb; pdb.set_trace()
    source_dsq_regrid = regrid_util(source_dsq, target_grid, method="linear", region=target_region)