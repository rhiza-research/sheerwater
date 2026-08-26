import matplotlib.pyplot as plt

from sheerwater.utils import start_remote
import pca_lib


# --- config ---
REGION = "africa"
RESOLUTION = 0.1        # degrees; one of pca_lib.RESOLUTION_TO_GRID
BLOCK_SIZE = 15          # low-res cell = BLOCK_SIZE x BLOCK_SIZE hi-res pixels (square)
START_TIME = "2016-01-01"
END_TIME = "2024-12-31"
SEASON = None             # "DJF", "MAM", "JJA", "SON", or None for no filtering

VARIANCE_THRESHOLD = 0.95        # fraction of squared-singular-value energy required
MIN_RAIN, MAX_RAIN = 1.0, None   # only decompose days with mean cell rainfall in [MIN_RAIN, MAX_RAIN)

N_PATTERNS = 3            # cell 2: plot the top N singular-vector patterns, one panel each

TARGET_LAT = -2.0         # cell 3: focused single-block check
TARGET_LON = 23.0
N_COMPONENTS_MANUAL = 5

N_NMF_RUNS = 5             # cell 4: nmf consistency across restarts


if __name__ == "__main__":
    client = start_remote(remote_name="downscale_pca", remote_config="large_cluster")

    # pca_lib is a plain local module (not part of the installed sheerwater
    # package), so workers can't `import pca_lib` on their own -- upload it
    # explicitly so functions referencing it (e.g. inside apply_ufunc) can
    # be deserialized on the workers.
    client.upload_file(pca_lib.__file__)

    imerg_hi = pca_lib.load_hi_res(REGION, RESOLUTION, START_TIME, END_TIME)
    imerg_hi = pca_lib.filter_season(imerg_hi, SEASON)
    blocked = pca_lib.make_blocked(imerg_hi, BLOCK_SIZE)
    blocked_stacked = pca_lib.stack_and_chunk(blocked)

    # --- cell 1: number of significant singular values across the region ---
    dimensionality = pca_lib.compute_dimensionality(
        blocked_stacked, imerg_hi, BLOCK_SIZE,
        threshold=VARIANCE_THRESHOLD, lo=MIN_RAIN, hi=MAX_RAIN,
    )
    pca_lib.plot_n_significant(dimensionality, binwidth=5)
    plt.show()
    breakpoint()

    # --- cell 1b: number of days meeting rain-filter criteria, per cell ---
    pca_lib.plot_n_days(dimensionality)
    plt.show()
    breakpoint()

    # --- cell 1c: n_significant vs n_days, per cell ---
    pca_lib.plot_n_days_vs_significant(dimensionality)
    plt.show()
    breakpoint()

    # --- cell 2: leading spatial patterns across the region ---
    fig, axes = plt.subplots(1, N_PATTERNS, figsize=(6 * N_PATTERNS, 5), constrained_layout=True)
    if N_PATTERNS == 1:
        axes = [axes]
    for sv in range(N_PATTERNS):
        pattern_full = pca_lib.compute_pattern_full(
            blocked_stacked, imerg_hi, BLOCK_SIZE, sv=sv, lo=MIN_RAIN, hi=MAX_RAIN,
        )
        pattern_full.plot(ax=axes[sv], x="lon")
        axes[sv].set_title(f"sv {sv}")
    plt.show()
    breakpoint()

    # --- cell 3: focused single-block check ---
    i, j, block = pca_lib.find_nearest_valid_block(blocked, TARGET_LAT, TARGET_LON)
    block_lat, block_lon = float(block.lat.mean()), float(block.lon.mean())
    print(f"using block lat_lo={i}, lon_lo={j}, lat~{block_lat:.2f}, lon~{block_lon:.2f} "
          f"(target lat={TARGET_LAT}, lon={TARGET_LON})")

    n_days = block.sizes["time"]
    x = block.values.reshape(n_days, BLOCK_SIZE * BLOCK_SIZE)
    x_norm = pca_lib.filter_and_normalize_days(x, lo=MIN_RAIN, hi=MAX_RAIN)

    pca_lib.plot_decomp_comparison(x_norm, BLOCK_SIZE, N_COMPONENTS_MANUAL, block_lat, block_lon)
    plt.show()
    breakpoint()

    # --- cell 4: nmf consistency across restarts ---
    nmf_results = pca_lib.run_nmf_repeats(x_norm, N_COMPONENTS_MANUAL, N_NMF_RUNS, init="random")
    pca_lib.plot_nmf_repeats(nmf_results, BLOCK_SIZE, block_lat, block_lon)
    plt.show()
    breakpoint()
