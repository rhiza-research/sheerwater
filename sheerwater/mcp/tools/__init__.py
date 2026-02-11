"""MCP tools for Sheerwater benchmarking."""

from .discovery import (
    get_metric_info,
    list_forecasts,
    list_metrics,
    list_truth_datasets,
)
from .evaluation import (
    compare_models,
    estimate_query_time,
    run_metric,
)
from .visualization import (
    generate_comparison_chart,
    get_dashboard_link,
)

__all__ = [
    # Discovery
    "list_forecasts",
    "list_metrics",
    "list_truth_datasets",
    "get_metric_info",
    # Evaluation
    "run_metric",
    "compare_models",
    "estimate_query_time",
    # Visualization
    "get_dashboard_link",
    "generate_comparison_chart",
]
