from dashboard_data.station_paired_analysis import paired_histogram
from sheerwater.utils import start_remote
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # get the joint estimate-truth histogram
    start_remote(remote_name = "fishing")
    start_time = "2015-01-01"
    end_time = "2024-12-31"
    estimate = "oya"
    truth = "tahmo_avg"

    agg_days = 5
    grid = "global0_25"
    space_grouping = "country"
    time_grouping = "month_of_year"
    region = "global"

    hist = paired_histogram(start_time, end_time, 
               estimate, truth, agg_days, 
               grid=grid, space_grouping=space_grouping, time_grouping=time_grouping, region=region)
    
    import pdb; pdb.set_trace()
    # 1. sum over group to get total counts by region
    # now dims: (estimate, truth, region)
    hist = hist.sum(dim="group")

    # 2. normalize along estimate to get p(estimate|truth)
    nevents = hist.sum(dim="estimate")
    # drop truth dimensions where nevents is < threshold
    threshold = 100
    nevents = nevents.where(nevents >= threshold)
    hist = hist.where(nevents >= threshold)
    pcond = hist / nevents.expand_dims({"estimate": hist.estimate})

    # 3. add tiny epsilon to avoid log(0)
    eps = 1e-12
    p_smooth = pcond + eps
    # normalize once to make probabilities sum to 1
    p_smooth = p_smooth / p_smooth.sum(dim="estimate")

    # 4. compute log probabilities
    log_p = xr.ufuncs.log(p_smooth)

    # 5. finite difference along truth dimension
    dx = hist.truth.diff(dim="truth")  # array of delta x (length = truth-1)
    dlogp_dx = log_p.diff(dim="truth") / dx  # shape smaller by 1 along truth

    # 6. align probabilities for weighting (midpoint of truth edges)
    p_mid = 0.5 * (p_smooth.isel(truth=slice(0, -1)) + p_smooth.isel(truth=slice(1, None)))

    # 7. empirical Fisher information: sum over estimate dimension
    fisher = (dlogp_dx ** 2 * p_mid).sum(dim="estimate")

    weight = nevents / nevents.mean(dim="truth")
    fisher_weighted = fisher * weight

    # cramer-rao
    rez = 1 / xr.ufuncs.sqrt(fisher_weighted)

    # plot
    regions = ["kenya", "ghana"]
    fig, ax = plt.subplots(figsize=(10, 10))
    for i, region in enumerate(regions):
        rez.sel(region=region).precip.plot(ax=ax, label=region)
    ax.legend()
    ax.set_title("Best Separation for Regions")
    ax.set_xlabel("Truth")
    ax.set_ylabel("Best Separation")
    plt.show()
    import pdb; pdb.set_trace()
    plt.savefig("best_separation.png")
    
    
