"""Sheerwater MCP Server - Main entry point."""

import argparse
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

from fastmcp import FastMCP  # noqa: E402, I001
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
    run_metric,
)
from sheerwater.mcp.tools.visualization import (  # noqa: E402
    generate_comparison_chart,
    get_dashboard_link,
)

# Create the MCP server
mcp = FastMCP(
    name="sheerwater",
    instructions="""
    You are an assistant that helps meteorologists and forecasters evaluate and compare
    weather forecast models. You have access to the Sheerwater benchmarking platform.

    ## Available Capabilities

    1. **Discovery**: List available forecasts, metrics, and ground truth datasets
    2. **Evaluation**: Run metrics to compare forecasts against ground truth
    3. **Visualization**: Generate charts or link to Grafana dashboards

    ## Workflow Guidance

    When a user asks "which model is best?":
    1. First clarify: for what region, variable, and time period?
    2. Use `list_forecasts` to show available models
    3. Use `compare_models` to rank them on relevant metrics
    4. Explain results with metric interpretations

    For long-running queries (>1 minute):
    - Use `estimate_query_time` first to warn the user
    - Consider using a smaller region (e.g., 'Kenya' instead of 'global')

    ## Metric Guidance

    - **MAE/RMSE**: Lower is better. Good for overall accuracy.
    - **Bias**: Closer to 0 is better. Shows systematic over/under-prediction.
    - **ACC**: Higher is better (-1 to 1). Shows anomaly correlation skill.
    - **SEEPS**: Lower is better. Specifically designed for precipitation.
    - **Heidke/ETS**: Higher is better. Categorical skill scores.
    """,
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


# Register visualization tools
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
    """Generate a chart comparing models.

    Args:
        forecasts: List of forecast models to include
        metric: Metric to visualize
        region: Geographic region
        chart_type: Type of chart ('bar')
        truth: Ground truth dataset (default: chirps_v3)
        variable: Variable to evaluate (default: precip)

    Returns:
        Base64-encoded image and caption.
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
