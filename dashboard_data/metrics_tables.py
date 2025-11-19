"""Cahable Grafana tables for metrics."""
import xarray as xr
import numpy as np

from nuthatch import cache
from sheerwater.utils import dask_remote, start_remote
from sheerwater.metrics import metric


@dask_remote
def _metric_table(start_time, end_time, variable,
                  truth, metric_name, agg_days, forecasts,
                  time_grouping=None,
                  grid='global1_5', region='global'):
    """Internal function to compute summary metrics table for flexible leads and forecasts."""
    # For the time grouping we are going to store it in an xarray with dimensions
    # forecast and time, which we instantiate
    results_ds = xr.Dataset(coords={'forecast': forecasts, 'time': None})

    # Make sure agg_days is a list
    if not isinstance(agg_days, list):
        agg_days = [agg_days]

    for forecast in forecasts:
        for _, agg in enumerate(agg_days):
            print(
                f"Running for {forecast} and {agg} with variable {variable}, "
                f"metric {metric_name}, grid {grid}, region {region}, "
                f"time grouping {time_grouping}")
            # First get the value without the baseline
            try:
                ds = metric(start_time, end_time, variable,
                            agg_days=agg, forecast=forecast, truth=truth,
                            metric_name=metric_name, time_grouping=time_grouping, spatial=False,
                            grid=grid, region=region, recompute=False, retry_null_cache=True)
            except NotImplementedError:
                ds = None

            if 'prediction_timedelta' in ds.coords and len(agg_days) > 1:
                raise ValueError("Cannot run multiple aggregation days in the same table for a forecast with leads.")

            if ds:
                ds = ds.rename({variable: agg})
                ds = ds.expand_dims({'forecast': [forecast]}, axis=0)
                # For climatology forecasts, we need to expand the prediction_timedelta coordinate
                if 'prediction_timedelta' in ds.coords and 'climatology' in forecast:
                    ds = ds.squeeze('prediction_timedelta')
                    ds = ds.expand_dims({'lead_day': np.arange(100)})  # 100 lead days for climatology forecasts
                elif 'prediction_timedelta' in ds.coords:
                    lead_values = ds.prediction_timedelta.values / np.timedelta64(1, 'D')
                    ds = ds.assign_coords(prediction_timedelta=lead_values)
                    ds = ds.rename({'prediction_timedelta': 'lead_day'})
                # results_ds = xr.combine_by_coords([results_ds, ds], combine_attrs='override')
                results_ds = results_ds.merge(ds)

    if not time_grouping:
        results_ds = results_ds.reset_coords('time', drop=True)

    results_ds = results_ds.drop_vars([var for var in results_ds.coords if var not in results_ds.dims], errors='ignore')
    df = results_ds.to_dataframe()

    df = df.reset_index().rename(columns={'index': 'forecast'})

    if 'time' in df.columns:
        order = ['time', 'forecast'] + agg_days
    else:
        order = ['forecast'] + agg_days

    # Reorder the columns if necessary
    df = df[order]

    return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
       backend='sql',
       backend_kwargs={
           'hash_postgres_table_name': True,
       })
def weekly_metric_table(start_time, end_time, variable,
                        truth, metric_name, time_grouping=None,
                        grid='global1_5', region='global'):
    """Runs metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['fuxi', 'salient', 'ecmwf_ifs_er', 'ecmwf_ifs_er_debiased', 'climatology_2015',
                 'climatology_trend_2015', 'climatology_rolling', 'gencast', 'graphcast']
    df = _metric_table(start_time, end_time, variable, truth, metric_name,
                       agg_days=7, forecasts=forecasts,
                       time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
       backend='sql')
def monthly_metric_table(start_time, end_time, variable,
                         truth, metric_name, time_grouping=None,
                         grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['salient', 'climatology_2015']
    df = _metric_table(start_time, end_time, variable, truth, metric_name,
                       agg_days=30, forecasts=forecasts,
                       time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
       backend='sql')
def ground_truth_metric_table(start_time, end_time, variable,
                              truth, metric_name, time_grouping=None,
                              grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['era5', 'chirps', 'imerg', 'cbam']
    agg_days = [1, 7, 14, 30]
    df = _metric_table(start_time, end_time, variable, truth, metric_name,
                       agg_days, forecasts,
                       time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
       backend='sql')
def biweekly_metric_table(start_time, end_time, variable,
                          truth, metric_name, time_grouping=None,
                          grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['perpp', 'ecmwf_ifs_er', 'ecmwf_ifs_er_debiased', 'climatology_2015',
                 'climatology_trend_2015', 'climatology_rolling']
    df = _metric_table(start_time, end_time, variable, truth, metric_name,
                       agg_days=14, forecasts=forecasts,
                       time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df
