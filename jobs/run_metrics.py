"""A combined runner utility that reads metrics.yaml, and allows the running and monitoring of multiple metrics."""
#!/usr/bin/env python
import argparse
import dask
import time
import yaml
import copy
import sys
import itertools
import sheerwater.metrics as metrics
import dashboard_data
from sheerwater.utils import start_remote
import multiprocessing

def run_in_parallel(func, iterable, parallelism, skip=0, name=""):
    """Run a function in parallel with dask delayed.

    Args:
        func(callable): A function to call. Must take one of iterable as an argument.
        iterable (iterable): Any iterable object to pass to func.
        parallelism (int): Number of func(iterables) to run in parallel at a time.
        skip (int): Number of iterables to skip.
        name (str): Name of the runner for printing.
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

            if name:
                print(f"{name}: Running {i+1}/{length}")
            else:
                print(f"Running {i+1}/{length}")

            out = func(**it)
            if out is not None:
                success_count += 1
            else:
                failed.append(it)
    else:
        for it in itertools.batched(iterable, parallelism):
            if counter < skip:
                counter = counter + parallelism
                continue

            output = []

            if name:
                print(f"{name}: Running {counter+1}...{counter+parallelism}/{length}")
            else:
                print(f"Running {counter+1}...{counter+parallelism}/{length}")

            sys.stdout.flush()

            for i in it:
                out = dask.delayed(func)(**i)
                if out is None:
                    failed.append(i)

                output.append(out)

            start_time = time.perf_counter()
            results = dask.compute(output)[0]
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            ls_count = 0
            for i, r in enumerate(results):
                if r is not None:
                    ls_count += 1
                    success_count += 1
                else:
                    failed.append(it[i])
                    print(f" -- Failed metric: {it[i]} -- ")

            if name:
                print(f"{name}: {ls_count} succeeded in {(int)(execution_time/parallelism)}s per metric.")
            else:
                print(f"{ls_count} succeeded in {(int)(execution_time/parallelism)}s per metric.")

            counter = counter + parallelism

    if name:
        print(f"{name}: {success_count}/{length} returned non-null values. Runs that failed: {failed}")
    else:
        print(f"{success_count}/{length} returned non-null values. Runs that failed: {failed}")


def extract_combos_from_args(args):
    """Extracts combinations of metrics to run from the arguments."""
    if 'start_time' not in args or 'end_time' not in args:
        raise ValueError("If explicitly passing metrics arguments, start_time and end_time must be specified")

    # Get list of arguments that have been passed
    args_to_extract = ['forecast', 'truth', 'variable', 'grid', 'agg_days', 'space_grouping', 'time_grouping', 'metric']
    args_for_product = {key: getattr(args, key) for key in args_to_extract if getattr(args, key)}

    def product_dict(**kwargs):
        keys = kwargs.keys()
        for instance in itertools.product(*kwargs.values()):
            yield dict(zip(keys, instance))

    product_of_args = list(product_dict(**args_for_product))

    if 'start_time' not in args or 'end_time' not in args:
        raise ValueError("If explicitly passing metrics arguments, start_time and end_time must be specified")

    # Now for each value of this list add in start and end time
    for v in product_of_args:
        v['start_time'] = args.start_time
        v['end_time'] = args.end_time

    return product_of_args

def extract_combos_from_file(file, metric_group):
    """Extract all metric combinations from a section of a metrics file."""
    function = None
    data = None
    with open(file, 'r') as f:
        data = yaml.safe_load(f)

        if metric_group not in data:
            raise ValueError(f"Metric group {metric_group} not found in {file}")

        if 'function' not in data[metric_group]:
            raise ValueError(f"Function name not found in {metric_group} in {file}")

        function = data[metric_group]['function']
        del data[metric_group]['function']
        data = data[metric_group]

    combos = []
    all_combos = {}
    if '_all' in data:
        all_combos = data['_all']
        del data['_all']

    for key, value in data.items():
        current_combo = copy.deepcopy(all_combos)
        #print(current_combo)
        #print(data[key])

        # Update and add section-specific options
        current_combo.update(data[key])

        # Anything that is a string should be turned into a list for the product
        for k, v in current_combo.items():
            if not isinstance(v, list):
                current_combo[k] = [v]

        def product_dict(**kwargs):
            keys = kwargs.keys()
            for instance in itertools.product(*kwargs.values()):
                yield dict(zip(keys, instance))

        order = ['start_time', 'end_time', 'forecast', 'truth', 'variable', 'grid', 'agg_days', 'metric_name', 'space_grouping', 'time_grouping']
        ordered_combo = {key: current_combo[key] for key in order if key in current_combo}
        ordered_combo.update({
            key: current_combo[key] for key in current_combo if key not in order
        })

        products = list(product_dict(**ordered_combo))

        combos.extend(products)

    return function, combos


def start_and_run_group(combos, parallelism, skip, remote_name, remote_config, function):
    """Start a cluster and run a set of function combinations on that cluster."""
    iterable, combos_copy = itertools.tee(combos)
    length = len(list(combos_copy))
    print(f"Starting cluster {remote_name} to run {length} metrics with {parallelism} parallelism.\n \
            \tcluster_config: {remote_config}")

    start_remote(remote_name=remote_name, remote_config=remote_config)
    combos = copy.deepcopy(combos)
    run_in_parallel(function, combos, parallelism, skip=skip, name=remote_name)


if __name__ == "__main__":
    ## Parse arguments
    parser = argparse.ArgumentParser()

    # These arguments get packed and passed through to the metric runner function as a kwarg
    parser.add_argument('--function', type=str, help='Name of the metric function to run')
    parser.add_argument("--start-time", type=str, help="Start time for evaluation.")
    parser.add_argument("--end-time", type=str, help="End time for evaluation.")
    parser.add_argument("--forecast", type=str, nargs='*', help="Forecasts to evaluate.")
    parser.add_argument("--truth", type=str, nargs='*', help="Truth data to evaluate against.")
    parser.add_argument("--variable", type=str, nargs='*', help="Variables to evaluate.")
    parser.add_argument("--metric", type=str, nargs='*', help="Metrics to evaluate.")
    parser.add_argument("--grid", type=str, nargs='*', help="Grids to evaluate.")
    parser.add_argument("--space-grouping", type=str, nargs='*', help="Space groupings to evaluate.")
    parser.add_argument("--agg-days", type=int, nargs='*', help="Aggregation days to evaluate.")
    parser.add_argument("--time-grouping", type=str, nargs='*', help="Time groupings to evaluate.")

    # Instead of passing the arguments in a bespoke way, you can also get combinations from metrics.yaml
    parser.add_argument("--from-file", "-f", type=str, help="A file that defines combinations of metrics to run")
    parser.add_argument("--metric-group", "-m",  type=str, help="The section of metrics.yaml to run")

    # These control how the metrics are run
    parser.add_argument("--divide-by", type=str, nargs='*',
                        help="A sub-property to device the metrics by for running. \
                        Will start a cluster for each value.")
    parser.add_argument("--backend", type=str, default=None, help="Backend to use for evaluation.")
    parser.add_argument("--recompute", action=argparse.BooleanOptionalAction,
                        default=False, help="Whether to recompute existing metrics.")
    parser.add_argument("--memoize-forecast", action=argparse.BooleanOptionalAction,
                        default=False, help="Whether to memoize the forecast.")
    parser.add_argument("--memoize-truth", action=argparse.BooleanOptionalAction,
                        default=False, help="Whether to memoize the truth.")
    parser.add_argument("--target-read-chunk-size-mb", type=int, help="Number of runs to run in parallel.")
    parser.add_argument("--filepath-only", action=argparse.BooleanOptionalAction, default=True,
                        help="Whether to run the nuthatch cache with filepath only.")
    parser.add_argument("--remote", action=argparse.BooleanOptionalAction,
                        default=True, help="Whether to run on remote cluster.")
    parser.add_argument("--remote-order", type=str, nargs='*',
                        help="Order of remote clusters to use. Finds corresponding remote name and \
                        config for each divide by group.")
    parser.add_argument("--remote-name", type=str, nargs='*',
                        help="Name of remote cluster to use. If using divide by can be passed \
                        once for all clusters or for each divide by group.")
    parser.add_argument("--parallelism", type=int, nargs='*',
                        help="Number of runs to run in parallel. If using divide by can be passed \
                        once for all clusters or for each divide by group.")
    parser.add_argument("--remote-config", type=str, action='append', nargs='*',
                        help="Remote configuration to use. If using divide by can be passed \
                        once for all clusters or for each divide by group.")
    parser.add_argument("--skip", type=int, nargs='*',
                        help="Start runs at this index by skipping the first N runs. If using divide by can be passed \
                        once for all clusters or for each divide by group.")
    args = parser.parse_args()

    #### Get all the combinations of metrics to run -
    # either through a product of passed options - or by resolving the yaml file
    combos_to_run = []
    if args.from_file:
        # Use the file
        if args.metric_group is None:
            raise ValueError("If passing a file, a metric group must be specified")

        function, combos_to_run = extract_combos_from_file(args.from_file, args.metric_group)
    else:
        # Verify a valid function has been passed
        if args.function is None:
            raise ValueError("If not passing a file, a function must be specified")

        function = args.function
        combos_to_run = extract_combos_from_args(args)

    if args.metric_group is not None:
        name_prefix = args.metric_group
    else:
        name_prefix = args.function

    # Resolve extra variables to good defaults (filepath_only, recompute, storage_backend,
    # target_read_chunk_size, memoize_forecast, memoize_truth)
    # Insert in each combo so that combo can be passed as **kwargs
    for combo in combos_to_run:
        combo.setdefault('filepath_only', args.filepath_only)

        # If recompute we likely want to overwrite
        combo.setdefault('recompute', args.recompute)
        if args.recompute:
            combo.setdefault('cache_mode', 'overwrite')

        combo.setdefault('storage_backend', args.backend)
        if args.target_read_chunk_size_mb:
            combo.setdefault('backend_kwargs', {'target_read_chunk_size_mb': args.target_read_chunk_size_mb})
        else:
            combo.setdefault('backend_kwargs', None)
        if args.function == 'metric':
            combo.setdefault('memoize_forecast', args.memoize_forecast)
            combo.setdefault('memoize_truth', args.memoize_truth)

    # Now we have al list of combinations, we need to split it into lists based on the divide by arguments
    dict_of_combos_to_run = {}
    if args.divide_by is not None:
        for combo in combos_to_run:
            key = ""
            for divide_by in args.divide_by:
                if divide_by not in combo:
                    raise ValueError(f"Divide by argument {divide_by} not found in combination {combo}")

                #key += f"{name_prefix}-{combo[divide_by]}"
                key = f"{combo[divide_by]}"

            if key not in dict_of_combos_to_run:
                dict_of_combos_to_run[key] = []

            dict_of_combos_to_run[key].append(combo)
    else:
        dict_of_combos_to_run[f'{name_prefix}'] = combos_to_run

    # Check that the cluster arguments match the number of divide by groups
    if (args.remote_name is not None and len(args.remote_name) != len(dict_of_combos_to_run)
                                     and len(args.remote_name) != 1):
        raise ValueError(f"Number of remote names ({len(args.remote_name)}) \
        does not match number of divide by groups ({len(dict_of_combos_to_run)})")

    if (args.remote_config is not None and len(args.remote_config) != len(dict_of_combos_to_run)
                                       and len(args.remote_config) != 1):
        raise ValueError(f"Number of remote configs ({len(args.remote_config)}) \
                does not match number of divide by groups ({len(dict_of_combos_to_run)})")

    if (args.parallelism is not None and len(args.parallelism) != len(dict_of_combos_to_run)
                                     and len(args.parallelism) != 1):
        raise ValueError(f"Number of parallelism ({len(args.parallelism)}) \
        does not match number of divide by groups ({len(dict_of_combos_to_run)})")

    if args.skip is not None and len(args.skip) != len(dict_of_combos_to_run) and len(args.skip) != 1:
        raise ValueError(f"Number of skip ({len(args.skip)}) \
        does not match number of divide by groups ({len(dict_of_combos_to_run)})")

    if args.remote_order is not None and len(args.remote_order) != len(dict_of_combos_to_run):
        raise ValueError(f"Number of remote order ({len(args.remote_order)}) \
        does not match number of divide by groups ({len(dict_of_combos_to_run)})")

    # Resolve the function being run
    try:
        function = getattr(metrics, function)
    except AttributeError:
        try:
            function = getattr(dashboard_data, function)
        except AttributeError:
            raise ValueError(f"Function {function} not found in metrics or dashboard_data modules")



    # Start threads for each divide by group
        # In each thread start a cluster for each divide by group
        # Run in parallel for each group
    processes = []
    if len(dict_of_combos_to_run) == 1:
        combos = list(dict_of_combos_to_run.values())[0]

        if args.parallelism is None:
            parallelism = 1
        else:
            parallelism = args.parallelism[0]

        if args.skip is None:
            skip = 0
        else:
            skip = args.skip[0]

        if args.remote_name is None:
            remote_name = name_prefix + '-' + list(dict_of_combos_to_run.keys())[0]
        else:
            remote_name = args.remote_name[0]

        if args.remote_config is None:
            remote_config = []
        else:
            remote_config = args.remote_config[0]

        if parallelism <= 1:
            start_and_run_group(combos, parallelism, skip, remote_name, remote_config, function)
        else:
            processes.append(multiprocessing.Process(target=start_and_run_group,
                                                    args=(combos, parallelism, skip,
                                                        remote_name, remote_config, function)))
    else:
        for key, value in dict_of_combos_to_run.items():
            if args.parallelism is None:
                parallelism = 1
            elif len(args.parallelism) == 1:
                parallelism = args.parallelism[0]
            elif args.remote_order and key in args.remote_order:
                index = args.remote_order.index(key)
                parallelism = args.parallelism[index]
            else:
                raise ValueError("Multiple parallelism arguments passed but no value remote \
                                 order passed to index the parallelism arguments.")

            if args.skip is None:
                skip = 1
            elif len(args.skip) == 1:
                skip = args.skip[0]
            elif args.remote_order and key in args.remote_order:
                index = args.remote_order.index(key)
                skip = args.skip[index]
            else:
                raise ValueError("Multiple skip arguments passed but no value remote order \
                                 passed to index the skip arguments.")

            if args.remote_name is None:
                remote_name = 'metrics-' + name_prefix + '-' + key
            elif len(args.remote_name) == 1:
                remote_name = args.remote_name[0] + '-' + name_prefix + '-' + key
            elif args.remote_order and key in args.remote_order:
                index = args.remote_order.index(key)
                remote_name = args.remote_name[index] + '-' + name_prefix + '-' + key
            else:
                raise ValueError("Multiple remote_name arguments passed but no value remote order \
                                 passed to index the remote_name arguments.")

            if args.remote_config is None:
                remote_config = []
            elif len(args.remote_config) == 1:
                remote_config = args.remote_config[0]
            elif args.remote_order and key in args.remote_order:
                index = args.remote_order.index(key)
                remote_config = args.remote_config[index]
            else:
                raise ValueError("Multiple remote_config arguments passed but no value remote order \
                                 passed to index the remote_config arguments.")

            processes.append(multiprocessing.Process(target=start_and_run_group,
                                                     args=(value, parallelism, skip,
                                                           remote_name, remote_config, function)))


    # Start all the processes
    for process in processes:
        process.start()

    # Print progress for all processes until they all complete
    while True:
        all_complete = True
        for process in processes:
            if process.is_alive():
                all_complete = False
                break

        if all_complete:
            break

        time.sleep(1)

    for process in processes:
        process.join()

    print("All processes completed!")
