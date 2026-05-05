from sheerwater.utils import start_remote
from dashboard_data.station_paired_analysis import paired_histogram
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

if __name__ == "__main__":
    start_remote(remote_name = "mohini")

    # times
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    # data sources
    estimate = "imerg_final"
    truth = "stations"

    # event defintion
    agg_days = 5

    # spatial specs
    grid = "global0_25"
    space_grouping = None
    region = "ghana"
    spatial = False

    # get joint histogram
    bins = np.arange(0, 20, 0.1)

    hist = paired_histogram(start_time, end_time, estimate, truth, agg_days, grid=grid,
                            space_grouping=space_grouping, time_grouping=None, region=region,
                            spatial=spatial, bins=bins, recompute=True, zero_bin=True)
    
    station_thresholds = np.arange(0, 20, 0.5)
    satellite_thresholds = np.arange(0, 20, 0.5)

    station_da = xr.DataArray(
    station_thresholds,
    dims="station_threshold",
    coords={"station_threshold": station_thresholds},
    )

    sat_da = xr.DataArray(
    satellite_thresholds,
    dims="sat_threshold",
    coords={"sat_threshold": satellite_thresholds},
    )

    # Events (now both broadcast over thresholds)
    truth_event = hist.truth >= station_da
    est_event = hist.estimate >= sat_da

    # Metrics over full 2D grid
    hits = hist.where(truth_event & est_event).sum(dim=["truth", "estimate"])
    misses = hist.where(truth_event & ~est_event).sum(dim=["truth", "estimate"])
    false_positives = hist.where(~truth_event & est_event).sum(dim=["truth", "estimate"])
    true_negatives = hist.where(~truth_event & ~est_event).sum(dim=["truth", "estimate"])

    pod = hits / (hits + misses)
    far = false_positives / (false_positives + true_negatives)

    results = xr.Dataset({
    "pod": pod.precip,
    "far": far.precip,
    })
    import pdb; pdb.set_trace()

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    good_region = (results.pod > 0.8) & (results.far < 0.2)
    # POD
    results.pod.plot(
        ax=axes[0],
        cmap="Greens",
        vmin=0, vmax=1
    )
    axes[0].set_title("POD")

    # FAR
    results.far.plot(
        ax=axes[1],
        cmap="Reds",
        vmin=0, vmax=1
    )
    axes[1].set_title("FAR")

    # GOOD REGION MASK
    good_region.astype(int).plot(
        ax=axes[2],
        cmap="Blues",
        vmin=0, vmax=1
    )
    axes[2].set_title("POD > 0.9 & FAR < 0.2")

    plt.tight_layout()
    plt.show()