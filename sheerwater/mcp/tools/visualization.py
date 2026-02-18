"""Visualization tools for dashboards and charts.

This module provides flexible visualization capabilities:

- render_plotly: Render ANY valid Plotly figure specification (full flexibility)
- generate_comparison_chart: Convenience wrapper for model metric comparisons
- get_dashboard_link: Link to Grafana dashboards

The LLM has full Plotly flexibility via render_plotly - it can construct
any chart, map, or visualization that Plotly supports.
"""

import json
import logging
from typing import Any
from urllib.parse import urlencode

from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

from .chart_storage import upload_chart

logger = logging.getLogger(__name__)

# Grafana dashboard configuration
GRAFANA_BASE_URL = "https://dashboards.rhizaresearch.org"
# TODO: this should be dynamic, and every dashboard should have metadata that explains what it is used for.
DASHBOARDS = {
    "forecast-eval": "ee2jzeymn1o8wf",
    "forecast-eval-maps": "ae39q2k3jv668d",
    "ground-truth": "bf5u4y7w1vv28b",
    "reanalysis": "ce6tgp4j3d9fkf",
}


def _create_tool_result(png_url: str, html_url: str, text_summary: str, metadata: dict | None = None) -> ToolResult:
    """Create a standardized ToolResult with chart URLs and summary."""
    # Return both URLs - clients pick what they can handle
    # PNG is default (works everywhere), HTML is for interactive clients
    chart_urls_content = json.dumps({"png_url": png_url, "html_url": html_url})
    return ToolResult(
        content=[
            TextContent(type="text", text=chart_urls_content),
            TextContent(type="text", text=text_summary),
        ],
        structured_content={
            "png_url": png_url,
            "html_url": html_url,
            "caption": text_summary,
            **(metadata or {}),
        },
    )


async def render_plotly(
    figure: dict,
    title: str | None = None,
) -> ToolResult | dict[str, Any]:
    """Render any Plotly figure specification to an interactive chart.

    This is the low-level primitive that gives full Plotly flexibility.
    Pass a complete Plotly figure specification as a dict.

    IMPORTANT: This server runs Plotly v6. Use the Plotly v6 API only.
    Key v6 changes: colorbar.titleside is removed (use colorbar.title.side),
    colorbar.titlefont is removed (use colorbar.title.font).

    Args:
        figure: A Plotly figure specification dict with 'data' and optionally 'layout'.
                Example: {"data": [{"type": "bar", "x": ["A", "B"], "y": [1, 2]}]}
                See https://plotly.com/python/reference/ for full specification.
        title: Optional title (will be merged into layout if provided)

    Returns:
        ToolResult with chart URL, or error dict.

    Examples:
        # Simple bar chart
        {"data": [{"type": "bar", "x": ["A", "B", "C"], "y": [1, 3, 2]}]}

        # Scatter plot
        {"data": [{"type": "scatter", "x": [1, 2, 3], "y": [4, 1, 2], "mode": "markers"}]}

        # Line chart with layout
        {
            "data": [{"type": "scatter", "x": [1, 2, 3], "y": [4, 1, 2], "mode": "lines"}],
            "layout": {"title": "My Chart", "xaxis": {"title": "X"}, "yaxis": {"title": "Y"}}
        }

        # Choropleth map
        {
            "data": [{
                "type": "choropleth",
                "locations": ["USA", "CAN", "MEX"],
                "z": [1, 2, 3],
                "locationmode": "country names"
            }]
        }

        # Geo scatter
        {
            "data": [{
                "type": "scattergeo",
                "lon": [0, 10, 20],
                "lat": [0, 10, 20],
                "mode": "markers",
                "marker": {"size": 10}
            }]
        }
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        return {"error": "plotly not available"}

    if not figure:
        return {"error": "figure specification is required"}

    if "data" not in figure:
        return {"error": "figure must contain 'data' key with trace specifications"}

    try:
        # Create figure from specification
        # skip_invalid=True handles deprecated properties (e.g. colorbar.titleside)
        # that LLMs may generate from older training data
        fig = go.Figure(figure, skip_invalid=True)

        # Merge title into layout if provided
        if title:
            fig.update_layout(title=title)

        # Apply default template if not specified
        if "template" not in figure.get("layout", {}):
            fig.update_layout(template="plotly_white")

    except Exception as e:
        logger.exception("Failed to create Plotly figure")
        return {"error": "Invalid Plotly figure specification", "details": str(e)}

    # Upload to GCS (both PNG and HTML)
    try:
        chart_urls = upload_chart(fig)
    except Exception as e:
        logger.exception("Failed to upload chart to GCS")
        return {"error": "Failed to upload chart", "details": str(e)}

    # Build summary
    trace_types = [t.get("type", "unknown") for t in figure.get("data", [])]
    text_summary = f"Rendered Plotly figure with {len(trace_types)} trace(s): {', '.join(trace_types)}."
    if title:
        text_summary = f"{title}. {text_summary}"

    return _create_tool_result(
        png_url=chart_urls.png_url,
        html_url=chart_urls.html_url,
        text_summary=text_summary,
    )


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
    """Generate a chart comparing forecast models on a metric.

    This is a convenience wrapper that fetches comparison data and renders it.
    For full flexibility, use compare_models() to get data, then render_plotly().

    Args:
        forecasts: List of forecast models to compare
        metric: Metric to visualize (e.g., 'mae', 'rmse', 'acc')
        region: Geographic region
        chart_type: Type of chart ('bar', 'horizontal_bar')
        truth: Ground truth dataset (default: chirps_v3)
        variable: Variable to evaluate (default: precip)

    Returns:
        ToolResult with chart URL and text summary, or error dict.
    """
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

    if not scores:
        return {
            "error": "No valid comparison data available",
            "message": "All models failed to compute metrics.",
            "details": comparison_result.get("result", {}).get("errors", []),
        }

    # Determine sort direction
    lower_is_better = metric.lower() in ["mae", "rmse", "seeps", "far", "crps", "bias"]
    items = sorted(scores.items(), key=lambda x: x[1], reverse=not lower_is_better)
    labels = [item[0] for item in items]
    values = [item[1] for item in items]

    # Build Plotly figure spec
    if chart_type == "horizontal_bar":
        figure = {
            "data": [{
                "type": "bar",
                "y": labels,
                "x": values,
                "orientation": "h",
                "text": [f"{v:.2f}" for v in values],
                "textposition": "outside",
            }],
            "layout": {
                "title": f"{metric.upper()} Comparison for {region}",
                "yaxis": {"title": "Forecast Model"},
                "xaxis": {"title": metric.upper()},
            },
        }
    else:
        figure = {
            "data": [{
                "type": "bar",
                "x": labels,
                "y": values,
                "text": [f"{v:.2f}" for v in values],
                "textposition": "outside",
            }],
            "layout": {
                "title": f"{metric.upper()} Comparison for {region}",
                "xaxis": {"title": "Forecast Model"},
                "yaxis": {"title": metric.upper()},
            },
        }

    result = await render_plotly(figure)

    if isinstance(result, dict) and "error" in result:
        return result

    # Enhance summary
    direction = "lower" if lower_is_better else "higher"
    best_model = labels[0]
    scores_summary = ", ".join(f"{m}: {s:.2f}" for m, s in items)

    enhanced_summary = (
        f"{metric.upper()} comparison for {region}: {scores_summary}. "
        f"{direction.capitalize()} is better. Best: {best_model}."
    )

    if isinstance(result, ToolResult):
        return ToolResult(
            content=[
                result.content[0],
                TextContent(type="text", text=enhanced_summary),
            ],
            structured_content={
                **result.structured_content,
                "metric": metric,
                "best_model": best_model,
                "direction": direction,
                "data": scores,
            },
        )

    return result
