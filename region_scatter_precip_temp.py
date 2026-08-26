import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sheerwater.utils import start_remote
import pca_lib


REGIONS = ["africa", "europe", "south_america", "asia"]
REGION_COLORS = {
    "africa": "tab:orange",
    "europe": "tab:blue",
    "south_america": "tab:green",
    "asia": "tab:red",
}

START_TIME = "2016-01-01"
END_TIME = "2024-12-31"
SEASON = None             # "DJF", "MAM", "JJA", "SON", or None for no filtering
VARIANCE_THRESHOLD = 0.95  # fraction of squared-singular-value energy required

POINT_SIZE = 40
POINT_ALPHA = 0.15


def compute_region_dimensionality(region, resolution, block_size, dataset, variable, lo, hi, normalization):
    hi_res = pca_lib.load_hi_res(region, resolution, START_TIME, END_TIME, dataset=dataset, variable=variable)
    hi_res = pca_lib.filter_season(hi_res, SEASON)
    data_var = pca_lib.data_variable(dataset, variable)
    blocked = pca_lib.make_blocked(hi_res, block_size, variable=data_var)
    blocked_stacked = pca_lib.stack_and_chunk(blocked)
    return pca_lib.compute_dimensionality(
        blocked_stacked, hi_res, block_size,
        threshold=VARIANCE_THRESHOLD, lo=lo, hi=hi, normalization=normalization,
    )


if __name__ == "__main__":
    client = start_remote(remote_name="downscale_pca", remote_config="large_cluster")

    # pca_lib is a plain local module (not part of the installed sheerwater
    # package), so workers can't `import pca_lib` on their own -- upload it
    # explicitly so functions referencing it (e.g. inside apply_ufunc) can
    # be deserialized on the workers.
    client.upload_file(pca_lib.__file__)

    # imerg precip
    PRECIP_RESOLUTION = 0.25
    PRECIP_BLOCK_SIZE = 6
    MIN_RAIN, MAX_RAIN = 1.0, None   # only include days with mean cell rainfall in [MIN_RAIN, MAX_RAIN)

    # era5 tmp2m
    TEMP_RESOLUTION = 0.25
    TEMP_BLOCK_SIZE = 6

    precip_data = {}
    for region in REGIONS:
        print(f"computing precip dimensionality for {region}...")
        precip_data[region] = compute_region_dimensionality(
            region, PRECIP_RESOLUTION, PRECIP_BLOCK_SIZE, "imerg", None,
            lo=MIN_RAIN, hi=MAX_RAIN, normalization="sum",
        )

    temp_data = {}
    for region in REGIONS:
        print(f"computing tmp2m dimensionality for {region}...")
        temp_data[region] = compute_region_dimensionality(
            region, TEMP_RESOLUTION, TEMP_BLOCK_SIZE, "era5", "tmp2m",
            lo=None, hi=None, normalization="zscore",
        )

    # shared x/y lims across both subplots (and both datasets), so panels are directly comparable
    all_n_days = [d.n_days.values.flatten() for d in list(precip_data.values()) + list(temp_data.values())]
    all_n_significant = [d.n_significant.values.flatten() for d in list(precip_data.values()) + list(temp_data.values())]
    xlim = (0, np.nanmax(np.concatenate(all_n_days)) * 1.05)
    ylim = (0, np.nanmax(np.concatenate(all_n_significant)) * 1.05)

    fig, (ax_precip, ax_temp) = plt.subplots(2, 1, figsize=(8, 10))

    for region in REGIONS:
        dimensionality = precip_data[region]
        ax_precip.scatter(
            dimensionality.n_days.values.flatten(),
            dimensionality.n_significant.values.flatten(),
            s=POINT_SIZE, alpha=POINT_ALPHA,
            color=REGION_COLORS.get(region),
            label=region,
        )

    ax_precip.set_xlabel("n_days")
    ax_precip.set_ylabel("n_significant")
    ax_precip.set_title("imerg precip")
    ax_precip.set_xlim(xlim)
    ax_precip.set_ylim(ylim)
    ax_precip.legend()

    for region in REGIONS:
        dimensionality = temp_data[region]
        ax_temp.scatter(
            dimensionality.n_days.values.flatten(),
            dimensionality.n_significant.values.flatten(),
            s=POINT_SIZE, alpha=POINT_ALPHA,
            color=REGION_COLORS.get(region),
            label=region,
        )

    ax_temp.set_xlabel("n_days")
    ax_temp.set_ylabel("n_significant")
    ax_temp.set_title("era5 tmp2m")
    ax_temp.set_xlim(xlim)
    ax_temp.set_ylim(ylim)
    ax_temp.legend()

    plt.tight_layout()
    plt.show()

    breakpoint()
