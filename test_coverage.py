from sheerwater.metrics import station_coverage
from sheerwater.utils import start_remote

if __name__ == "__main__":
    start_remote()
    start_time = "2023-01-01"
    end_time = "2023-12-31"
    variable = "precip"
    agg_days = 5
    station_data = "tahmo_avg"
    time_grouping = "year"
    space_grouping = "country"
    grid = "global1_5"
    mask = "lsm"
    region = "africa"

    ds = station_coverage(start_time=start_time, end_time=end_time, variable=variable, agg_days=agg_days, station_data=station_data,
                          time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask=mask, region=region)

    import pdb; pdb.set_trace()