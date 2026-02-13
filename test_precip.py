from sheerwater.satellite_station_misses import pairwise_precip
from sheerwater.utils import start_remote

if __name__ == "__main__":
    start_remote()

    # time stuff
    start_time = "2012-01-01"
    end_time = "2025-12-31"
    agg_days = 1

    # space stuff
    grid = 'global1_5'
    mask = 'lsm'
    region = "africa"

    ds = pairwise_precip(start_time, end_time, "tahmo_avg", "imerg", agg_days=agg_days, 
    climatology="climatology_tahmo_avg_2015_2025", grid=grid, mask=mask, region=region)
    
    import pdb; pdb.set_trace()