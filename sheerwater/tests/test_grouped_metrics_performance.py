"""Performance tests for grouped metrics with different space and time groupings."""
import time

import pytest

from sheerwater.metrics import metric
from sheerwater.utils import plot_by_region, start_remote


@pytest.fixture(scope="module")
def setup_remote():
    """Set up remote cluster for tests."""
    start_remote(remote_config='large_cluster')


@pytest.mark.parametrize("region", ["global", "country", "continent", "subregion"])
@pytest.mark.parametrize("time_grouping", [None, "month_of_year", "year", "quarter_of_year"])
def test_grouped_metrics_performance(setup_remote, region, time_grouping):  # noqa: ARG001
    """Test performance of grouped metrics with different space and time groupings."""
    start_time = "2016-01-01"
    end_time = "2022-12-31"
    variable = "precip"
    agg_days = 7
    forecast = "ecmwf_ifs_er_debiased"
    truth = "era5"
    metric_name = "heidke-1-5-10-20"
    grid = "global0_25"
    mask = "lsm"

    start = time.time()
    result = metric(
        start_time=start_time,
        end_time=end_time,
        variable=variable,
        agg_days=agg_days,
        forecast=forecast,
        truth=truth,
        metric_name=metric_name,
        time_grouping=time_grouping,
        spatial=False,
        grid=grid,
        mask=mask,
        region=region,
        recompute=False
    )
    elapsed = time.time() - start

    assert result is not None, f"Metric computation failed for region={region}, time_grouping={time_grouping}"

    print(f"Region: {region}, Time grouping: {time_grouping}, Time: {elapsed:.2f}s")


def test_grouped_metrics_performance_summary():
    """Run a comprehensive performance test and print summary."""
    start_time = "2016-01-01"
    end_time = "2022-12-31"
    variable = "precip"
    agg_days = 7
    forecast = "imerg"
    truth = "ghcn"
    metric_name = "mae"
    grid = "global0_25"
    mask = "lsm"

    regions = ["global", "global", "country", "continent", "subregion"]
    time_groupings = [None, "month_of_year", "year", "month"]

    results = []
    for region in regions:
        for time_grouping in time_groupings:
            start = time.time()
            result = metric(
                start_time=start_time,
                end_time=end_time,
                variable=variable,
                agg_days=agg_days,
                forecast=forecast,
                truth=truth,
                metric_name=metric_name,
                time_grouping=time_grouping,
                spatial=False,
                grid=grid,
                mask=mask,
                region=region,
                recompute=True,
                force_overwrite=True
            )
            elapsed = time.time() - start

            results.append({
                "region": region,
                "time_grouping": time_grouping,
                "elapsed": elapsed,
                "success": result is not None
            })

            print(
                f"Region: {region:15s} | Time grouping: {str(time_grouping):20s} | "
                f"Time: {elapsed:6.2f}s | Success: {result is not None}")

    print("\nPerformance Summary:")
    print("=" * 80)
    for r in results:
        print(f"{r['region']:15s} | {str(r['time_grouping']):20s} | {r['elapsed']:6.2f}s | {r['success']}")

    all_success = all(r["success"] for r in results)
    assert all_success, "Some metric computations failed"

    avg_time = sum(r["elapsed"] for r in results) / len(results)
    max_time = max(r["elapsed"] for r in results)
    min_time = min(r["elapsed"] for r in results)

    print(f"\nAverage time: {avg_time:.2f}s")
    print(f"Min time: {min_time:.2f}s")
    print(f"Max time: {max_time:.2f}s")


def test_grouped_metrics_performance_comprehensive():
    """Run a comprehensive performance test and print summary."""
    start_time = "2016-01-01"
    end_time = "2022-12-31"
    variable = "precip"
    agg_days = 7
    forecast = "imerg"
    truth = "ghcn_avg"
    # metric_name = "heidke-1-5-10-20"
    metric_name = "far-1"
    # metric_name = "mae"
    grid = "global1_5"
    mask = "lsm"
    region = "country"
    # region = "countr"
    # time_grouping = "month"
    time_grouping = None

    results = []
    for i in range(1):
        start = time.time()
        result = metric(
            start_time=start_time,
            end_time=end_time,
            variable=variable,
            agg_days=agg_days,
            forecast=forecast,
            truth=truth,
            metric_name=metric_name,
            time_grouping=time_grouping,
            spatial=False,
            grid=grid,
            mask=mask,
            region=region,
            # recompute=['metric'],
            recompute=False,
            force_overwrite=True
        )
        elapsed = time.time() - start

        plot_by_region(result, region, metric_name=metric_name)

        results.append({
            "region": region,
            "time_grouping": time_grouping,
            "elapsed": elapsed,
            "success": result is not None
        })

        print(
            f"Iteration {i}: Region: {region:15s} | Time grouping: {str(time_grouping):20s} | "
            f"Time: {elapsed:6.2f}s | Success: {result is not None}")

    print("\nPerformance Summary:")
    print("=" * 80)
    for r in results:
        print(f"{r['region']:15s} | {str(r['time_grouping']):20s} | {r['elapsed']:6.2f}s | {r['success']}")

    all_success = all(r["success"] for r in results)
    assert all_success, "Some metric computations failed"

    avg_time = sum(r["elapsed"] for r in results) / len(results)
    max_time = max(r["elapsed"] for r in results)
    min_time = min(r["elapsed"] for r in results)

    print(f"\nAverage time: {avg_time:.2f}s")
    print(f"Min time: {min_time:.2f}s")
    print(f"Max time: {max_time:.2f}s")


if __name__ == "__main__":
    # start_remote(remote_config=['xxxlarge_node', 'single_cluster'], remote_name='single_cluster_test')
    # test_grouped_metrics_performance_summary()
    start_remote(remote_config='xlarge_cluster', remote_name='nuthatch_genevieve')
    test_grouped_metrics_performance()
