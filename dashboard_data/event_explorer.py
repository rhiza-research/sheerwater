"""Cahable Grafana tables for metrics."""
import xarray as xr
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
                   'time_grouping', 'grid', 'region'], backend='sql', backend_kwargs={'hash_table_name': True})
def forecast_metric_points(start_time, end_time, variable,
                        forecast, truth, agg_days, metric_name,
                        metric_kwargs=None, lead_days=7,
                        time_grouping=None, grid='global1_5',
                        region='global'):

    if 'early_season_accumulation' in metric_name:
        stat = "mae"
    elif 'big_rain_days' in metric_name:
        stat = "smape"
    elif 'in_season_dry_spell' in metric_name:
        stat = "mae"
    else:
        raise ValueError(f"Metric {metric_name} is not supported")

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
    
    import pdb; pdb.set_trace()
    # convert to dataframe
    ds = ds.drop_vars([c for c in ds.coords if c not in ds.dims])
    # rename the statistic to "value" so it can be handled consistently in dashboard
    ds = ds[stat].rename("value")
    df = ds.to_dataframe()
    df = df.dropna(subset=["value"], how='all')
    df = df.reset_index()
    return df