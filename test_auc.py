# call the auc 
from sheerwater.metrics import auc_roc
from sheerwater.utils import start_remote

if __name__ == "__main__":
    start_remote()
    start_time = "2024-01-01"
    end_time = "2024-12-31"
    satellite = "imerg"
    station = "ghcn_avg"
    station_threshold = 20
    agg_days = 5
    time_grouping = None
    space_grouping = "country"
    grid = 'global1_5'

    auc_roc = auc_roc(start_time, end_time, satellite, station, station_threshold=station_threshold, agg_days=agg_days,
    time_grouping=time_grouping, space_grouping=space_grouping, grid='global1_5', mask='lsm', region='global',spatial=True)
    import pdb; pdb.set_trace()