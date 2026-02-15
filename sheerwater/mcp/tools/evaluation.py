"""Evaluation tools for running metrics and comparing models."""

import asyncio
import logging
import os
from typing import Any

import numpy as np
from sheerwater.interfaces import get_data
from sheerwater.masks import spatial_mask
from sheerwater.metrics import metric as sw_metric
from sheerwater.spatial_subdivisions import clip_region, space_grouping_labels
from sheerwater.utils.grouping_utils import groupby_region, groupby_time

logger = logging.getLogger(__name__)

# Cache mode for nuthatch - 'local' allows computation, 'local_api' is read-only
CACHE_MODE = os.environ.get("NUTHATCH_CACHE_MODE", "local")

# Default time range for queries if not specified
DEFAULT_START_TIME = "2020-01-01"
DEFAULT_END_TIME = "2020-12-31"

# Timeout for individual metric computations (seconds)
METRIC_TIMEOUT = int(os.environ.get("SHEERWATER_MCP_TIMEOUT", "300"))


async def _run_metric_with_timeout(timeout: int = METRIC_TIMEOUT, **kwargs) -> Any:
    """Run sw_metric in a thread pool with timeout protection.

    Args:
        timeout: Maximum seconds to wait for the computation.
        **kwargs: Arguments passed to sheerwater.metrics.metric().

    Returns:
        The xarray Dataset result from sw_metric.

    Raises:
        TimeoutError: If computation exceeds the timeout.
    """
    return await asyncio.wait_for(
        asyncio.to_thread(sw_metric, **kwargs),
        timeout=timeout,
    )


# TODO: Move to sheerwater core — general-purpose xarray metric result conversion.
def _convert_result_to_dict(result, metric_name: str) -> dict[str, Any]:
    """Convert xarray Dataset result to a JSON-friendly dict."""
    computed = result.compute()

    # Get the metric data variable
    metric_var = metric_name.lower()
    if metric_var not in computed.data_vars:
        # Try to find the metric in data_vars
        metric_var = list(computed.data_vars)[0]

    # Convert lead times and values
    lead_times = []
    values = []
    for i, lead in enumerate(computed.prediction_timedelta.values):
        lead_days = int(lead / 86400000000000)  # Convert nanoseconds to days
        val = float(computed[metric_var].values[i])
        lead_times.append(f"{lead_days}d")
        values.append(round(val, 3))

    # Calculate summary statistics
    mean_value = float(computed[metric_var].mean())

    return {
        "by_lead_time": dict(zip(lead_times, values)),
        "mean": round(mean_value, 3),
        "min": round(float(computed[metric_var].min()), 3),
        "max": round(float(computed[metric_var].max()), 3),
        "lead_times": lead_times,
    }


async def run_metric(
    forecast: str,
    truth: str,
    metric: str,
    region: str = "global",
    variable: str = "precip",
    start_time: str | None = None,
    end_time: str | None = None,
    agg_days: int = 7,
) -> dict[str, Any]:
    """Run a single evaluation metric.

    Calls sheerwater.metrics.metric() with timeout protection.
    Results are cached by Nuthatch; subsequent calls for the same
    parameters return quickly.

    Args:
        forecast: Forecast model name
        truth: Ground truth dataset name
        metric: Metric name
        region: Geographic region
        variable: Variable to evaluate
        start_time: Start date (YYYY-MM-DD)
        end_time: End date (YYYY-MM-DD)
        agg_days: Aggregation period in days

    Returns:
        Metric result with interpretation, or job info if queued.
    """
    # Use defaults if not specified
    start = start_time or DEFAULT_START_TIME
    end = end_time or DEFAULT_END_TIME

    try:
        # Call the real Sheerwater metric function
        logger.info(f"Running metric {metric} for {forecast} vs {truth} in {region}")
        result = await _run_metric_with_timeout(
            start_time=start,
            end_time=end,
            variable=variable,
            agg_days=agg_days,
            forecast=forecast,
            truth=truth,
            metric_name=metric,
            region=region,
            grid="global1_5",
            cache_mode=CACHE_MODE,
        )

        # Convert xarray result to dict
        result_dict = _convert_result_to_dict(result, metric)
        mean_value = result_dict["mean"]

        return {
            "status": "complete",
            "result": {
                "metric": metric,
                "value": mean_value,
                "values_by_lead": result_dict["by_lead_time"],
                "forecast": forecast,
                "truth": truth,
                "region": region,
                "variable": variable,
                "time_range": {"start": start, "end": end},
                "agg_days": agg_days,
            },
            "interpretation": _interpret_metric(metric, mean_value),
        }

    except TimeoutError:
        logger.warning(f"Metric {metric} for {forecast} timed out after {METRIC_TIMEOUT}s")
        return {
            "status": "error",
            "error": f"Computation timed out after {METRIC_TIMEOUT} seconds",
            "suggestion": "Try a smaller region or shorter time range, or use estimate_query_time() first.",
            "params": {"forecast": forecast, "truth": truth, "metric": metric, "region": region},
        }

    except Exception as e:
        error_msg = str(e)
        logger.exception(f"Error running metric: {error_msg}")

        # Check for common errors and provide helpful messages
        if "Unknown metric" in error_msg:
            from sheerwater.metrics_library import list_metrics

            available = list_metrics()
            return {
                "status": "error",
                "error": f"Unknown metric: {metric}",
                "available_metrics": available,
            }

        if "not found" in error_msg.lower() or "unknown" in error_msg.lower():
            return {
                "status": "error",
                "error": error_msg,
                "suggestion": "Use list_forecasts() or list_truth_datasets() to see available options",
            }

        return {
            "status": "error",
            "error": error_msg,
            "params": {
                "forecast": forecast,
                "truth": truth,
                "metric": metric,
                "region": region,
            },
        }


# TODO: Move core logic (run metric across models + rank) to sheerwater core.
async def compare_models(
    forecasts: list[str],
    truth: str,
    metric: str,
    region: str = "global",
    variable: str = "precip",
    start_time: str | None = None,
    end_time: str | None = None,
    agg_days: int = 7,
) -> dict[str, Any]:
    """Compare multiple forecast models on a metric.

    Args:
        forecasts: List of forecast model names
        truth: Ground truth dataset name
        metric: Metric for comparison
        region: Geographic region
        variable: Variable to evaluate
        start_time: Start date
        end_time: End date
        agg_days: Aggregation period in days

    Returns:
        Ranked list of models with scores.
    """
    start = start_time or DEFAULT_START_TIME
    end = end_time or DEFAULT_END_TIME

    # Run metric for each forecast model
    scores = {}
    errors = []

    for forecast in forecasts:
        try:
            logger.info(f"Comparing {forecast} on {metric}")
            result = await _run_metric_with_timeout(
                start_time=start,
                end_time=end,
                variable=variable,
                agg_days=agg_days,
                forecast=forecast,
                truth=truth,
                metric_name=metric,
                region=region,
                grid="global1_5",
                cache_mode=CACHE_MODE,
            )
            result_dict = _convert_result_to_dict(result, metric)
            scores[forecast] = result_dict["mean"]
        except TimeoutError:
            logger.warning(f"Metric {metric} for {forecast} timed out after {METRIC_TIMEOUT}s")
            errors.append({"forecast": forecast, "error": f"Timed out after {METRIC_TIMEOUT}s"})
        except Exception as e:
            logger.exception(f"Error computing {metric} for {forecast}: {e}")
            errors.append({"forecast": forecast, "error": str(e)})

    if not scores:
        return {
            "status": "error",
            "error": "Failed to compute metric for all models",
            "details": errors,
        }

    # Determine if lower or higher is better
    lower_better_metrics = ["mae", "rmse", "mse", "bias", "seeps", "far", "mape", "smape"]
    lower_is_better = metric.lower() in lower_better_metrics
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=not lower_is_better)

    ranking = [
        {"rank": i + 1, "model": name, "score": round(score, 3)} for i, (name, score) in enumerate(sorted_scores)
    ]

    direction = "lower" if lower_is_better else "higher"
    best_model = ranking[0]["model"]
    best_score = ranking[0]["score"]

    result_data = {
        "status": "complete",
        "result": {
            "metric": metric,
            "truth": truth,
            "region": region,
            "variable": variable,
            "time_range": {"start": start, "end": end},
            "ranking": ranking,
        },
        "interpretation": (
            f"{direction.capitalize()} {metric} is better. {best_model} ranks first with {best_score:.3f}."
        ),
    }

    if errors:
        result_data["warnings"] = errors

    return result_data


async def estimate_query_time(
    forecast: str,
    truth: str,
    metric: str,
    region: str = "global",
    variable: str = "precip",  # noqa: ARG001
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict[str, Any]:
    """Estimate how long a query will take.

    Uses heuristics based on region size, time range, and cache status.

    Args:
        forecast: Forecast model name
        truth: Ground truth dataset name
        metric: Metric name
        region: Geographic region
        variable: Variable (reserved for future use)
        start_time: Start date
        end_time: End date

    Returns:
        Time estimate and recommendations.
    """
    # Region size estimates (grid cells)
    region_sizes = {
        "global": 50000,
        "africa": 15000,
        "east africa": 3000,
        "kenya": 500,
        "tanzania": 800,
        "uganda": 200,
        "ethiopia": 1000,
    }

    region_size = region_sizes.get(region.lower(), 1000)

    # Base estimate: 30 seconds per 10000 grid cells
    base_seconds = 30 * (region_size / 10000)

    # Adjust for time range if specified
    if start_time and end_time:
        # TODO: Parse dates and calculate actual range
        base_seconds *= 1.5  # Assume longer range

    # Check if likely cached
    is_common_query = (
        forecast in ["ecmwf_ifs_er", "fuxi"]
        and truth in ["chirps_v3", "imerg_final"]
        and metric in ["mae", "rmse", "bias"]
        and region.lower() in ["kenya", "east africa"]
    )

    if base_seconds < 60:
        time_estimate = "< 1 minute"
    elif base_seconds < 300:
        time_estimate = "1-5 minutes"
    elif base_seconds < 3600:
        time_estimate = f"~{int(base_seconds / 60)} minutes"
    else:
        time_estimate = f"~{int(base_seconds / 3600)} hours"

    recommendation = None
    if base_seconds > 1800:  # > 30 minutes
        smaller_estimate = int(base_seconds * 500 / region_size / 60)
        recommendation = (
            f"This is a large query. Consider starting with a smaller region "
            f"like 'Kenya' or 'East Africa' first, which would take "
            f"~{smaller_estimate} minutes."
        )

    return {
        "estimated_time": time_estimate,
        "cached": is_common_query,
        "cache_status": "likely cached" if is_common_query else "likely needs computation",
        "query_size": {
            "region_size": region_size,
            "estimated_grid_cells": region_size,
        },
        "recommendation": recommendation,
    }


# TODO: Move to sheerwater core — general-purpose metric interpretation.
def _interpret_metric(metric: str, value: float) -> str:
    """Generate human-readable interpretation of a metric value."""
    metric_lower = metric.lower().split("-")[0]

    # Build interpretation based on metric type
    if metric_lower == "mae":
        return f"MAE of {value:.2f} - lower is better"
    elif metric_lower == "rmse":
        return f"RMSE of {value:.2f} - lower is better"
    elif metric_lower == "bias":
        if value > 0:
            direction = "over-predicting"
        elif value < 0:
            direction = "under-predicting"
        else:
            direction = "unbiased"
        return f"Bias of {value:+.2f} - {direction}"
    elif metric_lower == "acc":
        if value > 0.6:
            skill = "good skill"
        elif value > 0.3:
            skill = "moderate skill"
        else:
            skill = "low skill"
        return f"ACC of {value:.2f} - {skill}"
    elif metric_lower == "seeps":
        if value < 0.5:
            quality = "good"
        elif value < 1.0:
            quality = "moderate"
        else:
            quality = "poor"
        return f"SEEPS of {value:.2f} - {quality} for precipitation"
    else:
        return f"{metric} = {value:.2f}"


async def _fetch_truth_data(
    truth: str,
    variable: str,
    start_time: str,
    end_time: str,
    agg_days: int,
    grid: str,
    region: str,
    space_grouping: str,
    time_grouping: str | None,
    agg_fn: str,
    timeout: int = METRIC_TIMEOUT,
) -> Any:
    """Fetch and aggregate truth data in a thread pool with timeout."""

    def _do_fetch():
        truth_fn = get_data(truth)
        cache_kwargs = {
            "start_time": start_time,
            "end_time": end_time,
            "variable": variable,
            "agg_days": agg_days,
            "grid": grid,
            "mask": "lsm",
            "region": region,
        }
        try:
            ds = truth_fn(**cache_kwargs, memoize=True)
        except TypeError:
            ds = truth_fn(**cache_kwargs)

        # Temporal aggregation
        ds = groupby_time(ds, time_grouping, agg_fn=agg_fn)

        # Spatial aggregation by region
        space_ds = space_grouping_labels(grid=grid, space_grouping=space_grouping)
        mask_ds = spatial_mask("lsm", grid, memoize=True)
        space_ds = clip_region(space_ds, grid=grid, region=region)
        mask_ds = clip_region(mask_ds, grid=grid, region=region)
        ds = groupby_region(ds, space_ds, mask_ds, agg_fn=agg_fn, weighted=(agg_fn == "mean"))

        return ds.compute()

    return await asyncio.wait_for(
        asyncio.to_thread(_do_fetch),
        timeout=timeout,
    )


def _convert_truth_to_dict(ds, variable: str, time_grouping: str | None) -> dict[str, Any]:
    """Convert aggregated truth xarray Dataset to a JSON-friendly dict."""
    var_name = variable
    if var_name not in ds.data_vars:
        var_name = list(ds.data_vars)[0]

    data = ds[var_name]

    if time_grouping and "time" in data.dims:
        # Return {region: {time_label: value}}
        result = {}
        for region in data.region.values:
            region_str = str(region)
            vals = data.sel(region=region)
            result[region_str] = {}
            for t in vals.time.values:
                val = float(vals.sel(time=t).values)
                if not np.isnan(val):
                    result[region_str][str(t)] = round(val, 2)
            if not result[region_str]:
                del result[region_str]
        return result
    else:
        # Return {region: value}
        result = {}
        for region in data.region.values:
            val = float(data.sel(region=region).values)
            if not np.isnan(val):
                result[str(region)] = round(val, 2)
        return result


async def extract_truth_data(
    truth: str,
    variable: str = "precip",
    region: str = "global",
    start_time: str | None = None,
    end_time: str | None = None,
    agg_days: int = 7,
    space_grouping: str = "country",
    time_grouping: str | None = None,
    agg_fn: str = "mean",
) -> dict[str, Any]:
    """Extract raw values from a ground truth dataset, aggregated by region.

    Args:
        truth: Ground truth dataset name (e.g., 'chirps_v3', 'era5')
        variable: Variable to extract (e.g., 'precip', 'tmp2m')
        region: Geographic region to clip to (e.g., 'Africa', 'Kenya', 'global')
        start_time: Start date (YYYY-MM-DD)
        end_time: End date (YYYY-MM-DD)
        agg_days: Temporal aggregation period in days
        space_grouping: Spatial grouping ('country', 'continent', 'subregion', etc.)
        time_grouping: Temporal grouping ('year', 'month_of_year', 'month', None for mean)
        agg_fn: Aggregation function ('mean' or 'sum')

    Returns:
        Data values aggregated by region (and optionally time).
    """
    start = start_time or DEFAULT_START_TIME
    end = end_time or DEFAULT_END_TIME

    try:
        logger.info(f"Extracting {variable} from {truth} for {region} ({space_grouping})")
        ds = await _fetch_truth_data(
            truth=truth,
            variable=variable,
            start_time=start,
            end_time=end,
            agg_days=agg_days,
            grid="global1_5",
            region=region,
            space_grouping=space_grouping,
            time_grouping=time_grouping,
            agg_fn=agg_fn,
        )

        data = _convert_truth_to_dict(ds, variable, time_grouping)

        units = "mm/day" if variable == "precip" else "C" if variable == "tmp2m" else None

        return {
            "status": "complete",
            "result": {
                "truth": truth,
                "variable": variable,
                "region": region,
                "space_grouping": space_grouping,
                "time_grouping": time_grouping,
                "agg_fn": agg_fn,
                "time_range": {"start": start, "end": end},
                "units": units,
                "data": data,
            },
        }

    except TimeoutError:
        logger.warning(f"Truth data extraction timed out after {METRIC_TIMEOUT}s")
        return {
            "status": "error",
            "error": f"Computation timed out after {METRIC_TIMEOUT} seconds",
            "suggestion": "Try a smaller region or shorter time range.",
        }

    except Exception as e:
        error_msg = str(e)
        logger.exception(f"Error extracting truth data: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
        }
