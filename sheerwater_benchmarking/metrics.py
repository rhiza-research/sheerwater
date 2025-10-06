"""Verification metrics for forecasters and reanalyses."""
from .metrics_library import metric_factory
from sheerwater_benchmarking.utils import (cacheable, dask_remote,
                                           get_lead_info,
                                           get_datasource_fn)
from sheerwater_benchmarking.climatology import climatology_2020, seeps_wet_threshold, seeps_dry_fraction
import xskillscore
from weatherbench2.metrics import SpatialQuantileCRPS, SpatialSEEPS
import numpy as np
from inspect import signature
import xarray as xr

# Disable scientific notation globally
np.set_printoptions(suppress=True)


@dask_remote
@cacheable(data_type='array',
           cache_args=['start_time', 'end_time', 'variable', 'lead', 'forecast',
                       'truth', 'metric', 'time_grouping', 'spatial', 'grid', 'mask', 'region'],
           chunking={"lat": 121, "lon": 240, "time": -1},
           chunk_by_arg={
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           },
           cache=True)
def grouped_metric(start_time, end_time, variable, lead, forecast, truth,
                   metric, time_grouping=None, spatial=False, grid="global1_5",
                   mask='lsm', region='africa'):
    """Compute a grouped metric for a forecast at a specific lead."""
    # TODO: Delete, keeping around for cachable function atm
    pass


@dask_remote
@cacheable(data_type='array',
           cache_args=['start_time', 'end_time', 'variable', 'lead', 'forecast', 'truth',
                       'metric', 'time_grouping', 'spatial', 'grid', 'mask', 'region'],
           chunking={"lat": 121, "lon": 240, "time": 30, 'region': 300, 'lead_time': -1},
           chunk_by_arg={
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           },
           cache=True)
def grouped_metric_new(start_time, end_time, variable, lead, forecast, truth,
                       metric, time_grouping=None, spatial=False, grid="global1_5",
                       mask='lsm', region='countries'):
    """Compute a grouped metric for a forecast at a specific lead."""
    # Use the metric registry to get the metric class
    cache_kwargs = {
        'start_time': start_time,
        'end_time': end_time,
        'variable': variable,
        'lead': lead,
        'forecast': forecast,
        'truth': truth,
        'time_grouping': time_grouping,
        'spatial': spatial,
        'grid': grid,
        'mask': mask,
        'region': region,
    }
    metric_obj = metric_factory(metric, **cache_kwargs)
    m_ds = metric_obj.compute()
    return m_ds


@dask_remote
@cacheable(data_type='array',
           cache_args=['variable', 'lead', 'forecast', 'truth', 'metric', 'baseline',
                       'time_grouping', 'spatial', 'grid', 'region'],
           cache=False)
def skill_metric(start_time, end_time, variable, lead, forecast, truth,
                 metric, baseline, time_grouping=None, spatial=False, grid="global1_5",
                 region='global'):
    """Compute skill either spatially or as a region summary."""
    try:
        m_ds = grouped_metric(start_time, end_time, variable, lead, forecast,
                              truth, metric, time_grouping, spatial=spatial,
                              grid=grid, region=region)
    except NotImplementedError:
        return None
    if not m_ds:
        return None

    # Get the baseline if it exists and run its metric
    base_ds = grouped_metric(start_time, end_time, variable, lead, baseline,
                             truth, metric, time_grouping, spatial=spatial, grid=grid, region=region)
    if not base_ds:
        raise NotImplementedError("Cannot compute skill for null base")
    print("Got metrics. Computing skill")

    # Compute the skill
    # TODO - think about base metric of 0
    m_ds = (1 - (m_ds/base_ds))
    return m_ds


@dask_remote
def _summary_metrics_table(start_time, end_time, variable,
                           truth, metric, leads, forecasts,
                           time_grouping=None,
                           grid='global1_5', region='global'):
    """Internal function to compute summary metrics table for flexible leads and forecasts."""
    # For the time grouping we are going to store it in an xarray with dimensions
    # forecast and time, which we instantiate
    results_ds = xr.Dataset(coords={'forecast': forecasts, 'time': None})

    for forecast in forecasts:
        for i, lead in enumerate(leads):
            print(f"""Running for {forecast} and {lead} with variable {variable},
                      metric {metric}, grid {grid}, and region {region}""")
            # First get the value without the baseline
            try:
                ds = grouped_metric(start_time, end_time, variable,
                                    lead=lead, forecast=forecast, truth=truth,
                                    metric=metric, time_grouping=time_grouping, spatial=False,
                                    grid=grid, region=region,
                                    retry_null_cache=True)
            except NotImplementedError:
                ds = None

            if ds:
                ds = ds.rename({variable: lead})
                ds = ds.expand_dims({'forecast': [forecast]}, axis=0)
                results_ds = xr.combine_by_coords([results_ds, ds], combine_attrs='override')

    if not time_grouping:
        results_ds = results_ds.reset_coords('time', drop=True)

    df = results_ds.to_dataframe()

    df = df.reset_index().rename(columns={'index': 'forecast'})

    if 'time' in df.columns:
        order = ['time', 'forecast'] + leads
    else:
        order = ['forecast'] + leads

    # Reorder the columns if necessary
    df = df[order]

    return df


@dask_remote
@cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric',
                       'time_grouping', 'grid', 'region'],
           hash_postgres_table_name=True,
           backend='postgres',
           cache=True,
           primary_keys=['time', 'forecast'])
def summary_metrics_table(start_time, end_time, variable,
                          truth, metric, time_grouping=None,
                          grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    if variable == 'rainy_onset' or variable == 'rainy_onset_no_drought':
        forecasts = ['climatology_2015', 'ecmwf_ifs_er', 'ecmwf_ifs_er_debiased',  'fuxi']
        if variable == 'rainy_onset_no_drought':
            leads = ['day1', 'day8', 'day15', 'day20']
        else:
            leads = ['day1', 'day8', 'day15', 'day20', 'day29', 'day36']
    else:
        forecasts = ['fuxi', 'salient', 'ecmwf_ifs_er', 'ecmwf_ifs_er_debiased', 'climatology_2015',
                     'climatology_trend_2015', 'climatology_rolling', 'gencast', 'graphcast']
        leads = ["week1", "week2", "week3", "week4", "week5", "week6"]
    df = _summary_metrics_table(start_time, end_time, variable, truth, metric, leads, forecasts,
                                time_grouping=time_grouping,
                                grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric',
                       'time_grouping', 'grid', 'region'],
           cache=True,
           primary_keys=['time', 'forecast'])
def seasonal_metrics_table(start_time, end_time, variable,
                           truth, metric, time_grouping=None,
                           grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['salient', 'climatology_2015']
    leads = ["month1", "month2", "month3"]
    df = _summary_metrics_table(start_time, end_time, variable, truth, metric, leads, forecasts,
                                time_grouping=time_grouping,
                                grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric',
                       'time_grouping', 'grid', 'region'],
           cache=True,
           primary_keys=['time', 'forecast'])
def station_metrics_table(start_time, end_time, variable,
                          truth, metric, time_grouping=None,
                          grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['era5', 'chirps', 'imerg', 'cbam']
    leads = ["daily", "weekly", "biweekly", "monthly"]
    df = _summary_metrics_table(start_time, end_time, variable, truth, metric, leads, forecasts,
                                time_grouping=time_grouping,
                                grid=grid, region=region)

    print(df)
    return df


@dask_remote
@cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric',
                       'time_grouping', 'grid', 'region'],
           cache=True)
def biweekly_summary_metrics_table(start_time, end_time, variable,
                                   truth, metric, time_grouping=None,
                                   grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['perpp', 'ecmwf_ifs_er', 'ecmwf_ifs_er_debiased', 'climatology_2015',
                 'climatology_trend_2015', 'climatology_rolling']
    leads = ["weeks34", "weeks56"]
    df = _summary_metrics_table(start_time, end_time, variable, truth, metric, leads, forecasts,
                                time_grouping=time_grouping,
                                grid=grid, region=region)

    print(df)
    return df


__all__ = ['global_statistic', 'grouped_metric', 'skill_metric',
           'summary_metrics_table', 'biweekly_summary_metrics_table']
