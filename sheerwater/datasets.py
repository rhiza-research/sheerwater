import numpy as np
import xarray as xr

from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.interfaces import spatial, get_data
from sheerwater.utils import dask_remote, get_grid, groupby_time, regrid, add_dayofyear, pad_with_leapdays
from sheerwater.spatial_subdivisions import clip_to_region_envelope
from sheerwater.forecasts.ecmwf_er import ifs_extended_range


@dask_remote
@cache(cache_args=['variable', 'data', 'first_year', 'last_year', 'time_grouping',
                   'margin_in_days', 'agg_days', 'grid', 'region'],
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
        data_fn = get_data(data)
        ds = data_fn(start_time, end_time, variable=variable, agg_days=agg_days, grid=grid, mask=None, region='global')
    except ValueError:
        if data == 'ecmwf_ifs_er':
            # TODO: temporary fix for ECMWF reforecasts, make this a generic reforecast getter
            ds = ifs_extended_range(start_time, end_time, variable, forecast_type='reforecast',
                                    run_type='average', time_group='daily', grid=grid, mask=None, region='global')
            ds = ds.rename({'lead_time': 'prediction_timedelta'})
        else:
            raise ValueError(f"Unsupported data source: {data}")
    # Select only the variable of interest
    ds = ds[[variable]]

    # Clip to region envelope before computing ranks
    _, _, grid_res, _ = get_grid(grid)
    ds = clip_to_region_envelope(ds, region, padding=grid_res)

    is_forecast = 'prediction_timedelta' in ds.coords

    def compute_quantiles(x, ranks):
        return x.groupby("group").quantile(q=ranks, dim="time", skipna=True)

    import pdb
    pdb.set_trace()
    ranks = np.arange(0, 1.1, 0.1)
    # round ranks to 1 decimal place
    ranks = np.round(ranks, 1)

    if time_grouping is not None:
        if is_forecast:
            # Model issuance date determines the calendar grouping for reforecasts
            ds = groupby_time(ds, time_grouping, agg_fn=None, time_dim='model_issuance_date')
            ds = ds.stack(time=("model_issuance_date", "start_year"))
        else:
            ds = groupby_time(ds, time_grouping, agg_fn=None, time_dim='time')
        ds = ds.chunk({"time": -1})
        if is_forecast:
            qs = ds.groupby("prediction_timedelta").map(compute_quantiles, ranks=ranks)
        else:
            qs = ds.groupby("group").quantile(q=ranks, dim="time", skipna=True)
    else:
        if is_forecast:
            ds = add_dayofyear(ds, time_dim='model_issuance_date')
            ds = pad_with_leapdays(ds, time_dim='model_issuance_date')
            ds = ds.rename({'dayofyear': 'group'})
            ds = ds.assign_coords(year=ds.model_issuance_date.dt.year)
            ds = ds.set_index(model_issuance_date=['group', 'year']).unstack('model_issuance_date')
        else:
            ds = add_dayofyear(ds, time_dim='time')
            ds = pad_with_leapdays(ds, time_dim='time')
            ds = ds.rename({'dayofyear': 'group'})
            ds = ds.assign_coords(year=ds.time.dt.year)
            ds = ds.set_index(time=['group', 'year']).unstack('time')

        ds = ds.sortby('group')

        half = margin_in_days // 2
        window = 2 * half + 1

        chunk_dims = {'group': -1, 'year': -1}
        if is_forecast:
            chunk_dims['start_year'] = -1

        if half > 0:
            # Create a padded dataset with the missing days at the start and end
            ds_pad = xr.concat([
                ds.isel(group=slice(-half, None)),   # late December wraps to early January
                ds,
                ds.isel(group=slice(0, half)),
            ], dim='group')
            ds_pad = ds_pad.chunk(chunk_dims)
        else:
            ds_pad = ds

        windowed = ds_pad.rolling(group=window, center=True, min_periods=1).construct('group_window')
        windowed = windowed.isel(group=slice(half, -half))

        if is_forecast:
            samples = windowed.stack(sample=('year', 'start_year', 'group_window'))
        else:
            samples = windowed.stack(sample=('year', 'group_window'))
        qs = samples.quantile(ranks, dim='sample', skipna=True)
        qs = qs.assign_coords(group=('group', [f'D{d.dt.dayofyear:03d}' for d in qs.group]))

    return qs


@dask_remote
@timeseries()
@cache(cache_args=['variable', 'margin_in_days', 'run_type', 'time_group', 'grid'],
       cache_disable_if={'grid': 'global1_5'},
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "lead_time": 1,
                        "start_date": 1000,
                        "model_issuance_date": 1000, "start_year": 1,
                        "member": 1},
           'chunk_by_arg': {
               'grid': {
                   # A note: a setting where time is in groups of 200 works better for regridding tasks,
                   # but is less good for storage.
                   'global0_25': {"lat": 721, "lon": 1440, 'model_issuance_date': 30, "start_date": 30}
               },
           }
})
def data_quantile_regridded(start_time, end_time, variable,
                            margin_in_days=6, run_type='average',
                            time_group='weekly', grid="global1_5",
                            mask=None, region='global'):
    """Computes the debiased ECMWF forecasts."""
