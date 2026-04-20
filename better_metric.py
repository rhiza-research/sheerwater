# get joint histogram at 0.25 grid in ghana for imerg_late and tahmo_avg
from dashboard_data.station_paired_analysis import paired_histogram
from sheerwater.utils import start_remote
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



def compute_weighted_best_fit(grid):
    """Compute weighted linear fit y = m*x + b from a 2D histogram grid.

    grid.index   → y values (satellite)
    grid.columns → x values (stations)
    grid.values  → weights (counts)
    """
    # bin coordinates
    x_vals = grid.columns.values.astype(float)
    y_vals = grid.index.values.astype(float)

    # meshgrid of bin centers
    xx, yy = np.meshgrid(x_vals, y_vals)

    # weights
    w = grid.values

    # flatten
    x = xx.flatten()
    y = yy.flatten()
    w = w.flatten()

    # valid points only
    mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(w) & (w > 0)
    x = x[mask]
    y = y[mask]
    w = w[mask]

    # weighted linear regression
    m, b = np.polyfit(x, y, 1, w=w)

    return m, b


def plot_histogram(df, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)

    grid = df["precip"].unstack(level="truth")

    # log transform (safe for zeros)
    data = np.log1p(grid)

    # normalization (single plot)
    # vmin = np.nanmin(data.values)
    #vmax = np.nanmax(data.values)
    #norm = Normalize(vmin=vmin, vmax=vmax)

    # colormap: white (low) → yellow → red → black (high)
    cmap = plt.get_cmap("gnuplot2")
    # flip the colormap
    cmap = cmap.reversed()
    # main heatmap
    im = ax.imshow(
        data,
        origin="lower",
        aspect="auto",
        cmap=cmap,
    )

       # 1. add x = y line
    x_vals = grid.columns.values.astype(float)
    y_vals = grid.index.values.astype(float)

    min_val = min(x_vals.min(), y_vals.min())
    max_val = max(x_vals.max(), y_vals.max())

    # 1. x = y line (red)
    ax.plot(
        [min_val, max_val],
        [min_val, max_val],
        color="red",
        linewidth=1.5, alpha=0.5,
        label="x = y"
    )

    # 2. weighted best-fit line
    m, b = compute_weighted_best_fit(grid)

    x_line = np.linspace(min_val, max_val, 200)
    y_line = m * x_line + b

    ax.plot(
        x_line,
        y_line,
        color="darkblue",
        linewidth=1.5, alpha=0.5,
        label=f"best fit (m={m:.2f})"
    )

    ax.set_xlabel("stations (mm/day)")
    ax.set_ylabel("satellite (mm/day)")
    ax.set_title("stations vs satellite precipitation")

    # --- marginals ---
    truth_dist = grid.sum(axis=0)
    est_dist = grid.sum(axis=1)

    high_density_color = cmap(0.95)

    ax_top = ax.inset_axes([0, 1.05, 1, 0.22], sharex=ax)
    ax_right = ax.inset_axes([1.05, 0, 0.22, 1], sharey=ax)

    ax_top.bar(truth_dist.index, truth_dist.values, color=high_density_color)
    ax_right.barh(est_dist.index, est_dist.values, color=high_density_color)

    ax_top.axis("off")
    ax_right.axis("off")

if __name__ == "__main__":
    start_remote(remote_name="error_hist_viz")

    start_time = "2020-01-01"
    end_time = "2025-12-31"
    region = "kenya"

    grids = ["global1_5", "global0_25", "global0_1"]
    agg_days_list = [1, 5, 10]
    results = {}


    for grid in grids:
        for agg_days in agg_days_list:
            ds = paired_histogram(start_time, end_time, "imerg_final", "tahmo", agg_days, grid=grid, region=region, spatial=False, space_grouping=None)
            df = ds.to_dataframe()
            df.to_csv(f"{region}_hist_aggdays_{agg_days}_{grid}.csv")
            results[f"{grid}_{agg_days}"] = df


    # load df from csv
    for grid in grids:
        for agg_days in agg_days_list:
            df = pd.read_csv(f"{region}_hist_aggdays_{agg_days}_{grid}.csv")
            df["estimate"] = df["estimate"].astype(int)
            df["truth"] = df["truth"].astype(int)
            df.set_index(["estimate", "truth"], inplace=True)
            results[f"{grid}_{agg_days}"] = df
    import pdb; pdb.set_trace()

    fig, axes = plt.subplots(len(grids), len(agg_days_list), figsize=(12, 8), constrained_layout=True, sharex=True, sharey=True)
    axes = axes.flatten()
    # plot all histograms
    for i, (key, df) in enumerate(results.items()):
        ax = axes[i]
        plot_histogram(df, ax=ax)
        grid_str = "0." + key.split("_")[1] + "°"
        agg_days_str = key.split("_")[2]
        ax.set_title(f"{grid_str} grid, {agg_days_str} day aggregation")

    import pdb; pdb.set_trace()
    # colorbar
    cbar = fig.colorbar(axes[0].images[0], ax=axes, location="right", shrink=0.85, pad=0.02)
    cbar.set_label("log(event count)")

    plt.show()
