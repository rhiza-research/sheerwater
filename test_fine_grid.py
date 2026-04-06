# test paired histogram on fine grid

from sheerwater.utils import start_remote
from sheerwater.data import imerg
from sheerwater.data import tahmo
from sheerwater.utils.time_utils import groupby_time
from dashboard_data.station_paired_analysis import paired_histogram, hist_df
import matplotlib.pyplot as plt
from dashboard_data.station_paired_analysis import region_codes
from sheerwater.spatial_subdivisions import spacegrouping_category_codes

if __name__ == "__main__":
    start_remote(remote_config="xxxlarge_cluster", remote_name="sheerwater_histograms")  
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    grid = "global0_25"
    estimate = "imerg_late"
    truth = "stations"
    agg_days = 1
    space_grouping = "country"
    time_grouping = "month_of_year"

    hdf = hist_df(start_time, end_time, estimate=estimate, truth=truth, agg_days=agg_days, grid=grid, space_grouping=space_grouping, time_grouping=time_grouping, recompute=["hist_df"])
    #hdf = paired_histogram(start_time, end_time, estimate=estimate, truth=truth, agg_days=agg_days, grid=grid, space_grouping=space_grouping, time_grouping=time_grouping)
    import pdb; pdb.set_trace()