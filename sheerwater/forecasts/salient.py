"""Pulls Salient Predictions S2S forecasts from the Salient API."""
import numpy as np
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, get_variable, regrid, shift_by_days, roll_and_agg
from sheerwater.interfaces import forecast as sheerwater_forecast, spatial


@dask_remote
def salient_blend_raw(variable, timescale="sub-seasonal", version="v9"):  # noqa: ARG001
    """Salient function that returns data from GCP mirror.

    Args:
        variable (str): The weather variable to fetch.
        timescale (str): The timescale of the forecast. One of:
            - sub-seasonal
            - seasonal
            - long-range
        version (str): The version of the Salient data to use.

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
@spatial()
@cache(cache_args=['variable', 'timescale', 'grid'],
       backend_kwargs={
           'chunking': {"lat": 721, "lon": 1440, "forecast_date": 30, 'lead': 1, 'quantiles': 1}
})
def salient_blend(start_time, end_time, variable, timescale="sub-seasonal",  # noqa: ARG001
                  grid="global0_25", mask=None, region='global'):  # noqa: ARG001
    """Processed Salient forecast files."""
    ds = salient_blend_raw(variable, timescale=timescale)
    ds = ds.dropna('forecast_date', how='all')

    # Regrid the data
    ds = regrid(ds, grid, base='base180', method='conservative', region=region)
    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'lead_time': 1, 'member': 1}})
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

    ds = salient_blend(forecast_start, forecast_end, variable, timescale=timescale, grid=grid, mask=mask, region=region)
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


@dask_remote
@timeseries(timeseries='forecast_date')
@spatial()
@cache(cache_args=['variable', 'grid'],
       backend_kwargs={
           'chunking': {"lat": 73, "lon": 77, "forecast_date": 4, 'lead': 7, 'sample': 200}
})
def salient_gem_raw(start_time, end_time, variable, grid='global0_25', mask=None, region='eastern_africa'):  # noqa: ARG001
    # Your credentials are needed to access the store
    storage_options = dict(
        key="8121a8558bc21d1452c22291f8853bc8",
        secret="10c9d8a28aa65d48a9b211cca19f9e1a17c23d3950643dc3ad0969fd93fb6113",
        client_kwargs={"endpoint_url": "https://f9921545a0bfa802eb169b5408437b5f.r2.cloudflarestorage.com"},
        s3_additional_kwargs={"ACL": "private"}
    )
    fs_kwargs = {"storage_options": storage_options}
    ds = xr.open_zarr("s3://nimbus-gemv2/east_africa.zarr", **fs_kwargs)

    var = get_variable(variable, 'salient')
    ds = ds[var].to_dataset()
    ds = ds.rename({var: variable})

    # Regrid the data
    ds = regrid(ds, grid, base='base180', method='conservative', region=region)
    return ds


@dask_remote
@timeseries(timeseries='forecast_date')
@spatial()
@cache(cache_args=['variable', 'grid'],
       cache_disable_if={'agg_days': 1},
       backend_kwargs={
           'chunking': {"lat": 20, "lon": 20, "forecast_date": 30, 'lead': 126, 'sample': 200}
})
def salient_gem_rolled(start_time, end_time, variable, agg_days=7, grid='global0_25',
                       mask=None, region='eastern_africa'):
    """Salient GEM rolled and aggregated."""
    ds = salient_gem_raw(start_time, end_time, variable, grid=grid, mask=mask, region=region)
    ds = roll_and_agg(ds, agg=agg_days, agg_col="lead", agg_fn="mean")
    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'lead_time': 1, 'member': 1}})
def salient_gem(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic',
              grid='global1_5', mask='lsm', region="eastern_africa"):  # noqa: ARG001
    """Final Salient GEM interface."""
    if prob_type != 'deterministic':
        raise NotImplementedError("Only deterministic forecast implemented for graphcast")

    # Get the data with the right days - the forecast is 126 days long, so pull before and after
    forecast_start = shift_by_days(start_time, -126) if start_time is not None else None
    forecast_end = shift_by_days(end_time, 126) if end_time is not None else None

    # Get the data with the right days
    ds = salient_gem_raw(forecast_start, forecast_end, variable, agg_days=agg_days, grid=grid, mask=mask, region=region)
    if prob_type == 'deterministic':
        ds = ds.mean(dim='samples')
        ds = ds.reset_coords("samples", drop=True)
        ds = ds.assign_attrs(prob_type="deterministic")
    elif prob_type == "probabilistic":
        ds = ds.rename({'samples': 'member'})
        ds = ds.assign_attrs(prob_type="ensemble")
    else:
        raise ValueError("Invalid probabilistic type")

    # Rename to standard naming
    ds = ds.rename({'time': 'init_time', 'lead_time': 'prediction_timedelta'})

    return ds
