"""Shared helpers for writing Rhiza Envelope-compliant Zarr stores.

The envelope is defined in forecasting-skills/ENVELOPE.md. Briefly:
- spatial dims `latitude`/`longitude` (or station_id for station envelopes), CF attrs
- temporal dims `time` (observations) or `step` + scalar `time` (forecasts)
- root attrs prefixed `rhiza_*` for traceability
- per-variable encoding cleared, written with `consolidated=True`
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import xarray as xr


_LAT_NAMES = ("latitude", "lat", "y")
_LON_NAMES = ("longitude", "lon", "x")


def stamp_cf_coords(ds: xr.Dataset) -> xr.Dataset:
    """Stamp CF standard_name/units/axis on spatial and time coords."""
    for name in _LAT_NAMES:
        if name in ds.coords:
            ds[name].attrs.setdefault("standard_name", "latitude")
            ds[name].attrs.setdefault("units", "degrees_north")
            ds[name].attrs.setdefault("axis", "Y")
            break
    for name in _LON_NAMES:
        if name in ds.coords:
            ds[name].attrs.setdefault("standard_name", "longitude")
            ds[name].attrs.setdefault("units", "degrees_east")
            ds[name].attrs.setdefault("axis", "X")
            break
    if "time" in ds.coords:
        ds["time"].attrs.setdefault("standard_name", "time")
        ds["time"].attrs.setdefault("axis", "T")
    return ds


def stamp_root_attrs(ds: xr.Dataset, **rhiza_attrs: Any) -> xr.Dataset:
    """Stamp `rhiza_*` attrs on the dataset root.

    Pass attribute names without the `rhiza_` prefix; e.g. `source="chirps"` becomes
    `rhiza_source="chirps"`. None values are dropped.
    """
    for key, value in rhiza_attrs.items():
        if value is None:
            continue
        ds.attrs[f"rhiza_{key}"] = str(value)
    return ds


def clear_encoding(ds: xr.Dataset) -> xr.Dataset:
    """Clear per-variable encoding (codecs, chunks, dtype, fill_value).

    Required by the envelope: encoding is not part of the contract and codec
    objects are not guaranteed to round-trip across skill boundaries.
    """
    for v in ds.variables:
        ds[v].encoding = {}
    return ds


def write_envelope(
    ds: xr.Dataset,
    output: str | Path,
    *,
    source: str | None = None,
    region: str | None = None,
    date: str | None = None,
    aggregation: str | None = None,
    downscale_factor: int | None = None,
    overwrite: bool = True,
) -> Path:
    """Write a dataset as a Rhiza Envelope-compliant Zarr store.

    Stamps CF coord attrs, the requested `rhiza_*` root attrs, clears per-variable
    encoding, and writes with `consolidated=True`.
    """
    out = Path(output)
    if out.exists():
        if not overwrite:
            raise FileExistsError(out)
        shutil.rmtree(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    ds = stamp_cf_coords(ds)
    ds = stamp_root_attrs(
        ds,
        source=source,
        region=region,
        date=date,
        aggregation=aggregation,
        downscale_factor=downscale_factor,
    )
    ds = clear_encoding(ds)
    ds.to_zarr(out, mode="w", consolidated=True)
    return out


def open_envelope(input_path: str | Path) -> xr.Dataset:
    """Open a Zarr envelope for reading."""
    return xr.open_zarr(str(input_path), consolidated=True, decode_timedelta=True)
