"""Cahable Grafana tables for metrics."""
import xarray as xr
import numpy as np
import pandas as pd

from nuthatch import cache, config_parameter
from sheerwater.utils import dask_remote
from sheerwater.metrics import metric

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
                   'time_grouping', 'grid', 'region'])
def forecast_metric_map(start_time, end_time, variable,
                        forecast, truth, agg_days, metric_name,
                        metric_kwargs=None, lead_days=7,
                        time_grouping=None, grid='global1_5',
                        region='global'):

    # Get the metric
    ds = metric(start_time, end_time, variable,
                agg_days=agg_days, forecast=forecast, truth=truth,
                metric_name=metric_name, metric_kwargs=metric_kwargs,
                time_grouping=time_grouping, spatial=True,
                grid=grid, region=region, recompute=False, retry_null_cache=False,
                fail_if_no_cache=True)

    # Select the correct lead in days
    target_lead = pd.Timedelta(days=lead_days)
    if target_lead in ds.prediction_timedelta:
        ds = ds.sel(prediction_timedelta=target_lead)
    else:
        print("Lead not found in metric - returning None")
        return None

    return ds


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable',   'forecast', 'truth', 'agg_days',
                   'metric_name',  'metric_kwargs',
                   'time_grouping', 'grid', 'region'])
def ground_truth_metric_map(start_time, end_time, variable,
                        forecast, truth, agg_days, metric_name,
                        metric_kwargs=None,
                        time_grouping=None, grid='global1_5',
                        region='global'):

    # Get the metric
    ds = metric(start_time, end_time, variable,
                agg_days=agg_days, forecast=forecast, truth=truth,
                metric_name=metric_name, metric_kwargs=metric_kwargs,
                time_grouping=time_grouping, spatial=True,
                grid=grid, region=region, recompute=False, retry_null_cache=False,
                fail_if_no_cache=True)

    return ds


