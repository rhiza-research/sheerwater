from sheerwater.metrics import coverage
from sheerwater.data.coverage_tables import coverage_table
from sheerwater.utils import start_remote

import matplotlib.pyplot as plt
import itertools


if __name__ == "__main__":
    # start_remote(remote_name="mohini_cache_coverage")
    # arguments for coverage runs
    start_time = "2012-01-01"
    end_time = "2025-01-01"

    agg_days = [5, 7, 10]
    variable = "precip"

    stations = ["ghcn_avg", "tahmo_avg"]
    time_groupings = ["month_of_year"]
    space_groupings = ["country", "subregion"]
    grids = ["global1_5", "global0_25"]

    mask = "lsm"
    region = "global"

    combos = itertools.product(stations, time_groupings, space_groupings, grids)
    ncombos = len(stations) * len(time_groupings) * len(space_groupings) * len(grids)

    count = 0
    combos = [combo for combo in combos]

    station_data, time_grouping, space_grouping, grid = combos[0]

    df = coverage_table(start_time=start_time, end_time=end_time, variable=variable, agg_days=agg_days, 
                        stations=station_data, time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask=mask, region=region)
    import pdb; pdb.set_trace()
