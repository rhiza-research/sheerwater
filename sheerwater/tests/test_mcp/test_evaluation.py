"""Tests for evaluation tools.

These tests use real Sheerwater calls with small regions that are cached
for fast execution.
"""

import pytest

from sheerwater.mcp.tools.evaluation import (
    compare_models,
    estimate_query_time,
    extract_truth_data,
    run_metric,
)

# Use Kenya and short time ranges for fast cached queries
TEST_REGION = "Kenya"
TEST_START = "2020-01-01"
TEST_END = "2020-03-31"


@pytest.mark.asyncio
async def test_run_metric_returns_result():
    """run_metric should return metric values."""
    result = await run_metric(
        forecast="ecmwf_ifs_er",
        truth="chirps_v3",
        metric="mae",
        region=TEST_REGION,
        start_time=TEST_START,
        end_time=TEST_END,
    )

    assert result["status"] == "complete"
    assert "result" in result
    assert "value" in result["result"]
    assert "interpretation" in result


@pytest.mark.asyncio
async def test_run_metric_includes_lead_times():
    """run_metric should include values by lead time."""
    result = await run_metric(
        forecast="ecmwf_ifs_er",
        truth="chirps_v3",
        metric="mae",
        region=TEST_REGION,
        start_time=TEST_START,
        end_time=TEST_END,
    )

    assert result["status"] == "complete"
    assert "values_by_lead" in result["result"]
    lead_values = result["result"]["values_by_lead"]
    assert len(lead_values) > 0
    # Should have multiple lead times
    assert "0d" in lead_values or "1d" in lead_values


@pytest.mark.asyncio
async def test_run_metric_invalid_metric():
    """run_metric should handle invalid metric names gracefully."""
    result = await run_metric(
        forecast="ecmwf_ifs_er",
        truth="chirps_v3",
        metric="not_a_real_metric",
        region=TEST_REGION,
        start_time=TEST_START,
        end_time=TEST_END,
    )

    assert result["status"] == "error"
    assert "error" in result


@pytest.mark.asyncio
async def test_compare_models_returns_ranking():
    """compare_models should return ranked list of models."""
    result = await compare_models(
        forecasts=["ecmwf_ifs_er", "fuxi"],
        truth="chirps_v3",
        metric="mae",
        region=TEST_REGION,
        start_time=TEST_START,
        end_time=TEST_END,
    )

    assert result["status"] == "complete"
    assert "result" in result
    assert "ranking" in result["result"]

    ranking = result["result"]["ranking"]
    assert len(ranking) == 2

    # Rankings should be ordered 1, 2
    assert ranking[0]["rank"] == 1
    assert ranking[1]["rank"] == 2

    # Each should have model name and score
    for r in ranking:
        assert "model" in r
        assert "score" in r


@pytest.mark.asyncio
async def test_compare_models_lower_is_better_for_mae():
    """compare_models should rank lower MAE first."""
    result = await compare_models(
        forecasts=["ecmwf_ifs_er", "fuxi"],
        truth="chirps_v3",
        metric="mae",
        region=TEST_REGION,
        start_time=TEST_START,
        end_time=TEST_END,
    )

    assert result["status"] == "complete"
    ranking = result["result"]["ranking"]

    # First place should have lower score than second
    assert ranking[0]["score"] <= ranking[1]["score"]


@pytest.mark.asyncio
async def test_estimate_query_time_small_region():
    """estimate_query_time should give fast estimate for small regions."""
    result = await estimate_query_time(
        forecast="ecmwf_ifs_er",
        truth="chirps_v3",
        metric="mae",
        region=TEST_REGION,
    )

    assert "estimated_time" in result
    assert "cached" in result
    # Kenya is a common query and should be marked as likely cached
    assert result["cached"] is True or "minute" in result["estimated_time"].lower()


@pytest.mark.asyncio
async def test_estimate_query_time_large_region():
    """estimate_query_time should give longer estimate for large regions."""
    result = await estimate_query_time(
        forecast="ecmwf_ifs_er",
        truth="chirps_v3",
        metric="mae",
        region="global",
    )

    assert "estimated_time" in result
    # Global region should have a longer estimate
    assert "hour" in result["estimated_time"].lower() or "minute" in result["estimated_time"].lower()


@pytest.mark.asyncio
async def test_extract_truth_data_returns_countries():
    """extract_truth_data should return data grouped by country."""
    result = await extract_truth_data(
        truth="chirps_v3",
        variable="precip",
        region=TEST_REGION,
        start_time=TEST_START,
        end_time=TEST_END,
        space_grouping="country",
    )

    assert result["status"] == "complete"
    assert "result" in result
    assert "data" in result["result"]
    data = result["result"]["data"]
    assert len(data) > 0
    # Values should be numeric
    for value in data.values():
        assert isinstance(value, (int, float))


@pytest.mark.asyncio
async def test_extract_truth_data_with_time_grouping():
    """extract_truth_data with time_grouping should return nested data."""
    result = await extract_truth_data(
        truth="chirps_v3",
        variable="precip",
        region=TEST_REGION,
        start_time=TEST_START,
        end_time=TEST_END,
        space_grouping="country",
        time_grouping="month_of_year",
    )

    assert result["status"] == "complete"
    data = result["result"]["data"]
    assert len(data) > 0
    # With time grouping, values should be dicts of {time_label: value}
    for region_data in data.values():
        assert isinstance(region_data, dict)
        for value in region_data.values():
            assert isinstance(value, (int, float))


@pytest.mark.asyncio
async def test_extract_truth_data_includes_metadata():
    """extract_truth_data should include metadata in result."""
    result = await extract_truth_data(
        truth="chirps_v3",
        variable="precip",
        region=TEST_REGION,
        start_time=TEST_START,
        end_time=TEST_END,
    )

    assert result["status"] == "complete"
    r = result["result"]
    assert r["truth"] == "chirps_v3"
    assert r["variable"] == "precip"
    assert r["region"] == TEST_REGION
    assert r["units"] == "mm/day"
    assert "time_range" in r


@pytest.mark.asyncio
async def test_extract_truth_data_invalid_dataset():
    """extract_truth_data should handle invalid dataset names."""
    result = await extract_truth_data(
        truth="not_a_real_dataset",
        variable="precip",
        region=TEST_REGION,
        start_time=TEST_START,
        end_time=TEST_END,
    )

    assert result["status"] == "error"
    assert "error" in result
