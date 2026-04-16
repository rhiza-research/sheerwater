"""`sheerwater data` — fetch and list data sources from the registry.

Data sources are functions decorated with `@sheerwater_data` (see
`sheerwater.interfaces.datasets`). The CLI is registry-driven so adding a new
data source automatically makes it available here.
"""
from __future__ import annotations

import sys

import click

from ._envelope import write_envelope
from ._errors import cli_run


@click.group()
def data():
    """Fetch and discover data sources (observations, reanalysis, station data)."""


@data.command("list")
@click.option("--json", "as_json", is_flag=True, help="Emit a JSON array instead of newline-separated names.")
def list_data_cmd(as_json: bool) -> None:
    """List all registered data source names."""
    from sheerwater.interfaces import list_data

    names = sorted(list_data())
    if as_json:
        import json as _json

        click.echo(_json.dumps(names))
    else:
        for n in names:
            click.echo(n)


@data.command("fetch")
@click.argument("name")
@click.option("--start", "start_time", help="Start date YYYY-MM-DD (function default if omitted).")
@click.option("--end", "end_time", help="End date YYYY-MM-DD (function default if omitted).")
@click.option("--variable", "-v", help="Variable name (e.g. precip, tmp2m).")
@click.option("--agg-days", type=int, help="Aggregation period in days.")
@click.option("--grid", help="Output grid (e.g. global0_25, global1_5).")
@click.option("--mask", help="Mask name (e.g. lsm) or 'none' to disable.")
@click.option("--region", help="Region name (e.g. global, kenya, ethiopia).")
@click.option("--recompute", is_flag=True, help="Force recompute, bypass cache.")
@click.option("--cache-mode", help="Nuthatch cache mode (e.g. local_overwrite).")
@click.option("--output", "-o", required=True, help="Output Zarr path.")
@cli_run
def fetch_data(
    name: str,
    start_time: str | None,
    end_time: str | None,
    variable: str | None,
    agg_days: int | None,
    grid: str | None,
    mask: str | None,
    region: str | None,
    recompute: bool,
    cache_mode: str | None,
    output: str,
) -> None:
    """Fetch a registered data source and write an envelope-compliant Zarr.

    NAME is one of the registered data source names (see `sheerwater data list`).
    """
    from sheerwater.interfaces import get_data

    try:
        fn = get_data(name)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc))

    kwargs: dict = {}
    if start_time is not None:
        kwargs["start_time"] = start_time
    if end_time is not None:
        kwargs["end_time"] = end_time
    if variable is not None:
        kwargs["variable"] = variable
    if agg_days is not None:
        kwargs["agg_days"] = agg_days
    if grid is not None:
        kwargs["grid"] = grid
    if mask is not None:
        kwargs["mask"] = None if mask.lower() == "none" else mask
    if region is not None:
        kwargs["region"] = region
    if recompute:
        kwargs["recompute"] = True
    if cache_mode is not None:
        kwargs["cache_mode"] = cache_mode

    print(f"Fetching {name} -> {output}", file=sys.stderr)
    ds = fn(**kwargs)

    out = write_envelope(
        ds,
        output,
        source=name,
        region=region,
        date=end_time,
    )
    print(f"Wrote: {out}", file=sys.stderr)
