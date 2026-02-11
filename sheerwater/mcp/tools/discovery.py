"""Discovery tools for listing available forecasts, metrics, and datasets."""

from typing import Any

from sheerwater.interfaces import list_data as sw_list_data
from sheerwater.interfaces import list_forecasts as sw_list_forecasts
from sheerwater.metrics_library import list_metrics as sw_list_metrics


async def list_forecasts() -> dict[str, Any]:
    """List available forecast models.

    Returns information about each model from Sheerwater's forecast registry.
    """
    forecasts = sw_list_forecasts()
    return {
        "forecasts": sorted(forecasts, key=lambda x: x["name"]),
        "count": len(forecasts),
    }


async def list_metrics() -> dict[str, Any]:
    """List available evaluation metrics.

    Returns information about each metric including interpretation guidance.
    """
    metrics = sw_list_metrics()

    # TODO: Move metric categorization to sheerwater core (metrics_library).
    # Build categories dynamically from metric attributes
    # Note: metrics can belong to multiple categories
    categories: dict[str, list[str]] = {
        "continuous": [],
        "categorical": [],
        "probabilistic": [],
    }
    for m in metrics:
        name = m["name"]
        # Probabilistic metrics (for ensemble/probabilistic forecasts)
        if m.get("prob_type") == "probabilistic":
            categories["probabilistic"].append(name)
        # Categorical metrics (for threshold-based evaluation)
        if m.get("categorical", False):
            categories["categorical"].append(name)
        # Continuous metrics (deterministic, non-categorical)
        if m.get("prob_type") == "deterministic" and not m.get("categorical", False):
            categories["continuous"].append(name)

    return {
        "metrics": sorted(metrics, key=lambda x: x["name"]),
        "count": len(metrics),
        "categories": categories,
    }


async def list_truth_datasets() -> dict[str, Any]:
    """List available ground truth datasets.

    Returns information about each dataset including coverage and resolution.
    """
    datasets = sw_list_data()
    return {
        "datasets": sorted(datasets, key=lambda x: x["name"]),
        "count": len(datasets),
    }


async def get_metric_info(metric_name: str) -> dict[str, Any]:
    """Get detailed information about a specific metric.

    Args:
        metric_name: Name of the metric (case-insensitive)

    Returns:
        Detailed metric information including formula and usage guidance.
    """
    metric_key = metric_name.lower().split("-")[0]  # Handle variants like 'heidke-1-5-10'

    metrics = sw_list_metrics()
    metrics_by_name = {m["name"]: m for m in metrics}

    if metric_key not in metrics_by_name:
        available = ", ".join(metrics_by_name.keys())
        return {
            "error": f"Unknown metric: {metric_name}",
            "available_metrics": available,
        }

    info = metrics_by_name[metric_key]
    return {
        "metric": metric_key,
        **info,
        "example_usage": (
            f"run_metric(forecast='ecmwf_ifs_er', truth='chirps_v3', metric='{metric_key}', region='Kenya')"
        ),
    }
