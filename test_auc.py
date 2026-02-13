# call the auc 
from sheerwater.metrics import auc
from sheerwater.utils import start_remote
from sheerwater.interfaces import list_data

if __name__ == "__main__":
    start_remote(remote_name="get-auc", remote_config="xlarge_cluster")

    # time stuff
    start_time = "1990-01-01"
    end_time = "2020-12-31"
    time_grouping = "month_of_year"
    agg_days = 5

    # space stuff
    grid = 'global1_5'
    mask = 'lsm'
    region = "africa"
    spatial = True

    # satellite and station stuff
    satellite = "imerg"
    station = "stations"
    station_threshold = "climatology_stations_2015_2025"

    auc_roc = auc(start_time, end_time, satellite, station, station_threshold=station_threshold, agg_days=agg_days,
    time_grouping=time_grouping, grid=grid, mask=mask, region=region, spatial=spatial)
    import pdb; pdb.set_trace()