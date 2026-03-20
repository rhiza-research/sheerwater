import xarray as xr
import numpy as np
from sheerwater.utils import start_remote
from sheerwater.data import imerg
from sheerwater.data import tahmo
from sheerwater.utils.time_utils import groupby_time
from dashboard_data.station_paired_analysis import paired_histogram, hist_df
import matplotlib.pyplot as plt
from dashboard_data.station_paired_analysis import region_codes
from sheerwater.spatial_subdivisions import spacegrouping_category_codes

if __name__ == "__main__":
    start_remote()
    start_time = "2015-01-01"
    end_time = "2024-12-31"
    grid = "global1_5"
    agg_days = 10

    # test category codes
    #df = spacegrouping_category_codes(grid=grid, space_grouping="country", region="global")
    #import pdb; pdb.set_trace()

    #region_codes = region_codes(start_time, end_time, estimate="imerg_late", truth="stations", agg_days=agg_days, grid=grid, recompute=["region_codes"])
    hdf = hist_df(start_time, end_time, estimate="chirps_v3", truth="stations", agg_days=agg_days, grid=grid)
    import pdb; pdb.set_trace()
