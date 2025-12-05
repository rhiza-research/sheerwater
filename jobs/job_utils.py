"""Utilities for running jobs."""
import argparse
import dask
import itertools
import multiprocessing
import tqdm

from sheerwater.metrics_library import metric_factory

skip = 0
station_eval = False


def parse_args():
    """Parses arguments for jobs."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-time", default="1998-01-01", type=str, help="Start time for evaluation.")
    parser.add_argument("--end-time", default="2024-12-31", type=str, help="End time for evaluation.")
    parser.add_argument("--forecast", type=str, nargs='*', help="Forecasts to evaluate.")
    parser.add_argument("--truth", type=str, nargs='*', help="Truth data to evaluate against.")
    parser.add_argument("--variable", type=str, nargs='*', help="Variables to evaluate.")
    parser.add_argument("--metric", type=str, nargs='*', help="Metrics to evaluate.")
    parser.add_argument("--grid", type=str, nargs='*', help="Grids to evaluate.")
    parser.add_argument("--region", type=str, nargs='*', help="Regions to evaluate.")
    parser.add_argument("--agg_days", type=int, nargs='*', help="Aggregation days to evaluate.")
    parser.add_argument("--time-grouping", type=str, nargs='*', help="Time groupings to evaluate.")
    parser.add_argument("--backend", type=str, default=None, help="Backend to use for evaluation.")
    parser.add_argument("--parallelism", type=int, default=1, help="Number of runs to run in parallel.")
    parser.add_argument("--recompute", action=argparse.BooleanOptionalAction,
                        default=False, help="Whether to recompute existing metrics.")
    parser.add_argument("--remote", action=argparse.BooleanOptionalAction,
                        default=True, help="Whether to run on remote cluster.")
    parser.add_argument("--station-evaluation", action=argparse.BooleanOptionalAction,
                        default=False, help="Whether to run station evaluation.")
    parser.add_argument("--seasonal", action=argparse.BooleanOptionalAction,
                        default=False, help="Whether to run seasonal evaluation.")
    parser.add_argument("--remote-name", type=str, default=None, help="Name of remote cluster to use.")
    parser.add_argument("--remote-config", type=str, nargs='*', help="Remote configuration to use.")
    parser.add_argument("--skip", type=int, default=0, help="Start runs at this index by skipping the first N runs.")
    args = parser.parse_args()

    global skip
    skip = args.skip

    global station_eval
    if args.station_evaluation:
        station_eval = True

    if args.station_evaluation:
        forecasts = ["chirps_v3", "imerg_late", "imerg_final", "era5", "chirp_v3"]
    elif args.seasonal:
        forecasts = ["salient", "climatology_2015"]
    else:
        forecasts = ["salient", "ecmwf_ifs_er", "ecmwf_ifs_er_debiased",
                     "climatology_2015", "climatology_trend_2015", "climatology_rolling", "fuxi",
                     "gencast", "graphcast"]

    if args.forecast:
        forecasts = args.forecast

    if args.station_evaluation:
        truth = ["tahmo", "tahmo_avg", "ghcn", "ghcn_avg"]
    else:
        truth = ["era5"]

    if args.truth:
        truth = args.truth

    if args.station_evaluation:
        metrics = ["mae", "rmse", "bias", "acc", "smape", "pod-1", "pod-5", "pod-10", "pearson",
                   "far-1", "far-5", "far-10", "ets-1", "ets-5", "ets-10", "heidke-1-5-10-20"]
    else:
        metrics = ["mae", "crps", "acc", "rmse", "bias",  "smape", "seeps", "pod-1", "pod-5",
                   "pod-10", "far-1", "far-5", "far-10", "ets-1", "ets-5", "ets-10", "heidke-1-5-10-20"]

    if args.metric:
        if args.metric == ['contingency']:
            metrics = ["pod-1", "pod-5", "pod-10", "far-1", "far-5",
                       "far-10", "ets-1", "ets-5", "ets-10", "heidke-1-5-10-20"]
        elif args.metric == ['coupled']:
            metrics = ["acc", "pod-1", "pod-5", "pod-10", "far-1", "far-5",
                       "far-10", "ets-1", "ets-5", "ets-10", "heidke-1-5-10-20"]
        elif args.metric == ['wet-dry']:
            metrics = ["pod-3.6", "pod-7.6", "pod-6.6", "far-3.6", "far-7.6", "far-6.6",
                       "ets-3.6", "ets-7.6", "ets-6.6", "csi-3.6", "csi-7.6", "csi-6.6",
                       "frequencybias-3.6", "frequencybias-7.6", "frequencybias-6.6",
                       "far-1.5",
                       "heidke-1.5-7.6"]
        elif args.metric == ['wet-dry-pod']:
            metrics = ["pod-3.6", "pod-7.6", "pod-6.6"]
        elif args.metric == ['wet-dry-far']:
            metrics = ["far-3.6", "far-7.6", "far-6.6"]
        elif args.metric == ['wet-dry-ets']:
            metrics = ["ets-3.6", "ets-7.6", "ets-6.6"]
        elif args.metric == ['wet-dry-csi']:
            metrics = ["csi-3.6", "csi-7.6", "csi-6.6"]
        elif args.metric == ['wet-dry-freq']:
            metrics = ["frequencybias-3.6", "frequencybias-7.6", "frequencybias-6.6"]
        elif args.metric == ['wet-dry-rest']:
            metrics = ["far-1.5", "heidke-1.5-7.6"]
        else:
            metrics = args.metric

    variables = ["precip", "tmp2m"]
    if args.variable:
        variables = args.variable

    if args.station_evaluation:
        grids = ["global1_5", "imerg", "global0_1", "global0_25"]
    else:
        grids = ["global0_25", "global1_5"]
    if args.grid:
        grids = args.grid

    regions = ["continent", "subregion", "global", "country"]
    if args.region:
        regions = args.region

    if args.station_evaluation:
        agg_days = [1, 5, 7, 10, 14, 30]
    elif args.seasonal:
        agg_days = [30]
    else:
        agg_days = [7]

    if args.agg_days:
        agg_days = args.agg_days

    time_groupings = [None, "month_of_year"]
    if args.time_grouping:
        time_groupings = args.time_grouping
        time_groupings = [x if x != 'None' else None for x in time_groupings]

    remote_config = ["large_cluster"]
    if args.remote_config:
        remote_config = args.remote_config

    return (args.start_time, args.end_time, forecasts, truth, metrics, variables, grids,
            regions, agg_days, time_groupings, args.parallelism,
            args.recompute, args.backend, args.remote_name, args.remote, remote_config)


def prune_metrics(combos, global_run=False):  # noqa: ARG001
    """Prunes a list of metrics combinations.

    Can skip all coupled metrics for global runs.
    """
    pruned_combos = []
    for combo in combos:
        forecast, truth, variable, grid, agg_days, region, time_grouping, metric_name = combo

        metric_obj = metric_factory(metric_name, start_time=None, end_time=None, variable=variable,
                                    agg_days=agg_days, forecast=forecast, truth=truth, time_grouping=time_grouping,
                                    spatial=False, grid=grid, mask=None, region=region)

        if metric_obj.valid_variables and variable not in metric_obj.valid_variables:
            continue

        if metric_name == 'seeps' and grid == 'global0_25':
            continue

        global station_eval
        if '-' in metric_name and station_eval and agg_days:
            thresh = float(metric_name.split('-')[1])

            # FAR dry spell
            if thresh == 1.5:
                if agg_days not in [7, 10]:
                    continue
            elif thresh == 6.6:
                if agg_days != 3:
                    continue
            elif thresh == 7.6:
                if agg_days != 5:
                    continue
            elif thresh == 3.6:
                if agg_days != 11:
                    continue

        pruned_combos.append(combo)

    return pruned_combos


def run_in_parallel(func, iterable, parallelism, local_multiproc=False):
    """Run a function in parallel with dask delayed.

    Args:
        func(callable): A function to call. Must take one of iterable as an argument.
        iterable (iterable): Any iterable object to pass to func.
        parallelism (int): Number of func(iterables) to run in parallel at a time.
        local_multiproc (bool): If true run using multiprocessing pool instead of dask delayed batches.
    """
    iterable, copy = itertools.tee(iterable)
    length = len(list(copy))
    counter = 0
    success_count = 0
    failed = []
    if parallelism <= 1:
        for i, it in enumerate(iterable):
            if i < skip:
                continue

            print(f"Running {i+1}/{length}")
            out = func(it)
            if out is not None:
                success_count += 1
            else:
                failed.append(it)
    else:
        if local_multiproc:
            with multiprocessing.Pool(parallelism) as p:
                results = list(tqdm.tqdm(p.imap_unordered(func, iterable), total=length))
                outputs = [result[0] for result in results]
                for out in outputs:
                    if out is not None:
                        success_count += 1
        else:
            for it in itertools.batched(iterable, parallelism):
                if counter < skip:
                    counter = counter + parallelism
                    continue

                output = []
                print(f"Running {counter+1}...{counter+parallelism}/{length}")
                for i in it:
                    out = dask.delayed(func)(i)
                    if out is None:
                        failed.append(i)

                    output.append(out)

                results = dask.compute(output)[0]
                ls_count = 0
                for i, r in enumerate(results):
                    if r is not None:
                        ls_count += 1
                        success_count += 1
                    else:
                        failed.append(it[i])
                        print(f"Failed metric: {it[i]}")
                print(f"{ls_count} succeeded.")
                counter = counter + parallelism

    print(f"{success_count}/{length} returned non-null values. Runs that failed: {failed}")
