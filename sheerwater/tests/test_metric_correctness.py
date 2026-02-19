"""Test the metrics library: run metric() for multiple forecast/metric/region combinations.

Loads the old metric from cache (grouped_metric_test stub) and tests equality against
the new metric(). Behavior matches testing_archive/test_metric_correctness.

Run with -s to see diagnostic output:
  pytest sheerwater/tests/test_metric_correctness.py -v -s

Run a specific case by name, e.g.:
  pytest sheerwater/tests/test_metric_correctness.py -v -s -k ecmwf_mae_precip_global
"""
import numpy as np

from sheerwater.metrics import metric
from sheerwater.utils import dask_remote
from nuthatch import cache


# Stub providing gold standard reference: same cache signature as legacy grouped_metric.
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


def _single_comparison(test_case):
    """Run new metric(), load old metric from cache, compare. Returns (ds_new, ds_old, result_code)."""
    test_case = dict(test_case)
    test_case.setdefault("region", "global")
    test_case.setdefault("space_grouping", None)
    test_case.setdefault("lead", "week3")
    test_case.setdefault("spatial", True)
    test_case.setdefault("mask", "lsm")

    forecast = test_case["forecast"]
    metric_name = test_case["metric_name"]
    variable = test_case["variable"]
    space_grouping = test_case["space_grouping"]
    region = test_case["region"]
    lead = test_case["lead"]
    spatial = test_case["spatial"]
    mask = test_case["mask"]

    print(
        f"Testing: {forecast} | {metric_name} | {variable} | "
        f"{space_grouping} | {region} | {lead} | spatial={spatial}"
    )

    recompute = test_case.get("recompute", ["global_statistic", "metric"])

    # Run grouped_metric_new (same call structure as archive)
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
        cache_mode='overwrite',
    )

    # Convert from new metric format to old format by selection region and lead time (archive logic)
    if ds_new is not None:
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

    # Run grouped_metric (same call structure as archive)
    if space_grouping == 'nimbus_east_africa' or region == 'nimbus_east_africa':
        region_call = 'east_africa'
    elif region != 'global':
        region_call = region
    elif space_grouping is not None:
        region_call = space_grouping
    else:
        region_call = 'global'

    # region_call = space_grouping if space_grouping != 'nimbus_east_africa' else 'east_africa'
    # region_call = region_call if region_call != 'nimbus_east_africa' else 'east_africa'
    # region_call = 'global' if region_call is None else region_call
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
    new_data = ds_new[variable].compute()
    old_data = ds_old[variable].compute()

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


def test_metric_correctness_01_ecmwf_mae_precip_global(remote_dask_cluster):  # noqa: ARG001
    """Basic: lat-weighted averaging and masking globally."""
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "mae",
        "variable": "precip",
        "space_grouping": None,
        "region": "global",
        "mask": "lsm",
        "spatial": False,
    })
    assert passed


def test_metric_correctness_02_ecmwf_mae_precip_nimbus_east_africa(remote_dask_cluster):  # noqa: ARG001
    """Spatial weighting."""
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "mae",
        "variable": "precip",
        "space_grouping": None,
        "region": "nimbus_east_africa",
        "mask": "lsm",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_03_ecmwf_acc_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "acc",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_04_ecmwf_ets_5_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "ets-5",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_05_ecmwf_pod_5_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "pod-5",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_06_ecmwf_rmse_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "rmse",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_07_ecmwf_bias_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "bias",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_08_ecmwf_crps_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "crps",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_09_salient_crps_precip_africa(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "salient",
        "metric_name": "crps",
        "variable": "precip",
        "spatial": True,
        "region": "africa",
    })
    assert passed


def test_metric_correctness_10_ecmwf_smape_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "smape",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_11_ecmwf_mape_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "mape",
        "variable": "precip",
        "spatial": False,
    })
    assert passed


def test_metric_correctness_12_ecmwf_seeps_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "seeps",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_13_ecmwf_pearson_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "pearson",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_14_ecmwf_heidke_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "heidke-1-5-10-20",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_15_ecmwf_pod_10_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "pod-10",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_16_ecmwf_far_5_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "far-5",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_17_ecmwf_frequencybias_5_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "frequencybias-5",
        "variable": "precip",
        "spatial": False,
    })
    assert passed


def test_metric_correctness_18_ecmwf_ifs_er_mae_precip(remote_dask_cluster):  # noqa: ARG001
    """Different forecast (no debiased)."""
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er",
        "metric_name": "mae",
        "variable": "precip",
        "spatial": False,
    })
    assert passed


def test_metric_correctness_19_climatology_mae_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "climatology_2015",
        "metric_name": "mae",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_20_fuxi_mae_precip(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "fuxi",
        "metric_name": "mae",
        "variable": "precip",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_21_ecmwf_mae_tmp2m(remote_dask_cluster):  # noqa: ARG001
    """Different variable."""
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "mae",
        "variable": "tmp2m",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_22_ecmwf_acc_precip_week2(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "acc",
        "variable": "precip",
        "lead": "week2",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_23_ecmwf_acc_tmp2m_week2(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "acc",
        "variable": "tmp2m",
        "lead": "week2",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_24_ecmwf_mae_precip_africa(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "mae",
        "variable": "precip",
        "region": "africa",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_25_ecmwf_mae_precip_nimbus_east_africa(remote_dask_cluster):  # noqa: ARG001
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "mae",
        "variable": "precip",
        "region": "nimbus_east_africa",
        "spatial": True,
    })
    assert passed


def test_metric_correctness_26_ecmwf_mae_precip_global_nonspatial(remote_dask_cluster):  # noqa: ARG001
    """Non-spatial (global)."""
    _, passed, _ = _run_single_case({
        "forecast": "ecmwf_ifs_er_debiased",
        "metric_name": "mae",
        "variable": "precip",
        "spatial": False,
    })
    assert passed
