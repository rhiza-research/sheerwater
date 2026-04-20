from sheerwater.utils import start_remote
from dashboard_data.station_paired_analysis import paired_histogram
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import math
import matplotlib.colors as mcolors
import xarray as xr

def joint_confidence(hist, xthreshold = 2, x_dim = "truth", y_dim = "estimate", mode="above"):
    """
    Given a threshold for x_dim, calculate the confidence for every possible threshold on y_dim
    that we are above (below) both thresholds.
    """

    hist_y = hist.sum(x_dim)
    y_area = hist_y.cumsum(dim=y_dim).shift({y_dim: 1}, fill_value=0)
    y_area = y_area.assign_coords({y_dim: hist[y_dim]})
    if mode == "above":
        all_area = hist_y.sum(dim=y_dim)
        y_area = all_area - y_area

    if mode == "below":
        x_area = hist.where(hist[x_dim] < xthreshold).sum(dim=x_dim)
    else: # mode == "above"
        x_area = hist.where(hist[x_dim] > xthreshold).sum(dim=x_dim)

    x_area_cumsum = x_area.cumsum(dim=y_dim).shift({y_dim: 1}, fill_value=0)
    x_area_cumsum = x_area_cumsum.assign_coords({y_dim: hist[y_dim]})
    x_area_total = x_area.sum(dim=y_dim)
    if mode == "above":
        x_area = x_area_total - x_area_cumsum
    
    confidence = x_area / y_area
    confidence = confidence.rename({"precip": "confidence"})

    return confidence


def contingency(hist, xthreshold=2, x_dim="truth", y_dim="estimate", mode="above"):
    """
    Compute contingency table components (hits, miss, false_pos, true_neg)
    for all thresholds along y_dim.

    mode="above": event = value > threshold
    mode="below": event = value < threshold
    """
    hist = hist.precip
    if mode == "above":
        x_event = hist.where(hist[x_dim] > xthreshold)
        x_nonevent = hist.where(hist[x_dim] <= xthreshold)
    else:
        x_event = hist.where(hist[x_dim] < xthreshold)
        x_nonevent = hist.where(hist[x_dim] >= xthreshold)

    x_event_y = x_event.sum(dim=x_dim)
    x_nonevent_y = x_nonevent.sum(dim=x_dim)

    x_event_cum = x_event_y.cumsum(dim=y_dim).shift({y_dim: 1}, fill_value=0)
    x_event_cum = x_event_cum.assign_coords({y_dim: hist[y_dim]})
    x_event_total = x_event_y.sum(dim=y_dim)

    x_nonevent_cum = x_nonevent_y.cumsum(dim=y_dim).shift({y_dim: 1}, fill_value=0)
    x_nonevent_cum = x_nonevent_cum.assign_coords({y_dim: hist[y_dim]})
    x_nonevent_total = x_nonevent_y.sum(dim=y_dim)

    if mode == "above":
        hits = x_event_total - x_event_cum
        false_pos = x_nonevent_total - x_nonevent_cum
        miss = x_event_cum
        true_neg = x_nonevent_cum
    else:
        hits = x_event_cum
        false_pos = x_nonevent_cum
        miss = x_event_total - x_event_cum
        true_neg = x_nonevent_total - x_nonevent_cum

    return xr.Dataset({
        "hits": hits,
        "miss": miss,
        "false_pos": false_pos,
        "true_neg": true_neg,
    })


def plot(hist):
    # calculate confidence
    import pdb; pdb.set_trace()

    ghana_regions = [r for r in hist.region.values if "ghana" in r]
    nregions = len(ghana_regions)

    ncols = 3
    nrows = math.ceil(nregions / ncols)

    fig, axs = plt.subplots(nrows, ncols, figsize=(15, 5 * nrows))
    axs = np.atleast_2d(axs)

    for i, region in enumerate(ghana_regions):
        ax = axs[i // ncols, i % ncols]

        region_hist = hist.sel(region=region)

        # Explicitly select the variable and convert to array
        data = region_hist["precip"].values  # should be 2D (truth, estimate)

        log_data = np.log1p(data)

        im = ax.imshow(log_data, origin="lower", aspect="auto")
        ax.set_title(str(region))
    # put x-label on axis in bottom row
    for ax in axs[-1]:
        ax.set_xlabel("stations (mm/day)")
    # put y-label on axis in left column
    for ax in axs[:, 0]:
        ax.set_ylabel("satellite (mm/day)")

    # Hide unused axes
    for j in range(nregions, nrows * ncols):
        axs[j // ncols, j % ncols].axis("off")

    plt.tight_layout()
    plt.show()
    import pdb; pdb.set_trace()


def plot_threshold(pod, far, pod_thresh=0.8, far_thresh=0.2):
    # find threshold where pod is at least 0.8 and far is at most 0.2
    pod_thresh, far_thresh = 0.8, 0.2
    mask = (pod >= pod_thresh) & (far <= far_thresh)
    valid = mask.any(dim="estimate")
    that = mask.idxmax(dim="estimate").where(valid)

    # where no threshold was found
    hasdata = (pod.notnull() & far.notnull()).any(dim="estimate")
    notfound = (~valid) & hasdata

    # set colormap so that cells where condition is not met are shown in black
    fig, ax = plt.subplots(figsize=(6, 5))
    that.plot(x="lon", cmap="YlGnBu", ax=ax)


    nf = notfound.astype(int)
    overlay_cmap = mcolors.ListedColormap([(0,0,0,0), (0,0,0,1)])

    nf.plot(
        ax=ax,
        cmap=overlay_cmap,
        add_colorbar=False,
    )


if __name__ == "__main__":
    start_remote(remote_name = "thresholds")#remote_config=["xlarge_cluster", "large_node"])

    # times
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    # data sources
    estimate = "imerg_final"
    truth = "stations"

    # event defintion
    agg_days = 5
    dry_threshold = 2

    # spatial specs
    grid = "global0_25"
    space_grouping = None
    region = "africa"
    spatial = True

    # get joint histogram
    bins = np.arange(0, 20, 0.5)
    hist = paired_histogram(start_time, end_time, estimate, truth, agg_days, grid=grid,
                            space_grouping=space_grouping, time_grouping=None, region=region,
                            spatial=spatial, recompute=True, bins=bins)

    ctable = contingency(hist, xthreshold=dry_threshold, x_dim="truth", y_dim="estimate", mode="above")
    # compute pod and far
    pod = ctable.hits / (ctable.hits + ctable.miss)
    far = ctable.false_pos / (ctable.false_pos + ctable.true_neg)
    plot_threshold(pod, far)

    plt.show()
    import pdb; pdb.set_trace()

    
    pod_thresh = 0.8
    far_thresh = 0.2
    # pod will decrease as thresh increases
    mask = pod > pod_thresh
    pod_thresh = pod["estimate"].where(mask).max(dim="estimate")
    # far will decrease as thresh increases
    mask = far < far_thresh
    far_thresh = far["estimate"].where(mask).min(dim="estimate")
    # plot these in side by side plots
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    pod_thresh.plot(ax=axs[0])
    far_thresh.plot(ax=axs[1])
    axs[0].set_title("Maximum threshold for pod > 0.8")
    axs[1].set_title("Minimum threshold for far < 0.2")
    plt.show()
    import pdb; pdb.set_trace()


    conf_above = joint_confidence(hist, xthreshold=dry_threshold, x_dim="truth", y_dim="estimate", mode="above")
    confidence_threshold = 0.8
    mask = conf_above.confidence > confidence_threshold
    first_estimate = conf_above.estimate.where(mask).min(dim="estimate")
    import pdb; pdb.set_trace()
    curves = conf_above.confidence.stack(points=("lat", "lon")).dropna("points", how="all")
    curves.plot.line(x="estimate", add_legend=False, alpha=0.3)
    import pdb; pdb.set_trace()

    da = first_estimate.compute()  # ensure it's loaded from dask

    # Define your bins (example for precipitation-like data)
    bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20]

    # Create a discrete colormap
    cmap = plt.get_cmap("tab10", len(bins) - 1)

    # Normalize into bins
    norm = mcolors.BoundaryNorm(bins, cmap.N)

    fig, ax = plt.subplots(figsize=(6, 5))

    im = ax.pcolormesh(
        da.lon,
        da.lat,
        da,
        cmap=cmap,
        norm=norm,
        shading="auto"
    )

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Estimate")

    ax.set_title("Categorical Estimate")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    plt.tight_layout()
    plt.show()
    import pdb; pdb.set_trace()

    # plot nicely
    # compute dask array
    # compute and sort
    da = first_estimate.compute()
    da_sorted = da.sortby(da)

    plt.figure(figsize=(20, 6))
    plt.bar(da_sorted.region.values, da_sorted.values, color="steelblue")

    # labels
    plt.ylabel("Satellite wet threshold for 80% confidence", fontsize=11)
    plt.xlabel("Region", fontsize=11)
    plt.title("First Estimate by Region", fontsize=13)

    # x ticks
    plt.xticks(rotation=90, fontsize=7)
    plt.yticks(fontsize=9)

    # ---- KEY PART ----
    ax = plt.gca()

    # major ticks (labeled): every 1.0
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1.0))

    # minor ticks (unlabeled): every 0.5
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.5))

    # grid styling
    ax.grid(which="major", axis="y", linestyle="-", alpha=0.7)
    ax.grid(which="minor", axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.show()
    import pdb; pdb.set_trace()

    import pdb; pdb.set_trace()
    conf_below = joint_confidence(hist, xthreshold=dry_threshold, x_dim="truth", y_dim="estimate", mode="below")
