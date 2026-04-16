"""`sheerwater eval` — compute forecast verification metrics.

Backed by `sheerwater.metrics.metric`. Default output is JSON for scalar / table
results; pass `--zarr-output` (and use `--spatial`) to emit gridded residuals as
an envelope-compliant Zarr.
"""
from __future__ import annotations

import json
import sys

import click

from ._envelope import write_envelope
from ._errors import cli_run


def _ds_to_json_value(ds) -> dict:
    """Reduce an xarray Dataset to a JSON-serialisable dict.

    Scalars become floats; gridded results are summarised as the per-variable
    mean (with a note) rather than dumping arrays into JSON.
    """
    out: dict = {}
    for var in ds.data_vars:
        arr = ds[var]
        if arr.size == 1:
            out[var] = float(arr.values)
        elif arr.ndim == 0 or all(d == 1 for d in arr.shape):
            out[var] = float(arr.values.flatten()[0])
        else:
            # Reduce to a per-coord mapping if the result is small (e.g. per region).
            try:
                out[var] = arr.to_pandas().to_dict()
            except Exception:
                out[var] = {
                    "_note": "result has structure; use --zarr-output for full data",
                    "mean": float(arr.mean().values),
                    "shape": list(arr.shape),
                    "dims": list(arr.dims),
                }
    return out


@click.group("eval")
def eval_():
    """Forecast verification metrics."""


@eval_.command("metric")
@click.option("--forecast", required=True, help="Forecast model name (see `sheerwater forecast list`).")
@click.option("--truth", required=True, help="Truth dataset name (see `sheerwater data list`).")
@click.option("--metric", "metric_name", required=True, help="Metric name (see `sheerwater list metrics`).")
@click.option("--start", "start_time", required=True, help="Start date YYYY-MM-DD.")
@click.option("--end", "end_time", required=True, help="End date YYYY-MM-DD.")
@click.option("--variable", "-v", default="precip", show_default=True)
@click.option("--agg-days", type=int, default=1, show_default=True)
@click.option("--grid", default="global1_5", show_default=True)
@click.option("--mask", default="lsm", show_default=True, help="Use 'none' to disable masking.")
@click.option("--region", default="global", show_default=True)
@click.option("--time-grouping", help="Time grouping (e.g. month, year, month_of_year).")
@click.option("--space-grouping", help="Space grouping (e.g. country, region).")
@click.option("--spatial", is_flag=True, help="Return gridded result instead of grouped scalar.")
@click.option("--output", "-o", help="JSON output path (default: stdout).")
@click.option("--zarr-output", help="Zarr output path for gridded result (implies --spatial).")
@cli_run
def metric_cmd(
    forecast: str,
    truth: str,
    metric_name: str,
    start_time: str,
    end_time: str,
    variable: str,
    agg_days: int,
    grid: str,
    mask: str,
    region: str,
    time_grouping: str | None,
    space_grouping: str | None,
    spatial: bool,
    output: str | None,
    zarr_output: str | None,
) -> None:
    """Compute a single verification metric for a forecast vs a truth source."""
    from sheerwater.metrics import metric

    if zarr_output:
        spatial = True

    mask_arg = None if mask.lower() == "none" else mask

    print(
        f"Computing {metric_name}({forecast}, {truth}) {start_time}..{end_time} "
        f"region={region} grid={grid}",
        file=sys.stderr,
    )
    ds = metric(
        start_time=start_time,
        end_time=end_time,
        variable=variable,
        forecast=forecast,
        truth=truth,
        metric_name=metric_name,
        agg_days=agg_days,
        time_grouping=time_grouping,
        space_grouping=space_grouping,
        spatial=spatial,
        grid=grid,
        mask=mask_arg,
        region=region,
    )

    if zarr_output:
        out = write_envelope(
            ds,
            zarr_output,
            source=f"eval:{metric_name}({forecast},{truth})",
            region=region,
        )
        print(f"Wrote gridded result: {out}", file=sys.stderr)
    else:
        result = {
            "forecast": forecast,
            "truth": truth,
            "metric": metric_name,
            "variable": variable,
            "agg_days": agg_days,
            "grid": grid,
            "region": region,
            "start_time": start_time,
            "end_time": end_time,
            "values": _ds_to_json_value(ds),
        }
        text = json.dumps(result, indent=2, default=str)
        if output:
            with open(output, "w") as f:
                f.write(text)
                f.write("\n")
            print(f"Wrote: {output}", file=sys.stderr)
        else:
            click.echo(text)


@eval_.command("compare")
@click.option(
    "--forecasts",
    required=True,
    help="Comma-separated forecast names.",
)
@click.option("--truth", required=True, help="Truth dataset name.")
@click.option(
    "--metrics",
    required=True,
    help="Comma-separated metric names.",
)
@click.option("--start", "start_time", required=True, help="Start date YYYY-MM-DD.")
@click.option("--end", "end_time", required=True, help="End date YYYY-MM-DD.")
@click.option("--variable", "-v", default="precip", show_default=True)
@click.option("--agg-days", type=int, default=1, show_default=True)
@click.option("--grid", default="global1_5", show_default=True)
@click.option("--mask", default="lsm", show_default=True, help="Use 'none' to disable masking.")
@click.option("--region", default="global", show_default=True)
@click.option("--output", "-o", help="JSON output path (default: stdout).")
@cli_run
def compare_cmd(
    forecasts: str,
    truth: str,
    metrics: str,
    start_time: str,
    end_time: str,
    variable: str,
    agg_days: int,
    grid: str,
    mask: str,
    region: str,
    output: str | None,
) -> None:
    """Compute a matrix of metrics for multiple forecasts against one truth source."""
    from sheerwater.metrics import metric

    forecast_names = [f.strip() for f in forecasts.split(",") if f.strip()]
    metric_names = [m.strip() for m in metrics.split(",") if m.strip()]
    mask_arg = None if mask.lower() == "none" else mask

    matrix: dict[str, dict] = {}
    for fcst in forecast_names:
        matrix[fcst] = {}
        for met in metric_names:
            print(f"  {met}({fcst}, {truth})", file=sys.stderr)
            ds = metric(
                start_time=start_time,
                end_time=end_time,
                variable=variable,
                forecast=fcst,
                truth=truth,
                metric_name=met,
                agg_days=agg_days,
                grid=grid,
                mask=mask_arg,
                region=region,
            )
            matrix[fcst][met] = _ds_to_json_value(ds)

    result = {
        "truth": truth,
        "variable": variable,
        "agg_days": agg_days,
        "grid": grid,
        "region": region,
        "start_time": start_time,
        "end_time": end_time,
        "matrix": matrix,
    }
    text = json.dumps(result, indent=2, default=str)
    if output:
        with open(output, "w") as f:
            f.write(text)
            f.write("\n")
        print(f"Wrote: {output}", file=sys.stderr)
    else:
        click.echo(text)
