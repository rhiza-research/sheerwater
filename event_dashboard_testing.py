from this import d
from dashboard_data.event_explorer import forecast_metric_points, event_list
from dashboard_data.metrics_maps import forecast_metric_map
from sheerwater.utils import start_remote
from sheerwater.metrics import metric, metric_event_series, event_count
from sheerwater.spatial_subdivisions import clip_region
from sheerwater.data import imerg_final
from sheerwater.forecasts import ecmwf_ifs_er

import numpy as np
import xarray as xr
import pandas as pd

import matplotlib.pyplot as plt

if __name__ == "__main__":

    start_remote(remote_name="mohini", remote_config="large_cluster")

    start_time = "2016-01-01"
    end_time = "2024-12-31"
    variable = "precip"
    grid = "global1_5"
    region = "western_africa"
    forecast = "ecmwf_ifs_er"
    truth = "imerg_final"
    time_grouping = None
    experiment = "big_rain_days"
    agg_days = 1
    lead_days = 7

    metric_kwargs = {
        "forecast_filter": False,
        "obs_filter": True
    }

    # caches map of aggregate metric values at each grid cell in the region
    ds = forecast_metric_points(start_time, end_time, variable, forecast, truth, agg_days, experiment, metric_kwargs, 
                                lead_days=lead_days, time_grouping=time_grouping, grid=grid, region=region)
    # caches list of event (times and metric value) that feed into aggregate for the cell
    df = event_list(start_time, end_time, variable,
            forecast=forecast, truth=truth,
            agg_days=agg_days,
            metric_name=experiment, metric_kwargs={'forecast_filter': False, 'obs_filter': True},
            time_grouping=time_grouping,
            grid=grid, region=region, lead_days=lead_days)
    lat, lon = 15, -7.5
    # get imerg
    dsimerg = imerg_final(start_time, end_time, grid=grid)
    dsecmwf = ecmwf_ifs_er(start_time, end_time, grid=grid, densify=True)
    import pdb; pdb.set_trace()

    import pdb; pdb.set_trace()
    n_events = 3
    # get imerg and ecmwf at the lat, lon and n random event times
    event_times = df[(df["lat"] == lat) & (df["lon"] == lon)].sample(n_events)['time'].values
    dsimerg = dsimerg.sel(lat=lat, lon=lon)
    target_lead = pd.Timedelta(days=lead_days)
    dsecmwf = dsecmwf.sel(lat=lat, lon=lon, prediction_timedelta=target_lead)

    fig, axs = plt.subplots(n_events, 1, figsize=(10, n_events*5))
    for i, event_time in enumerate(event_times):
        # plot 10 days before and after the event time
        event_time = pd.to_datetime(event_time)
        time_range = pd.date_range(event_time - pd.Timedelta(days=10), event_time + pd.Timedelta(days=10))
        x = dsimerg.sel(time=time_range)
        y = dsecmwf.sel(time=time_range)
        x.precip.plot(ax=axs[i], label='imerg')
        y.precip.plot(ax=axs[i], label='ecmwf')
        axs[i].legend()
        axs[i].set_title(f'Event time: {event_time}')
        axs[i].set_xlabel('Time')
        axs[i].set_ylabel('Precipitation (mm)')
    plt.show()

    import pdb; pdb.set_trace()



    ds3 = metric_event_series(start_time, end_time, variable,
            agg_days=agg_days, forecast=forecast, truth=truth,
            metric_name=experiment, metric_kwargs={'forecast_filter': False, 'obs_filter': True},
            time_grouping=time_grouping, spatial=True,
            grid=grid, region=region)

    var_name = 'smape'
    ds = ds3[var_name].chunk({'time': -1, 'prediction_timedelta': -1})
    times = ds.time.values
    def collect_nonnans(arr):
        mask = ~np.isnan(arr)
        return times[mask], arr[mask]
    valid_times, valid_values = xr.apply_ufunc(collect_nonnans, ds.load(), input_core_dims=[['time']], output_core_dims=[[], []],
                                               vectorize=True, output_dtypes=[object, object])
    df_times = valid_times.rename('time').to_dataframe().reset_index()
    df_values = valid_values.rename(var_name).to_dataframe().reset_index()
    df_times = df_times[df_times['time'].apply(len) > 0].reset_index(drop=True)
    df = df_times.merge(df_values, on=['lat', 'lon', 'prediction_timedelta'])
    df = df.explode(['time', var_name], ignore_index=True)

    import pdb; pdb.set_trace()

    # check that there are non nans
    xx = ds3.notnull().sum(dim='time').sum(dim='prediction_timedelta').smape.plot(x="lon")
    plt.show()



    "--------------------------------"


    metric_kwargs = {
        "obs_filter": True,
        "forecast_filter": False
    }

    # useful to check if the cache exists
    # dx = forecast_metric_map(start_time, end_time, variable, forecast, truth, agg_days, metric_name, metric_kwargs, time_grouping=time_grouping, lead_days=lead_days, grid=grid, region=region)
    # import pdb; pdb.set_trace()

    # hash : '1b59e5673ada59d2322536bd2a943560'
    # ds = forecast_metric_points(start_time, end_time, variable, forecast, truth, agg_days, metric_name, metric_kwargs, time_grouping=time_grouping, lead_days=lead_days, grid=grid, region=region,
    # recompute=True)

    ds = metric_event_series(start_time, end_time, variable,
            agg_days=agg_days, forecast=forecast, truth=truth,
            metric_name=experiment, metric_kwargs=metric_kwargs,
            time_grouping=time_grouping, spatial=True,
            grid=grid, region=region)
    ds2 = event_count(start_time, end_time, variable,
            agg_days=agg_days, forecast=forecast, truth=truth,
            metric_name=experiment, metric_kwargs=metric_kwargs,
            time_grouping=time_grouping, spatial=True,
            grid=grid, region=region)
    import pdb; pdb.set_trace()
    
    # clip to africa
    ds = clip_region(ds, region, grid)


    # get this into an array
    var_name = 'mae'
    ds = ds[var_name].chunk({'time': -1, 'prediction_timedelta': -1})
    times = ds.time.values
    def collect_nonnans(arr):
        mask = ~np.isnan(arr)
        return times[mask], arr[mask]
    valid_times, valid_values = xr.apply_ufunc(collect_nonnans, ds.load(), input_core_dims=[['time']], output_core_dims=[[], []],
                                               vectorize=True, output_dtypes=[object, object])
    df_times = valid_times.rename('time').to_dataframe().reset_index()
    df_values = valid_values.rename(var_name).to_dataframe().reset_index()
    df_times = df_times[df_times['time'].apply(len) > 0].reset_index(drop=True)
    df = df_times.merge(df_values, on=['lat', 'lon', 'prediction_timedelta'])

    # ds = metric(start_time, end_time, variable,
    #         agg_days=agg_days, forecast=forecast, truth=truth,
    #         metric_name=experiment, metric_kwargs={'forecast_filter': False, 'obs_filter': True},
    #         time_grouping=time_grouping, spatial=True,
    #         grid=grid, region=region)
    
    # ds2 = event_count(start_time, end_time, variable,
    #         agg_days=agg_days, forecast=forecast, truth=truth,
    #         metric_name=experiment,
    #         metric_kwargs={'forecast_filter': False, 'obs_filter': True},
    #         time_grouping=time_grouping, spatial=True,
    #         grid=grid, region=region, recompute=True)
    # import pdb; pdb.set_trace()
    

    import pdb; pdb.set_trace()

