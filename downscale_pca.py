import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm

from sheerwater.utils import start_remote
from sheerwater.data import imerg_final


VARIANCE_THRESHOLD = 0.95


def _normalized_svd(x, lo=None, hi=None):
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

    # normalize each day by its own total rainfall, so decomposition captures
    # spatial distribution (shape) rather than day-to-day rainfall magnitude
    row_sums = x.sum(axis=1, keepdims=True)
    if np.any(row_sums <= 0):
        return None, None, n_days
    x = x / row_sums

    _, s, vt = np.linalg.svd(x, full_matrices=False)
    return s, vt, n_days


def significant_singvals(x, threshold=VARIANCE_THRESHOLD, lo=None, hi=None):
    s, _, n_days = _normalized_svd(x, lo=lo, hi=hi)
    if s is None:
        return np.nan, n_days
    energy = np.cumsum(s ** 2) / np.sum(s ** 2)
    return float(np.searchsorted(energy, threshold) + 1), n_days


def singular_vector(x, sv, lo=None, hi=None):
    s, vt, _ = _normalized_svd(x, lo=lo, hi=hi)
    if s is None or sv >= len(s):
        return np.full(x.shape[1], np.nan)
    return vt[sv]


if __name__ == "__main__":
    start_remote(remote_name="downscale_pca", remote_config="large_cluster")

    region = "south_america"
    start_time = "2016-01-01"
    end_time = "2024-12-31"
    #imerg_lo = imerg_final(start_time, end_time, grid="global1_5", region=region)
    imerg_hi = imerg_final(start_time, end_time, grid="global0_1", region=region)

    n_lat, n_lon = 15, 15

    blocked = imerg_hi["precip"].coarsen(lat=n_lat, lon=n_lon, boundary="trim").construct(
        lat=("lat_lo", "lat_within"),
        lon=("lon_lo", "lon_within"),
    )
    blocked = blocked.stack(cell=("lat_within", "lon_within"))
    blocked = blocked.chunk(time=-1, cell=-1, lat_lo=10, lon_lo=10)

    lo_thresh, hi_thresh = 1.0, None

    n_significant, n_days = xr.apply_ufunc(
        significant_singvals,
        blocked,
        input_core_dims=[["time", "cell"]],
        output_core_dims=[[], []],
        kwargs={"threshold": VARIANCE_THRESHOLD, "lo": lo_thresh, "hi": hi_thresh},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float, float],
    )
    dimensionality = xr.Dataset({"n_significant": n_significant, "n_days": n_days})

    pattern = xr.apply_ufunc(
        singular_vector,
        blocked,
        input_core_dims=[["time", "cell"]],
        output_core_dims=[["cell"]],
        kwargs={"sv": 0, "lo": lo_thresh, "hi": hi_thresh},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float],
        dask_gufunc_kwargs={"output_sizes": {"cell": blocked.sizes["cell"]}},
    )

    n_lat_lo, n_lon_lo = dimensionality.sizes["lat_lo"], dimensionality.sizes["lon_lo"]
    lat_lo_coords = imerg_hi.lat.values[: n_lat_lo * n_lat].reshape(n_lat_lo, n_lat).mean(axis=1)
    lon_lo_coords = imerg_hi.lon.values[: n_lon_lo * n_lon].reshape(n_lon_lo, n_lon).mean(axis=1)

    dimensionality = dimensionality.assign_coords(
        lat_lo=lat_lo_coords,
        lon_lo=lon_lo_coords,
    ).rename(lat_lo="lat", lon_lo="lon")

    pattern = pattern.drop_vars(["lat", "lon"])
    pattern = pattern.assign_coords(
        lat_lo=("lat_lo", lat_lo_coords),
        lon_lo=("lon_lo", lon_lo_coords),
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
    pattern_full = abs(pattern_full)

    dimensionality = dimensionality.compute()
    pattern_full = pattern_full.compute()
    unique_days = dimensionality.n_significant / dimensionality.n_days

    # plot 1: map of number of significant singular values
    N_SIGNIFICANT_BINWIDTH = 5

    max_n_significant = float(np.nanmax(dimensionality.n_significant.values))
    n_bins = int(np.ceil(max_n_significant / N_SIGNIFICANT_BINWIDTH))
    bin_edges = 0.5 + N_SIGNIFICANT_BINWIDTH * np.arange(n_bins + 1)
    cmap = plt.get_cmap("turbo", n_bins)
    norm = BoundaryNorm(bin_edges, cmap.N)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = dimensionality.n_significant.plot(ax=ax, x="lon", cmap=cmap, norm=norm, add_colorbar=False)
    cbar = fig.colorbar(im, ax=ax, ticks=bin_edges[:-1] + N_SIGNIFICANT_BINWIDTH / 2)
    cbar.ax.set_yticklabels(
        [f"{int(lo + 0.5)}-{int(lo + N_SIGNIFICANT_BINWIDTH - 0.5)}" for lo in bin_edges[:-1]]
    )
    plt.show()
    breakpoint()

    # plot 2: map of number of days meeting criteria
    fig, ax = plt.subplots(figsize=(6, 5))
    dimensionality.n_days.plot(ax=ax, x="lon")
    plt.show()
    breakpoint()

    # plot 3: scatter of n_significant vs n_days, per cell
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(
        dimensionality.n_days.values.flatten(),
        dimensionality.n_significant.values.flatten(),
        s=8, alpha=0.5,
    )
    ax.set_xlabel("n_days")
    ax.set_ylabel("n_significant")
    plt.show()
    breakpoint()
