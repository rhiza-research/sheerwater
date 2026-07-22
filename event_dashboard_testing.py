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

