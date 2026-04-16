"""`sheerwater ops` — spatial and temporal transforms on envelope Zarr stores.

Each op reads a Zarr in, transforms in memory, writes a Zarr out. Stamps
the relevant `rhiza_*` attribute (region / aggregation / downscale_factor)
so downstream skills can see what was applied.
"""
from __future__ import annotations

import sys

import click

from ._envelope import open_envelope, write_envelope


@click.group()
def ops():
    """Spatial and temporal operations on envelope Zarr stores."""


@ops.command("clip")
@click.option("--input", "-i", "input_path", required=True, help="Input Zarr path.")
@click.option("--region", required=True, help="Region name (e.g. kenya, ethiopia, global).")
@click.option("--grid", required=True, help="Grid the region is defined against (e.g. global0_25, global1_5).")
@click.option("--output", "-o", required=True, help="Output Zarr path.")
def clip_cmd(input_path: str, region: str, grid: str, output: str) -> None:
    """Clip a dataset to a named region.

    Backed by `sheerwater.spatial_subdivisions.clip_region`.
    """
    from sheerwater.spatial_subdivisions import clip_region

    print(f"Clipping {input_path} to region={region} grid={grid}", file=sys.stderr)
    ds = open_envelope(input_path)
    ds = clip_region(ds, region=region, grid=grid)

    out = write_envelope(ds, output, region=region)
    print(f"Wrote: {out}", file=sys.stderr)


@ops.command("regrid")
@click.option("--input", "-i", "input_path", required=True, help="Input Zarr path.")
@click.option("--grid", "output_grid", required=True, help="Output grid (e.g. global0_25, global1_5).")
@click.option(
    "--method",
    type=click.Choice(["linear", "nearest", "cubic", "conservative", "most_common"]),
    default="conservative",
    show_default=True,
)
@click.option(
    "--base",
    type=click.Choice(["base180", "base360"]),
    default="base180",
    show_default=True,
    help="Longitude base of the output grid.",
)
@click.option("--region", default="global", show_default=True, help="Region to clip the output grid to.")
@click.option("--output", "-o", required=True, help="Output Zarr path.")
def regrid_cmd(
    input_path: str, output_grid: str, method: str, base: str, region: str, output: str
) -> None:
    """Regrid a dataset to a new grid resolution.

    Backed by `sheerwater.utils.data_utils.regrid`.
    """
    from sheerwater.utils.data_utils import regrid

    print(f"Regridding {input_path} -> grid={output_grid} method={method}", file=sys.stderr)
    ds = open_envelope(input_path)
    ds = regrid(ds, output_grid=output_grid, method=method, base=base, region=region)

    out = write_envelope(ds, output)
    print(f"Wrote: {out}", file=sys.stderr)


@ops.command("aggregate")
@click.option("--input", "-i", "input_path", required=True, help="Input Zarr path.")
@click.option("--agg", required=True, type=int, help="Rolling aggregation window (in units of agg-col).")
@click.option(
    "--agg-col",
    default="time",
    show_default=True,
    help="Coordinate to roll over (typically `time` or `step`).",
)
@click.option(
    "--agg-fn",
    type=click.Choice(["mean", "sum"]),
    default="mean",
    show_default=True,
)
@click.option(
    "--agg-thresh",
    type=int,
    help="Minimum number of valid points required in the window (default: agg).",
)
@click.option("--output", "-o", required=True, help="Output Zarr path.")
def aggregate_cmd(
    input_path: str,
    agg: int,
    agg_col: str,
    agg_fn: str,
    agg_thresh: int | None,
    output: str,
) -> None:
    """Rolling temporal aggregation (mean or sum) over an N-step window.

    Backed by `sheerwater.utils.data_utils.roll_and_agg`. Output windows are
    left-aligned.
    """
    from sheerwater.utils.data_utils import roll_and_agg

    print(
        f"Aggregating {input_path} agg={agg} {agg_col} fn={agg_fn}",
        file=sys.stderr,
    )
    ds = open_envelope(input_path)
    ds = roll_and_agg(ds, agg=agg, agg_col=agg_col, agg_fn=agg_fn, agg_thresh=agg_thresh)

    out = write_envelope(
        ds,
        output,
        aggregation=f"{agg}-{agg_col}-{agg_fn}",
    )
    print(f"Wrote: {out}", file=sys.stderr)
