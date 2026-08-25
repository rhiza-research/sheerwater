import numpy as np
import matplotlib.pyplot as plt

from sheerwater.utils import start_remote
from sheerwater.data import imerg_final


N_COMPONENTS = 10
TARGET_LAT = -30
TARGET_LON = 25


def decompose(x, method, n_components=N_COMPONENTS):
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

        # nmf requires non-negative input; raw rainfall already satisfies this
        model = NMF(n_components=n_components, init="nndsvda", max_iter=500)
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


if __name__ == "__main__":
    start_remote(remote_name="downscale_pca", remote_config="large_cluster")

    region = "africa"
    start_time = "2016-01-01"
    end_time = "2024-12-31"
    imerg_hi = imerg_final(start_time, end_time, grid="global0_1", region=region)

    n_lat, n_lon = 15, 15

    blocked = imerg_hi["precip"].coarsen(lat=n_lat, lon=n_lon, boundary="trim").construct(
        lat=("lat_lo", "lat_within"),
        lon=("lon_lo", "lon_within"),
    )
    n_lat_lo, n_lon_lo = blocked.sizes["lat_lo"], blocked.sizes["lon_lo"]

    lat_lo_centers = blocked["lat"].mean("lat_within").values
    lon_lo_centers = blocked["lon"].mean("lon_within").values

    candidates = sorted(
        ((i, j) for i in range(n_lat_lo) for j in range(n_lon_lo)),
        key=lambda ij: (lat_lo_centers[ij[0]] - TARGET_LAT) ** 2
        + (lon_lo_centers[ij[1]] - TARGET_LON) ** 2,
    )

    block = None
    block_vals = None
    for i, j in candidates:
        cand = blocked.isel(lat_lo=i, lon_lo=j)
        cand_vals = cand.values
        if not np.any(np.isnan(cand_vals)):
            block = cand
            block_vals = cand_vals
            print(f"using block lat_lo={i}, lon_lo={j}, "
                  f"lat~{float(cand.lat.mean()):.2f}, lon~{float(cand.lon.mean()):.2f} "
                  f"(target lat={TARGET_LAT}, lon={TARGET_LON})")
            break

    if block is None:
        raise RuntimeError("no fully land (all non-nan) block found near the target lat/lon")

    n_days = block_vals.shape[0]
    x = block_vals.reshape(n_days, n_lat * n_lon)
    PRECIP_THRESHOLD = 1
    mean = x.mean(axis=1)
    mask = mean >= PRECIP_THRESHOLD
    x = x[mask]
    n_days = x.shape[0]

    # normalize each day by its own total rainfall, so decomposition captures
    # spatial distribution (shape) rather than day-to-day rainfall magnitude.
    # scale-only (no mean-subtraction) so this stays non-negative for nmf.
    x_norm = x / x.sum(axis=1, keepdims=True)

    svd_components, svd_strength = decompose(x_norm, method="svd", n_components=N_COMPONENTS)
    nmf_components, nmf_strength = decompose(x_norm, method="nmf", n_components=N_COMPONENTS)

    rng = np.random.default_rng()
    example_idx = rng.choice(n_days, size=N_COMPONENTS, replace=False)

    LABEL_FONTSIZE = 8

    fig, axes = plt.subplots(3, N_COMPONENTS, figsize=(3 * N_COMPONENTS, 9), constrained_layout=True)

    day_vmax = x_norm[example_idx].max()
    for k in range(N_COMPONENTS):
        day_2d = x_norm[example_idx[k]].reshape(n_lat, n_lon)
        im = axes[0, k].imshow(day_2d, cmap="Blues", vmin=0, vmax=day_vmax)
        axes[0, k].set_title(f"day {example_idx[k]}", fontsize=LABEL_FONTSIZE)
    axes[0, 0].set_ylabel("example days", fontsize=LABEL_FONTSIZE)
    fig.colorbar(im, ax=axes[0, :].tolist(), fraction=0.02, pad=0.01)

    svd_vmax = np.abs(svd_components).max()
    for k in range(N_COMPONENTS):
        pattern_2d = svd_components[k].reshape(n_lat, n_lon)
        im = axes[1, k].imshow(pattern_2d, cmap="RdBu", vmin=-svd_vmax, vmax=svd_vmax)
        axes[1, k].set_title(f"sigma={svd_strength[k]:.2f}", fontsize=LABEL_FONTSIZE)
    axes[1, 0].set_ylabel("svd", fontsize=LABEL_FONTSIZE)
    fig.colorbar(im, ax=axes[1, :].tolist(), fraction=0.02, pad=0.01)

    nmf_vmax = nmf_components.max()
    for k in range(N_COMPONENTS):
        pattern_2d = nmf_components[k].reshape(n_lat, n_lon)
        im = axes[2, k].imshow(pattern_2d, cmap="Blues", vmin=0, vmax=nmf_vmax)
        axes[2, k].set_title(f"activation={nmf_strength[k]:.2f}", fontsize=LABEL_FONTSIZE)
    axes[2, 0].set_ylabel("nmf", fontsize=LABEL_FONTSIZE)
    fig.colorbar(im, ax=axes[2, :].tolist(), fraction=0.02, pad=0.01)

    for row in axes:
        for ax in row:
            ax.set_xticks([])
            ax.set_yticks([])

    block_lat = float(block.lat.mean())
    block_lon = float(block.lon.mean())
    fig.suptitle(f"lat={block_lat:.2f}, lon={block_lon:.2f}")

    breakpoint()
