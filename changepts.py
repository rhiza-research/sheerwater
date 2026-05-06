import numpy as np
import matplotlib.pyplot as plt

# sheerwater import
from sheerwater.utils import start_remote
from sheerwater.climatology import climatology
from dashboard_data.station_paired_analysis import paired_histogram


if __name__ == "__main__":

    start_remote(remote_name = "mohini")

    def get_conditional_dists(mmodel, bins):
        conditional_dists = {}
        for bin_name, bin_range in bins.items():
            mask = (mmodel.truth >= bin_range[0]) & (mmodel.truth <= bin_range[1])
            prob = mmodel.where(mask).sum(dim="truth")
            prob = prob / prob.sum(dim="estimate")
            # rename precip to probability
            prob = prob.rename({"precip": "probability"})
            conditional_dists[bin_name] = prob
        return conditional_dists


    def get_thresholds(conditional_dists, lo="dry", hi="wet", alpha=0.05):
        # P_lo (null)
        p_lo = conditional_dists[lo]["probability"].compute().values.astype(float)
        x = conditional_dists[lo]["estimate"].values

        # sort by estimate (ascending)
        order = np.argsort(x)
        x_sorted = x[order]
        p_lo_sorted = p_lo[order]

        # survival function: P_lo(X >= t)
        survival_lo = np.flip(np.cumsum(np.flip(p_lo_sorted)))

        # find smallest t such that survival <= alpha
        valid = np.where(survival_lo <= alpha)[0]
        if len(valid) == 0:
            return None, None

        idx = valid[0]
        threshold = x_sorted[idx]

        # ---- compute error under Phi (hi distribution) ----
        p_hi = conditional_dists[hi]["probability"].compute().values.astype(float)
        x_hi = conditional_dists[hi]["estimate"].values

        # Type II error: P_hi(X < threshold)
        mask = x_hi < threshold
        type_ii_error = p_hi[mask].sum()

        return threshold, type_ii_error


    # Step 1 - get measurement model
    mm = {}
    countries = ["ghana", "kenya", "rwanda", "nigeria"]
    agg_days = 1
    bins = np.arange(0, 20, 0.1)
    for country in countries:
        mm[country] = paired_histogram("2010-01-01", "2025-01-01", 
        "imerg_final", "tahmo_avg", agg_days,
        grid="global0_25", region=country, recompute=True, bins=bins, zero_bin=True)

    # Step 2 - determine station bins
    bins = {"dry": [0, 1], "wet": [5, 20], "vwet": [30, 50]}
    conditional_dists = {}
    for country in countries:
        conditional_dists[country] = get_conditional_dists(mm[country], bins)

    # Step 3 - determine neyman-pearson thresholds on satellite for station categories
    thresholds = {}
    t2errors = {}
    for country in countries:
        thresh, error = get_thresholds(conditional_dists[country], lo="dry", hi="wet", alpha=0.1)
        thresholds[country] = thresh
        t2errors[country] = error
    print(thresholds)
    print(t2errors)
    import pdb; pdb.set_trace()