#!/usr/bin/env python
"""Runs metrics and updates the caches."""
import itertools
import traceback


from sheerwater_benchmarking.metrics import metric
from sheerwater_benchmarking.utils import start_remote
from jobs import parse_args, run_in_parallel, prune_metrics

(start_time, end_time, forecasts, truth, metrics, variables, grids,
 regions, agg_days, time_groupings, parallelism,
 recompute, backend, remote_name, remote, remote_config) = parse_args()

if remote:
    start_remote(remote_config=remote_config, remote_name=remote_name)

combos = itertools.product(metrics, variables, grids, regions, agg_days, forecasts, time_groupings, truth)
combos = prune_metrics(combos)


def run_grouped(combo):
    """Run grouped metrics."""
    print(combo)
    metric_name, variable, grid, region, agg_days, forecast, time_grouping, truth = combo

    try:
        return metric(start_time, end_time, variable, agg_days=agg_days, forecast=forecast,
                      truth=truth, metric_name=metric_name,
                      spatial=False, time_grouping=time_grouping, grid=grid, region=region,
                      force_overwrite=True, filepath_only=True, recompute=recompute,
                      retry_null_cache=True)
    except KeyboardInterrupt as e:
        raise (e)
    except NotImplementedError:
        print(f"Metric {forecast} {agg_days} {grid} {variable} {metric_name} not implemented: {traceback.format_exc()}")
        return "Not Implemented"
    except:  # noqa:E722
        print(
            f"Failed to run global metric {forecast} {agg_days} {grid} {variable} {metric_name}: {traceback.format_exc()}")
        return None


if __name__ == "__main__":
    run_in_parallel(run_grouped, combos, parallelism)
