from sheerwater.utils import start_remote
from dashboard_data.station_paired_analysis import paired_histogram
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import math
import matplotlib.colors as mcolors
import xarray as xr
from sheerwater.spatial_subdivisions import spatial_subdivisions


def contingency_1d(hist, xthreshold=2, x_dim="truth", y_dim="estimate", mode="above"):
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


def contingency_2d(hist, x_dim="truth", y_dim="estimate", mode="above"):
    """
    Compute contingency table for all (xthreshold, ythreshold) pairs.
    Returns a Dataset with dimensions (x_dim, y_dim).
    """
    hist = hist.precip

    # total count
    total = hist.sum(dim=(x_dim, y_dim))

    # 2D cumulative sum
    xy_below = hist.cumsum(dim=x_dim).cumsum(dim=y_dim)
    x_below = hist.sum(dim=y_dim).cumsum(dim=x_dim)
    y_below = hist.sum(dim=x_dim).cumsum(dim=y_dim)

    if mode == "above":
        # regions:
        # hits: x > xt AND y > yt
        hits = total - x_below - y_below + xy_below
        # miss: x > xt AND y <= yt
        miss = y_below - xy_below
        # false_pos: x <= xt AND y > yt
        false_pos = x_below - xy_below
        # true_neg: x <= xt AND y <= yt
        true_neg = xy_below

    else:
        hits = xy_below
        miss = x_below - xy_below
        false_pos = y_below - xy_below
        true_neg = total - x_below - y_below + xy_below

    return xr.Dataset({
        "hits": hits,
        "miss": miss,
        "false_pos": false_pos,
        "true_neg": true_neg,
    })


def plot_threshold(pod, far, pod_thresh=0.9, far_thresh=0.1):
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


def plot_threshold_2d(pod, far, pod_thresh=0.9, far_thresh=0.1):
    mask = (pod >= pod_thresh) & (far <= far_thresh)
    # for each truth: which has an estimate that meets pod/far thresh 
    valid_est = mask.any(dim="estimate")
    # which is the lowest truth threshold that has any estimate that meets pod/far thresh
    truth_idx = valid_est.astype(int).argmax(dim="truth").compute()
    has_any = valid_est.any(dim="truth")
    first_truth = truth_idx.where(has_any, np.nan)
    # get first estimate that meets pod/far thresh at that value of truth
    est_idx = mask.argmax(dim="estimate").compute()
    best_estimate = est_idx.isel(truth=truth_idx).where(has_any)

    # =========================================================
    # 5. Plot
    # =========================================================
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    overlay_cmap = mcolors.ListedColormap([(0, 0, 0, 0), (1, 0, 0, 1)])  # red

    # --- subplot 1: first truth ---
    first_truth.plot(
        ax=axes[0],
        x="lon",
        y="lat",
        cmap="YlGnBu"
    )

    axes[0].set_title("Lowest valid truth threshold")

    # --- subplot 2: corresponding estimate ---
    best_estimate.plot(
        ax=axes[1],
        x="lon",
        y="lat",
        cmap="YlGnBu"
    )

    axes[1].set_title("Corresponding estimate threshold")

    plt.tight_layout()

    return fig, first_truth, best_estimate


if __name__ == "__main__":
    start_remote(remote_name = "thresholds")#remote_config=["xlarge_cluster", "large_node"])

    # times
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    # data sources
    estimate = "imerg_final"
    truth = "tahmo_avg"

    # event defintion
    agg_days = 5
    dry_threshold = 0.5

    # spatial specs
    grid = "global0_25"
    space_grouping = None
    region = "ghana"
    spatial = False

    # get joint histogram
    bins = np.arange(0, 20, 0.1)
    hist = paired_histogram(start_time, end_time, estimate, truth, agg_days, grid=grid,
                            space_grouping=space_grouping, time_grouping=None, region=region,
                            spatial=spatial, bins=bins, recompute=True)
    import pdb; pdb.set_trace()

    # 2D contingency table
    ctable2d = contingency_2d(hist, x_dim="truth", y_dim="estimate", mode="above")
    # compute pod and far
    pod2 = ctable2d.hits / (ctable2d.hits + ctable2d.miss)
    far2 = ctable2d.false_pos / (ctable2d.false_pos + ctable2d.true_neg)
    import pdb; pdb.set_trace()
    plot_threshold_2d(pod2, far2, pod_thresh=0.85, far_thresh=0.15)

    """
    Contingency metrics where we set a threshold on stations and vary it over satellites.
    """                        
    ctable = contingency_1d(hist, xthreshold=dry_threshold, x_dim="truth", y_dim="estimate", mode="above")
    # compute pod and far
    pod = ctable.hits / (ctable.hits + ctable.miss)
    far = ctable.false_pos / (ctable.false_pos + ctable.true_neg)