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
    agg_days = 1
    forecast = "imerg"
    truth = "tahmo"
    variable = "precip"

    station_threshold = 0.5
    satellite_thresholds = [0.5, 1, 5]

    # make a results directory if it doesn't exist
    if not os.path.exists(f"results/results_nosoft"):
        os.makedirs(f"results/results_nosoft")
    for satellite_threshold in satellite_thresholds:
        fig, axs = plt.subplots(2, 3, figsize=(10, 5))
        for idx, region in enumerate(["kenya", "ghana"]):
            print(f"Processing satellite threshold: {satellite_threshold} for region: {region}")
            pod = metric(start_time=start_time, end_time=end_time, 
            variable=variable, agg_days=agg_days, forecast=forecast, truth=truth, metric_name=f"pod-{station_threshold}-{satellite_threshold}",
            region=region, spatial=spatial, time_grouping=None, grid=grid, recompute=True, cache_mode='overwrite')
            
            far = metric(start_time=start_time, end_time=end_time, 
            variable=variable, agg_days=agg_days, forecast=forecast, truth=truth, metric_name=f"far-{station_threshold}-{satellite_threshold}",
            region=region, spatial=spatial, time_grouping=None, grid=grid, recompute=True, cache_mode='overwrite')

            # compute balanced error rate
            ber = ((1-pod.pod) + far.far) / 2

            # plot 
            pod.pod.plot(ax=axs[idx, 0], x="lon", vmin=0.5, vmax=1.0, cmap="rainbow", add_labels=False)
            far.far.plot(ax=axs[idx, 1], x="lon", vmin=0.0, vmax=0.5, cmap="rainbow", add_labels=False)
            ber.plot(ax=axs[idx, 2], x="lon", vmin=0.0, vmax=0.3, cmap="rainbow", add_labels=False)
            for i in range(3):
                ax = axs[idx, i]
                ax.set_ylabel(" ")
                ax.set_xlabel(" ")
                ax.set_title(" ")
            axs[idx, 0].set_ylabel(region)

        # set super title
        axs[0, 0].set_title("POD")
        axs[0, 1].set_title("FAR")
        axs[0, 2].set_title("BER")
        plt.suptitle(f"station: {station_threshold}mm | satellite: {satellite_threshold}mm | agg: {agg_days}d | no softening")
        plt.savefig(f"results/results_nosoft/ber_{station_threshold}_{satellite_threshold}.png")
        plt.close()

    import pdb; pdb.set_trace()