import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from sheerwater.utils import start_remote
import pca_lib


REGION = "africa"
RESOLUTION = 0.1
BLOCK_SIZE = 15          # low-res cell = BLOCK_SIZE x BLOCK_SIZE hi-res pixels (square, 1.5deg here)
START_TIME = "2016-01-01"
END_TIME = "2024-12-31"

TARGET_LAT = -2.0
TARGET_LON = 23.0

MIN_RAIN, MAX_RAIN = 1.0, None   # only include days with mean cell rainfall in [MIN_RAIN, MAX_RAIN)
N_DAYS_MATRIX = 100               # number of qualifying days to build the matrix from
N_EXAMPLE_DAYS = 10
N_COMPONENTS = 5

NORMALIZATION = "sum"


if __name__ == "__main__":
    start_remote(remote_name="downscale_pca", remote_config="large_cluster")

    imerg_hi = pca_lib.load_hi_res(REGION, RESOLUTION, START_TIME, END_TIME)
    blocked = pca_lib.make_blocked(imerg_hi, BLOCK_SIZE)

    i, j, block = pca_lib.find_nearest_valid_block(blocked, TARGET_LAT, TARGET_LON)
    block_lat, block_lon = float(block.lat.mean()), float(block.lon.mean())
    print(f"using block lat_lo={i}, lon_lo={j}, lat~{block_lat:.2f}, lon~{block_lon:.2f}")

    # ------------------------------------------------------------------
    # 1. Africa map with the low-res (1.5deg) box outlined around the hi-res pixels
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 8))
    imerg_hi["precip"].isel(time=0).plot(ax=ax, x="lon", cmap="viridis", add_colorbar=True)

    lat_min = float(block.lat.min()) - RESOLUTION / 2
    lat_max = float(block.lat.max()) + RESOLUTION / 2
    lon_min = float(block.lon.min()) - RESOLUTION / 2
    lon_max = float(block.lon.max()) + RESOLUTION / 2
    ax.add_patch(Rectangle(
        (lon_min, lat_min), lon_max - lon_min, lat_max - lat_min,
        fill=False, edgecolor="red", linewidth=2,
    ))
    ax.set_title(f"Africa (IMERG, 0.1deg) -- 1.5deg box at lat~{block_lat:.2f}, lon~{block_lon:.2f}")
    plt.show()
    breakpoint()

    # ------------------------------------------------------------------
    # 2. 10 random days of that box, raw (unfiltered), dated
    # ------------------------------------------------------------------
    rng = np.random.default_rng()
    n_days_total = block.sizes["time"]
    example_idx = rng.choice(n_days_total, size=N_EXAMPLE_DAYS, replace=False)
    example_idx.sort()

    fig, axes = plt.subplots(1, N_EXAMPLE_DAYS, figsize=(2.5 * N_EXAMPLE_DAYS, 3), constrained_layout=True)
    vmax = block.isel(time=example_idx).values.max()
    for k, idx in enumerate(example_idx):
        day_2d = block.isel(time=int(idx)).values
        date_str = str(block.time.isel(time=int(idx)).values)[:10]
        im = axes[k].imshow(day_2d, cmap="viridis", vmin=0, vmax=vmax)
        axes[k].set_title(date_str, fontsize=9)
        axes[k].set_xticks([])
        axes[k].set_yticks([])
    fig.colorbar(im, ax=axes.tolist(), fraction=0.02, pad=0.01)
    fig.suptitle(f"10 random days -- lat~{block_lat:.2f}, lon~{block_lon:.2f}")
    plt.show()
    breakpoint()

    # ------------------------------------------------------------------
    # 3. matrix of 100 qualifying days (cell x days -- each day is a column)
    # ------------------------------------------------------------------
    n_days_total = block.sizes["time"]
    raw = block.values.reshape(n_days_total, BLOCK_SIZE * BLOCK_SIZE)
    dates = block.time.values

    day_mean = raw.mean(axis=1)
    qualifying = (day_mean >= MIN_RAIN) if MAX_RAIN is None else ((day_mean >= MIN_RAIN) & (day_mean < MAX_RAIN))
    raw_qual = raw[qualifying]
    dates_qual = dates[qualifying]

    if raw_qual.shape[0] < N_DAYS_MATRIX:
        raise RuntimeError(f"only {raw_qual.shape[0]} qualifying days, need {N_DAYS_MATRIX}")
    sel_idx = rng.choice(raw_qual.shape[0], size=N_DAYS_MATRIX, replace=False)
    sel_idx.sort()
    x_days = raw_qual[sel_idx]         # (N_DAYS_MATRIX, cell)
    dates_sel = dates_qual[sel_idx]

    x_norm, valid = pca_lib.normalize_days(x_days, method=NORMALIZATION)
    x_days = x_days[valid]
    x_norm = x_norm[valid]
    dates_sel = dates_sel[valid]

    matrix = x_norm.T   # (cell, days) -- each day is a column

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(matrix, aspect="auto", cmap="viridis")
    ax.set_xlabel(f"days (width = {matrix.shape[1]})")
    ax.set_ylabel(f"cell ({BLOCK_SIZE}x{BLOCK_SIZE} flattened, height = {matrix.shape[0]})")
    ax.set_title("matrix to decompose (cell x days)")
    fig.colorbar(im, ax=ax, fraction=0.046)
    plt.show()
    breakpoint()

    # ------------------------------------------------------------------
    # 4. SVD of that matrix: U, Sigma, V
    # ------------------------------------------------------------------
    U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
    V = Vt.T
    Sigma = np.diag(S)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
    axes[0].imshow(U, aspect="auto", cmap="RdBu")
    axes[0].set_title(f"U ({U.shape[0]}x{U.shape[1]})")

    axes[1].imshow(Sigma, aspect="auto", cmap="viridis")
    axes[1].set_title(f"Sigma ({Sigma.shape[0]}x{Sigma.shape[1]})")

    axes[2].imshow(V, aspect="auto", cmap="RdBu")
    axes[2].set_title(f"V ({V.shape[0]}x{V.shape[1]})")

    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
    plt.show()
    breakpoint()

    # ------------------------------------------------------------------
    # 5. top N_COMPONENTS singular vectors (U's columns), reshaped to images
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(1, N_COMPONENTS, figsize=(3 * N_COMPONENTS, 3), constrained_layout=True)
    svec_vmax = np.abs(U[:, :N_COMPONENTS]).max()
    for k in range(N_COMPONENTS):
        pattern_2d = U[:, k].reshape(BLOCK_SIZE, BLOCK_SIZE)
        im = axes[k].imshow(pattern_2d, cmap="RdBu", vmin=-svec_vmax, vmax=svec_vmax)
        axes[k].set_title(f"sv {k}\nsigma={S[k]:.2f}", fontsize=9)
        axes[k].set_xticks([])
        axes[k].set_yticks([])
    fig.colorbar(im, ax=axes.tolist(), fraction=0.02, pad=0.01)
    fig.suptitle(f"top {N_COMPONENTS} singular vectors -- lat~{block_lat:.2f}, lon~{block_lon:.2f}")
    plt.show()
    breakpoint()
