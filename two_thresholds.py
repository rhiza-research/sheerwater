from sheerwater.utils import start_remote
from sheerwater.metrics import metric
import matplotlib.pyplot as plt
import os


if __name__ == "__main__":
    start_remote(remote_name = "mohini")

    # time parameters
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    # spatial parameters
    region = "africa"
    spatial = True
    grid = "global0_25"

    # event definition
    agg_days = 5
    forecast = "imerg"
    truth = "tahmo"
    variable = "precip"

    station_threshold = 5
    satellite_thresholds = [5, 8, 10]

    # make a results directory if it doesn't exist
    if not os.path.exists("results"):
        os.makedirs("results")

    for satellite_threshold in satellite_thresholds:
        print(f"Processing satellite threshold: {satellite_threshold}")
        pod = metric(start_time=start_time, end_time=end_time, 
        variable=variable, agg_days=agg_days, forecast=forecast, truth=truth, metric_name=f"pod-{station_threshold}-{satellite_threshold}",
        region=region, spatial=spatial, time_grouping=None, grid=grid, recompute=True)
        
        far = metric(start_time=start_time, end_time=end_time, 
        variable=variable, agg_days=agg_days, forecast=forecast, truth=truth, metric_name=f"far-{station_threshold}-{satellite_threshold}",
        region=region, spatial=spatial, time_grouping=None, grid=grid, recompute=True)

        fig, axs = plt.subplots(1, 2, figsize=(10, 5))
        pod.pod.plot(ax=axs[0], x="lon", vmin=0.5, vmax=1.0, cmap="rainbow")
        far.far.plot(ax=axs[1], x="lon", vmin=0.0, vmax=0.5, cmap="rainbow")
        axs[0].set_title(f"POD at {station_threshold} mm and {satellite_threshold} mm over {agg_days} days")
        axs[1].set_title(f"FAR at {station_threshold} mm and {satellite_threshold} mm over {agg_days} days")
        plt.savefig(f"results/pod_far_{station_threshold}_{satellite_threshold}.png")
        plt.close()

    import pdb; pdb.set_trace()