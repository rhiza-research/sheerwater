"""Sheerwater MCP Server - Main entry point."""

import argparse
import importlib.metadata
import logging
import os
import sys

# Configure all logging to stderr BEFORE importing anything else
# This is critical for MCP stdio transport - stdout must only contain JSON-RPC
logging.basicConfig(
    level=logging.WARNING,
    format="%(name)s %(levelname)s: %(message)s",
    stream=sys.stderr,
)
# Suppress noisy loggers
logging.getLogger("nuthatch").setLevel(logging.ERROR)
logging.getLogger("sheerwater").setLevel(logging.ERROR)
logging.getLogger("fsspec").setLevel(logging.ERROR)
logging.getLogger("gcsfs").setLevel(logging.ERROR)

from pathlib import Path  # noqa: E402, I001

from fastmcp import FastMCP  # noqa: E402
from nuthatch.nuthatch import set_global_cache_variables  # noqa: E402

# CRITICAL: Nuthatch adds its own stdout handler at import time.
# We must remove it to prevent breaking MCP's stdio JSON-RPC protocol.
import nuthatch.nuthatch  # noqa: E402, F401

_nuthatch_logger = logging.getLogger("nuthatch.nuthatch")
_nuthatch_logger.handlers.clear()  # Remove the stdout handler
_nuthatch_logger.addHandler(logging.StreamHandler(sys.stderr))  # Add stderr handler instead
_nuthatch_logger.setLevel(logging.WARNING)  # Reduce verbosity

# Set nuthatch cache mode from environment variable (default: local for computation)
_cache_mode = os.environ.get("NUTHATCH_CACHE_MODE", "local")
set_global_cache_variables(cache_mode=_cache_mode)

from sheerwater.mcp.tools.discovery import (  # noqa: E402
    get_metric_info,
    list_forecasts,
    list_metrics,
    list_truth_datasets,
)
from sheerwater.mcp.tools.evaluation import (  # noqa: E402
    compare_models,
    estimate_query_time,
    extract_truth_data,
    run_metric,
)
from sheerwater.mcp.tools.visualization import (  # noqa: E402
    generate_comparison_chart,
    get_dashboard_link,
    render_plotly,
)

# Create the MCP server
try:
    _version = importlib.metadata.version("sheerwater")
except importlib.metadata.PackageNotFoundError:
    _version = "unknown"

_instructions_path = Path(__file__).parent / "instructions.md"
_instructions = _instructions_path.read_text()

mcp = FastMCP(
    name="sheerwater",
    version=_version,
    instructions=_instructions,
)


# Register discovery tools
@mcp.tool()
async def tool_list_forecasts() -> dict:
    """List available forecast models for benchmarking.

    Returns information about each model including name, description,
    available date range, and supported variables.
    """
    return await list_forecasts()


@mcp.tool()
async def tool_list_metrics() -> dict:
    """List available evaluation metrics.

    Returns information about each metric including name, description,
    interpretation guidance, and which variables/forecast types it's valid for.
    """
    return await list_metrics()


@mcp.tool()
async def tool_list_truth_datasets() -> dict:
    """List available ground truth datasets.

    Returns information about each dataset including name, description,
    coverage, and date range.
    """
    return await list_truth_datasets()


@mcp.tool()
async def tool_get_metric_info(metric_name: str) -> dict:
    """Get detailed explanation of a specific metric.

    Args:
        metric_name: Name of the metric (e.g., 'mae', 'rmse', 'acc', 'seeps')

    Returns:
        Detailed information including formula, interpretation, and usage guidance.
    """
    return await get_metric_info(metric_name)


# Register evaluation tools
@mcp.tool()
async def tool_run_metric(
    forecast: str,
    truth: str,
    metric: str,
    region: str = "global",
    variable: str = "precip",
    start_time: str | None = None,
    end_time: str | None = None,
    agg_days: int = 7,
) -> dict:
    """Run a single evaluation metric comparing forecast to truth.

    Args:
        forecast: Forecast model name (e.g., 'ecmwf_ifs_er', 'fuxi')
        truth: Ground truth dataset name (e.g., 'chirps_v3', 'ghcn')
        metric: Metric name (e.g., 'mae', 'rmse', 'bias', 'acc')
        region: Geographic region (e.g., 'Kenya', 'global', 'East Africa')
        variable: Variable to evaluate (e.g., 'precip', 'tmp2m')
        start_time: Start date (YYYY-MM-DD format)
        end_time: End date (YYYY-MM-DD format)
        agg_days: Aggregation period in days (default: 7)

    Returns:
        Metric value with interpretation, or job_id if computation is queued.
    """
    return await run_metric(
        forecast=forecast,
        truth=truth,
        metric=metric,
        region=region,
        variable=variable,
        start_time=start_time,
        end_time=end_time,
        agg_days=agg_days,
    )


@mcp.tool()
async def tool_compare_models(
    forecasts: list[str],
    truth: str,
    metric: str,
    region: str = "global",
    variable: str = "precip",
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict:
    """Compare multiple forecast models on a metric.

    Args:
        forecasts: List of forecast model names to compare
        truth: Ground truth dataset name
        metric: Metric name for comparison
        region: Geographic region
        variable: Variable to evaluate
        start_time: Start date (YYYY-MM-DD format)
        end_time: End date (YYYY-MM-DD format)

    Returns:
        Ranking of models with scores and interpretation.
    """
    return await compare_models(
        forecasts=forecasts,
        truth=truth,
        metric=metric,
        region=region,
        variable=variable,
        start_time=start_time,
        end_time=end_time,
    )


@mcp.tool()
async def tool_estimate_query_time(
    forecast: str,
    truth: str,
    metric: str,
    region: str = "global",
    variable: str = "precip",
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict:
    """Estimate how long a query will take before running it.

    Args:
        forecast: Forecast model name
        truth: Ground truth dataset name
        metric: Metric name
        region: Geographic region
        variable: Variable to evaluate
        start_time: Start date
        end_time: End date

    Returns:
        Estimated time, whether it's cached, and recommendations.
    """
    return await estimate_query_time(
        forecast=forecast,
        truth=truth,
        metric=metric,
        region=region,
        variable=variable,
        start_time=start_time,
        end_time=end_time,
    )


@mcp.tool()
async def tool_extract_truth_data(
    truth: str,
    variable: str = "precip",
    region: str = "global",
    start_time: str | None = None,
    end_time: str | None = None,
    agg_days: int = 7,
    space_grouping: str = "country",
    time_grouping: str | None = None,
    agg_fn: str = "mean",
) -> dict:
    """Extract raw values from a ground truth dataset, aggregated by region.

    Use this to get actual observed data (e.g., precipitation, temperature) from
    truth datasets like CHIRPS, ERA5, IMERG, etc. Returns values grouped by
    spatial region (country, continent, etc.) and optionally by time period.

    The returned data can be passed directly to render_plotly for visualization.

    Args:
        truth: Ground truth dataset name (e.g., 'chirps_v3', 'era5', 'imerg_final')
        variable: Variable to extract ('precip' or 'tmp2m')
        region: Geographic region ('global', 'Africa', 'East Africa', 'Kenya', etc.)
        start_time: Start date (YYYY-MM-DD format)
        end_time: End date (YYYY-MM-DD format)
        agg_days: Temporal aggregation period in days (default: 7)
        space_grouping: How to group spatially ('country', 'continent', 'subregion')
        time_grouping: How to group in time ('year', 'month_of_year', 'month', or null for period mean)
        agg_fn: Aggregation function ('mean' for averages, 'sum' for totals)

    Returns:
        Data values by region (and time if time_grouping specified), with units.
    """
    return await extract_truth_data(
        truth=truth,
        variable=variable,
        region=region,
        start_time=start_time,
        end_time=end_time,
        agg_days=agg_days,
        space_grouping=space_grouping,
        time_grouping=time_grouping,
        agg_fn=agg_fn,
    )


# Register visualization tools
@mcp.tool()
async def tool_render_plotly(
    figure: dict,
    title: str | None = None,
) -> dict:
    """Render any Plotly figure specification to an interactive chart.

    This gives full flexibility to create any visualization Plotly supports.
    Pass a complete figure specification with 'data' (required) and 'layout' (optional).

    Args:
        figure: Plotly figure spec. Must have 'data' key with list of traces.
                Each trace needs 'type' (e.g., 'bar', 'scatter', 'choropleth').
                See https://plotly.com/python/reference/ for options.
        title: Optional title (merged into layout)

    Returns:
        Chart URL for the rendered interactive visualization.

    Example figures:
        Bar: {"data": [{"type": "bar", "x": ["A", "B"], "y": [1, 2]}]}
        Line: {"data": [{"type": "scatter", "x": [1,2,3], "y": [1,2,1], "mode": "lines"}]}
        Map: {"data": [{"type": "scattergeo", "lon": [0], "lat": [0], "mode": "markers"}]}
        Choropleth: {"data": [{"type": "choropleth", "locations": ["USA"], "z": [1], "locationmode": "country names"}]}
    """
    return await render_plotly(figure=figure, title=title)


@mcp.tool()
async def tool_get_dashboard_link(
    forecast: str | None = None,
    metric: str | None = None,
    region: str | None = None,
    variable: str | None = None,
) -> dict:
    """Get a Grafana dashboard URL for detailed exploration.

    Args:
        forecast: Optional forecast model to pre-select
        metric: Optional metric to pre-select
        region: Optional region to pre-select
        variable: Optional variable to pre-select

    Returns:
        Dashboard URL and description.
    """
    return await get_dashboard_link(
        forecast=forecast,
        metric=metric,
        region=region,
        variable=variable,
    )


@mcp.tool()
async def tool_generate_comparison_chart(
    forecasts: list[str],
    metric: str,
    region: str = "global",
    chart_type: str = "bar",
    truth: str = "chirps_v3",
    variable: str = "precip",
) -> dict:
    """Generate a chart comparing forecast models on a metric.

    Convenience wrapper that fetches data and renders a comparison chart.
    For full flexibility, use compare_models() + render_plotly() separately.

    Args:
        forecasts: List of forecast models to compare
        metric: Metric to visualize (e.g., 'mae', 'rmse', 'acc')
        region: Geographic region
        chart_type: Type of chart ('bar' or 'horizontal_bar')
        truth: Ground truth dataset (default: chirps_v3)
        variable: Variable to evaluate (default: precip)

    Returns:
        Interactive chart URL and summary.
    """
    return await generate_comparison_chart(
        forecasts=forecasts,
        metric=metric,
        region=region,
        chart_type=chart_type,
        truth=truth,
        variable=variable,
    )


def _configure_debug_logging():
    """Enable verbose logging for debugging MCP issues."""
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger("sheerwater.mcp").setLevel(logging.DEBUG)
    logging.getLogger("nuthatch").setLevel(logging.WARNING)
    logging.getLogger("sheerwater").setLevel(logging.INFO)
    # Keep transport-noisy loggers quiet even in debug mode
    logging.getLogger("fsspec").setLevel(logging.WARNING)
    logging.getLogger("gcsfs").setLevel(logging.WARNING)
    print("Sheerwater MCP: debug logging enabled", file=sys.stderr)


def main():
    """Run the MCP server."""
    parser = argparse.ArgumentParser(description="Sheerwater MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport (default: 8000)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging to stderr",
    )
    args = parser.parse_args()

    if args.debug:
        _configure_debug_logging()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="sse", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
