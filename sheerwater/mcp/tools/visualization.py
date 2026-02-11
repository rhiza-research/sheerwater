"""Visualization tools for dashboards and charts."""

import base64
import io
import json
from typing import Any
from urllib.parse import urlencode

from fastmcp.tools.tool import ToolResult
from mcp.types import ImageContent, TextContent

# Grafana dashboard configuration
GRAFANA_BASE_URL = "https://dashboards.rhizaresearch.org"
# TODO: this should be dynamic, and every dashboard should have metadata that explains what it is used for.
DASHBOARDS = {
    "forecast-eval": "ee2jzeymn1o8wf",
    "forecast-eval-maps": "ae39q2k3jv668d",
    "ground-truth": "bf5u4y7w1vv28b",
    "reanalysis": "ce6tgp4j3d9fkf",
}


async def get_dashboard_link(
    forecast: str | None = None,
    metric: str | None = None,
    region: str | None = None,
    variable: str | None = None,
) -> dict[str, Any]:
    """Generate a Grafana dashboard URL with pre-selected filters.

    Args:
        forecast: Optional forecast model to pre-select
        metric: Optional metric to pre-select
        region: Optional region to pre-select
        variable: Optional variable to pre-select

    Returns:
        Dashboard URL and description.
    """
    # Build query parameters for Grafana variables
    params = {}
    if forecast:
        params["var-forecast"] = forecast
    if metric:
        params["var-metric"] = metric
    if region:
        params["var-region"] = region
    if variable:
        params["var-variable"] = variable

    # Choose appropriate dashboard
    dashboard_id = DASHBOARDS["forecast-eval"]

    # Build URL
    base_url = f"{GRAFANA_BASE_URL}/d/{dashboard_id}/forecast-evaluation"
    if params:
        url = f"{base_url}?{urlencode(params)}"
    else:
        url = base_url

    # Generate description
    filters = []
    if forecast:
        filters.append(f"forecast={forecast}")
    if metric:
        filters.append(f"metric={metric}")
    if region:
        filters.append(f"region={region}")
    if variable:
        filters.append(f"variable={variable}")

    description = "Forecast Evaluation Dashboard"
    if filters:
        description += f" (filtered by {', '.join(filters)})"

    return {
        "url": url,
        "description": description,
        "dashboard": "forecast-evaluation",
        "available_dashboards": list(DASHBOARDS.keys()),
    }


async def generate_comparison_chart(
    forecasts: list[str],
    metric: str,
    region: str = "global",
    chart_type: str = "bar",
    truth: str = "chirps_v3",
    variable: str = "precip",
) -> ToolResult | dict[str, Any]:
    """Generate a chart comparing forecast models.

    Args:
        forecasts: List of forecast models to compare
        metric: Metric to visualize
        region: Geographic region
        chart_type: Type of chart ('bar', 'line', 'heatmap')
        truth: Ground truth dataset (default: chirps_v3)
        variable: Variable to evaluate (default: precip)

    Returns:
        Image content and metadata, or error dict.
    """
    # Validate chart_type early to avoid unnecessary computation
    supported_types = ["bar"]
    if chart_type not in supported_types:
        if chart_type == "line":
            return {
                "error": "Line chart not yet implemented for model comparison",
                "suggestion": "Use chart_type='bar' for model comparison, or get_dashboard_link() for time series",
                "supported_types": supported_types,
            }
        return {
            "error": f"Unknown chart type: {chart_type}",
            "supported_types": supported_types,
        }

    try:
        import matplotlib
        import matplotlib.pyplot as plt

        matplotlib.use("Agg")  # Non-interactive backend
    except ImportError:
        return {
            "error": "matplotlib not available",
            "message": "Chart generation requires matplotlib. Use get_dashboard_link() for visualization.",
        }

    # Get actual comparison data from Sheerwater
    from sheerwater.mcp.tools.evaluation import compare_models

    comparison_result = await compare_models(
        forecasts=forecasts,
        truth=truth,
        metric=metric,
        region=region,
        variable=variable,
    )

    if comparison_result.get("status") == "error":
        return {
            "error": "Failed to get comparison data",
            "details": comparison_result.get("error"),
        }

    # Extract scores from ranking
    ranking = comparison_result.get("result", {}).get("ranking", [])
    scores = {item["model"]: item["score"] for item in ranking}

    # Create the chart (bar chart - the only supported type)
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = plt.cm.viridis([i / len(forecasts) for i in range(len(forecasts))])
    bars = ax.bar(list(scores.keys()), list(scores.values()), color=colors)
    ax.set_ylabel(metric.upper())
    ax.set_xlabel("Forecast Model")
    ax.set_title(f"{metric.upper()} Comparison for {region}")

    # Add value labels on bars
    for bar, value in zip(bars, scores.values()):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Add grid and styling
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    # Save to buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
    buffer.seek(0)
    image_bytes = buffer.getvalue()
    plt.close(fig)

    # Determine direction for interpretation
    direction = "lower" if metric.lower() in ["mae", "rmse", "seeps", "far", "crps"] else "higher"
    best_model = min(scores, key=scores.get) if direction == "lower" else max(scores, key=scores.get)

    # Return MCP ImageContent + TextContent via ToolResult
    metadata = {
        "caption": f"{metric.upper()} comparison for {region}. {direction.capitalize()} is better. Best: {best_model}",
        "data": scores,
        "chart_type": chart_type,
    }
    return ToolResult(
        content=[
            ImageContent(
                type="image",
                data=base64.b64encode(image_bytes).decode("utf-8"),
                mimeType="image/png",
            ),
            TextContent(type="text", text=json.dumps(metadata)),
        ],
        structured_content=metadata,
    )
