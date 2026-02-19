"""Performance tests for metrics functions.

Run only performance tests: pytest -m performance -v -s
Exclude from default runs: pytest -m "not performance"
Run a specific case with -k: pytest -m performance -v -s -k "1" or -k "mae_global" or -k "acc"

Each test runs three times: (1) cold with full recompute, (2) warm with full recompute,
(3) warm with recompute only on metric (statistic from cache). Results and baseline
comparisons are printed; timings written to metrics_performance_baseline.json.

On subsequent runs, current timings are compared to the baseline and the file is
updated with the latest run.
"""
import json
import time
from pathlib import Path

import pytest

from sheerwater.metrics import metric

pytestmark = pytest.mark.performance


# Baseline file: stores last run timings; new runs compare against it then overwrite.
BASELINE_PATH = Path(__file__).resolve().parent / "metrics_performance_baseline.json"

# Optional upper bound (seconds) per test to catch regressions. Set to None to only record timings.
METRIC_MAX_SECONDS = None
# Fail if current run is more than this many times slower than baseline (e.g. 2.0 = 2x slower).
SLOWDOWN_THRESHOLD = 4.0

# Recompute options: full (statistic + metric), or metric-only (statistic from cache).
METRIC_RECOMPUTE_FULL = ["global_statistic", "metric"]
METRIC_RECOMPUTE_METRIC_ONLY = ["metric"]
METRIC_CACHE_MODE = "overwrite"


def _load_baseline():
    """Load baseline timings from file, or return empty dict."""
    if not BASELINE_PATH.exists():
        return {}
    try:
        return json.loads(BASELINE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_baseline(data):
    """Write baseline timings to file."""
    BASELINE_PATH.write_text(json.dumps(data, indent=2))


def _record_and_compare(test_key, cold_sec, warm_full_sec=None, warm_metric_only_sec=None, warm_memoized_sec=None):
    """Load baseline, print comparison with previous run (if any), fail if >2x slower, then save."""
    baseline = _load_baseline()
    prev = baseline.get(test_key)

    if prev:
        for label, curr, key in [
            ("cold (full recompute)", cold_sec, "cold_sec"),
            ("warm (full recompute)", warm_full_sec, "warm_full_sec"),
            ("warm (metric-only recompute)", warm_metric_only_sec, "warm_metric_only_sec"),
            ("warm (memoized)", warm_memoized_sec, "warm_memoized_sec"),
        ]:
            if curr is None:
                continue
            p = prev.get(key)
            if p is not None and p > 0:
                delta = (curr - p) / p
                print(f"  vs baseline {label}: {curr:.3f}s (was {p:.3f}s, {delta:+.1%})")
                if curr > SLOWDOWN_THRESHOLD * p:
                    raise AssertionError(
                        f"Performance regression: {label} {curr:.3f}s is more than "
                        f"{SLOWDOWN_THRESHOLD}x baseline {p:.3f}s (test_key={test_key})"
                    )
    else:
        print("  (no baseline yet for this test)")

    entry = {"cold_sec": round(cold_sec, 6)}
    if warm_full_sec is not None:
        entry["warm_full_sec"] = round(warm_full_sec, 6)
    if warm_metric_only_sec is not None:
        entry["warm_metric_only_sec"] = round(warm_metric_only_sec, 6)
    if warm_memoized_sec is not None:
        entry["warm_memoized_sec"] = round(warm_memoized_sec, 6)
    baseline[test_key] = entry
    _save_baseline(baseline)


def _print_metric_performance(name, config, result, cold_sec, warm_full_sec=None, warm_metric_only_sec=None,
                              warm_memoized_sec=None, test_key=None):
    """Print performance metrics for cold, warm full recompute, and warm metric-only recompute."""
    print(f"\n--- {name} ---")
    print(f"  config: {config}")
    print(f"  elapsed_sec (cold, full recompute): {cold_sec:.3f}")
    if warm_full_sec is not None:
        print(f"  elapsed_sec (warm, full recompute): {warm_full_sec:.3f}")
        if cold_sec > 0:
            print(f"  speedup cold→warm full: {cold_sec / warm_full_sec:.2f}x")
    if warm_metric_only_sec is not None:
        print(f"  elapsed_sec (warm, metric-only recompute): {warm_metric_only_sec:.3f}")
        if cold_sec > 0:
            print(f"  speedup cold→warm metric-only: {cold_sec / warm_metric_only_sec:.2f}x")
    if warm_memoized_sec is not None:
        print(f"  elapsed_sec (warm, memoized): {warm_memoized_sec:.3f}")
        if warm_memoized_sec > 0:
            print(f"  speedup cold→warm memoized: {cold_sec / warm_memoized_sec:.2f}x")
    if test_key is not None:
        _record_and_compare(
            test_key,
            cold_sec,
            warm_full_sec=warm_full_sec,
            warm_metric_only_sec=warm_metric_only_sec,
            warm_memoized_sec=warm_memoized_sec,
        )
    if result is not None:
        data_vars = list(result.data_vars)
        for v in data_vars[:5]:  # first few variables
            da = result[v]
            print(f"  {v}: shape={da.dims} sizes={dict(da.sizes)}")
        if len(data_vars) > 5:
            print(f"  ... and {len(data_vars) - 5} more data_vars")
    print()


def _metric_kwargs(overrides=None):
    """Default kwargs for metric() used in performance tests (recompute so timings are meaningful)."""
    kwargs = {
        "start_time": "2016-01-01",
        "end_time": "2022-12-31",
        "variable": "precip",
        "agg_days": 7,
        "forecast": "ecmwf_ifs_er_debiased",
        "truth": "era5",
        "metric_name": "mae",
        "time_grouping": None,
        "space_grouping": None,
        "spatial": False,
        "grid": "global1_5",
        "mask": "lsm",
        "region": "global",
        "recompute": METRIC_RECOMPUTE_FULL,
        "cache_mode": METRIC_CACHE_MODE,
    }
    if overrides:
        kwargs.update(overrides)
    return kwargs


def _run_metric_three_ways(kwargs):
    """Run metric() cold full, warm full, warm metric-only.

    Returns (result, cold_sec, warm_full_sec, warm_metric_only_sec).
    """
    kw_full = {**kwargs, "recompute": METRIC_RECOMPUTE_FULL, "cache_mode": METRIC_CACHE_MODE}
    kw_metric_only = {**kwargs, "recompute": METRIC_RECOMPUTE_METRIC_ONLY, "cache_mode": METRIC_CACHE_MODE}

    start = time.perf_counter()
    result = metric(**kwargs)
    cold_sec = time.perf_counter() - start

    start = time.perf_counter()
    result = metric(**kw_full)
    warm_full_sec = time.perf_counter() - start

    start = time.perf_counter()
    result = metric(**kw_metric_only)
    warm_metric_only_sec = time.perf_counter() - start

    return result, cold_sec, warm_full_sec, warm_metric_only_sec


def _assert_metric_result(result, cold_sec, expected_var=None, test_label=""):
    """Common asserts: result not None, optional expected_var in result, optional METRIC_MAX_SECONDS."""
    assert result is not None
    if expected_var is not None:
        assert expected_var in result
    if METRIC_MAX_SECONDS is not None:
        assert cold_sec <= METRIC_MAX_SECONDS, (
            f"{test_label} took {cold_sec:.2f}s, max allowed {METRIC_MAX_SECONDS}s"
        )


def _expected_var(metric_name):
    """Result variable name for metric_name (e.g. 'ets-5' -> 'ets')."""
    return metric_name.split("-")[0] if "-" in metric_name else metric_name


# (overrides for _metric_kwargs, baseline test_key). Id and display derived from index + test_key.
PERFORMANCE_TEST_CASES = [
    ({}, "metric_mae_global"),
    ({"spatial": True, "region": "nimbus_east_africa"}, "metric_mae_spatial_region"),
    ({"metric_name": "seeps", "variable": "precip"}, "metric_seeps_precip"),
    ({"metric_name": "heidke-1-5-10-20", "variable": "precip"}, "metric_heidke-1-5-10-20_precip"),
    ({"metric_name": "acc", "variable": "precip"}, "metric_acc_precip"),
    ({"time_grouping": None}, "metric_time_grouping_None"),
    ({"time_grouping": "month"}, "metric_time_grouping_month"),
    ({"time_grouping": "year"}, "metric_time_grouping_year"),
    ({"space_grouping": None}, "metric_space_grouping_None"),
    ({"space_grouping": "country"}, "metric_space_grouping_country"),
]


def _perf_case_id(i, test_key):
    """-k-friendly id: number + test_key with hyphens as underscores."""
    return f"{i + 1}_{test_key.replace('-', '_')}"


@pytest.mark.parametrize(
    "overrides, test_key",
    PERFORMANCE_TEST_CASES,
    ids=[_perf_case_id(i, tk) for i, (_, tk) in enumerate(PERFORMANCE_TEST_CASES)],
)
def test_metric_performance(remote_dask_cluster, overrides, test_key):  # noqa: ARG001
    """Time metric(): cold full, warm full, warm metric-only recompute. One parametrized test per case."""
    kwargs = _metric_kwargs(overrides)
    result, cold_sec, warm_full_sec, warm_metric_only_sec = _run_metric_three_ways(kwargs)
    metric_name = overrides.get("metric_name", "mae")
    expected_var = _expected_var(metric_name)
    config_str = ", ".join(f"{k}={v}" for k, v in sorted(overrides.items())) if overrides else "default"

    _print_metric_performance(
        test_key,
        config_str,
        result,
        cold_sec=cold_sec,
        warm_full_sec=warm_full_sec,
        warm_metric_only_sec=warm_metric_only_sec,
        test_key=test_key,
    )
    _assert_metric_result(result, cold_sec, expected_var=expected_var, test_label=test_key)
