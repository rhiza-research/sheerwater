"""Cahable Grafana tables for metrics."""
import xarray as xr
import numpy as np

from nuthatch import cache
from sheerwater.utils import dask_remote
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
                # Get the metric name to rename the variable
                if '-' in metric_name:
                    met_name = metric_name.split('-')[0].lower()
                else:
                    met_name = metric_name.lower()
                ds = ds.rename({met_name: agg})

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

    order = ['forecast', 'time_grouping', 'region'] + agg_days

    # Reorder the columns if necessary
    if 'time' in df.columns:
        df = df.rename(columns={'time': 'time_grouping'})
        df['time_grouping'] = df['time_grouping'].map({'M01': 'January',
                                                       'M02': 'February',
                                                       'M03': 'March',
                                                       'M04': 'April',
                                                       'M05': 'May',
                                                       'M06': 'June',
                                                       'M07': 'July',
                                                       'M08': 'August',
                                                       'M09': 'September',
                                                       'M10': 'October',
                                                       'M11': 'November',
                                                       'M12': 'December'})
    else:
        df['time_grouping'] = None

    if 'region' not in df.columns:
        df['region'] = None

    df = df[order]

    return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
       backend='sql', backend_kwargs={'hash_table_name': True})
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
       backend='sql', backend_kwargs={'hash_table_name': True})
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
       backend='sql', backend_kwargs={'hash_table_name': True})
def ground_truth_metric_table(start_time, end_time, variable,
                              truth, metric_name, time_grouping=None,
                              grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['era5', 'chirps_v3', 'chirp_v3', 'imerg_final', 'imerg_late']

    if '-' in metric_name:
        thresh = float(metric_name.split('-')[1])

        # FAR dry spell
        if thresh == 1.5:
            agg_days = [7, 10]
        elif thresh == 6.6:
            agg_days = [3]
        elif thresh == 7.6:
            agg_days = [5]
        elif thresh == 3.6:
            agg_days = [11]
    else:
        agg_days = [1, 5, 7, 10]
    df = _metric_table(start_time, end_time, variable, truth, metric_name,
                       agg_days, forecasts,
                       time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
       backend='sql', backend_kwargs={'hash_table_name': True})
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
