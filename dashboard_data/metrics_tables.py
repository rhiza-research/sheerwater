"""Cahable Grafana tables for metrics."""
import xarray as xr
import numpy as np

from nuthatch import cache, config_parameter
from sheerwater.utils import dask_remote
from sheerwater.metrics import metric
from sheerwater.spatial_subdivisions import space_grouping_labels, clip_region

from google.cloud import secretmanager


_MONTH_LABELS = {
    'M01': 'January',
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
    'M12': 'December',
}


@config_parameter('password', location='root', backend='sql', secret=True)
def postgres_write_password():
    """Get a postgres write password."""
    client = secretmanager.SecretManagerServiceClient()

    response = client.access_secret_version(
        request={"name": "projects/750045969992/secrets/postgres-write-password/versions/latest"})
    key = response.payload.data.decode("UTF-8")

    return key


def _append_forecast_result(results_ds, ds, forecast):
    """Expand a per-forecast result, normalize lead days, and merge into results."""
    ds = ds.expand_dims({'forecast': [forecast]}, axis=0)
    if 'prediction_timedelta' in ds.coords:
        lead_values = (ds.prediction_timedelta.values / np.timedelta64(1, 'D')).astype('int64')
        ds = ds.assign_coords(prediction_timedelta=lead_values)
        ds = ds.rename({'prediction_timedelta': 'lead_day'})
    return results_ds.merge(ds)


def _finalize_table_df(df, time_grouping, order):
    """Normalize time_grouping / region columns and select output order."""
    if 'time' in df.columns:
        df = df.rename(columns={'time': 'time_grouping'})
        if time_grouping == 'month_of_year':
            df['time_grouping'] = df['time_grouping'].map(_MONTH_LABELS)
    else:
        df['time_grouping'] = None

    if 'region' not in df.columns:
        df['region'] = None

    return df[order]


@dask_remote
def _metric_table(start_time, end_time, variable,
                  truth, metric_name, agg_days, forecasts,
                  metric_kwargs=None,
                  time_grouping=None,
                  grid='global1_5', space_grouping=None,
                  region='global'):
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
                f"metric {metric_name}, grid {grid}, space_grouping {space_grouping}, "
                f"time grouping {time_grouping}")
            # First get the value without the baseline
            try:
                ds = metric(start_time, end_time, variable,
                            agg_days=agg, forecast=forecast, truth=truth,
                            metric_name=metric_name, metric_kwargs=metric_kwargs, time_grouping=time_grouping, spatial=False,
                            grid=grid, space_grouping=space_grouping, region=region, recompute=False, retry_null_cache=False)
            except NotImplementedError:
                ds = None

            if ds is None:
                continue

            if 'prediction_timedelta' in ds.coords and len(agg_days) > 1:
                raise ValueError("Cannot run multiple aggregation days in the same table for a forecast with leads.")

            # Ground-truth tables rename the metric variable to the agg window length.
            if 'prediction_timedelta' not in ds.coords:
                if '-' in metric_name:
                    met_name = metric_name.split('-')[0].lower()
                else:
                    met_name = metric_name.lower()
                ds = ds.rename({met_name: agg})

            results_ds = _append_forecast_result(results_ds, ds, forecast)
            print(results_ds)

    if not time_grouping:
        results_ds = results_ds.reset_coords('time', drop=True)

    results_ds = results_ds.drop_vars([var for var in results_ds.coords if var not in results_ds.dims], errors='ignore')
    results_ds = results_ds[[metric_name]]
    print(results_ds)

    if 'space_grouping' in results_ds.dims:
        results_ds = results_ds.rename({'space_grouping': 'region'})

    df = results_ds.to_dataframe()

    df = df.reset_index().rename(columns={'index': 'forecast'})

    if 'lead_day' in df.columns:
        order = ['forecast', 'time_grouping', 'region', 'lead_day', f'{metric_name}']
    else:
        order = ['forecast', 'time_grouping', 'region'] + agg_days

    return _finalize_table_df(df, time_grouping, order)


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable',  'truth', 'agg_days',
                   'metric_name', 'metric_kwargs', 'time_grouping', 'grid', 'space_grouping',
                   'region'],
       backend='sql', backend_kwargs={'hash_table_name': True})
def forecast_metric_table(start_time, end_time, variable,
                          forecasts, truth, agg_days, metric_name, metric_kwargs=None, time_grouping=None,
                          grid='global1_5', space_grouping=None, region='global'):
    """Runs metric repeatedly for all forecasts and creates a pandas table out of them."""
    df = _metric_table(start_time, end_time, variable, truth, metric_name,
                       agg_days=agg_days, forecasts=forecasts, metric_kwargs=metric_kwargs,
                       time_grouping=time_grouping, grid=grid, space_grouping=space_grouping, region=region)

    print(df)
    return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'truth', 'metric_name', 'time_grouping', 'grid', 'space_grouping'],
       backend='sql', backend_kwargs={'hash_table_name': True})
def ground_truth_metric_table(start_time, end_time, variable,
                              truth, metric_name, time_grouping=None,
                              grid='global1_5', space_grouping=None):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    forecasts = ['era5', 'chirps_v3', 'chirp_v3', 'imerg_final', 'imerg_late', "rain_over_africa", "tamsat", "oya"]

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
                       time_grouping=time_grouping, grid=grid, space_grouping=space_grouping)

    print(df)


@dask_remote
def _metric_table_spatial(start_time, end_time, variable,
                          truth, metric_name,
                          agg_days, forecasts,
                          metric_kwargs=None,
                          time_grouping=None,
                          space_grouping=None,
                          region=None,
                          grid='global1_5'):
    """Internal function to compute summary metrics table for flexible leads and forecasts."""
    # For the time grouping we are going to store it in an xarray with dimensions
    # forecast and time, which we instantiate
    results_ds = xr.Dataset(coords={'forecast': forecasts, 'time': None})

    # Make sure space grouping is a list
    if not isinstance(space_grouping, list):
        space_grouping = [space_grouping]

    # Make sure agg_days is a list
    if not isinstance(agg_days, list):
        agg_days = [agg_days]

    # Metric column name (stable even if every forecast cache-misses)
    if 'thresh' in metric_name:
        mn = metric_name.split("-thresh-")[0]
    else:
        mn = metric_name

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
                            metric_name=metric_name, metric_kwargs=metric_kwargs,
                            time_grouping=time_grouping, spatial=True,
                            grid=grid, region=region,
                            retry_null_cache=False, fail_if_no_cache=True)

                ds = ds.compute()

                exp_metric = ds.attrs.get('metric_name') or list(ds.data_vars)[0]
                ds = ds.rename({exp_metric: mn})

            except (NotImplementedError, RuntimeError) as e:
                print(f"Skipping {forecast} for {metric_name}: {e}")
                continue

            if 'prediction_timedelta' in ds.coords and len(agg_days) > 1:
                raise ValueError("Cannot run multiple aggregation days in the same table for a forecast with leads.")

            results_ds = _append_forecast_result(results_ds, ds, forecast)
            print(results_ds)

    if not time_grouping:
        results_ds = results_ds.reset_coords('time', drop=True)

    results_ds = results_ds.drop_vars([var for var in results_ds.coords if var not in results_ds.dims], errors='ignore')

    if 'space_grouping' in results_ds.dims:
        results_ds = results_ds.rename({'space_grouping': 'region'})

    grouping_labels = space_grouping_labels(grid=grid, space_grouping=space_grouping)
    grouping_labels = clip_region(grouping_labels, grid=grid, region=region)
    grouping_labels = grouping_labels.compute()
    results_ds = results_ds.assign_coords(region=grouping_labels.region)
    for grp in space_grouping:
        results_ds = results_ds.assign_coords(**{f'{grp}': grouping_labels[f'{grp}_region']})

    df = results_ds.to_dataframe()
    df = df.reset_index()

    if 'lead_day' in df.columns:
        order = ['forecast', 'lat', 'lon', 'time_grouping', 'lead_day', f'{mn}']
    else:
        order = ['forecast', 'lat', 'lon', 'time_grouping', f'{mn}']

    if 'percent_good' in df.columns:
        order = order + ['percent_good', 'event_count']
    if 'percent_good_members' in df.columns:
        order = order + ['percent_good_members']

    order = order + ['region'] + space_grouping

    return _finalize_table_df(df, time_grouping, order)


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'truth',
                   'metric_name', 'metric_kwargs', 'time_grouping',
                   'grid', 'space_grouping', 'region'],
       backend='sql', backend_kwargs={'hash_table_name': True})
def advanced_spatial_metric_table(start_time, end_time, variable,
                                  forecasts, truth, metric_name, metric_kwargs=None, time_grouping=None,
                                  grid='global1_5', space_grouping=None, region=None):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    df = _metric_table_spatial(start_time=start_time, end_time=end_time, variable=variable,
                               truth=truth, metric_name=metric_name, agg_days=1, forecasts=forecasts,
                               time_grouping=time_grouping, grid=grid, space_grouping=space_grouping,
                               region=region, metric_kwargs=metric_kwargs)

    print(df)
    return df


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'truth',
                   'metric_name', 'metric_kwargs', 'time_grouping',
                   'grid', 'space_grouping', 'region'],
       backend='sql', backend_kwargs={'hash_table_name': True})
def advanced_ground_truth_spatial_metric_table(start_time, end_time, variable,
                                               forecasts, truth, metric_name, metric_kwargs=None,
                                               time_grouping=None, grid='global1_5', space_grouping=None,
                                               region=None):
    """Runs summary metric repeatedly for all forecasts and creates a pandas table out of them."""
    df = _metric_table_spatial(start_time=start_time, end_time=end_time, variable=variable,
                               truth=truth, metric_name=metric_name, agg_days=1, forecasts=forecasts,
                               time_grouping=time_grouping, grid=grid, space_grouping=space_grouping,
                               region=region, metric_kwargs=metric_kwargs)

    print(df)
    return df
