#!/usr/bin/env python
"""Runs metrics and updates the caches."""
import itertools
import traceback


from sheerwater.metrics import metric
from sheerwater.utils import start_remote
from jobs import parse_args, run_in_parallel, prune_metrics

(start_time, end_time, forecasts, truth, metrics, variables, grids,
 regions, agg_days, time_groupings, parallelism,
 recompute, backend, remote_name, remote, remote_config) = parse_args()

if remote:
    start_remote(remote_config=remote_config, remote_name=remote_name)

combos = itertools.product(forecasts, truth,  variables, grids, agg_days, regions, time_groupings, metrics)
combos = prune_metrics(combos)


def run_grouped(combo):
    """Run grouped metrics."""
    print(combo)
    forecast, truth, variable, grid, agg_days, region, time_grouping, metric_name = combo

    try:
        return metric(start_time, end_time, variable, agg_days=agg_days, forecast=forecast,
                      truth=truth, metric_name=metric_name,
                      spatial=False, time_grouping=time_grouping, grid=grid, region=region,
                      force_overwrite=True, filepath_only=True, recompute=recompute, retry_null_cache=True)
    except KeyboardInterrupt as e:
        raise (e)
    except NotImplementedError:
        print(f"Metric {forecast} {agg_days} {grid} {variable} {metric_name} not implemented: {traceback.format_exc()}")
        return "Not Implemented"
    except:  # noqa:E722
        print(
            f"Failed to run global metric {forecast} {agg_days}"
            f"{grid} {variable} {metric_name}: {traceback.format_exc()}")
        return None


if __name__ == "__main__":
    run_in_parallel(run_grouped, combos, parallelism)
