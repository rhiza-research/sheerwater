from dashboard_data.event_explorer import forecast_metric_points
from dashboard_data.metrics_maps import forecast_metric_map
from sheerwater.utils import start_remote
from sheerwater.metrics import metric, metric_event_series

if __name__ == "__main__":

    start_remote(remote_name="mohini", remote_config="large_cluster")

    start_time = "2016-01-01"
    end_time = "2024-12-31"
    forecast = "ecmwf_ifs_ens"
    truth = "imerg_final"
    variable = "precip"
    grid = "global1_5"
    lead_days = 7
    agg_days = 1


    region = "africa_bimodal_season"
    time_grouping = "None"

    metric_name = "early_season_accumulation-30d"
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
            metric_name=metric_name, metric_kwargs=metric_kwargs,
            time_grouping=time_grouping, spatial=True,
            grid=grid, region=region)
    import pdb; pdb.set_trace()

