# get era5 climatology for ghana
from sheerwater.utils import start_remote
from sheerwater.climatology import climatology_stations_2015_2025, climatology_tahmo_avg_2015_2025


if __name__ == "__main__":
    start_remote()
    start_time = "2024-01-01"
    end_time = "2024-12-31"
    ds = climatology_tahmo_avg_2015_2025(start_time, end_time, "precip", agg_days=7, grid="global1_5")
    import pdb; pdb.set_trace()