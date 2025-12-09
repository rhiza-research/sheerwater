"""Pulls Salient Predictions S2S forecasts from the Salient API."""
import numpy as np
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.forecasts.forecast_decorator import forecast
from sheerwater.utils import dask_remote, get_variable, regrid, shift_by_days


@dask_remote
def salient_blend_raw(variable, timescale="sub-seasonal"):
    """Salient function that returns data from GCP mirror.

    Args:
        start_time (str): The start date to fetch data for.
        end_time (str): The end date to fetch.
        variable (str): The weather variable to fetch.
        timescale (str): The timescale of the forecast. One of:
            - sub-seasonal
            - seasonal
            - long-range

    """
    # Pull the Salient dataset
    var = get_variable(variable, 'salient')
    filename = f'gs://sheerwater-datalake/salient-data/v9/africa/{var}_{timescale}/blend'
    ds = xr.open_zarr(filename,
                      chunks={'forecast_date': 3, 'lat': 300, 'lon': 316,
                              'lead': 10, 'quantile': 23, 'model': 5})
    ds = ds['vals'].to_dataset()
    ds = ds.rename(vals=variable)
    return ds


@dask_remote
@timeseries(timeseries='forecast_date')
@cache(cache_args=['variable', 'timescale', 'grid'],
       backend_kwargs={
           'chunking': {"lat": 721, "lon": 1440, "forecast_date": 30, 'lead': 1, 'quantiles': 1}
       })
def salient_blend(start_time, end_time, variable, timescale="sub-seasonal", grid="global0_25"):  # noqa: ARG001
    """Processed Salient forecast files."""
    ds = salient_blend_raw(variable, timescale=timescale)
    ds = ds.dropna('forecast_date', how='all')

    # Regrid the data
    ds = regrid(ds, grid, base='base180', method='conservative')
    return ds


@dask_remote
@timeseries()
@forecast
@cache(cache=False)
def salient(start_time=None, end_time=None, variable="precip", agg_days=7, prob_type='deterministic',
            grid='global0_25', mask='lsm', region='africa'):  # noqa: ARG001
    """Standard format forecast data for Salient."""
    lead_params = {
        7: "sub-seasonal",
        30: "seasonal",
        90: "long-range",
    }
    timescale = lead_params.get(agg_days, None)
    if timescale is None:
        raise NotImplementedError(f"Agg days {agg_days} not implemented for Salient.")

    # Get the data with the right days
    forecast_start = shift_by_days(start_time, -366) if start_time is not None else None
    forecast_end = shift_by_days(end_time, 366) if end_time is not None else None

    ds = salient_blend(forecast_start, forecast_end, variable, timescale=timescale, grid=grid)
    if prob_type == 'deterministic':
        # Get the median forecast
        ds = ds.sel(quantiles=0.5)
        # drop the quantiles dimension
        ds = ds.reset_coords("quantiles", drop=True)
        ds = ds.assign_attrs(prob_type="deterministic")
    elif prob_type == "probabilistic":
        # Set an attribute to say this is a quantile forecast
        ds = ds.rename({'quantiles': 'member'})
        ds = ds.assign_attrs(prob_type="quantile")
    else:
        raise ValueError("Invalid probabilistic type")

    # Convert salient lead naming to match our standard
    if timescale == "sub-seasonal":
        ds = ds.assign_coords(prediction_timedelta=('lead', [np.timedelta64(
            i-1, 'W').astype('timedelta64[ns]') for i in ds.lead.values]))
    elif timescale == "long-range":
        ds = ds.assign_coords(prediction_timedelta=('lead', [np.timedelta64(
            (i-1)*120, 'D').astype('timedelta64[ns]') for i in ds.lead.values]))
    elif timescale == "seasonal":
        # TODO: salient's monthly leads are 31 days, but we define them as 30 days
        ds = ds.assign_coords(prediction_timedelta=(
            'lead', [i-np.timedelta64(1, 'D').astype('timedelta64[ns]') for i in ds.lead.values]))
    else:
        raise ValueError(f"Invalid timescale: {timescale}")
    ds = ds.sortby(ds.forecast_date)
    ds = ds.swap_dims({'lead': 'prediction_timedelta'})
    ds = ds.drop_vars('lead')
    ds = ds.rename({'forecast_date': 'init_time'})

    return ds
