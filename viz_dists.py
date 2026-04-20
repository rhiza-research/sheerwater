import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import Normalize

def make_grid(df):
    return df.pivot(index="estimate", columns="truth", values="precip")

def plot_dist(grid, ax, norm, cmap):
    data = np.log1p(grid)

    im = ax.imshow(
        data,
        origin="lower",
        aspect="auto",
        cmap=cmap,
        norm=norm
    )

    ax.set_xlabel("stations (mm/day)")
    ax.set_ylabel("satellite (mm/day)")

    return im

def add_marginals(grid, ax, color):
    truth_dist = grid.sum(axis=0)
    est_dist = grid.sum(axis=1)

    ax_top = ax.inset_axes([0, 1.05, 1, 0.22], sharex=ax)
    ax_right = ax.inset_axes([1.05, 0, 0.22, 1], sharey=ax)

    ax_top.bar(truth_dist.index, truth_dist.values, color=color)
    ax_right.barh(est_dist.index, est_dist.values, color=color)

    ax_top.axis("off")
    ax_right.axis("off")


if __name__ == "__main__":
    region = "uganda"
    df1  = pd.read_csv(f"{region}_hist_aggdays_1_global0_1.csv")
    df5  = pd.read_csv(f"{region}_hist_aggdays_5_global0_1.csv")
    df10 = pd.read_csv(f"{region}_hist_aggdays_10_global0_1.csv")

    # ORDER: increasing aggregation
    grids = [
        make_grid(df1),
        make_grid(df5),
        make_grid(df10),
    ]
    labels = ["1-day", "5-day", "10-day"]

    # --- GLOBAL NORMALIZATION ---
    all_vals = np.concatenate([
        np.log1p(g.values.flatten())
        for g in grids
    ])

    vmin = np.nanmin(all_vals)
    vmax = np.nanmax(all_vals)
    norm = Normalize(vmin=vmin, vmax=vmax)

    # --- COLORMAP: flipped "hot" ---
    cmap = cm.get_cmap("hot_r").copy()
    cmap.set_bad(color="white")  # NaNs → white (blend with low density)

    # high-density color for marginals (dark end of colormap)
    high_density_color = cmap(0.95)

    # --- PLOT ---
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), constrained_layout=True)

    for ax, grid, label in zip(axes, grids, labels):
        im = plot_dist(grid, ax, norm, cmap)
        ax.set_title(label)

        add_marginals(grid, ax, high_density_color)

    # --- COLORBAR ---
    cbar = fig.colorbar(im, ax=axes, location="right", shrink=0.85, pad=0.02)
    cbar.set_label("log(event count)")
    import pdb; pdb.set_trace()

    plt.show()
