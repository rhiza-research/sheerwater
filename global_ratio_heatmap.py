import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm

from sheerwater.utils import start_remote
import pca_lib


REGION = "global"
START_TIME = "2016-01-01"
END_TIME = "2024-12-31"
SEASON = None             # "DJF", "MAM", "JJA", "SON", or None for no filtering
VARIANCE_THRESHOLD = 0.95  # fraction of squared-singular-value energy required


if __name__ == "__main__":
    client = start_remote(remote_name="global_downscale_pca", remote_config="large_cluster")

    # pca_lib is a plain local module (not part of the installed sheerwater
    # package), so workers can't `import pca_lib` on their own -- upload it
    # explicitly so functions referencing it (e.g. inside apply_ufunc) can
    # be deserialized on the workers.
    client.upload_file(pca_lib.__file__)

    # ==================================================================
    # imerg precip
    # ==================================================================
    RESOLUTION = 0.25
    BLOCK_SIZE = 6
    MIN_RAIN, MAX_RAIN = 1.0, None   # only include days with mean cell rainfall in [MIN_RAIN, MAX_RAIN)
    MIN_DAYS_THRESHOLD = 500          # mask out cells with fewer than this many qualifying days
    BINWIDTH = 5

    hi_res = pca_lib.load_hi_res(REGION, RESOLUTION, START_TIME, END_TIME, dataset="imerg")
    hi_res = pca_lib.filter_season(hi_res, SEASON)
    blocked = pca_lib.make_blocked(hi_res, BLOCK_SIZE, variable="precip")
    blocked_stacked = pca_lib.stack_and_chunk(blocked)

    dimensionality = pca_lib.compute_dimensionality(
        blocked_stacked, hi_res, BLOCK_SIZE,
        threshold=VARIANCE_THRESHOLD, lo=MIN_RAIN, hi=MAX_RAIN, normalization="sum",
    )

    n_significant = dimensionality.n_significant.where(dimensionality.n_days >= MIN_DAYS_THRESHOLD)

    max_n_significant = float(np.nanmax(n_significant.values))
    n_bins = int(np.ceil(max_n_significant / BINWIDTH))
    bin_edges = 0.5 + BINWIDTH * np.arange(n_bins + 1)
    cmap = plt.get_cmap("turbo", n_bins)
    norm = BoundaryNorm(bin_edges, cmap.N)

    fig, ax = plt.subplots(figsize=(12, 6))
    im = n_significant.plot(ax=ax, x="lon", cmap=cmap, norm=norm, add_colorbar=False)
    cbar = fig.colorbar(im, ax=ax, ticks=bin_edges[:-1] + BINWIDTH / 2)
    cbar.ax.set_yticklabels([f"{int(lo + 0.5)}-{int(lo + BINWIDTH - 0.5)}" for lo in bin_edges[:-1]])
    ax.set_title("imerg precip: n_significant")
    plt.show()

    # keep precip's colorbar range/binning for the temp plot too, so the two
    # maps are directly comparable on the same scale
    shared_bin_edges, shared_cmap, shared_norm, shared_binwidth = bin_edges, cmap, norm, BINWIDTH

    breakpoint()

    # ==================================================================
    # era5 tmp2m
    # ==================================================================
    RESOLUTION = 0.25
    BLOCK_SIZE = 6

    hi_res = pca_lib.load_hi_res(REGION, RESOLUTION, START_TIME, END_TIME, dataset="era5", variable="tmp2m")
    hi_res = pca_lib.filter_season(hi_res, SEASON)
    blocked = pca_lib.make_blocked(hi_res, BLOCK_SIZE, variable="tmp2m")
    blocked_stacked = pca_lib.stack_and_chunk(blocked)

    dimensionality = pca_lib.compute_dimensionality(
        blocked_stacked, hi_res, BLOCK_SIZE,
        threshold=VARIANCE_THRESHOLD, lo=None, hi=None, normalization="zscore",
    )

    n_significant = dimensionality.n_significant

    fig, ax = plt.subplots(figsize=(12, 6))
    im = n_significant.plot(ax=ax, x="lon", cmap=shared_cmap, norm=shared_norm, add_colorbar=False)
    cbar = fig.colorbar(im, ax=ax, ticks=shared_bin_edges[:-1] + shared_binwidth / 2)
    cbar.ax.set_yticklabels(
        [f"{int(lo + 0.5)}-{int(lo + shared_binwidth - 0.5)}" for lo in shared_bin_edges[:-1]]
    )
    ax.set_title("era5 tmp2m: n_significant")
    plt.show()

    breakpoint()
