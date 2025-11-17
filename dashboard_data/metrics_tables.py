"""Cahable Grafana tables for metrics."""
import xarray as xr
import numpy as np

from sheerwater_benchmarking.utils import cacheable, dask_remote, start_remote
from sheerwater_benchmarking.metrics import metric

# Lead labels for standrad aggregrations
lead_dict_standard = {
    7: ('weekly',
        {
            np.timedelta64(0, 'D').astype('timedelta64[ns]'): 'week1',
            np.timedelta64(7, 'D').astype('timedelta64[ns]'): 'week2',
            np.timedelta64(14, 'D').astype('timedelta64[ns]'): 'week3',
            np.timedelta64(21, 'D').astype('timedelta64[ns]'): 'week4',
            np.timedelta64(28, 'D').astype('timedelta64[ns]'): 'week5',
            np.timedelta64(35, 'D').astype('timedelta64[ns]'): 'week6'
        }),
    14: ('biweekly',
         {
             np.timedelta64(0, 'D').astype('timedelta64[ns]'): 'weeks12',
             np.timedelta64(14, 'D').astype('timedelta64[ns]'): 'weeks34',
             np.timedelta64(28, 'D').astype('timedelta64[ns]'): 'weeks56'
         }),
    30: ('monthly',
         {
             np.timedelta64(0, 'D').astype('timedelta64[ns]'): 'month1',
             np.timedelta64(30, 'D').astype('timedelta64[ns]'): 'month2',
             np.timedelta64(60, 'D').astype('timedelta64[ns]'): 'month3'
         }),
    90: ('quarterly',
         {
             np.timedelta64(0, 'D').astype('timedelta64[ns]'): 'quarter1',
             np.timedelta64(90, 'D').astype('timedelta64[ns]'): 'quarter2',
             np.timedelta64(180, 'D').astype('timedelta64[ns]'): 'quarter3',
             np.timedelta64(270, 'D').astype('timedelta64[ns]'): 'quarter4'
         }),
}


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
        lead_dict = lead_dict_standard[agg_days[0]][1]
    lead_labels = [lead_dict_standard[agg][0] for agg in agg_days]

    for forecast in forecasts:
        for i, agg in enumerate(agg_days):
            print(
                f"Running for {forecast} and {agg} with variable {variable}, "
                f"metric {metric_name}, grid {grid}, region {region}, "
                f"time grouping {time_grouping}")
            # First get the value without the baseline
            try:
                ds = metric(start_time, end_time, variable,
                            agg_days=agg, forecast=forecast, truth=truth,
                            metric_name=metric_name, time_grouping=time_grouping, spatial=False,
                            grid=grid, region=region, recompute=True,
                            retry_null_cache=True)
            except NotImplementedError:
                ds = None

            if 'prediction_timedelta' in ds.coords and len(agg_days) > 1:
                raise ValueError("Cannot run multiple aggregation days in the same table for a forecast with leads.")

            if ds:
                ds = ds.rename({variable: lead_labels[i]})
                ds = ds.expand_dims({'forecast': [forecast]}, axis=0)
                # For climatology forecasts, we need to expand the prediction_timedelta coordinate
                if 'prediction_timedelta' in ds.coords and 'climatology' in forecast:
                    ds = ds.squeeze('prediction_timedelta')
                    ds = ds.expand_dims({'lead_time': list(lead_dict.values())})
                elif 'prediction_timedelta' in ds.coords:
                    # Get the intersection of the prediction_timedelta coordinate and the lead_sel
                    lead_sel = np.intersect1d(ds.prediction_timedelta.values, list(lead_dict.keys()))
                    # Select the approriate leads
                    ds = ds.sel(prediction_timedelta=lead_sel)
                    # Map lead values to labels using the lead_dict
                    timedelta_labels = [lead_dict[x] for x in ds.prediction_timedelta.values]
                    ds = ds.rename({'prediction_timedelta': 'lead_time'})
                    ds = ds.assign_coords(lead_time=timedelta_labels)
                # results_ds = xr.combine_by_coords([results_ds, ds], combine_attrs='override')
                results_ds = results_ds.merge(ds)

    if not time_grouping:
        results_ds = results_ds.reset_coords('time', drop=True)

    results_ds = results_ds.drop_vars([var for var in results_ds.coords if var not in results_ds.dims], errors='ignore')
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
    forecasts = ['fuxi', 'salient', 'ecmwf_ifs_er', 'ecmwf_ifs_er_debiased', 'climatology_2015',
                 'climatology_trend_2015', 'climatology_rolling', 'gencast', 'graphcast']
    df= _summary_metrics_table(start_time, end_time, variable, truth, metric_name,
                                agg_days=7, forecasts=forecasts,
                                time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@ dask_remote
@ cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
           cache=True,
           primary_keys=['time', 'forecast'])
def seasonal_metrics_table(start_time, end_time, variable,
                           truth, metric_name, time_grouping=None,
                           grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts= ['salient', 'climatology_2015']
    df= _summary_metrics_table(start_time, end_time, variable, truth, metric_name,
                                agg_days=30, forecasts=forecasts,
                                time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@ dask_remote
@ cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
           cache=True,
           primary_keys=['time', 'forecast'])
def station_metrics_table(start_time, end_time, variable,
                          truth, metric_name, time_grouping=None,
                          grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts= ['era5', 'chirps', 'imerg', 'cbam']
    agg_days= [1, 7, 14, 30]
    df= _summary_metrics_table(start_time, end_time, variable, truth, metric_name,
                                agg_days, forecasts,
                                time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


@ dask_remote
@ cacheable(data_type='tabular',
           cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'region'],
           cache=True)
def biweekly_summary_metrics_table(start_time, end_time, variable,
                                   truth, metric_name, time_grouping=None,
                                   grid='global1_5', region='global'):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts= ['perpp', 'ecmwf_ifs_er', 'ecmwf_ifs_er_debiased', 'climatology_2015',
                 'climatology_trend_2015', 'climatology_rolling']
    df= _summary_metrics_table(start_time, end_time, variable, truth, metric_name,
                                agg_days=14, forecasts=forecasts,
                                time_grouping=time_grouping, grid=grid, region=region)

    print(df)
    return df


if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster')
    start_time= "2016-01-01"
    end_time= "2022-12-31"
    variable= "precip"
    truth= "era5"
    metric_name= "mae"
    time_grouping= None
    grid= "global1_5"
    region= "global"
    df= summary_metrics_table(start_time, end_time, variable, truth,
                               metric_name, time_grouping, grid, region=region, recompute=True, force_overwrite=True)
    print(df)
    df= seasonal_metrics_table(start_time, end_time, variable, truth,
                                metric_name, time_grouping, grid, region=region)
    print(df)
    df= station_metrics_table(start_time, end_time, variable, truth,
                               metric_name, time_grouping, grid, region=region)
    print(df)
    df= biweekly_summary_metrics_table(start_time, end_time, variable, truth,
                                        metric_name, time_grouping, grid, region=region)
    print(df)
