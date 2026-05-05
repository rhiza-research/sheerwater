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
    region = "kenya"
    spatial = True
    grid = "global0_25"

    # event definition
    agg_days = 5
    forecast = "imerg"
    truth = "tahmo"
    variable = "precip"

    station_threshold = 0.5
    satellite_threshold = 1
    softening = 3

    pod = metric(start_time=start_time, end_time=end_time, 
                variable=variable, agg_days=agg_days, forecast=forecast, truth=truth, metric_name=f"pod-{station_threshold}-{satellite_threshold}",
                region=region, spatial=spatial, time_grouping=None, grid=grid, recompute=True, cache_mode='overwrite')
                
    far = metric(start_time=start_time, end_time=end_time, 
                variable=variable, agg_days=agg_days, forecast=forecast, truth=truth, metric_name=f"far-{station_threshold}-{satellite_threshold}",
                region=region, spatial=spatial, time_grouping=None, grid=grid, recompute=True, cache_mode='overwrite')

    ber = ((1-pod.pod) + far.far) / 2

    fig, axs = plt.subplots(1, 3, figsize=(10, 5))
    pod.pod.plot(ax=axs[0], x="lon", vmin=0.5, vmax=1.0, cmap="rainbow", add_labels=False)
    far.far.plot(ax=axs[1], x="lon", vmin=0.0, vmax=0.5, cmap="rainbow", add_labels=False)
    ber.plot(ax=axs[2], x="lon", vmin=0.0, vmax=0.3, cmap="rainbow", add_labels=False)
    axs[0].set_title("POD")
    axs[1].set_title("FAR")
    axs[2].set_title("BER")
    plt.suptitle(f"station: {station_threshold}mm | satellite: {satellite_threshold}mm | agg: {agg_days}d")

    import pdb; pdb.set_trace()
