from sheerwater.satellite_station_misses import precip_events_table
from sheerwater.utils import start_remote
import numpy as np
import itertools
from jobs import run_in_parallel

def run_event_combos(combo):
    start_time, end_time, truth, event_def, satellite, which_metric = combo
    days, precip_threshold = event_def[0], event_def[1]
    events = precip_events_table(start_time, end_time, days, precip_threshold, satellite, truth, which_metric, grid, region,
    backend='sql', cache_mode='overwrite')
    return events


if __name__ == "__main__":
    start_remote(remote_config=["xlarge_cluster", "large_node"], remote_name="event_tables")
    # period of interest
    start_time = "2020-01-01"
    end_time = "2025-12-31"
    # ground truth is tahmo
    truth = "tahmo_avg"
    # spatial resolution and region
    grid = 'global0_25'
    region = "ghana"

    # event definitions
    event_defs = [(3, 20), (5, 38), (11, 40), (10, 25)]

    # satellite and metrics
    satellites = ["imerg", "chirps"]
    which_metrics = ["false_negative", "true_positive"]

    arg_combos = itertools.product(event_defs, satellites, which_metrics)
    # append start_time, end_time, truth to combos
    arg_combos = [(start_time, end_time, truth, *combo) for combo in arg_combos]

    parallelism = 1
    run_in_parallel(run_event_combos, arg_combos, parallelism)