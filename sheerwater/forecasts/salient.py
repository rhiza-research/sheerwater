"""Pulls Salient Predictions S2S forecasts from the Salient API."""
import numpy as np
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, get_variable, regrid, shift_by_days
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
       cache_args=['variable', 'agg_days', 'event', 'event_kwargs', 'processors', 'processor_kwargs',
                   'lookback_source', 'densify', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'lead_time': 1, 'member': 1}})
def salient(start_time=None, end_time=None, variable="precip", agg_days=7, prob_type='deterministic',
            event=None, event_kwargs=None,  # noqa: ARG001
            processors=None, processor_kwargs=None,  # noqa: ARG001
            lookback_source=None, densify=False,  # noqa: ARG001
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

    # Assign agg days so decorator knows this is already aggregated
    ds = ds.assign_attrs(agg_days=agg_days)

    return ds


@dask_remote
@timeseries(timeseries='forecast_date')
@spatial()
@cache(cache=False,
       cache_args=['variable'],
       backend_kwargs={
           'chunking': {"lat": 73, "lon": 77, "forecast_date": 4, 'lead': 7, 'sample': 200}
})
def salient_gem_raw(start_time, end_time, variable, # noqa: ARG001
                    mask=None, region=None):  # noqa: ARG001
    """Salient GEM raw data."""
    ds = xr.open_zarr("gs://sheerwater-datalake/salient-data/gem/east_africa.zarr")
    var = get_variable(variable, 'salient')
    ds = ds[var].to_dataset()
    ds = ds.rename({var: variable})

    return ds

@dask_remote
@timeseries(timeseries='forecast_date')
@spatial()
@cache(cache_args=['variable', 'grid', 'prob_type'],
       backend_kwargs={
           'chunking': {"lat": 73, "lon": 77, "forecast_date": 50, 'lead': 125}
       },
       cache_disable_if={
           'prob_type': 'probabilistic',
           'grid': 'global0_25'
       })
def salient_gem_processed(start_time, end_time, variable, grid, prob_type='deterministic',
                          mask=None, region=None): # noqa: ARG001
    """A cache of salient GEM that means the samples."""
    # Get the data with the right days
    ds = salient_gem_raw(start_time, end_time, variable, mask=mask, region=region)
    if prob_type == 'deterministic':
        ds = ds.mean(dim='sample')
        ds = ds.assign_attrs(prob_type="deterministic")
    elif prob_type == "probabilistic":
        ds = ds.rename({'sample': 'member'})
        # We just can't benchmark 200 members - down to 50. As a stride
        # incase they have some underlying order (?)
        ds = ds.isel(member=slice(0, None, 4))
        ds = ds.assign_attrs(prob_type="ensemble")
    else:
        raise ValueError("Invalid probabilistic type")

    if 'spatial_ref' in ds:
        ds= ds.reset_coords('spatial_ref')

    if 'number' in ds:
        ds= ds.reset_coords('number')

    if grid != 'global0_25':
        # Regrid the data
        ds = regrid(ds, grid, base='base180', method='conservative', region=region)

    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'event', 'event_kwargs', 'processors', 'processor_kwargs',
                   'lookback_source', 'densify', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 365, 'lead_time': 1, 'member': 1}})
def salient_gem(start_time=None, end_time=None, variable="precip", agg_days=1,  # noqa: ARG001
                prob_type='deterministic',
                event=None, event_kwargs=None,  # noqa: ARG001
                processors=None, processor_kwargs=None,  # noqa: ARG001
                lookback_source=None, densify=False,  # noqa: ARG001
                grid='global1_5', mask='lsm', region="eastern_africa"):  # noqa: ARG001
    """Final Salient GEM interface."""
    # Get the data with the right days - the forecast is 126 days long, so pull before and after
    forecast_start = shift_by_days(start_time, -126) if start_time is not None else None
    forecast_end = shift_by_days(end_time, 126) if end_time is not None else None

    ds = salient_gem_processed(forecast_start, forecast_end, variable, grid=grid,
                               prob_type=prob_type, mask=mask, region=region)

    # Rename to standard naming
    ds = ds.rename({'forecast_date': 'init_time', 'lead': 'prediction_timedelta'})

    return ds
