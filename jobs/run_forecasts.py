#!/usr/bin/env python
"""Runs metrics and updates the caches."""
import itertools
import traceback

from sheerwater.utils import start_remote, get_datasource_fn
from jobs import parse_args, run_in_parallel

(start_time, end_time, forecasts, truth, metrics, variables, grids,
 regions, agg_days, time_groupings, parallelism,
 recompute, backend, remote_name, remote, remote_config) = parse_args()

if remote:
    start_remote(remote_config=remote_config, remote_name=remote_name)

combos = itertools.product(forecasts, truth, variables, grids, agg_days)
#combos = prune_metrics(combos)

def run_grouped(combo):
    """Run grouped metrics."""
    print(combo)
    forecast, truth, variable, grid, agg_days = combo

    try:
        fn = get_datasource_fn(forecast)
        fn(start_time, end_time, variable=variable, agg_days=agg_days, grid=grid,
                  recompute=recompute, force_overwrite=True)
        fn = get_datasource_fn(truth)
        return fn(start_time, end_time, variable=variable, agg_days=agg_days, grid=grid,
                  recompute=recompute, force_overwrite=True)
    except KeyboardInterrupt as e:
        raise (e)
    except NotImplementedError:
        print(f"Data source {forecast} {agg_days} {grid} {variable} not implemented: {traceback.format_exc()}")
        return "Not Implemented"
    except:  # noqa:E722
        print(
            f"Failed to run {forecast} {agg_days}"
            f"{grid} {variable}: {traceback.format_exc()}")
        return None


if __name__ == "__main__":
    run_in_parallel(run_grouped, combos, parallelism)
