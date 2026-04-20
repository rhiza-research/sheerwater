
"""Visualize paired histograms and scatters at different grids."""
# get joint histogram at 0.25 grid in ghana for imerg_late and tahmo_avg
from dashboard_data.station_paired_analysis import paired_histogram
from sheerwater.utils import start_remote
import matplotlib.pyplot as plt
import numpy as np
from dashboard_data.station_paired_analysis import scatter_data

from matplotlib.colors import Normalize

def plot_histogram(df, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)

    grid = df["precip"].unstack(level="truth")

    # log transform (safe for zeros)
    data = np.log1p(grid)

    # normalization (single plot)
    vmin = np.nanmin(data.values)
    vmax = np.nanmax(data.values)
    norm = Normalize(vmin=vmin, vmax=vmax)

    # colormap: white (low) → yellow → red → black (high)
    cmap = plt.get_cmap("viridis")
    cmap.set_bad("black")  # NaNs = white

    # main heatmap
    ax.imshow(
        data,
        origin="lower",
        aspect="auto",
        cmap=cmap,
        norm=norm
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
    start_remote(remote_name="tuned_pod")

    start_time = "2010-01-01"
    end_time = "2025-12-31"
    region = "ghana"
    agg_days = 5

    bins = np.arange(0, 100, 1)

    grid3 = "global0_1"
    ds3 = paired_histogram(
        start_time,
        end_time,
        "imerg_final",
        "tahmo_avg",
        agg_days,
        grid=grid3,
        region=region,
        spatial=False,
        space_grouping=None,
        bins=bins,
    )
    df3 = ds3.to_dataframe()
    df3 = df3["precip"].unstack(level="truth")
    dfs3 = scatter_data(start_time, end_time, agg_days=agg_days, region=region, grid=grid3)


    grid1 = "global1_5"
    ds1 = paired_histogram(
        start_time,
        end_time,
        "imerg_final",
        "tahmo_avg",
        agg_days,
        grid=grid1,
        region=region,
        spatial=False,
        space_grouping=None,
        bins=bins,
    )
    df1 = ds1.to_dataframe()
    df1 = df1["precip"].unstack(level="truth")
    dfs1 = scatter_data(start_time, end_time, agg_days=agg_days, region=region, grid=grid1)

    grid2 = "global0_25"
    ds2 = paired_histogram(
        start_time,
        end_time,
        "imerg_final",
        "tahmo_avg",
        agg_days,
        grid=grid2,
        region=region,
        spatial=False,
        space_grouping=None,
        bins=bins,
    )
    df2 = ds2.to_dataframe()
    df2 = df2["precip"].unstack(level="truth")
    dfs2 = scatter_data(start_time, end_time, agg_days=agg_days, region=region, grid=grid2)


    fig, axes = plt.subplots(3, 2, figsize=(12, 8), constrained_layout=True)
    axes[0, 0].imshow(np.log(df1), origin="lower", aspect="auto")
    axes[0, 1].scatter(dfs1["tahmo_avg_precip"], dfs1["imerg_final_precip"], alpha=0.3, c="green")
    axes[1, 0].imshow(np.log(df2), origin="lower", aspect="auto")
    axes[1, 1].scatter(dfs2["tahmo_avg_precip"], dfs2["imerg_final_precip"], alpha=0.3, c="green")
    axes[2, 0].imshow(np.log(df3), origin="lower", aspect="auto")
    axes[2, 1].scatter(dfs3["tahmo_avg_precip"], dfs3["imerg_final_precip"], alpha=0.3, c="green")

    axes[0, 0].set_ylabel(grid1)
    axes[1, 0].set_ylabel(grid2)
    axes[2, 0].set_ylabel(grid3)
    plt.show()

    # plot histograms
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    axes = axes.flatten()
    plot_histogram(df1, ax=axes[0])
    plot_histogram(df2, ax=axes[1])
    axes[2].scatter(dfs1["imerg_final_precip"], dfs1["tahmo_avg_precip"], alpha=0.3, c="green")
    axes[2].set_title(grid1)
    axes[3].scatter(dfs2["imerg_final_precip"], dfs2["tahmo_avg_precip"], alpha=0.3, c="green")
    axes[3].set_title(grid2)
    plt.show()

 
