"""Compute paired histogram and persist cached results for OYA runs."""

from sheerwater.utils import start_remote
from dashboard_data.station_paired_analysis import hist_df

if __name__ == "__main__":
    start_remote(remote_config=["xxlarge_cluster", "large_node"], remote_name="cache_histograms")
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    grid = "global0_1"
    estimate = "imerg_late"
    truth = "tahmo"
    agg_days = 5
    space_grouping = "country"
    time_grouping = "month_of_year"

    hdf = hist_df(
        start_time,
        end_time,
        estimate=estimate,
        truth=truth,
        agg_days=agg_days,
        grid=grid,
        space_grouping=space_grouping,
        time_grouping=time_grouping,
    )
    # hdf = paired_histogram(
    #     start_time, end_time, estimate=estimate, truth=truth, agg_days=agg_days,
    #     grid=grid, space_grouping=space_grouping, time_grouping=time_grouping
    # )
