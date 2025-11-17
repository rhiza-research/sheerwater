"""Cahable Grafana tables for metrics."""
import xarray as xr
import numpy as np

from sheerwater_benchmarking.utils import cacheable, dask_remote, start_remote
from sheerwater_benchmarking.metrics import metric

# Lead labels for standrad aggregrations
lead_dict = {
    7: ('weekly',
        ['week1', 'week2', 'week3', 'week4', 'week5', 'week6'],
        [np.timedelta64(0, 'D'), np.timedelta64(7, 'D'), np.timedelta64(14, 'D'), np.timedelta64(21, 'D'), np.timedelta64(28, 'D'), np.timedelta64(35, 'D')]),
    14: ('biweekly',
         ['weeks12', 'weeks34', 'weeks56'],
         [np.timedelta64(0, 'D'), np.timedelta64(14, 'D'), np.timedelta64(28, 'D')]),
    30: ('monthly',
         ['month1', 'month2', 'month3'],
         [np.timedelta64(0, 'D'), np.timedelta64(30, 'D'), np.timedelta64(60, 'D')]),
    90: ('quarterly',
         ['quarter1', 'quarter2', 'quarter3', 'quarter4'],
         [np.timedelta64(0, 'D'), np.timedelta64(90, 'D'), np.timedelta64(180, 'D'), np.timedelta64(270, 'D')]),
}


def get_lead_labels(agg_values):
    lead_labels = []
    try:
        if len(agg_values) == 1:
            return lead_dict[agg_values[0]][1]
        else:
            for agg in agg_values:
                lead_labels.append(lead_dict[agg][0])
    except KeyError:
        raise ValueError(f"Invalid aggregation days {agg}")
    return lead_labels


@dask_remote
def _summary_metrics_table(start_time, end_time, variable,
                           truth, metric_name, agg_days, forecasts,
                           time_grouping=None,
                           grid='global1_5', region='global'):
    """Internal function to compute summary metrics table for flexible leads and forecasts."""
    # For the time grouping we are going to store it in an xarray with dimensions
    # forecast and time, which we instantiate
    results_ds = xr.Dataset(coords={'forecast': forecasts, 'time': None})

    # Agg days can either by a single value or a list of values.
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
                            grid=grid, region=region,
                            retry_null_cache=True)
            except NotImplementedError:
                ds = None

            if 'prediction_timedelta' in ds.coords and len(agg_days) > 1:
                raise ValueError("Cannot run multiple aggregation days in the same table for a forecast with leads.")

            if ds:
                ds = ds.expand_dims({'forecast': [forecast]}, axis=0)
                results_ds = results_ds.merge(ds)

    if not time_grouping:
        results_ds = results_ds.reset_coords('time', drop=True)

    if len(agg_days) > 1:
        agg_values = agg_days
    else:
        agg_values = results_ds.prediction_timedelta.values

    lead_labels = get_lead_labels(agg_values)

    df = results_ds.to_dataframe()

    df = df.reset_index().rename(columns={'index': 'forecast'})

    if 'time' in df.columns:
        order = ['time', 'forecast'] + lead_labels
    else:
        order = ['forecast'] + lead_labels

    # Reorder the columns if necessary
    df = df[order]

    return df


@dask_remote
@cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
           hash_postgres_table_name=True,
           backend='postgres',
           cache=True,
           primary_keys=['time', 'forecast'])
def summary_metrics_table(start_time, end_time, variable,
                          truth, metric_name, time_grouping=None,
                          grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    # forecasts = ['fuxi', 'salient', 'ecmwf_ifs_er', 'ecmwf_ifs_er_debiased', 'climatology_2015',
    #             #  'climatology_trend_2015', 'climatology_rolling', 'gencast', 'graphcast']
    forecasts = ['ecmwf_ifs_er_debiased', 'climatology_2015']
    df = _summary_metrics_table(start_time, end_time, variable, truth, metric_name,
                                agg_days=7, forecasts=forecasts,
                                time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
           cache=True,
           primary_keys=['time', 'forecast'])
def seasonal_metrics_table(start_time, end_time, variable,
                           truth, metric_name, time_grouping=None,
                           grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['salient', 'climatology_2015']
    df = _summary_metrics_table(start_time, end_time, variable, truth, metric_name,
                                agg_days=30, forecasts=forecasts,
                                time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
           cache=True,
           primary_keys=['time', 'forecast'])
def station_metrics_table(start_time, end_time, variable,
                          truth, metric_name, time_grouping=None,
                          grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['era5', 'chirps', 'imerg', 'cbam']
    agg_days = [1, 7, 14, 30]
    df = _summary_metrics_table(start_time, end_time, variable, truth, metric_name,
                                agg_days, forecasts,
                                time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
           cache=True)
def biweekly_summary_metrics_table(start_time, end_time, variable,
                                   truth, metric_name, time_grouping=None,
                                   grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['perpp', 'ecmwf_ifs_er', 'ecmwf_ifs_er_debiased', 'climatology_2015',
                 'climatology_trend_2015', 'climatology_rolling']
    df = _summary_metrics_table(start_time, end_time, variable, truth, metric_name,
                                agg_days=14, forecasts=forecasts,
                                time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster')
    start_time = "2016-01-01"
    end_time = "2022-12-31"
    variable = "precip"
    truth = "era5"
    metric_name = "mae"
    time_grouping = None
    grid = "global1_5"
    region = "global"
    df = summary_metrics_table(start_time, end_time, variable, truth, metric_name, time_grouping, grid, region)
    print(df)
    df = seasonal_metrics_table(start_time, end_time, variable, truth, metric_name, time_grouping, grid, region)
    print(df)
    df = station_metrics_table(start_time, end_time, variable, truth, metric_name, time_grouping, grid, region)
    print(df)
    df = biweekly_summary_metrics_table(start_time, end_time, variable, truth, metric_name, time_grouping, grid, region)
    print(df)
