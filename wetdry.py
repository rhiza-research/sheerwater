from sheerwater.utils import start_remote
from dashboard_data.station_paired_analysis import paired_histogram
import matplotlib.pyplot as plt
import numpy as np

def joint_confidence(hist, xthreshold = 2, x_dim = "truth", y_dim = "estimate", mode="above"):
    """
    Given a threshold for x_dim, calculate the confidence for every possible threshold on y_dim
    that we are above (below) both thresholds.
    """

    hist_y = hist.sum(x_dim)
    y_area = hist_y.cumsum(dim=y_dim).shift({y_dim: 1}, fill_value=0)
    y_area = y_area.assign_coords({y_dim: hist[y_dim]})
    if mode == "above":
        all_area = hist_y.sum(dim=y_dim)
        y_area = all_area - y_area

    if mode == "below":
        x_area = hist.where(hist[x_dim] < xthreshold).sum(dim=x_dim)
    else: # mode == "above"
        x_area = hist.where(hist[x_dim] > xthreshold).sum(dim=x_dim)

    x_area_cumsum = x_area.cumsum(dim=y_dim).shift({y_dim: 1}, fill_value=0)
    x_area_cumsum = x_area_cumsum.assign_coords({y_dim: hist[y_dim]})
    x_area_total = x_area.sum(dim=y_dim)
    if mode == "above":
        x_area = x_area_total - x_area_cumsum
    
    confidence = x_area / y_area
    confidence = confidence.rename({"precip": "confidence"})

    return confidence


if __name__ == "__main__":
    start_remote(remote_name = "thresholds")

    # times
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    # data sources
    estimate = "imerg_final"
    truth = "stations"

    # event defintion
    agg_days = 5
    dry_threshold = 1

    # spatial specs
    grid = "global0_25"
    space_grouping = "country"
    region = "global"

    # get joint histogram
    bins = np.arange(0, 25, 0.5)
    hist = paired_histogram(start_time, end_time, estimate, truth, agg_days, grid=grid,
                            space_grouping=space_grouping, time_grouping=None, region=region,
                            bins=bins, recompute=True)

    # calculate confidence
    import pdb; pdb.set_trace()
    conf = joint_confidence(hist, xthreshold=dry_threshold, x_dim="truth", y_dim="estimate", mode="above")

    confidence_threshold = 0.8
    mask = conf.confidence > confidence_threshold
    first_estimate = conf.estimate.where(mask).min(dim="estimate")

    import pdb; pdb.set_trace()
    df = hist.to_dataframe()
    # split multi-index into separate columns
    df = df.reset_index()
    # drop lat and lon columns
    df = df.drop(columns=["lat", "lon"])
    # make estimate into columns and truth into rows
    df = df.pivot(index="truth", columns="estimate", values="precip")
    import pdb; pdb.set_trace()

    # get confidence values
    confidence = joint_confidence(hist, xthreshold=2, x_dim="truth", y_dim="estimate", mode="above")
    import pdb; pdb.set_trace()
    # get satellite threshold for selected confidence
    confidence_threshold = 0.9
    mask = confidence.confidence > confidence_threshold
    estimate_threshold = mask.argmax(dim="estimate")

    import pdb; pdb.set_trace()
    
    regions = ["kenya", "ghana", "germany", "france", "australia"]
    colors = ["red", "green", "blue", "purple", "orange"]
    # plot confidence path for each region
    fig, ax = plt.subplots(figsize=(10, 10))
    for i, region in enumerate(regions):
        confidence.sel(region=region).confidence.plot(ax=ax, label=region, color=colors[i])
        # indicate the estimate threshold
        ax.axvline(x=estimate_threshold.sel(region=region), color=colors[i], linestyle="--")
    ax.legend()
    ax.set_title("Wet Confidence")
    ax.set_xlabel("Time")
    ax.set_ylabel("Confidence")
    import pdb; pdb.set_trace()
