"""Regrid station data convenience runner."""
from sheerwater.interfaces import get_data
from sheerwater.utils import start_remote

if __name__ == "__main__":
    start_remote(remote_config=["xxlarge_cluster", "large_node"], remote_name="cache_histograms")
    start_time = "2015-01-01"
    end_time = "2024-12-31"
    estimate = "imerg_late"
    truth = "stations"
    agg_days = 5
    grid = "global0_1"
    mask = "lsm"
    region = "global"
    space_grouping = "country"
    time_grouping = "month_of_year"

    variable = "precip"
    truth_ds = get_data(truth)(start_time, end_time, variable, agg_days=agg_days, grid=grid, mask=mask, region=region)
 

