"""Cahable Grafana tables for metrics."""
import xarray as xr
import pandas as pd
import numpy as np

from nuthatch import cache, config_parameter
from sheerwater.utils import dask_remote
from sheerwater.metrics import metric, metric_event_series

from google.cloud import secretmanager


@config_parameter('password', location='root', secret=True)
def postgres_write_password():
    """Get a postgres write password."""
    client = secretmanager.SecretManagerServiceClient()

    response = client.access_secret_version(
        request={"name": "projects/750045969992/secrets/postgres-write-password/versions/latest"})
    key = response.payload.data.decode("UTF-8")

    return key


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable',   'forecast', 'truth', 'agg_days',
                   'metric_name',  'metric_kwargs', 'lead_days',
                   'time_grouping', 'grid', 'region'], backend='sql', backend_kwargs={'hash_table_name': True})
def forecast_metric_points(start_time, end_time, variable,
                           forecast, truth, agg_days, metric_name,
                           metric_kwargs=None, lead_days=7,
                           time_grouping=None, grid='global1_5',
                           region='global'):

    # Match advanced_metrics: dry-spell score is forecastvalue when scoring
    # observed events, obsvalue when scoring forecast-triggered events.
    mk = metric_kwargs or {}
    if 'early_season_accumulation' in metric_name:
        stat = "mae"
    elif 'big_rain_days' in metric_name or 'extreme_rain_days' in metric_name:
        stat = "smape"
    elif 'in_season_dry_spell' in metric_name:
        if mk.get('forecast_filter') and not mk.get('obs_filter'):
            stat = "obsvalue"
        elif mk.get('obs_filter') and not mk.get('forecast_filter'):
            stat = "forecastvalue"
        else:
            raise ValueError(
                "in_season_dry_spell requires exactly one of forecast_filter/obs_filter True"
            )
    else:
        raise ValueError(f"Metric {metric_name} is not supported")

    # Get the metric. Some combos are unsupported (e.g. early-season with
    # forecast_filter on short-lead models needing 120 lead days) — skip them.
    try:
        ds = metric(start_time, end_time, variable,
                    agg_days=agg_days, forecast=forecast, truth=truth,
                    metric_name=metric_name, metric_kwargs=metric_kwargs,
                    time_grouping=time_grouping, spatial=True,
                    grid=grid, region=region, recompute=False)
    except ValueError as e:
        print(f"Skipping forecast_metric_points ({metric_name}, {forecast}, "
              f"{region}, lead={lead_days}, kwargs={mk}): {e}")
        return None

    # Select the correct lead in days. Some forecasts only expose a subset of
    # leads (e.g. climatology / short-range models); skip missing ones.
    target_lead = pd.Timedelta(days=lead_days)
    try:
        ds = ds.sel(prediction_timedelta=target_lead)
    except KeyError:
        available = list(pd.to_timedelta(ds.prediction_timedelta.values))
        print(f"Lead {lead_days}d not found in metric (available={available}) "
              f"for {forecast}/{region}/{metric_name} - returning None")
        return None

    # convert to dataframe
    ds = ds.drop_vars([c for c in ds.coords if c not in ds.dims])
    if stat not in ds:
        print(
            f"Expected '{stat}' in metric output for {metric_name} "
            f"(kwargs={mk}); available: {list(ds.data_vars)} - returning None"
        )
        return None
    # rename the statistic to "value" so it can be handled consistently in dashboard
    ds = ds[stat].rename("value")
    df = ds.to_dataframe()
    df = df.dropna(subset=["value"], how='all')
    df = df.reset_index()
    return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable',   'forecast', 'truth',
                   'metric_name',  'metric_kwargs', 'lead_days',
                   'time_grouping', 'grid', 'region'], backend='sql', backend_kwargs={'hash_table_name': True})
def event_list(start_time, end_time, variable,
               forecast, truth, agg_days, metric_name,
               metric_kwargs=None, lead_days=7,
               time_grouping=None, grid='global1_5',
               region='global'):

    try:
        ds = metric_event_series(start_time, end_time, variable,
                                 agg_days=agg_days, forecast=forecast, truth=truth,
                                 metric_name=metric_name, metric_kwargs=metric_kwargs,
                                 time_grouping=time_grouping, spatial=True,
                                 grid=grid, region=region)
    except ValueError as e:
        print(f"Skipping event_list ({metric_name}, {forecast}, "
              f"{region}, lead={lead_days}, kwargs={metric_kwargs}): {e}")
        return None

    # get the variable name of interest - we assume it is the first
    var_name = list(ds.data_vars)[0]
    # Select lead; skip if this forecast does not have that lead.
    target_lead = pd.Timedelta(days=lead_days)
    try:
        ds = ds.sel(prediction_timedelta=target_lead).drop_vars('prediction_timedelta')
    except KeyError:
        available = list(pd.to_timedelta(ds.prediction_timedelta.values))
        print(f"Lead {lead_days}d not found in event series (available={available}) "
              f"for {forecast}/{region}/{metric_name} - returning None")
        return None
    ds = ds[var_name].chunk({'time': -1})

    # collect lists of event times and metric values
    times = ds.time.values

    def collect_nonnans(arr):
        mask = ~np.isnan(arr)
        return times[mask], arr[mask]
    valid_times, valid_values = xr.apply_ufunc(collect_nonnans, ds.load(), input_core_dims=[['time']], output_core_dims=[[], []],
                                               vectorize=True, output_dtypes=[object, object])

    # convert results to a dataframe
    df_times = valid_times.rename('time').to_dataframe().reset_index()
    df_values = valid_values.rename(var_name).to_dataframe().reset_index()
    # remove locations with no event times
    df_times = df_times[df_times['time'].apply(len) > 0].reset_index(drop=True)
    df = df_times.merge(df_values, on=['lat', 'lon'])
    df = df.explode(['time', var_name], ignore_index=True)
    # for consistency, rename the variable to "value"
    df = df.rename(columns={var_name: "value"})
    # convert to good types for sql
    df = df.astype({'lat': 'float', 'lon': 'float', 'time': 'datetime64[ns]', 'value': 'float'})
    return df
