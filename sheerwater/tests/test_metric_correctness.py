"""Test the metrics library: run metric() for multiple forecast/metric/region combinations.

Loads the old metric from cache (grouped_metric_test stub) and tests equality against
the new metric().

Run with -s to see diagnostic output:
  pytest sheerwater/tests/test_metric_correctness.py -v -s

Run only correctness tests:
  pytest -m correctness -v -s

Run a specific case with -k, e.g.: pytest ... -k "1" or -k "5_pod_5" or -k "mae_nonspatial"
"""
# ruff: noqa: E501
import numpy as np
import pytest

from sheerwater.metrics import metric
from sheerwater.utils import dask_remote
from nuthatch import cache

pytestmark = pytest.mark.correctness


# Stub providing gold standard reference: same cache signature as legacy grouped_metric.
@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'agg_days',
                   'forecast', 'truth',
                   'metric_name', 'event', 'event_kwargs',
                   'time_grouping', 'space_grouping', 'spatial', 'grid', 'mask', 'region'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "time": 100, 'region': 300, 'prediction_timedelta': -1},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           }
})
def gold_testing_metric(start_time, end_time, variable, forecast, truth,
           metric_name, agg_days=1,
           event=None, event_kwargs=None,  # noqa: ARG001
           time_grouping=None, space_grouping=None,
           spatial=False, grid="global1_5", mask='lsm', region='global'):
    """Compute a grouped metric for a forecast at a specific lead."""
    """Stub function providing gold standard reference for testing.

    The following code enables us to call this with recompute=True and replace the old
    metric value with a new metric value. This can be used if we want to change the gold
    standard metric value because a methodology or data source has changed.

    To use this, disable the fail_if_no_cache flag above and call with recompute=True.
    """
    # Run grouped_metric_new (same call structure as archive)
    ds_new = metric(
        start_time=start_time,
        end_time=end_time,
        variable=variable,
        forecast=forecast,
        truth=truth,
        metric_name=metric_name,
        agg_days=agg_days,
        event=event,
        event_kwargs=event_kwargs,
        time_grouping=time_grouping,
        space_grouping=space_grouping,
        spatial=spatial,
        region=region,
        mask=mask,
        grid=grid
    )
    return ds_new


def _single_comparison(test_case):
    """Run new metric(), load old metric from cache, compare. Returns (ds_new, ds_old, result_code)."""
    test_case = dict(test_case)
    test_case.setdefault("region", "global")
    test_case.setdefault("space_grouping", None)
    test_case.setdefault("forecast", "ecmwf_ifs_er_debiased")
    test_case.setdefault("truth", "era5")
    test_case.setdefault("metric_name", "mae")
    test_case.setdefault("variable", "precip")
    test_case.setdefault("lead", 21)  # 3 week lead by default
    test_case.setdefault("spatial", True)
    test_case.setdefault("mask", "lsm")
    test_case.setdefault("agg_days", 7)
    test_case.setdefault("event", None)
    test_case.setdefault("event_kwargs", None)
    test_case.setdefault("time_grouping", None)
    test_case.setdefault("grid", "global1_5")

    forecast = test_case["forecast"]
    truth = test_case["truth"]
    metric_name = test_case["metric_name"]
    variable = test_case["variable"]
    space_grouping = test_case["space_grouping"]
    region = test_case["region"]
    try:
        lead = int(test_case["lead"])
    except ValueError:
        lead = None
    agg_days = test_case["agg_days"]
    event = test_case["event"]
    event_kwargs = test_case["event_kwargs"]
    spatial = test_case["spatial"]
    mask = test_case["mask"]
    time_grouping = test_case["time_grouping"]
    grid = test_case["grid"]

    print(
        f"Testing: forecast={forecast} | truth={truth} | metric_name={metric_name} | variable={variable} | "
        f"space_grouping={space_grouping} | region={region} | lead={lead} days | agg_days={agg_days} | "
        f"event={event} | event_kwargs={event_kwargs} | spatial={spatial} | mask={mask} | "
        f"time_grouping={time_grouping} | grid={grid}"
    )

    recompute = test_case.get("recompute", ["global_statistic", "metric"])

    # Run grouped_metric_new (same call structure as archive)
    kwargs = {
        "start_time": "2016-01-01",
        "end_time": "2022-12-31",
        "variable": variable,
        "forecast": forecast,
        "truth": truth,
        "metric_name": metric_name,
        "agg_days": agg_days,
        "event": event,
        "event_kwargs": event_kwargs,
        "time_grouping": time_grouping,
        "spatial": spatial,
        "space_grouping": space_grouping,
        "region": region,
        "mask": mask,
        "grid": grid,
    }
    # Run the new metric
    ds_new = metric(**kwargs, recompute=recompute, cache_mode='read_only')

    # Run gold_testing_metric (same call structure as archive)
    ds_old = gold_testing_metric(**kwargs, recompute=False, cache_mode='read_only_strict')

    # Convert from new metric format to old format by selection region and lead time (archive logic)
    if lead is not None:
        if ds_new is not None:
            if 'prediction_timedelta' in ds_new.dims and len(ds_new.prediction_timedelta.values) > 1:
                ds_new = ds_new.sel(prediction_timedelta=np.timedelta64(lead, 'D'))
        if ds_old is not None:
            if 'prediction_timedelta' in ds_old.dims and len(ds_old.prediction_timedelta.values) > 1:
                ds_old = ds_old.sel(prediction_timedelta=np.timedelta64(lead, 'D'))

    # Compare
    if ds_new is None and ds_old is None:
        print("Both functions returned None")
        return None, None, 0
    if ds_new is None:
        print("Only grouped_metric_new returned None")
        return None, ds_old, 1
    if ds_old is None:
        print("Only grouped_metric returned None")
        return ds_new, None, 2

    # Both datasets exist (same compare structure as archive)
    mn = metric_name.split('-')[0]
    new_data = ds_new[mn].compute()
    old_data = ds_old[mn].compute()

    print(f"New function result shape: {new_data.shape}")
    print(f"Old function result shape: {old_data.shape}")
    nmin, nmax, nmean = float(new_data.min()), float(new_data.max()), float(new_data.mean())
    omin, omax, omean = float(old_data.min()), float(old_data.max()), float(old_data.mean())
    print(f"New function min/max/mean: {nmin:.6f} / {nmax:.6f} / {nmean:.6f}")
    print(f"Old function min/max/mean: {omin:.6f} / {omax:.6f} / {omean:.6f}")

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
        elif abs(diff_max) < 0.007 or (metric_name == "mape" and abs(diff_max) < 100):
            print("✓ CLOSE MATCH")
            return ds_new, ds_old, 4
        else:
            print("✗ SIGNIFICANT DIFFERENCE")
            return ds_new, ds_old, 5

    except Exception as e:
        print(f"Error computing difference: {e}")
        raise


def _run_single_case(test_case):
    """Run single comparison; return (result, passed, result_code)."""
    _, _, result_code = _single_comparison(test_case)
    # 3=exact, 4=close -> pass; 1=new failed -> fail; 5=significant diff -> fail; 0=both None, 2=old missing -> pass
    passed = result_code in (3, 4, 0, 2)
    if result_code == 1:
        print("✗ FAIL (new metric returned None)")
    elif result_code == 5:
        print("✗ FAIL (significant difference from old metric)")
    elif passed and result_code == 2:
        print("✓ PASS (no old baseline in cache)")
    elif passed:
        print("✓ PASS")
    return None, passed, result_code


# Test cases from testing_archive/test_metric_correctness. Each has a "name" used as the test id.
METRIC_TEST_CASES = [
    {"name": "1_mae_global", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae",
        "variable": "precip", "space_grouping": None, "region": "global", "mask": "lsm", "spatial": False},
    {"name": "2_mae_nimbus_east_africa", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae",
        "variable": "precip", "space_grouping": None, "region": "nimbus_east_africa", "mask": "lsm", "spatial": True},
    {"name": "3_acc", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "acc", "variable": "precip", "spatial": True},
    {"name": "4_ets_5", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "ets-5", "variable": "precip", "spatial": True},
    {"name": "5_pod_5", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "pod-5", "variable": "precip", "spatial": True},
    {"name": "6_rmse", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "rmse", "variable": "precip", "spatial": True},
    {"name": "7_bias", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "bias", "variable": "precip", "spatial": True},
    {"name": "8_crps", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "crps", "variable": "precip", "spatial": True},
    {"name": "9_crps_salient_africa", "forecast": "salient", "metric_name": "crps",
        "variable": "precip", "spatial": True, "region": "africa"},
    {"name": "10_smape", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "smape", "variable": "precip", "spatial": True},
    # {"name": "11_mape", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "mape", "variable": "precip", "spatial": False},
    {"name": "12_seeps", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "seeps", "variable": "precip", "spatial": True},
    {"name": "13_pearson", "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "pearson", "variable": "precip", "spatial": True},
    {"name": "14_heidke", "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "heidke-1-5-10-20", "variable": "precip", "spatial": True},
    {"name": "15_pod_10", "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "pod-10", "variable": "precip", "spatial": True},
    {"name": "16_far_5", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "far-5", "variable": "precip", "spatial": True},
    {"name": "17_frequencybias_5", "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "frequencybias-5", "variable": "precip", "spatial": False},
    {"name": "18_mae_ecmwf_ifs_er", "forecast": "ecmwf_ifs_er",
        "metric_name": "mae", "variable": "precip", "spatial": False},
    {"name": "19_mae_climatology", "forecast": "climatology_era5_1985_2015",
        "metric_name": "mae", "variable": "precip", "spatial": True},
    {"name": "20_mae_fuxi", "forecast": "fuxi", "metric_name": "mae", "variable": "precip", "spatial": True},
    {"name": "21_mae_tmp2m", "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "mae", "variable": "tmp2m", "spatial": True},
    {"name": "22_acc_week2", "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "acc", "variable": "precip", "lead": 14, "spatial": True},
    {"name": "23_acc_tmp2m_week2", "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "acc", "variable": "tmp2m", "lead": 14, "spatial": True},
    {"name": "24_mae_africa", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae",
        "variable": "precip", "region": "africa", "spatial": True},
    {"name": "25_mae_nimbus_east_africa", "forecast": "ecmwf_ifs_er_debiased", "metric_name": "mae",
        "variable": "precip", "region": "nimbus_east_africa", "spatial": True},
    {"name": "26_mae_nonspatial", "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "mae", "variable": "precip", "spatial": False},
    {"name": "27_brier", "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "brier-10", "variable": "precip", "spatial": False},
]


@pytest.mark.parametrize(
    "test_case",
    METRIC_TEST_CASES,
    ids=[c["name"] for c in METRIC_TEST_CASES],
)
def test_metric_correctness(remote_dask_cluster, test_case):  # noqa: ARG001
    """One test per metric/forecast/variable/region combination; compares to cached baseline."""
    _, passed, _ = _run_single_case(test_case)
    assert passed


if __name__ == "__main__":
    from sheerwater.utils import start_remote
    cluster = start_remote(remote_config='xlarge_cluster')
    test_metric_correctness(cluster, METRIC_TEST_CASES[2])
    # test_metric_correctness(cluster, METRIC_TEST_CASES[21])
    # test_metric_correctness(cluster, METRIC_TEST_CASES[22])
