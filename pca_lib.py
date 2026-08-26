"""Shared functions for exploring sub-grid spatial structure of IMERG rainfall
via SVD / NMF decomposition of high-res data blocked into low-res grid cells.

Consolidates the logic originally developed in downscale_pca.py (whole-region
apply_ufunc pipeline) and manual_pca_check.py (single-block manual checks).
"""
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm

from sheerwater.data import imerg_final
from sheerwater.reanalysis.era5 import era5


RESOLUTION_TO_GRID = {
    0.1: "global0_1",
    0.25: "global0_25",
    1.5: "global1_5",
}


# ---------------------------------------------------------------------------
# data loading / blocking
# ---------------------------------------------------------------------------

def load_hi_res(region, resolution, start_time="2016-01-01", end_time="2024-12-31",
                 dataset="imerg", variable=None):
    """Fetch a hi-res Dataset at the given resolution (degrees) and region.

    dataset: "imerg" (final precip) or "era5" (any era5 variable, e.g. "tmp2m" --
    see sheerwater.reanalysis.era5.era5 for available variables).
    variable: required when dataset="era5"; ignored for "imerg" (always precip).
    """
    if resolution not in RESOLUTION_TO_GRID:
        raise ValueError(f"unsupported resolution {resolution!r}, choose from {list(RESOLUTION_TO_GRID)}")
    grid = RESOLUTION_TO_GRID[resolution]

    if dataset == "imerg":
        return imerg_final(start_time, end_time, grid=grid, region=region)
    elif dataset == "era5":
        if variable is None:
            raise ValueError("variable is required when dataset='era5'")
        return era5(start_time, end_time, variable=variable, grid=grid, region=region)
    else:
        raise ValueError(f"unknown dataset {dataset!r}, choose 'imerg' or 'era5'")


def data_variable(dataset, variable=None):
    """Name of the data variable inside the Dataset returned by load_hi_res."""
    if dataset == "imerg":
        return "precip"
    elif dataset == "era5":
        if variable is None:
            raise ValueError("variable is required when dataset='era5'")
        return variable
    else:
        raise ValueError(f"unknown dataset {dataset!r}, choose 'imerg' or 'era5'")


def make_blocked(hi_res, block_size, variable="precip"):
    """Reshape hi_res into (lat_lo, lat_within, lon_lo, lon_within) blocks of
    size block_size x block_size. lat_within/lon_within are kept separate
    (not stacked) so this is usable both for whole-region apply_ufunc work
    (after stack_and_chunk) and for single-block manual inspection."""
    n = block_size
    return hi_res[variable].coarsen(lat=n, lon=n, boundary="trim").construct(
        lat=("lat_lo", "lat_within"),
        lon=("lon_lo", "lon_within"),
    )


def stack_and_chunk(blocked, lat_chunk=10, lon_chunk=10):
    """Stack lat_within/lon_within into a single "cell" dim and rechunk so
    each low-res cell's full time x cell matrix lives in one dask chunk."""
    stacked = blocked.stack(cell=("lat_within", "lon_within"))
    return stacked.chunk(time=-1, cell=-1, lat_lo=lat_chunk, lon_lo=lon_chunk)


def filter_season(imerg_hi, season):
    """Filter imerg_hi's time dim down to a meteorological season.

    season: one of "DJF", "MAM", "JJA", "SON" (or None to skip filtering).
    """
    if season is None:
        return imerg_hi
    valid = {"DJF", "MAM", "JJA", "SON"}
    if season not in valid:
        raise ValueError(f"unknown season {season!r}, choose from {sorted(valid)}")
    return imerg_hi.sel(time=imerg_hi["time"].dt.season == season)


def lo_res_coords(imerg_hi, block_size, n_lat_lo, n_lon_lo):
    """Low-res lat/lon coordinate values, derived from the hi-res grid and
    block_size (block-mean of each group of hi-res coordinates)."""
    n = block_size
    lat_coords = imerg_hi.lat.values[: n_lat_lo * n].reshape(n_lat_lo, n).mean(axis=1)
    lon_coords = imerg_hi.lon.values[: n_lon_lo * n].reshape(n_lon_lo, n).mean(axis=1)
    return lat_coords, lon_coords


# ---------------------------------------------------------------------------
# core per-block decomposition (pure numpy, used directly and via apply_ufunc)
# ---------------------------------------------------------------------------

NORMALIZATION_METHODS = ("sum", "zscore")


def normalize_days(x, method="sum"):
    """Normalize each day (row) by its own stats, so decomposition captures
    spatial distribution (shape) rather than day-to-day magnitude.

    method:
      "sum": divide each day by its own total. Non-negative-preserving (safe
        for nmf), appropriate for a strictly non-negative quantity like
        precip -- the row scale is meaningless (or sign-flipping) for
        variables that can be zero-mean or negative, like temperature.
      "zscore": subtract each day's own mean and divide by its own std.
        Appropriate for signed/unbounded variables like temperature; not
        safe for nmf, since it introduces negative values.

    Returns (x_norm, valid): valid is a per-row boolean mask, False where
    that day's scale factor was degenerate (zero sum / zero std).
    """
    if method == "sum":
        scale = x.sum(axis=1, keepdims=True)
        valid = scale[:, 0] > 0
        x_norm = x / scale
    elif method == "zscore":
        mean = x.mean(axis=1, keepdims=True)
        std = x.std(axis=1, keepdims=True)
        valid = std[:, 0] > 0
        x_norm = (x - mean) / std
    else:
        raise ValueError(f"unknown normalization {method!r}, choose from {NORMALIZATION_METHODS}")
    return x_norm, valid


def normalized_svd(x, lo=None, hi=None, normalization="sum"):
    """Filter, normalize, and decompose a single low-res cell's raw data.

    x: raw array of shape (time, cell) (unnormalized).
    lo/hi: keep only days whose mean value across the cell falls in [lo, hi).
    normalization: "sum" or "zscore" -- see normalize_days.

    Returns (s, vt, n_days): descending singular values, the corresponding right
    singular vectors (vt[i] is the length-`cell` spatial pattern for s[i]), and
    the number of days that survived filtering. s/vt are None if too few days
    survive filtering, data is missing, or normalization was degenerate for
    any surviving day.
    """
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

    x, valid = normalize_days(x, method=normalization)
    if not np.all(valid):
        return None, None, n_days

    _, s, vt = np.linalg.svd(x, full_matrices=False)
    return s, vt, n_days


def significant_singvals(x, threshold=0.95, lo=None, hi=None, normalization="sum"):
    """Number of leading singular values needed to reach `threshold` of the
    total energy, and the number of days that survived filtering."""
    s, _, n_days = normalized_svd(x, lo=lo, hi=hi, normalization=normalization)
    if s is None:
        return np.nan, n_days
    energy = np.cumsum(s ** 2) / np.sum(s ** 2)
    return float(np.searchsorted(energy, threshold) + 1), n_days


def singular_vector(x, sv, lo=None, hi=None, normalization="sum"):
    """The `sv`-th (0-indexed) right singular vector: the length-`cell` spatial
    pattern associated with the sv-th largest singular value."""
    s, vt, _ = normalized_svd(x, lo=lo, hi=hi, normalization=normalization)
    if s is None or sv >= len(s):
        return np.full(x.shape[1], np.nan)
    return vt[sv]


def filter_and_normalize_days(x, lo=1.0, hi=None, normalization="sum"):
    """Filter a raw (days, cell) array to days whose mean value falls in
    [lo, hi), then normalize each surviving day (dropping any day whose
    normalization was degenerate, e.g. zero sum / zero std)."""
    day_mean = x.mean(axis=1)
    mask = np.ones(x.shape[0], dtype=bool)
    if lo is not None:
        mask &= day_mean >= lo
    if hi is not None:
        mask &= day_mean < hi
    x = x[mask]
    x_norm, valid = normalize_days(x, method=normalization)
    return x_norm[valid]


def decompose(x, method, n_components=5, random_state=None, init=None):
    """Decompose x (days x cell) into `n_components` spatial patterns.

    Returns (components, strength): components has shape (n_components, cell);
    strength is a length-n_components array to display alongside each pattern
    (singular value for svd, total activation for nmf).
    """
    if method == "svd":
        _, s, vt = np.linalg.svd(x, full_matrices=False)
        return vt[:n_components], s[:n_components]
    elif method == "nmf":
        from sklearn.decomposition import NMF

        model = NMF(
            n_components=n_components,
            init=init or "nndsvda",
            max_iter=500,
            random_state=random_state,
        )
        w = model.fit_transform(x)
        h = model.components_

        # h rows aren't unit-normalized, so raw activation sums aren't
        # comparable across components. Rescale each component to unit norm
        # and fold that norm into w instead (w @ h is unchanged) so strength
        # reflects both how strongly a pattern is used and how large it is.
        h_norm = np.linalg.norm(h, axis=1)
        h_unit = h / h_norm[:, None]
        w_rescaled = w * h_norm[None, :]
        return h_unit, w_rescaled.sum(axis=0)
    else:
        raise ValueError(f"unknown method {method!r}")


# ---------------------------------------------------------------------------
# whole-region computation (apply_ufunc pipeline, from downscale_pca.py)
# ---------------------------------------------------------------------------

def compute_dimensionality(blocked_stacked, imerg_hi, block_size, threshold=0.95, lo=1.0, hi=None,
                            normalization="sum"):
    """Number of significant singular values (and number of surviving days)
    per low-res cell across the whole region, as an xr.Dataset with real
    lat/lon coordinates."""
    n_significant, n_days = xr.apply_ufunc(
        significant_singvals,
        blocked_stacked,
        input_core_dims=[["time", "cell"]],
        output_core_dims=[[], []],
        kwargs={"threshold": threshold, "lo": lo, "hi": hi, "normalization": normalization},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float, float],
    )
    dimensionality = xr.Dataset({"n_significant": n_significant, "n_days": n_days})

    n_lat_lo, n_lon_lo = dimensionality.sizes["lat_lo"], dimensionality.sizes["lon_lo"]
    lat_coords, lon_coords = lo_res_coords(imerg_hi, block_size, n_lat_lo, n_lon_lo)
    dimensionality = dimensionality.assign_coords(
        lat_lo=lat_coords, lon_lo=lon_coords
    ).rename(lat_lo="lat", lon_lo="lon")
    return dimensionality.compute()


def compute_pattern_full(blocked_stacked, imerg_hi, block_size, sv=0, lo=1.0, hi=None, normalization="sum"):
    """Leading (or sv-th) singular-vector spatial pattern per low-res cell,
    exploded back out onto the full hi-res grid with real lat/lon coords."""
    n = block_size
    pattern = xr.apply_ufunc(
        singular_vector,
        blocked_stacked,
        input_core_dims=[["time", "cell"]],
        output_core_dims=[["cell"]],
        kwargs={"sv": sv, "lo": lo, "hi": hi, "normalization": normalization},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float],
        dask_gufunc_kwargs={"output_sizes": {"cell": blocked_stacked.sizes["cell"]}},
    )

    n_lat_lo, n_lon_lo = pattern.sizes["lat_lo"], pattern.sizes["lon_lo"]
    lat_coords, lon_coords = lo_res_coords(imerg_hi, n, n_lat_lo, n_lon_lo)

    pattern = pattern.drop_vars(["lat", "lon"])
    pattern = pattern.assign_coords(
        lat_lo=("lat_lo", lat_coords),
        lon_lo=("lon_lo", lon_coords),
    )
    pattern = pattern.unstack("cell")

    pattern_full = pattern.stack(
        lat_stacked=("lat_lo", "lat_within"),
        lon_stacked=("lon_lo", "lon_within"),
    )
    n_hi_lat = pattern_full.sizes["lat_stacked"]
    n_hi_lon = pattern_full.sizes["lon_stacked"]
    pattern_full = (
        pattern_full
        .reset_index(["lat_stacked", "lon_stacked"], drop=True)
        .rename(lat_stacked="lat", lon_stacked="lon")
        .assign_coords(lat=imerg_hi.lat.values[:n_hi_lat], lon=imerg_hi.lon.values[:n_hi_lon])
    )
    return abs(pattern_full).compute()


def plot_n_significant(dimensionality, binwidth=5, cmap_name="turbo", ax=None):
    """Plot n_significant with a stepped (binned) colormap, one color per
    `binwidth`-sized range of significant-singular-value counts."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 5))

    max_n_significant = float(np.nanmax(dimensionality.n_significant.values))
    n_bins = int(np.ceil(max_n_significant / binwidth))
    bin_edges = 0.5 + binwidth * np.arange(n_bins + 1)
    cmap = plt.get_cmap(cmap_name, n_bins)
    norm = BoundaryNorm(bin_edges, cmap.N)

    im = dimensionality.n_significant.plot(ax=ax, x="lon", cmap=cmap, norm=norm, add_colorbar=False)
    cbar = ax.figure.colorbar(im, ax=ax, ticks=bin_edges[:-1] + binwidth / 2)
    cbar.ax.set_yticklabels([f"{int(lo + 0.5)}-{int(lo + binwidth - 0.5)}" for lo in bin_edges[:-1]])
    return ax


def plot_n_days(dimensionality, cmap_name="viridis", ax=None):
    """Map of the number of days meeting the rain-filter criteria, per low-res cell."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 5))
    dimensionality.n_days.plot(ax=ax, x="lon", cmap=cmap_name)
    ax.set_title("n_days meeting criteria")
    return ax


def plot_n_days_vs_significant(dimensionality, ax=None):
    """Scatter of n_days (x) vs n_significant (y), one point per low-res cell."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 5))
    n_days = dimensionality.n_days.values.flatten()
    n_significant = dimensionality.n_significant.values.flatten()
    ax.scatter(n_days, n_significant, s=8, alpha=0.5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n_days")
    ax.set_ylabel("n_significant")
    ax.set_title("n_significant vs n_days, per cell")
    return ax


def plot_ratio_heatmap(dimensionality, cmap_name="turbo", ax=None, min_days=None, binwidth_pct=0.5):
    """Map of the n_significant / n_days ratio (shown as a percentage), per
    low-res cell, with a stepped colormap (one color per `binwidth_pct`-sized
    range).

    min_days: if set, cells with fewer than this many qualifying days (i.e.
    not enough data to trust the ratio) are masked out before plotting.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 6))
    ratio_pct = 100 * dimensionality.n_significant / dimensionality.n_days
    ratio_pct = ratio_pct.where(np.isfinite(ratio_pct))
    if min_days is not None:
        ratio_pct = ratio_pct.where(dimensionality.n_days >= min_days)

    max_pct = float(np.nanmax(ratio_pct.values))
    n_bins = int(np.ceil(max_pct / binwidth_pct))
    bin_edges = binwidth_pct * np.arange(n_bins + 1)
    cmap = plt.get_cmap(cmap_name, n_bins)
    norm = BoundaryNorm(bin_edges, cmap.N)

    im = ratio_pct.plot(ax=ax, x="lon", cmap=cmap, norm=norm, add_colorbar=False)
    cbar = ax.figure.colorbar(im, ax=ax, ticks=bin_edges[:-1] + binwidth_pct / 2)
    cbar.ax.set_yticklabels([f"{lo:.1f}-{lo + binwidth_pct:.1f}%" for lo in bin_edges[:-1]])
    ax.set_title("n_significant / n_days (%)")
    return ax


# ---------------------------------------------------------------------------
# single-block manual inspection (from manual_pca_check.py)
# ---------------------------------------------------------------------------

def find_nearest_valid_block(blocked, target_lat, target_lon):
    """Find the low-res block nearest to (target_lat, target_lon) whose full
    hi-res sub-grid is free of NaNs (i.e. fully on land, for all days).

    Returns (i, j, block) where block is the DataArray for that cell, with
    dims (time, lat_within, lon_within) and real lat/lon coordinates.
    """
    n_lat_lo, n_lon_lo = blocked.sizes["lat_lo"], blocked.sizes["lon_lo"]
    lat_lo_centers = blocked["lat"].mean("lat_within").values
    lon_lo_centers = blocked["lon"].mean("lon_within").values

    candidates = sorted(
        ((i, j) for i in range(n_lat_lo) for j in range(n_lon_lo)),
        key=lambda ij: (lat_lo_centers[ij[0]] - target_lat) ** 2
        + (lon_lo_centers[ij[1]] - target_lon) ** 2,
    )

    for i, j in candidates:
        cand = blocked.isel(lat_lo=i, lon_lo=j)
        if not np.any(np.isnan(cand.values)):
            return i, j, cand

    raise RuntimeError("no fully land (all non-nan) block found near the target lat/lon")


def plot_decomp_comparison(x_norm, block_size, n_components, block_lat, block_lon, label_fontsize=8):
    """The 3-row (example days / svd / nmf) comparison plot from
    manual_pca_check.py, given an already filtered+normalized (days, cell)
    array."""
    n_days = x_norm.shape[0]
    svd_components, svd_strength = decompose(x_norm, method="svd", n_components=n_components)
    nmf_components, nmf_strength = decompose(x_norm, method="nmf", n_components=n_components)

    rng = np.random.default_rng()
    example_idx = rng.choice(n_days, size=n_components, replace=False)

    fig, axes = plt.subplots(3, n_components, figsize=(3 * n_components, 9), constrained_layout=True)

    day_vmax = x_norm[example_idx].max()
    for k in range(n_components):
        day_2d = x_norm[example_idx[k]].reshape(block_size, block_size)
        im = axes[0, k].imshow(day_2d, cmap="Blues", vmin=0, vmax=day_vmax)
        axes[0, k].set_title(f"day {example_idx[k]}", fontsize=label_fontsize)
    axes[0, 0].set_ylabel("example days", fontsize=label_fontsize)
    fig.colorbar(im, ax=axes[0, :].tolist(), fraction=0.02, pad=0.01)

    svd_vmax = np.abs(svd_components).max()
    for k in range(n_components):
        pattern_2d = svd_components[k].reshape(block_size, block_size)
        im = axes[1, k].imshow(pattern_2d, cmap="RdBu", vmin=-svd_vmax, vmax=svd_vmax)
        axes[1, k].set_title(f"sigma={svd_strength[k]:.2f}", fontsize=label_fontsize)
    axes[1, 0].set_ylabel("svd", fontsize=label_fontsize)
    fig.colorbar(im, ax=axes[1, :].tolist(), fraction=0.02, pad=0.01)

    nmf_vmax = nmf_components.max()
    for k in range(n_components):
        pattern_2d = nmf_components[k].reshape(block_size, block_size)
        im = axes[2, k].imshow(pattern_2d, cmap="Blues", vmin=0, vmax=nmf_vmax)
        axes[2, k].set_title(f"activation={nmf_strength[k]:.2f}", fontsize=label_fontsize)
    axes[2, 0].set_ylabel("nmf", fontsize=label_fontsize)
    fig.colorbar(im, ax=axes[2, :].tolist(), fraction=0.02, pad=0.01)

    for row in axes:
        for ax in row:
            ax.set_xticks([])
            ax.set_yticks([])

    fig.suptitle(f"lat={block_lat:.2f}, lon={block_lon:.2f}")
    return fig, axes


def run_nmf_repeats(x_norm, n_components, n_runs, init="random"):
    """Run NMF n_runs times (different random_state each time) and return a
    list of (components, strength) tuples, for visually comparing
    run-to-run consistency."""
    results = []
    for run in range(n_runs):
        components, strength = decompose(
            x_norm, method="nmf", n_components=n_components, random_state=run, init=init
        )
        results.append((components, strength))
    return results


def plot_nmf_repeats(results, block_size, block_lat, block_lon, label_fontsize=8):
    """Plot each NMF run's components as one row, so rows can be visually
    compared for consistency across restarts."""
    n_runs = len(results)
    n_components = results[0][0].shape[0]
    vmax = max(components.max() for components, _ in results)

    fig, axes = plt.subplots(n_runs, n_components, figsize=(3 * n_components, 3 * n_runs), constrained_layout=True)
    if n_runs == 1:
        axes = axes[None, :]

    for run, (components, strength) in enumerate(results):
        for k in range(n_components):
            pattern_2d = components[k].reshape(block_size, block_size)
            im = axes[run, k].imshow(pattern_2d, cmap="Blues", vmin=0, vmax=vmax)
            axes[run, k].set_title(f"activation={strength[k]:.2f}", fontsize=label_fontsize)
        axes[run, 0].set_ylabel(f"run {run}", fontsize=label_fontsize)
        fig.colorbar(im, ax=axes[run, :].tolist(), fraction=0.02, pad=0.01)

    for row in axes:
        for ax in row:
            ax.set_xticks([])
            ax.set_yticks([])

    fig.suptitle(f"nmf across {n_runs} restarts, lat={block_lat:.2f}, lon={block_lon:.2f}")
    return fig, axes
