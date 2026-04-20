# --- SINGLE PAIRED HISTOGRAM FROM CSV (log counts, keep 0,0 bin) ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize

if __name__ == "__main__":
    region = "uganda"
    agg_days = 1
    grid_name = "global0_1"
    csv_file = f"{region}_hist_aggdays_{agg_days}_{grid_name}.csv"

    # --- READ CSV ---
    df = pd.read_csv(csv_file)
    df["estimate"] = df["estimate"].astype(int)
    df["truth"] = df["truth"].astype(int)
    df.set_index(["estimate", "truth"], inplace=True)

    # --- CONVERT TO 2D GRID ---
    grid = df["precip"].unstack(level="truth")

    # --- LOG TRANSFORM (keep 0,0 as-is) ---
    data = np.log1p(grid)  # zeros (including 0,0) become 0 in log1p

    # --- NORMALIZATION ---
    vmin = np.nanmin(data.values)
    vmax = np.nanmax(data.values)
    norm = Normalize(vmin=vmin, vmax=vmax)

    # --- COLORMAP ---
    cmap = cm.get_cmap("hot_r").copy()
    cmap.set_bad("white")
    high_density_color = cmap(0.95)

    # --- FIGURE ---
    fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)

    im = ax.imshow(
        data,
        origin="lower",
        aspect="auto",
        cmap=cmap,
        norm=norm
    )

    ax.set_xlabel("stations (mm/day)")
    ax.set_ylabel("satellite (mm/day)")
    ax.set_title(f"{region}: {agg_days}-day stations vs satellite precipitation")

    # --- MARGINAL DISTRIBUTIONS ---
    truth_dist = np.log1p(grid.sum(axis=0))
    est_dist   = np.log1p(grid.sum(axis=1))

    # top marginal
    ax_top = ax.inset_axes([0, 1.05, 1, 0.22], sharex=ax)
    ax_top.bar(truth_dist.index, truth_dist.values, color=high_density_color)
    ax_top.axis("off")

    # right marginal
    ax_right = ax.inset_axes([1.05, 0, 0.22, 1], sharey=ax)
    ax_right.barh(est_dist.index, est_dist.values, color=high_density_color)
    ax_right.axis("off")

    # --- COLORBAR ---
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label("log(event count)")

    plt.show()
