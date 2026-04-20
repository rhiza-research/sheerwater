"""Batch-run cached histogram data computations for multiple sources."""

from sheerwater.utils import start_remote
from dashboard_data.station_paired_analysis import hist_df

if __name__ == "__main__":
    start_remote(remote_config=["xxlarge_cluster", "large_node"], remote_name="sheerwater_histograms")
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    grids = ["global0_1"]
    estimates = ["oya"]
    truths = ["tahmo", "tahmo_avg"]
    agg_day_values = [1, 5, 10]
    region = "global"


    space_grouping = "country"
    time_grouping = "month_of_year"

    for grid in grids:
        for estimate in estimates:
            for truth in truths:
                for agg_days in agg_day_values:
                    print(
                        f"Running for {estimate} vs {truth} on {grid} with {agg_days} day aggregation"
                    )
                    hdf = hist_df(
                        start_time,
                        end_time,
                        estimate=estimate,
                        truth=truth,
                        agg_days=agg_days,
                        grid=grid,
                        space_grouping=space_grouping,
                        time_grouping=time_grouping,
                        region=region,
                        recompute=False,
                    )

    # hdf = hist_df(
    #     start_time, end_time, estimate=estimate, truth=truth, agg_days=agg_days,
    #     grid=grid, space_grouping=space_grouping, time_grouping=time_grouping, recompute=False
    # )
    # hdf = paired_histogram(
    #     start_time, end_time, estimate=estimate, truth=truth, agg_days=agg_days,
    #     grid=grid, space_grouping=space_grouping, time_grouping=time_grouping
    # )
