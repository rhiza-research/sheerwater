import numpy as np
import matplotlib.pyplot as plt

from sheerwater.utils import start_remote
from sheerwater.data import imerg_final


DECOMP_METHOD = "svd"  # "svd" or "nmf"
N_COMPONENTS = 5


def decompose(x, method=DECOMP_METHOD, n_components=N_COMPONENTS):
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
    imerg_hi = imerg_final(start_time, end_time, grid="global0_25", region=region)

    n_lat, n_lon = 6, 6

    blocked = imerg_hi["precip"].coarsen(lat=n_lat, lon=n_lon, boundary="trim").construct(
        lat=("lat_lo", "lat_within"),
        lon=("lon_lo", "lon_within"),
    )
    n_lat_lo, n_lon_lo = blocked.sizes["lat_lo"], blocked.sizes["lon_lo"]

    center_i, center_j = n_lat_lo // 2, n_lon_lo // 2
    candidates = sorted(
        ((i, j) for i in range(n_lat_lo) for j in range(n_lon_lo)),
        key=lambda ij: (ij[0] - center_i) ** 2 + (ij[1] - center_j) ** 2,
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
                  f"lat~{float(cand.lat.mean()):.2f}, lon~{float(cand.lon.mean()):.2f}")
            break

    if block is None:
        raise RuntimeError("no fully land (all non-nan) block found")

    n_days = block_vals.shape[0]
    x = block_vals.reshape(n_days, n_lat * n_lon)
    # filter to days where mean rainfall is >= 1 mm
    PRECIP_THRESHOLD = 1
    mean = x.mean(axis=1)
    mask = mean >= PRECIP_THRESHOLD
    x = x[mask]
    n_days = x.shape[0]

    components, strength = decompose(x, method=DECOMP_METHOD, n_components=N_COMPONENTS)
    strength_label = "sigma" if DECOMP_METHOD == "svd" else "activation"

    fig, axes = plt.subplots(1, N_COMPONENTS, figsize=(3 * N_COMPONENTS, 3))
    for k in range(N_COMPONENTS):
        pattern_2d = components[k].reshape(n_lat, n_lon)
        im = axes[k].imshow(pattern_2d, cmap="RdBu_r")
        axes[k].set_title(f"{DECOMP_METHOD} {k}\n{strength_label}={strength[k]:.2f}")
        plt.colorbar(im, ax=axes[k], fraction=0.046)
    plt.tight_layout()

    breakpoint()
