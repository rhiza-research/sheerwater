"""Cahable Grafana tables for metrics."""
import xarray as xr
import numpy as np
import pandas as pd

from nuthatch import cache, config_parameter
from sheerwater.utils import dask_remote, regrid
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

    value_max = None
    target_grid = grid
    if metric_name == 'early_season_accumulation-30d':
        value_max = 45
        target_grid = 'global0_25'
    elif metric_name == 'big_rain_days':
        value_max = 0.45
        target_grid = 'global0_25'
    elif metric_name == 'extreme_rain_days':
        value_max = 0.45
        target_grid = 'global0_25'
    elif metric_name == 'in_season_dry_spell':
        value_max = 30

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

    if value_max:
        ds = xr.where(ds > value_max, value_max, ds)

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

    value_max = None
    if metric_name == 'early_season_accumulation-30d':
        value_max = 45
    elif metric_name == 'big_rain_days':
        value_max = 0.45
    elif metric_name == 'in_season_dry_spell':
        value_max = 30

    # Get the metric
    ds = metric(start_time, end_time, variable,
                agg_days=agg_days, forecast=forecast, truth=truth,
                metric_name=metric_name, metric_kwargs=metric_kwargs,
                time_grouping=time_grouping, spatial=True,
                grid=grid, region=region, recompute=False, retry_null_cache=False,
                fail_if_no_cache=True)


    from sheerwater.spatial_subdivisions import get_spatial_subdivision_level, polygon_subdivision_geodataframe
    try:
        country_gdf = polygon_subdivision_geodataframe(level='continent', merged=False)
        country_gdf = country_gdf[country_gdf['region_name'] == 'africa']
    except Exception as e:
        print(f"Error getting country boundaries for region {region}: {e}")
        country_gdf = None

    if value_max:
        ds = xr.where(ds > value_max, value_max, ds)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ds.mae.plot(x='lon', ax=ax)
    country_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5, facecolor='none')
    plt.show()
    return ds
