"""Functions to fetch and process data from the ECMWF WeatherBench dataset."""
import numpy as np
import pandas as pd
import xarray as xr
from dateutil.relativedelta import relativedelta
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.reanalysis import era5
from sheerwater.utils import dask_remote, get_grid, get_variable, lon_base_change, regrid, roll_and_agg, shift_by_days
from sheerwater.interfaces import forecast as sheerwater_forecast, spatial


@dask_remote
@timeseries(timeseries=['start_date', 'model_issuance_date'])
@cache(cache=False,
       cache_args=['variable', 'forecast_type', 'run_type', 'time_group', 'grid'],
       backend_kwargs={'chunking': {"lat": 121, "lon": 240, "lead_time": 46,
                                    "start_date": 29, "start_year": 29,
                                    "model_issuance_date": 1}})
def ifs_extended_range_raw(start_time, end_time, variable, forecast_type,  # noqa ARG001
                           run_type='average', time_group='weekly', grid="global1_5"):
    """Fetches IFS extended range forecast data from the WeatherBench2 dataset.

    Args:
        start_time (str): The start date to fetch data for.
        end_time (str): The end date to fetch.
        variable (str): The weather variable to fetch.
        forecast_type (str): The type of forecast to fetch. One of "forecast" or "reforecast".
        run_type (str): The type of run to fetch. One of:
            - average: to download the averaged of the perturbed runs
            - perturbed: to download all perturbed runs
            - [int 0-50]: to download a specific  perturbed run
        time_group (str): The time grouping to use. One of: "daily", "weekly", "biweekly"
        grid (str): The grid resolution to fetch the data at. One of:
            - global1_5: 1.5 degree global grid
    """
    if grid != 'global1_5':
        raise NotImplementedError("Only global 1.5 degree grid is implemented.")

    forecast_str = "-reforecast" if forecast_type == "reforecast" else ""
    run_str = "_ens_mean" if run_type == "average" else ""
    avg_str = "-avg" if time_group == "daily" else "_avg"  # different naming for daily
    time_str = "" if time_group == "daily" else "-weekly" if time_group == "weekly" else "-biweekly"
    file_str = f'ifs-ext{forecast_str}-full-single-level{time_str}{avg_str}{run_str}.zarr'
    filepath = f'gs://weatherbench2/datasets/ifs_extended_range/{time_group}/{file_str}'

    # Pull the google dataset
    ds = xr.open_zarr(filepath, decode_timedelta=True, chunks={})

    # Select the right variable
    var = get_variable(variable, 'ecmwf_ifs_er')
    ds = ds[var].to_dataset()
    ds = ds.rename_vars(name_dict={var: variable})

    # Convert local dataset naming and units
    ds = ds.rename({'latitude': 'lat', 'longitude': 'lon', 'prediction_timedelta': 'lead_time'})
    if run_type != 'average':
        ds = ds.rename({'number': 'member'})
    if forecast_type == 'reforecast':
        ds = ds.rename({'forecast_time': 'start_date'})
        ds = ds.drop('time')
    else:
        ds = ds.rename({'time': 'start_date'})

    ds = ds.drop_vars('valid_time')

    # If a specific run, select
    if isinstance(run_type, int):
        ds = ds.sel(member=run_type)
    return ds


@dask_remote
@timeseries(timeseries=['start_date'])
@spatial()
@cache(cache_args=['variable', 'forecast_type', 'run_type', 'time_group', 'grid'],
       cache_disable_if={'grid': 'global1_5'},
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "lead_time": 1,
                        "start_date": 1000, "hindcast_year": 1,
                        "member": 1},
           'chunk_by_arg': {
               'grid': {
                   # A note: a setting where time is in groups of 200 works better for regridding tasks,
                   # but is less good for storage.
                   'global0_25': {"lat": 721, "lon": 1440, "start_date": 30}
               },
           }
})
def ifs_extended_range(start_time, end_time, variable, forecast_type,
                       run_type='average', time_group='daily',
                       grid="global1_5", mask=None, region='global'):  # noqa: ARG001
    """Fetches IFS extended range forecast and reforecast data from the WeatherBench2 dataset.

    Args:
        start_time (str): The start date to fetch data for.
        end_time (str): The end date to fetch.
        variable (str): The weather variable to fetch.
        forecast_type (str): The type of forecast to fetch. One of "forecast" or "reforecast".
        run_type (str): The type of run to fetch. One of:
            - average: to download the averaged of the perturbed runs
            - perturbed: to download all perturbed runs
            - [int 0-50]: to download a specific  perturbed run
        time_group (str): The time grouping to use. One of: "daily", "weekly", "biweekly"
        grid (str): The grid resolution to fetch the data at. One of:
            - global1_5: 1.5 degree global grid
        mask: Spatial mask to apply.
        region: Region to fetch data for.
    """
    """IRI ECMWF average forecast with regridding."""
    ds = ifs_extended_range_raw(start_time, end_time, variable, forecast_type,
                                run_type, time_group=time_group, grid='global1_5')
    # Convert to base180 longitude
    ds = lon_base_change(ds, to_base="base180")

    if variable in ['tmp2m', 'tmax2m', 'tmin2m']:
        ds[variable] = ds[variable] - 273.15
        ds.attrs.update(units='C')
    elif variable == 'precip':
        ds[variable] = ds[variable] * 1000.0
        ds.attrs.update(units='mm')
        ds = np.maximum(ds, 0)
    elif variable == 'ssrd':
        ds.attrs.update(units='Joules/m^2')
        ds = np.maximum(ds, 0)
    if grid == 'global1_5':
        return ds

    _, _, size, _ = get_grid(grid)
    if size < 1.5:
        raise NotImplementedError("Unable to regrid ECMWF smaller than 1.5x1.5")
    if forecast_type == 'reforecast':
        raise NotImplementedError("Regridding reforecast data should be done with extreme care. It's big.")

    # Need all lats / lons in a single chunk to be reasonable
    chunks = {'lat': 121, 'lon': 240, 'lead_time': 1}
    if run_type == 'perturbed':
        chunks['member'] = 1
        chunks['start_date'] = 200
    else:
        chunks['start_date'] = 200
    ds = ds.chunk(chunks)
    # Need all lats / lons in a single chunk for the output to be reasonable
    ds = regrid(ds, grid, base='base180', method='conservative',
                output_chunks={"lat": 721, "lon": 1440}, region=region)
    return ds


@dask_remote
def _ecmwf_ifs_er_unified(start_time, end_time, variable, agg_days, prob_type='deterministic',
                          grid="global1_5", mask='lsm', region="global", reforecast=False):  # noqa: ARG001
    """Unified API accessor for ECMWF raw and debiased forecasts."""
    # The earliest and latest forecast dates for the set of all leads
    # ECMWF extended range forecasts have 46 days, so we shift to include all forecasters who could
    # overlaps with the start and end period
    forecast_start = shift_by_days(start_time, -46) if start_time is not None else None
    forecast_end = shift_by_days(end_time, 46) if end_time is not None else None

    run_type = 'perturbed' if prob_type == 'probabilistic' else 'average'
    forecast_type = 'reforecast' if reforecast else 'forecast'
    ds = ifs_extended_range(forecast_start, forecast_end, variable, run_type=run_type, forecast_type=forecast_type,
                            grid=grid, mask=mask, region=region)

    ds = roll_and_agg(ds, agg=agg_days, agg_col='lead_time', agg_fn='mean')

    # Assign probability label
    prob_label = prob_type if prob_type == 'deterministic' else 'ensemble'
    ds = ds.assign_attrs(prob_type=prob_label)
    if 'spatial_ref' in ds.variables:
        ds = ds.drop_vars('spatial_ref')

    # Rename to standard naming
    ds = ds.rename({'start_date': 'init_time', 'lead_time': 'prediction_timedelta'})
    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'lead_time': 1, 'member': 1}})
def ecmwf_ifs_er(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic',
                 grid='global1_5', mask='lsm', region="global", reforecast=False, debiaser=None, debiaser_options=None):
    """Standard format forecast data for ECMWF forecasts."""
    return _ecmwf_ifs_er_unified(start_time=start_time, end_time=end_time, variable=variable,
                                 agg_days=agg_days, prob_type=prob_type,
                                 grid=grid, mask=mask, region=region, reforecast=reforecast)


@dask_remote
@sheerwater_forecast()
@cache(cache=False, cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'lead_time': 1, 'member': 1}})
def ecmwf_ifs_er_debiased(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic',
                          grid='global1_5', mask='lsm', region="global", reforecast=False):
    """Standard format forecast data for ECMWF forecasts."""
    return ecmwf_ifs_er(start_time=start_time, end_time=end_time, variable=variable,
                                 agg_days=agg_days, prob_type=prob_type,
                                 grid=grid, mask=mask, region=region, debiaser='ecmwf_mean')
