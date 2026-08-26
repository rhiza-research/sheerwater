"""Simple downscaling experiments. 

This script provides some simple statistical transformations to
explore the dimensionality and recurring patterns in high resolution
precipitation data. It can also be applied to temperature fields for
comparison.
"""
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm

from sheerwater.utils import start_remote
from sheerwater.data import imerg_final
from sheerwater.reanalysis.era5 import era5


# ============================================================================
# config
# ============================================================================

DATASET = "imerg"          # "imerg" (final precip) or "era5" (any era5 variable)
VARIABLE = "tmp2m"          # only used when DATASET == "era5"
NORMALIZATION = "sum"       # "sum" (precip, non-negative) or "zscore" (temperature-like)

REGION = "africa"                                          # map + single-block pattern comparison
REGIONS = ["africa", "europe", "south_america", "asia"]     # regions compared in the scatter
REGION_COLORS = {"africa": "tab:orange", "europe": "tab:blue",
                  "south_america": "tab:green", "asia": "tab:red"}

RESOLUTION = 0.25    # hi-res grid spacing (degrees)
BLOCK_SIZE = 6        # low-res cell = BLOCK_SIZE x BLOCK_SIZE hi-res pixels (square)
RESOLUTION_TO_GRID = {0.1: "global0_1", 0.25: "global0_25", 1.5: "global1_5"}

START_TIME = "2016-01-01"
END_TIME = "2024-12-31"
SEASON = None                       # "DJF", "MAM", "JJA", "SON", or None

VARIANCE_THRESHOLD = 0.95            # fraction of squared-singular-value energy required
MIN_VALUE, MAX_VALUE = 1.0, None     # only include days whose mean cell value is in [MIN_VALUE, MAX_VALUE)
MIN_DAYS = 365                        # mask cells with fewer qualifying days than this, in the map

TARGET_LAT, TARGET_LON = -2.0, 23.0   # block used for the svd/nmf pattern comparison
N_COMPONENTS = 5


# ============================================================================
# data loading / blocking
# ============================================================================

def load_hi_res(region, resolution=RESOLUTION, dataset=DATASET, variable=VARIABLE):
    """Fetch a hi-res Dataset for `region` at `resolution` degrees."""
    grid = RESOLUTION_TO_GRID[resolution]
    if dataset == "imerg":
        return imerg_final(START_TIME, END_TIME, grid=grid, region=region)
    return era5(START_TIME, END_TIME, variable=variable, grid=grid, region=region)


def data_variable(dataset=DATASET, variable=VARIABLE):
    """Name of the data variable inside the Dataset returned by load_hi_res."""
    return "precip" if dataset == "imerg" else variable


def filter_season(ds, season=SEASON):
    """Filter ds's time dim to a meteorological season, or pass through."""
    return ds if season is None else ds.sel(time=ds["time"].dt.season == season)


def make_blocked(hi_res, block_size=BLOCK_SIZE, variable=None):
    """Reshape into (lat_lo, lat_within, lon_lo, lon_within) blocks of
    block_size x block_size hi-res pixels."""
    variable = variable or data_variable()
    n = block_size
    return hi_res[variable].coarsen(lat=n, lon=n, boundary="trim").construct(
        lat=("lat_lo", "lat_within"), lon=("lon_lo", "lon_within"),
    )


def lo_res_coords(hi_res, block_size, n_lat_lo, n_lon_lo):
    """Low-res lat/lon coords, derived as block-means of the hi-res grid."""
    lat = hi_res.lat.values[: n_lat_lo * block_size].reshape(n_lat_lo, block_size).mean(axis=1)
    lon = hi_res.lon.values[: n_lon_lo * block_size].reshape(n_lon_lo, block_size).mean(axis=1)
    return lat, lon


# ============================================================================
# core per-cell decomposition
# ============================================================================

def normalize_days(x, method=NORMALIZATION):
    """Normalize each day (row) so decomposition captures spatial shape
    rather than day-to-day magnitude. Returns (x_norm, valid_row_mask)."""
    if method == "sum":
        scale = x.sum(axis=1, keepdims=True)
        return x / scale, scale[:, 0] > 0
    mean, std = x.mean(axis=1, keepdims=True), x.std(axis=1, keepdims=True)
    return (x - mean) / std, std[:, 0] > 0


def normalized_svd(x, lo=MIN_VALUE, hi=MAX_VALUE, normalization=NORMALIZATION):
    """Filter a (time, cell) block to qualifying days, normalize, and SVD it.
    Returns (s, vt, n_days); s/vt are None if too few valid days remain."""
    day_mean = np.nanmean(x, axis=1)
    mask = np.ones(x.shape[0], dtype=bool)
    if lo is not None:
        mask &= day_mean >= lo
    if hi is not None:
        mask &= day_mean < hi
    x = x[mask]
    n_days = x.shape[0]
    if n_days < 2 or np.any(np.isnan(x)):
        return None, None, n_days
    x, valid = normalize_days(x, normalization)
    if not np.all(valid):
        return None, None, n_days
    _, s, vt = np.linalg.svd(x, full_matrices=False)
    return s, vt, n_days


def significant_singvals(x, threshold=VARIANCE_THRESHOLD, lo=MIN_VALUE, hi=MAX_VALUE,
                          normalization=NORMALIZATION):
    """Number of leading singular values needed to reach `threshold` of total
    energy, and number of qualifying days. For use with xr.apply_ufunc."""
    s, _, n_days = normalized_svd(x, lo, hi, normalization)
    if s is None:
        return np.nan, n_days
    energy = np.cumsum(s ** 2) / np.sum(s ** 2)
    return float(np.searchsorted(energy, threshold) + 1), n_days


def filter_and_normalize_days(x, lo=MIN_VALUE, hi=MAX_VALUE, normalization=NORMALIZATION):
    """Filter a raw (days, cell) array to qualifying days, then normalize."""
    day_mean = x.mean(axis=1)
    mask = np.ones(x.shape[0], dtype=bool)
    if lo is not None:
        mask &= day_mean >= lo
    if hi is not None:
        mask &= day_mean < hi
    x_norm, valid = normalize_days(x[mask], normalization)
    return x_norm[valid]


def decompose(x, method, n_components=N_COMPONENTS, random_state=None):
    """SVD or NMF of an already-normalized (days, cell) matrix.
    Returns (components, strength): components (n_components, cell); strength
    is the singular value (svd) or rescaled total activation (nmf)."""
    if method == "svd":
        _, s, vt = np.linalg.svd(x, full_matrices=False)
        return vt[:n_components], s[:n_components]
    from sklearn.decomposition import NMF
    model = NMF(n_components=n_components, init="nndsvda", max_iter=500, random_state=random_state)
    w = model.fit_transform(x)
    h = model.components_
    # rescale h to unit norm and fold the norm into w (w @ h unchanged), so
    # strength reflects both usage and pattern magnitude
    h_norm = np.linalg.norm(h, axis=1)
    return h / h_norm[:, None], (w * h_norm[None, :]).sum(axis=0)


def find_nearest_valid_block(blocked, target_lat, target_lon):
    """Nearest block to (target_lat, target_lon) with no missing hi-res data.
    Returns the block DataArray (dims time, lat_within, lon_within)."""
    n_lat_lo, n_lon_lo = blocked.sizes["lat_lo"], blocked.sizes["lon_lo"]
    lat_centers = blocked["lat"].mean("lat_within").values
    lon_centers = blocked["lon"].mean("lon_within").values
    candidates = sorted(
        ((i, j) for i in range(n_lat_lo) for j in range(n_lon_lo)),
        key=lambda ij: (lat_centers[ij[0]] - target_lat) ** 2 + (lon_centers[ij[1]] - target_lon) ** 2,
    )
    for i, j in candidates:
        block = blocked.isel(lat_lo=i, lon_lo=j)
        if not np.any(np.isnan(block.values)):
            return block
    raise RuntimeError("no fully valid block found near the target lat/lon")


# ============================================================================
# region-wide dimensionality
# ============================================================================

def compute_dimensionality(region, resolution=RESOLUTION, block_size=BLOCK_SIZE):
    """n_significant / n_days per low-res cell across `region`, as an
    xr.Dataset with real lat/lon coordinates."""
    hi_res = filter_season(load_hi_res(region, resolution))
    blocked = make_blocked(hi_res, block_size).stack(cell=("lat_within", "lon_within"))
    blocked = blocked.chunk(time=-1, cell=-1, lat_lo=10, lon_lo=10)

    n_significant, n_days = xr.apply_ufunc(
        significant_singvals, blocked,
        input_core_dims=[["time", "cell"]], output_core_dims=[[], []],
        vectorize=True, dask="parallelized", output_dtypes=[float, float],
    )
    dimensionality = xr.Dataset({"n_significant": n_significant, "n_days": n_days})

    n_lat_lo, n_lon_lo = dimensionality.sizes["lat_lo"], dimensionality.sizes["lon_lo"]
    lat, lon = lo_res_coords(hi_res, block_size, n_lat_lo, n_lon_lo)
    dimensionality = dimensionality.assign_coords(lat_lo=lat, lon_lo=lon).rename(lat_lo="lat", lon_lo="lon")
    return dimensionality.compute()


# ============================================================================
# plotting
# ============================================================================

def plot_significance_map(dimensionality, binwidth=5, min_days=MIN_DAYS):
    """Map of n_significant with a stepped colormap, masking low-sample cells."""
    n_significant = dimensionality.n_significant.where(dimensionality.n_days >= min_days)
    max_n = float(np.nanmax(n_significant.values))
    n_bins = int(np.ceil(max_n / binwidth))
    bin_edges = 0.5 + binwidth * np.arange(n_bins + 1)
    cmap = plt.get_cmap("turbo", n_bins)
    norm = BoundaryNorm(bin_edges, cmap.N)

    fig, ax = plt.subplots(figsize=(10, 6))
    im = n_significant.plot(ax=ax, x="lon", cmap=cmap, norm=norm, add_colorbar=False)
    cbar = fig.colorbar(im, ax=ax, ticks=bin_edges[:-1] + binwidth / 2)
    cbar.ax.set_yticklabels([f"{int(lo + 0.5)}-{int(lo + binwidth - 0.5)}" for lo in bin_edges[:-1]])
    ax.set_title(f"n_significant ({DATASET}{'' if DATASET == 'imerg' else ':' + VARIABLE}, {REGION})")


def plot_region_scatters(regions):
    """n_days vs n_significant scatter, one subplot per region, shared lims."""
    per_region = {r: compute_dimensionality(r) for r in regions}
    all_days = np.concatenate([d.n_days.values.flatten() for d in per_region.values()])
    all_sig = np.concatenate([d.n_significant.values.flatten() for d in per_region.values()])
    xlim, ylim = (0, np.nanmax(all_days) * 1.05), (0, np.nanmax(all_sig) * 1.05)

    fig, axes = plt.subplots(1, len(regions), figsize=(5 * len(regions), 5), sharex=True, sharey=True)
    for ax, region in zip(axes, regions):
        d = per_region[region]
        ax.scatter(d.n_days.values.flatten(), d.n_significant.values.flatten(),
                   s=40, alpha=0.15, color=REGION_COLORS.get(region))
        ax.set_title(region)
        ax.set_xlabel("n_days")
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    axes[0].set_ylabel("n_significant")
    plt.tight_layout()


def plot_block_patterns(region, target_lat, target_lon, n_components=N_COMPONENTS):
    """Example days vs svd vs nmf spatial patterns for the block nearest
    (target_lat, target_lon)."""
    hi_res = filter_season(load_hi_res(region))
    blocked = make_blocked(hi_res)
    block = find_nearest_valid_block(blocked, target_lat, target_lon)
    block_lat, block_lon = float(block.lat.mean()), float(block.lon.mean())

    x = block.values.reshape(block.sizes["time"], BLOCK_SIZE * BLOCK_SIZE)
    x_norm = filter_and_normalize_days(x)

    svd_components, svd_strength = decompose(x_norm, "svd", n_components)
    nmf_components, nmf_strength = decompose(x_norm, "nmf", n_components)

    rng = np.random.default_rng()
    example_idx = rng.choice(x_norm.shape[0], size=n_components, replace=False)

    fig, axes = plt.subplots(3, n_components, figsize=(3 * n_components, 9), constrained_layout=True)

    day_vmax = x_norm[example_idx].max()
    for k in range(n_components):
        im = axes[0, k].imshow(x_norm[example_idx[k]].reshape(BLOCK_SIZE, BLOCK_SIZE),
                                cmap="viridis", vmin=0, vmax=day_vmax)
        axes[0, k].set_title(f"day {example_idx[k]}", fontsize=8)
    axes[0, 0].set_ylabel("example days", fontsize=8)
    fig.colorbar(im, ax=axes[0, :].tolist(), fraction=0.02, pad=0.01)

    svd_vmax = np.abs(svd_components).max()
    for k in range(n_components):
        im = axes[1, k].imshow(svd_components[k].reshape(BLOCK_SIZE, BLOCK_SIZE),
                                cmap="RdBu", vmin=-svd_vmax, vmax=svd_vmax)
        axes[1, k].set_title(f"sigma={svd_strength[k]:.2f}", fontsize=8)
    axes[1, 0].set_ylabel("svd", fontsize=8)
    fig.colorbar(im, ax=axes[1, :].tolist(), fraction=0.02, pad=0.01)

    nmf_vmax = nmf_components.max()
    for k in range(n_components):
        im = axes[2, k].imshow(nmf_components[k].reshape(BLOCK_SIZE, BLOCK_SIZE),
                                cmap="viridis", vmin=0, vmax=nmf_vmax)
        axes[2, k].set_title(f"activation={nmf_strength[k]:.2f}", fontsize=8)
    axes[2, 0].set_ylabel("nmf", fontsize=8)
    fig.colorbar(im, ax=axes[2, :].tolist(), fraction=0.02, pad=0.01)

    for row in axes:
        for ax in row:
            ax.set_xticks([])
            ax.set_yticks([])
    fig.suptitle(f"lat={block_lat:.2f}, lon={block_lon:.2f}")


# ============================================================================
# main
# ============================================================================

if __name__ == "__main__":
    start_remote(remote_name="downscale_pca", remote_config="large_cluster")

    # 1. map of n_significant across REGION
    dimensionality = compute_dimensionality(REGION)
    plot_significance_map(dimensionality)
    plt.show()
    breakpoint()

    # 2. n_days vs n_significant scatter compared across REGIONS
    plot_region_scatters(REGIONS)
    plt.show()
    breakpoint()

    # 3. svd/nmf spatial-pattern comparison for the block near TARGET_LAT/TARGET_LON
    plot_block_patterns(REGION, TARGET_LAT, TARGET_LON)
    plt.show()
    breakpoint()
