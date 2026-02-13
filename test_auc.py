# call the auc 
from sheerwater.metrics import auc_roc
from sheerwater.utils import start_remote
from sheerwater.interfaces import list_data

if __name__ == "__main__":
    start_remote(remote_name="get-auc")
    start_time = "2024-01-01"
    end_time = "2024-12-31"
    satellite = "imerg"
    station = "stations"
    station_threshold = "climatology_stations_2015_2025"
    agg_days = 5
    time_grouping = None
    space_grouping = "country"
    grid = 'global1_5'
    region = "africa"
    spatial = False


    auc_roc = auc_roc(start_time, end_time, satellite, station, station_threshold=station_threshold, agg_days=agg_days,
    time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask='lsm', region=region, spatial=spatial)
    import pdb; pdb.set_trace()