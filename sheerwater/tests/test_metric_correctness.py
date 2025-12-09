"""Test the metrics library."""
# flake8: noqa: E501
import matplotlib.pyplot as plt
import numpy as np
from nuthatch import cache

from sheerwater.metrics import metric
from sheerwater.utils import dask_remote, start_remote


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'lead', 'forecast', 'truth',
                   'metric', 'time_grouping', 'spatial', 'grid', 'mask', 'region'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "time": 100, 'region': 300, 'prediction_timedelta': -1},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           }
})
def grouped_metric_test(start_time, end_time, variable, lead, forecast, truth,
                             metric, time_grouping=None, spatial=False, grid="global1_5",
                             mask='lsm', region='africa'):  # noqa
    """Stub function providing gold standard reference for testing."""
    pass


def single_comparison(forecast="ecmwf_ifs_er_debiased",
                           metric_name="mae",
                           variable="precip",
                           space_grouping=None,
                           region="global",
                           lead="week3",
                           mask='lsm',
                           recompute=False,
                           spatial=True):  # noqa: E501
    """Test a single comparison between the two functions."""
    print(f"Testing: {forecast} | {metric_name} | {variable} | {space_grouping} | {region} | {lead} | spatial={spatial}")

    # Run grouped_metric_new
    ds_new = metric(
        start_time="2016-01-01",
        end_time="2022-12-31",
        variable=variable,
        agg_days=7,
        forecast=forecast,
        truth='era5',
        metric_name=metric_name,
        time_grouping=None,
        spatial=spatial,
        space_grouping=space_grouping,
        region=region,
        mask=mask,
        grid='global1_5',
        recompute=recompute,
        force_overwrite=True,
    )

    # Convert from new metric format to old format by selection region and lead time
    if region in ds_new.dims and len(ds_new.region.values) > 1:
        ds_new = ds_new.sel(region=region)
    if 'prediction_timedelta' in ds_new.dims and len(ds_new.prediction_timedelta.values) > 1:
        lead_dict = {
            'week1': 0,
            'week2': 7,
            'week3': 14,
            'week4': 21,
            'week5': 28,
            'week6': 35,
        }
        ds_new = ds_new.sel(prediction_timedelta=np.timedelta64(lead_dict[lead], 'D'))
        ds_new = ds_new.rename({'prediction_timedelta': 'lead_time'})
        ds_new.lead_time.values = lead

    if '-' in metric_name:
        mn = metric_name.split('-')[0]
    else:
        mn = metric_name
    ds_new = ds_new.rename_vars({mn: variable})

    # Run grouped_metric
    region_call = space_grouping if space_grouping != 'nimbus_east_africa' else 'east_africa'
    region_call = 'global' if region_call is None else region_call
    ds_old = grouped_metric_test(
        start_time="2016-01-01",
        end_time="2022-12-31",
        variable=variable,
        lead=lead,
        forecast=forecast,
        truth='era5',
        metric=metric_name,
        time_grouping=None,
        spatial=spatial,
        region=region_call,
        mask=mask,
        grid='global1_5',
        recompute=False,
        retry_null_cache=True
    )

    # Compare results
    if ds_new is None and ds_old is None:
        print("Both functions returned None")
        return None, None, 0

    if ds_new is None:
        print("Only grouped_metric_new returned None")
        return None, ds_old, 1

    if ds_old is None:
        print("Only grouped_metric returned None")
        return ds_new, None, 2

    # Both datasets exist
    new_data = ds_new[variable].compute()
    old_data = ds_old[variable].compute()

    print(f"New function result shape: {new_data.shape}")
    print(f"Old function result shape: {old_data.shape}")
    print(
        f"New function min/max/mean: {float(new_data.min()):.6f} / {float(new_data.max()):.6f} / {float(new_data.mean()):.6f}")
    print(
        f"Old function min/max/mean: {float(old_data.min()):.6f} / {float(old_data.max()):.6f} / {float(old_data.mean()):.6f}")

    # Compute difference
    try:
        diff = new_data - old_data
        diff_max = float(diff.max())
        diff_min = float(diff.min())
        diff_mean = float(diff.mean())
        diff_std = float(diff.std())

        print(f"Difference - min: {diff_min:.6f}, max: {diff_max:.6f}, mean: {diff_mean:.6f}, std: {diff_std:.6f}")

        if abs(diff_max) < 1e-10:
            print("✓ EXACT MATCH")
            return ds_new, ds_old, 3
        elif abs(diff_max) < 0.007 or (metric_name == "mape" and abs(diff_max) < 100):  # Allow for larger difference in mape
            print("✓ CLOSE MATCH")
            return ds_new, ds_old, 4
        else:
            print("✗ SIGNIFICANT DIFFERENCE")
            return ds_new, ds_old, 5

    except Exception as e:
        print(f"Error computing difference: {e}")
        raise e


def test_multiple_combinations():  # noqa: E501
    """Test multiple combinations of parameters."""
    test_cases = [
        # Our basic test, does lat-weighted averaging and masking globally
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae", "space_grouping": None, "region": "global",
            "mask": 'lsm', "variable": "precip", "spatial": False},
        # Have to test with spatial = True because old code had a spatial weighting bug
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae", "space_grouping": None, "region": "nimbus_east_africa",
            "mask": 'lsm', "variable": "precip", "spatial": True},

        # Now test all the metrics
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "acc", "variable": "precip", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "ets-5", "variable": "precip", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "pod-5", "variable": "precip", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "rmse", "variable": "precip", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "bias", "variable": "precip", "spatial": True},
        # Test quantileCRPS, which can only be done with Salient in Africa
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "crps", "variable": "precip", "spatial": True},
        {"forecast": "salient", "metric_name": "crps", "variable": "precip", "spatial": True, 'region': 'africa'},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "smape", "variable": "precip", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "mape", "variable": "precip", "spatial": False},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "seeps", "variable": "precip", "spatial": True},
        # Pearson only computed for week 3
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "pearson", "variable": "precip", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "heidke-1-5-10-20", "variable": "precip", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "pod-10", "variable": "precip", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "far-5", "variable": "precip", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "frequencybias-5", "variable": "precip", "spatial": False},

        # Different forecasts
        {"forecast": "ecmwf_ifs_er", "metric_name": "mae", "variable": "precip", "spatial": False},
        {"forecast": "climatology_2015", "metric_name": "mae", "variable": "precip", "spatial": True},
        {"forecast": "fuxi", "metric_name": "mae", "variable": "precip", "spatial": True},

        # # Different variables
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae", "variable": "tmp2m", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "acc",
            "variable": "precip", 'lead': 'week2', "spatial":  True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "acc", "variable": "tmp2m", 'lead': 'week2', "spatial":  True},

        # Different regions(need to test with spatial=True because old code had a spatial weighting bug)
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae",
            "variable": "precip", "space_grouping": "africa", "spatial": True},
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae",
            "variable": "precip", "space_grouping": "east_africa", "spatial": True},

        # Non-spatial tests, on coupled metrics.
        {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae", "variable": "precip", "spatial": False},
        # This one doesn't match because ACC wasn't spatially weigthed before
        # {"forecast": "ecmwf_ifs_er_debiased", "metric_name": "acc", "variable": "precip", "spatial": False},
    ]

    results = []

    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"Test case {i+1}/{len(test_cases)}")
        print(f"{'='*60}")

        # Set defaults
        test_case.setdefault("region", "global")
        test_case.setdefault("space_grouping", None)
        test_case.setdefault("lead", "week3")
        test_case.setdefault("recompute", ['global_statistic', 'metric'])
        # test_case.setdefault("recompute", False)
        test_case.setdefault("spatial", True)
        test_case.setdefault("mask", "lsm")

        ds_new, ds_old, result = single_comparison(**test_case)
        results.append({
            "test_case": i+1,
            "params": test_case,
            "result": result,
            "new_result": ds_new is not None,
            "old_result": ds_old is not None
        })

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    both_no_run = sum(1 for r in results if r["result"] == 0)
    new_failed = sum(1 for r in results if r["result"] == 1)
    old_failed = sum(1 for r in results if r["result"] == 2)
    exact_match = sum(1 for r in results if r["result"] == 3)
    close_match = sum(1 for r in results if r["result"] == 4)
    significant_difference = sum(1 for r in results if r["result"] == 5)

    print(f"Total tests: {len(results)}")
    print(f"Exact match: \t{exact_match} / {len(results)}, \t\t{exact_match/len(results)*100:.2f}%")
    print(f"Close match: \t{close_match} / {len(results)}, \t\t{close_match/len(results)*100:.2f}%")
    print(f"Sig. diff: \t{significant_difference} / {len(results)}, \t\t{significant_difference/len(results)*100:.2f}%")
    print(f"New failed: \t{new_failed} / {len(results)}, \t\t{new_failed/len(results)*100:.2f}%")
    print(f"Old failed: \t{old_failed} / {len(results)}, \t\t{old_failed/len(results)*100:.2f}%")
    print(f"Both no run: \t{both_no_run} / {len(results)}, \t\t{both_no_run/len(results)*100:.2f}%")

    failed_tests = [r['params'] for r in results if r["result"] in [0, 1, 5]]
    print(f"Failed tests: {failed_tests}")

    # If tests have failed, fail the test
    if len(failed_tests) > 0:
        assert False


def plot_comparison(forecast="ecmwf_ifs_er_debiased", metric="mae", variable="precip",
                    region="global", lead="week3", mask='lsm', spatial=True):
    """Create a plot comparing the results of both functions."""
    ds_new, ds_old = single_comparison(forecast, metric, variable, region, lead, mask, spatial)

    if ds_new is None or ds_old is None:
        print("Cannot plot - one or both datasets are None")
        return

    new_data = ds_new[variable].compute()
    old_data = ds_old[variable].compute()

    # Create subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Plot 1: New function result
    if spatial:
        new_data.plot(x='lon', ax=axes[0])
    else:
        axes[0].plot(new_data.values)
    axes[0].set_title(f'{metric.upper()} - New Function')

    # Plot 2: Old function result
    if spatial:
        old_data.plot(x='lon', ax=axes[1])
    else:
        axes[1].plot(old_data.values)
    axes[1].set_title(f'{metric.upper()} - Old Function')

    # Plot 3: Difference
    diff = new_data - old_data
    if spatial:
        diff.plot(x='lon', ax=axes[2])
    else:
        axes[2].plot(diff.values)
    axes[2].set_title(f'{metric.upper()} Difference (New - Old)')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Start remote cluster
    start_remote(remote_config='xlarge_cluster')

    print("Starting simple metrics comparison test...")
    # Run multiple test combinations
    test_multiple_combinations()

    # Create a specific plot comparison
    plot = False
    if plot:
        print("\nCreating detailed plot comparison...")
        plot_comparison(forecast="ecmwf_ifs_er_debiased", metric="mae", variable="precip", spatial=True)
        plot_comparison(forecast="climatology_2015", metric="bias", variable="tmp2m", spatial=True)
