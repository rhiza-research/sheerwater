#!/usr/bin/env python
"""Runs metrics and updates the caches."""
import itertools
import traceback


from sheerwater.metrics import station_coverage
from sheerwater.utils import start_remote
from jobs import parse_args, run_in_parallel, prune_metrics

(start_time, end_time, forecasts, truth, metrics, variables, grids,
 space_groupings, agg_days, time_groupings, parallelism,
 recompute, backend, remote_name, remote, remote_config) = parse_args()

if remote:
    start_remote(remote_config=remote_config, remote_name=remote_name)

combos = itertools.product([None], truth,  variables, grids, agg_days, space_groupings, time_groupings, [None])
combos = prune_metrics(combos)


def run_coverage(combo):
    """Run grouped metrics."""
    print(combo)
    _, truth, variable, grid, agg_days, space_grouping, time_grouping, _ = combo

    try:
        return station_coverage(start_time, end_time, variable, agg_days=agg_days,
                      station_data=truth, time_grouping=time_grouping, grid=grid, space_grouping=space_grouping,
                      cache_mode='overwrite', filepath_only=True, recompute=recompute, retry_null_cache=True, backend_kwargs={'target_read_chunk_size_mb': 1000})
    except KeyboardInterrupt as e:
        raise (e)
    except NotImplementedError:
        print(f"Station coverage {truth} {agg_days} {grid} {variable} not implemented: {traceback.format_exc()}")
        return "Not Implemented"
    except:  # noqa:E722
        print(
            f"Failed to run coverage for {truth} {agg_days}"
            f"{grid} {variable}: {traceback.format_exc()}")
        return None


if __name__ == "__main__":
    run_in_parallel(run_coverage, combos, parallelism)
