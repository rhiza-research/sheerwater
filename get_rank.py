from sheerwater.utils import start_remote
from sheerwater.interfaces import get_data
from sheerwater.utils.grouping_utils import groupby_time
from sheerwater.utils.data_utils import regrid

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def add_time_group(ds, time_grouping):
    if time_grouping is not None:
        if time_grouping == 'month_of_year':
            coords = [f'M{x:02d}' for x in ds.time.dt.month.values]
        elif time_grouping == 'year':
            coords = [f'Y{x:04d}' for x in ds.time.dt.year.values]
        elif time_grouping == 'quarter_of_year':
            coords = [f'Q{x:02d}' for x in ds.time.dt.quarter.values]
        elif time_grouping == 'day_of_year':
            coords = [f'D{x:03d}' for x in ds.time.dt.dayofyear.values]
        elif time_grouping == 'month':
            coords = [f'{pd.to_datetime(x).year:04d}-{pd.to_datetime(x).month:02d}-01' for x in ds.time.values]
        elif time_grouping == 'daily':
            coords = [pd.to_datetime(x).date() for x in ds.time.values]
            raise ValueError("Invalid time grouping")
    ds = ds.assign_coords(group=("time", coords))
    return ds

def get_rank(data_source):
    return


if __name__ == "__main__":
    start_remote(remote_name="mohini")

    region = "africa"


    # foreseen args
    source_grid = "global1_5"
    target_grid = "global0_25"
    time_grouping = "month_of_year"

    # years over which to get distribution for mapping
    start_year = 2015
    end_year = 2024
    start_time = f"{start_year}-01-01"
    end_time = f"{end_year}-12-31"

    # data source
    data_source = "imerg_final"
    agg_days = 1

    ds = get_data(data_source)(start_time, end_time, grid=source_grid, agg_days=agg_days)
    ds = add_time_group(ds, time_grouping)

    ranks = np.arange(0, 1, 0.1)

    ds = ds.chunk({"time": -1})
    qs = ds.groupby("group").quantile(q=ranks, dim="time", skipna=True)
    import pdb; pdb.set_trace()
    # regrid
    qs = regrid(qs, target_grid, method="linear")
    import pdb; pdb.set_trace()
    
