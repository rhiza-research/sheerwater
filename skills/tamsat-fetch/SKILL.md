---
name: tamsat-fetch
description: Fetch TAMSAT African daily rainfall (Rainfall Estimate v3.1) for a date range and write a Rhiza Envelope Zarr. Use when a task needs the TAMSAT African rainfall product as ground truth.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying TAMSAT data is read from the JASMIN public archive; set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# tamsat-fetch

TAMSAT (Tropical Applications of Meteorology using SATellite data) is a long-record African daily rainfall dataset. Sheerwater serves the v3.1 RFE (Rainfall Estimate) product from the JASMIN public archive (`gws-access.jasmin.ac.uk/public/tamsat/rfe/data_degraded/v3.1/daily/0.25/rfe1983-present_daily_0.25.v3.1.nc`).

The single registered dataset name is `tamsat`. Coverage starts in 1983.

## Cache vs live fetch

- **Cache hit**: anonymous, fast.
- **Cache miss**: live fetch reads the v3.1 NetCDF directly from JASMIN's public HTTP archive. No credentials needed for the live source either. Fully self-serve.

## When to use

- A task needs Africa-specific gridded rainfall as observations.
- Comparing African forecasts against a region-tuned truth dataset.

## Usage

```
uvx sheerwater@latest data fetch tamsat \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip] [--agg-days 1] \
    [--grid global0_25|tamsat] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — only `precip` is supported (daily mm).
- `--agg-days` — rolling-mean window in days (default 1).
- `--grid` — output grid (default `global0_25`). Native source is 0.25°; the loader rejects grids smaller than 0.25°. Pass `--grid tamsat` to keep the native form.

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with `precip` (mm/day), dims `(time, lat, lon)`, stamped with `rhiza_source=tamsat`.

## Example

```bash
uvx sheerwater@latest data fetch tamsat --start 2024-01-01 --end 2024-03-31 \
    --region ghana --output /tmp/tamsat_ghana.zarr
```
