"""Utilities for running jobs."""
import argparse
import dask
import itertools
import multiprocessing
import os
import sys
import time
import tqdm
from contextlib import contextmanager
from datetime import datetime

from sheerwater.metrics_library import metric_factory

skip = 0
station_eval = False


# Global benchmark context
_benchmark_context = None

def parse_args():
    """Parses arguments for jobs."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-time", default="1998-01-01", type=str)
    parser.add_argument("--end-time", default="2024-12-31", type=str)
    parser.add_argument("--forecast", type=str, nargs='*')
    parser.add_argument("--truth", type=str, nargs='*')
    parser.add_argument("--variable", type=str, nargs='*')
    parser.add_argument("--metric", type=str, nargs='*')
    parser.add_argument("--grid", type=str, nargs='*')
    parser.add_argument("--region", type=str, nargs='*')
    parser.add_argument("--agg_days", type=int, nargs='*')
    parser.add_argument("--time-grouping", type=str, nargs='*')
    parser.add_argument("--backend", type=str, default=None)
    parser.add_argument("--parallelism", type=int, default=1)
    parser.add_argument("--recompute", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--remote", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--station-evaluation", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--seasonal", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--remote-name", type=str, default=None)
    parser.add_argument("--remote-config", type=str, nargs='*')
    parser.add_argument("--gpu", type=str, nargs='?', const='t4', default=None,
                        choices=['t4', 't4_cluster', 'a100', 'a100_large', 'a100_cluster', 'a100_xlarge_cluster',
                                 'a100_4x', 'a100_8x', 'l4', 'l4_large', 'l4_cluster',
                                 't4_highmem', 't4_highmem_large', 't4_highmem_xlarge',
                                 'l4_highmem', 'l4_highmem_large'],
                        help="GPU options. High-memory single machines: t4_highmem (208GB), t4_highmem_large (416GB), "
                             "t4_highmem_xlarge (624GB), l4_highmem (192GB), l4_highmem_large (384GB)")
    parser.add_argument("--benchmark", action=argparse.BooleanOptionalAction, default=False,
                        help="Enable performance benchmarking (generates HTML report)")
    parser.add_argument("--benchmark-file", type=str, default=None,
                        help="Output filename for benchmark report (default: auto-generated)")
    parser.add_argument("--skip", type=int, default=0)
    args = parser.parse_args()

    global skip
    skip = args.skip

    global station_eval
    if args.station_evaluation:
        station_eval = True

    if args.station_evaluation:
        forecasts = ["chirps_v3", "chirp_v3", "imerg_late", "imerg_final", "era5"]
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

    # Add GPU config if --gpu flag is set
    use_gpu = args.gpu is not None
    if use_gpu:
        # Map GPU type to config preset
        gpu_config_map = {
            't4': 'gpu',
            't4_cluster': 'gpu_cluster',
            't4_highmem': 'gpu_t4_highmem',
            't4_highmem_large': 'gpu_t4_highmem_large',
            't4_highmem_xlarge': 'gpu_t4_highmem_xlarge',
            'l4': 'gpu_l4',
            'l4_large': 'gpu_l4_large',
            'l4_cluster': 'gpu_l4_cluster',
            'l4_highmem': 'gpu_l4_highmem',
            'l4_highmem_large': 'gpu_l4_highmem_large',
            'a100': 'gpu_a100',
            'a100_large': 'gpu_a100_large',
            'a100_cluster': 'gpu_a100_cluster',
            'a100_xlarge_cluster': 'gpu_a100_xlarge_cluster',
            'a100_4x': 'gpu_a100_4x',
            'a100_8x': 'gpu_a100_8x',
        }
        gpu_config = gpu_config_map.get(args.gpu, 'gpu')
        remote_config = list(remote_config) + [gpu_config]

        # Set GPU environment variable early so it's available when start_remote() is called
        # This allows the env var to be propagated to Coiled workers
        os.environ["SHEERWATER_GPU_ENABLED"] = "1"

    # Generate benchmark filename if not provided
    benchmark_file = args.benchmark_file
    if args.benchmark and not benchmark_file:
        script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gpu_suffix = f"_{args.gpu}" if use_gpu else "_cpu"
        benchmark_file = f"benchmark_{script_name}{gpu_suffix}_{timestamp}.html"

    return (args.start_time, args.end_time, forecasts, truth, metrics, variables, grids,
            regions, agg_days, time_groupings, args.parallelism,
            args.recompute, args.backend, args.remote_name, args.remote, remote_config,
            use_gpu, args.benchmark, benchmark_file)


def prune_metrics(combos, global_run=False):
    """Prunes a list of metrics combinations.

    Can skip all coupled metrics for global runs.
    """
    pruned_combos = []
    for combo in combos:
        forecast, truth, variable, grid, agg_days, region, time_grouping, metric_name = combo

        metric_obj = metric_factory(metric_name, start_time=None, end_time=None, variable=variable,
                                    agg_days=agg_days, forecast=forecast, truth=truth, time_grouping=time_grouping,
                                    spatial=False, grid=grid, mask=None, region=region)

        #if not global_run and 'tahmo' in truth and region != 'nimbus_east_africa':
        #    continue

        if metric_obj.valid_variables and variable not in metric_obj.valid_variables:
            continue

        if metric_name == 'seeps' and grid == 'global0_25':
            continue

        global station_eval
        if '-' in metric_name and station_eval:
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


@contextmanager
def benchmark_context(enabled=False, filename=None, use_gpu=False):
    """Context manager for benchmarking job execution.

    Wraps job execution with Dask performance reporting and timing.

    Args:
        enabled: Whether benchmarking is enabled.
        filename: Output HTML filename for the report.
        use_gpu: Whether GPU mode is enabled (for logging).

    Yields:
        dict: Benchmark results dictionary.

    Example:
        >>> with benchmark_context(do_benchmark, benchmark_file, use_gpu) as results:
        ...     run_in_parallel(run_metric, combos, parallelism)
        >>> print(f"Total time: {results['elapsed']:.2f}s")
    """
    global _benchmark_context

    results = {
        "enabled": enabled,
        "filename": filename,
        "gpu_enabled": use_gpu,
        "start_time": datetime.now().isoformat(),
    }

    if not enabled:
        yield results
        return

    # Print benchmark info
    mode = "GPU" if use_gpu else "CPU"
    print(f"\n{'='*60}")
    print(f"BENCHMARKING ENABLED ({mode} mode)")
    print(f"Report will be saved to: {filename}")
    print(f"{'='*60}\n")

    start = time.perf_counter()

    try:
        # Try to use Dask performance report
        from dask.distributed import performance_report
        with performance_report(filename=filename):
            _benchmark_context = results
            yield results
    except ImportError:
        print("Warning: dask.distributed not available, timing only")
        _benchmark_context = results
        yield results
    except Exception as e:
        print(f"Warning: Could not create performance report: {e}")
        print("Continuing with timing only...")
        _benchmark_context = results
        yield results
    finally:
        elapsed = time.perf_counter() - start
        results["elapsed"] = elapsed
        results["end_time"] = datetime.now().isoformat()
        _benchmark_context = None

        # Print summary
        print(f"\n{'='*60}")
        print(f"BENCHMARK COMPLETE ({mode} mode)")
        print(f"Total elapsed time: {elapsed:.2f}s ({elapsed/60:.2f} min)")
        if filename and os.path.exists(filename):
            print(f"Performance report saved to: {filename}")
            print(f"Open in browser to view task stream, worker profiles, etc.")
        print(f"{'='*60}\n")


def setup_job(use_gpu=False, do_benchmark=False, benchmark_file=None):
    """Setup job environment with GPU and benchmarking.

    Call this at the start of your job's main block.

    Args:
        use_gpu: Whether to enable GPU mode.
        do_benchmark: Whether benchmarking is enabled.
        benchmark_file: Output filename for benchmark report.

    Returns:
        Context manager for benchmarking (use with 'with' statement).

    Example:
        >>> if __name__ == "__main__":
        ...     with setup_job(use_gpu, do_benchmark, benchmark_file):
        ...         run_in_parallel(run_metric, combos, parallelism)
    """
    from sheerwater.utils import (enable_gpu, is_gpu_available, is_gpu_enabled,
                                   print_dask_dashboard_link, check_worker_gpu_status)

    # Enable GPU if requested
    if use_gpu:
        enable_gpu(True)
        gpu_available_locally = is_gpu_available()
        print(f"\n{'='*60}")
        print(f"GPU MODE REQUESTED")
        print(f"  SHEERWATER_GPU_ENABLED env var: {os.environ.get('SHEERWATER_GPU_ENABLED', 'not set')}")
        print(f"  cupy-xarray available locally: {gpu_available_locally}")
        if not gpu_available_locally:
            print(f"  NOTE: cupy requires CUDA (not available on macOS)")
            print(f"  GPU packages installed on Coiled workers via conda")
            print(f"  Workers will use GPU acceleration when cupy-xarray is available")
        else:
            print(f"  GPU acceleration active locally: {is_gpu_enabled()}")
        print(f"{'='*60}\n")

    # Print dashboard link if available
    try:
        print_dask_dashboard_link()
    except Exception:
        pass

    # Check GPU status on workers if GPU mode is enabled
    if use_gpu:
        try:
            check_worker_gpu_status()
        except Exception as e:
            print(f"Could not check worker GPU status: {e}")

    # Return benchmark context
    return benchmark_context(do_benchmark, benchmark_file, use_gpu)
