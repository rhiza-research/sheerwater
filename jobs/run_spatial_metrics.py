#!/usr/bin/env python
"""Runs metrics and updates the caches."""
import itertools
import traceback


from sheerwater.metrics import metric
from sheerwater.utils import start_remote
from jobs import parse_args, run_in_parallel, prune_metrics

(start_time, end_time, forecasts, truth, metrics, variables,
 grids, space_groupings, agg_days, time_groupings,
 parallelism, recompute, backend, remote_name, remote, remote_config) = parse_args()

if remote:
    start_remote(remote_config=remote_config, remote_name=remote_name)

combos = itertools.product(forecasts, truth, variables, grids, agg_days, [None], time_groupings, metrics)
combos = prune_metrics(combos)

filepath_only = True
if backend is not None:
    filepath_only = False


def run_metric(combo):
    """Run spatial metric."""
    print(combo)
    forecast, truth, variable, grid, agg_days, _, time_grouping, metric_name = combo

    try:
        return metric(start_time, end_time, variable, agg_days=agg_days, forecast=forecast,
               truth=truth, metric_name=metric_name, spatial=True,
               time_grouping=time_grouping, grid=grid, space_grouping=None,
               cache_mode='overwrite', filepath_only=filepath_only, recompute=recompute, storage_backend=backend, backend_kwargs={'target_read_chunk_size_mb': 1000})
    except KeyboardInterrupt as e:
        raise (e)
        return None
    except:  # noqa:E722
        print(f"Failed to run global metric {forecast} {agg_days} {grid} {variable} {metric}: {traceback.format_exc()}")
        return None


if __name__ == "__main__":
    run_in_parallel(run_metric, combos, parallelism)
