import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from sheerwater.utils import start_remote
import pca_lib


REGIONS = ["africa", "europe", "south_america", "asia"]
REGION_COLORS = {
    "africa": "tab:orange",
    "europe": "tab:blue",
    "south_america": "tab:green",
    "asia": "tab:red",
}

RESOLUTION = 0.1        # degrees; one of pca_lib.RESOLUTION_TO_GRID
BLOCK_SIZE = 15          # low-res cell = BLOCK_SIZE x BLOCK_SIZE hi-res pixels (square)
START_TIME = "2016-01-01"
END_TIME = "2024-12-31"
SEASON = None            # "DJF", "MAM", "JJA", "SON", or None for no filtering

VARIANCE_THRESHOLD = 0.95        # fraction of squared-singular-value energy required
MIN_RAIN, MAX_RAIN = 1.0, None   # only decompose days with mean cell rainfall in [MIN_RAIN, MAX_RAIN)

POINT_SIZE = 40
POINT_ALPHA = 0.15

OUTPUT_CSV = "region_scatter.csv"

# "highly compressible" box: cells with at least this many qualifying days,
# whose rainfall structure is explained by no more than this many singular values
BOX_MIN_N_DAYS = 500
BOX_MAX_N_SIGNIFICANT = 40


if __name__ == "__main__":
    client = start_remote(remote_name="downscale_pca", remote_config="large_cluster")

    # pca_lib is a plain local module (not part of the installed sheerwater
    # package), so workers can't `import pca_lib` on their own -- upload it
    # explicitly so functions referencing it (e.g. inside apply_ufunc) can
    # be deserialized on the workers.
    client.upload_file(pca_lib.__file__)

    region_dfs = []

    for region in REGIONS:
        print(f"computing dimensionality for {region}...")
        imerg_hi = pca_lib.load_hi_res(region, RESOLUTION, START_TIME, END_TIME)
        imerg_hi = pca_lib.filter_season(imerg_hi, SEASON)
        blocked = pca_lib.make_blocked(imerg_hi, BLOCK_SIZE)
        blocked_stacked = pca_lib.stack_and_chunk(blocked)

        dimensionality = pca_lib.compute_dimensionality(
            blocked_stacked, imerg_hi, BLOCK_SIZE,
            threshold=VARIANCE_THRESHOLD, lo=MIN_RAIN, hi=MAX_RAIN,
        )

        df = dimensionality.to_dataframe().reset_index()[["lat", "lon", "n_significant", "n_days"]]
        df["region"] = region
        region_dfs.append(df)

    all_regions = pd.concat(region_dfs, ignore_index=True)

    # shared x/y lims across all regions' subplots, so panels are directly comparable
    xlim = (0, all_regions["n_days"].max() * 1.05)
    ylim = (0, all_regions["n_significant"].max() * 1.05)

    fig, axes = plt.subplots(1, len(REGIONS), figsize=(5 * len(REGIONS), 5), sharex=True, sharey=True)
    for ax, region in zip(axes, REGIONS):
        df = all_regions[all_regions["region"] == region]
        ax.scatter(
            df["n_days"], df["n_significant"],
            s=POINT_SIZE, alpha=POINT_ALPHA,
            color=REGION_COLORS.get(region),
        )
        valid = df.dropna(subset=["n_significant"])
        in_box = (valid["n_days"] >= BOX_MIN_N_DAYS) & (valid["n_significant"] <= BOX_MAX_N_SIGNIFICANT)
        pct_in_box = 100 * in_box.mean() if len(valid) else 0.0

        ax.add_patch(Rectangle(
            (BOX_MIN_N_DAYS, ylim[0]),
            xlim[1] - BOX_MIN_N_DAYS,
            BOX_MAX_N_SIGNIFICANT - ylim[0],
            fill=False, edgecolor="black", linestyle="--", linewidth=1.5,
        ))
        ax.text(
            BOX_MIN_N_DAYS, BOX_MAX_N_SIGNIFICANT, f"{pct_in_box:.1f}%",
            ha="left", va="bottom", fontsize=9,
        )

        ax.set_title(region)
        ax.set_xlabel("n_days")
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    axes[0].set_ylabel("n_significant")
    plt.tight_layout()
    plt.show()
    all_regions.to_csv(OUTPUT_CSV, index=False)
    print(f"wrote {OUTPUT_CSV}")

    breakpoint()

    fig, ax = plt.subplots(figsize=(8, 6))
    for region in REGIONS:
        df = all_regions[all_regions["region"] == region]
        ratio = df["n_days"] / df["n_significant"]
        ratio = ratio[np.isfinite(ratio)]
        ax.hist(ratio, bins=30, alpha=POINT_ALPHA + 0.2, color=REGION_COLORS.get(region), label=region)

    ax.set_xlabel("n_days / n_significant")
    ax.set_ylabel("count")
    ax.legend()
    plt.show()

    breakpoint()
