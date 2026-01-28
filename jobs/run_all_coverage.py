#!/usr/bin/env python
"""Runs metrics and updates the caches."""
import itertools

from sheerwater.data.coverage_tables import coverage_table_stations_aggdays
from sheerwater.utils import start_remote
from jobs import parse_args, run_in_parallel

(start_time, end_time, forecasts, truth, metrics, variables, grids,
 regions, leads, time_groupings, space_groupings, parallelism,
 recompute, backend, remote_name, remote, remote_config) = parse_args()

def run_coverage(combo):
    """Run coverage."""
    grid, time_grouping, space_grouping = combo
    return coverage_table_stations_aggdays(start_time, end_time, variable='precip',
                                           time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, region="global")

if __name__ == "__main__":
    if remote:
        start_remote(remote_config=remote_config, remote_name=remote_name)

    combos = itertools.product(grids, time_groupings, space_groupings)

    run_in_parallel(run_coverage, combos, parallelism)