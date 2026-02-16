"""A combined runner utility that reads metrics.yaml, and allows the running and monitoring of multiple metrics"""

import argparse
import yaml
import itertools

def parse_metrics(metric_subgroup):
    """Loads the metrics.yaml file and creats a product of all the options to return as a dict."""
    with open('metrics.yaml', 'r') as f:
        data = yaml.safe_load(f)


if __name__ == "__main__":
    ## Parse arguments
    parser = argparse.ArgumentParser()

    # This controls which metric to run

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
    parser.add_argument("--from-file", type=str, help="A file that defines combinations of metrics to run")
    parser.add_argument("--metric-group", type=str, help="The section of metrics.yaml to run")

    # These control how the metrics are run
    parser.add_argument("--divide-by", type=str, help="A sub-property to device the metrics by for running. Will start a cluster for each value.")
    parser.add_argument("--backend", type=str, default=None, help="Backend to use for evaluation.")
    parser.add_argument("--parallelism", type=int, default=1, help="Number of runs to run in parallel.")
    parser.add_argument("--recompute", action=argparse.BooleanOptionalAction,
                        default=False, help="Whether to recompute existing metrics.")
    parser.add_argument("--remote", action=argparse.BooleanOptionalAction,
                        default=True, help="Whether to run on remote cluster.")
    parser.add_argument("--remote-name", type=str, default=None, help="Name of remote cluster to use.")
    parser.add_argument("--remote-config", type=str, nargs='*', help="Remote configuration to use.")
    parser.add_argument("--skip", type=int, default=0, help="Start runs at this index by skipping the first N runs.")
    args = parser.parse_args()


    #### Get all the combinations of metrics to run - either through a product of passed options - or by resolving the yaml file
    if args.from_file:
        # Use the file
        pass
    else:
        # Verify a valid function has been passed
        # TODO

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

