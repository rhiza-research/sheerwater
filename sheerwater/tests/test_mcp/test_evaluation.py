"""Tests for evaluation tools.

These tests use real Sheerwater calls with small regions that are cached
for fast execution.
"""

import pytest

from sheerwater.mcp.tools.evaluation import (
    compare_models,
    estimate_query_time,
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
