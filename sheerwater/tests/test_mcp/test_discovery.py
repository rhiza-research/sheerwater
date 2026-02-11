"""Tests for discovery tools."""

import pytest

from sheerwater.mcp.tools.discovery import (
    get_metric_info,
    list_forecasts,
    list_metrics,
    list_truth_datasets,
)


@pytest.mark.asyncio
async def test_list_forecasts_returns_forecasts():
    """list_forecasts should return a list of available forecasts."""
    result = await list_forecasts()

    assert "forecasts" in result
    assert "count" in result
    assert result["count"] > 0
    assert isinstance(result["forecasts"], list)

    # Each forecast should have required fields
    for forecast in result["forecasts"]:
        assert "name" in forecast
        assert "description" in forecast


@pytest.mark.asyncio
async def test_list_forecasts_includes_ecmwf():
    """list_forecasts should include ECMWF IFS ER model."""
    result = await list_forecasts()
    names = [f["name"] for f in result["forecasts"]]

    assert "ecmwf_ifs_er" in names


@pytest.mark.asyncio
async def test_list_metrics_returns_metrics():
    """list_metrics should return a list of available metrics."""
    result = await list_metrics()

    assert "metrics" in result
    assert "count" in result
    assert result["count"] > 0
    assert isinstance(result["metrics"], list)

    # Each metric should have required fields
    for metric in result["metrics"]:
        assert "name" in metric
        assert "description" in metric


@pytest.mark.asyncio
async def test_list_metrics_includes_common_metrics():
    """list_metrics should include common metrics like MAE, RMSE."""
    result = await list_metrics()
    names = [m["name"] for m in result["metrics"]]

    assert "mae" in names
    assert "rmse" in names
    assert "bias" in names


@pytest.mark.asyncio
async def test_list_truth_datasets_returns_datasets():
    """list_truth_datasets should return a list of available datasets."""
    result = await list_truth_datasets()

    assert "datasets" in result
    assert "count" in result
    assert result["count"] > 0
    assert isinstance(result["datasets"], list)

    # Each dataset should have required fields
    for dataset in result["datasets"]:
        assert "name" in dataset
        assert "description" in dataset


@pytest.mark.asyncio
async def test_list_truth_datasets_includes_chirps():
    """list_truth_datasets should include CHIRPS dataset."""
    result = await list_truth_datasets()
    names = [d["name"] for d in result["datasets"]]

    # Should have some variant of CHIRPS
    chirps_found = any("chirps" in name.lower() for name in names)
    assert chirps_found


@pytest.mark.asyncio
async def test_get_metric_info_known_metric():
    """get_metric_info should return details for known metrics."""
    result = await get_metric_info("mae")

    assert "metric" in result
    assert result["metric"] == "mae"
    assert "description" in result
    assert "interpretation" in result
    assert "example_usage" in result


@pytest.mark.asyncio
async def test_get_metric_info_unknown_metric():
    """get_metric_info should return error for unknown metrics."""
    result = await get_metric_info("not_a_real_metric")

    assert "error" in result
    assert "available_metrics" in result


@pytest.mark.asyncio
async def test_list_metrics_has_categories():
    """list_metrics should include dynamically built categories."""
    result = await list_metrics()

    assert "categories" in result
    categories = result["categories"]

    # Should have all three category types
    assert "continuous" in categories
    assert "categorical" in categories
    assert "probabilistic" in categories

    # Each category should be a non-empty list
    assert isinstance(categories["continuous"], list)
    assert isinstance(categories["categorical"], list)
    assert isinstance(categories["probabilistic"], list)

    # Continuous should have MAE, RMSE, etc.
    assert "mae" in categories["continuous"]
    assert "rmse" in categories["continuous"]

    # Categorical should have threshold-based metrics
    assert "heidke" in categories["categorical"]

    # Probabilistic should have ensemble metrics
    assert "crps" in categories["probabilistic"]


@pytest.mark.asyncio
async def test_list_metrics_categories_derived_from_metadata():
    """list_metrics categories should be derived from metric metadata, not hardcoded."""
    result = await list_metrics()
    categories = result["categories"]
    metrics = result["metrics"]

    # Verify each metric in a category has matching metadata
    for metric in metrics:
        name = metric["name"]
        prob_type = metric.get("prob_type")
        categorical = metric.get("categorical", False)

        if prob_type == "probabilistic":
            assert name in categories["probabilistic"], (
                f"Metric '{name}' with prob_type=probabilistic not in probabilistic category"
            )
        if categorical:
            assert name in categories["categorical"], (
                f"Metric '{name}' with categorical=True not in categorical category"
            )
        if prob_type == "deterministic" and not categorical:
            assert name in categories["continuous"], (
                f"Metric '{name}' (deterministic, non-categorical) not in continuous category"
            )


@pytest.mark.asyncio
async def test_brier_in_multiple_categories():
    """Brier should be in both categorical and probabilistic (binary probabilistic)."""
    result = await list_metrics()
    categories = result["categories"]

    # Brier is for probabilistic forecasts of binary events
    assert "brier" in categories["probabilistic"]
    assert "brier" in categories["categorical"]
