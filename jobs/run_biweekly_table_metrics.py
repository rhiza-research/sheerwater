#!/usr/bin/env python
"""Runs metrics and updates the caches."""
import itertools
import traceback

from sheerwater.utils import start_remote
from dashboard_data import biweekly_metric_table
from jobs import parse_args, run_in_parallel

(start_time, end_time, forecasts, metrics,
 variables, grids, regions, agg_days,
 time_groupings, parallelism, recompute,
 backend, remote_name, remote, remote_config) = parse_args()

if remote:
    start_remote(remote_config=remote_config, remote_name=remote_name)

combos = itertools.product(metrics, variables, grids, regions, time_groupings)

filepath_only = True
if backend is not None:
    filepath_only = False


def run_metrics_table(combo):
    """Run table metrics."""
    metric_name, variable, grid, region, time_grouping = combo

    try:
        biweekly_metric_table(start_time, end_time, variable, "era5", metric_name,
                              time_grouping=time_grouping, grid=grid, region=region,
                              force_overwrite=True, filepath_only=filepath_only,
                              recompute=recompute, storage_backend=backend)
    except KeyboardInterrupt as e:
        raise (e)
    except:  # noqa: E722
        print(f"Failed to run biweekly metric {grid} {variable} {metric_name} \
                {region} {time_grouping}: {traceback.format_exc()}")


if __name__ == "__main__":
    run_in_parallel(run_metrics_table, combos, parallelism)
