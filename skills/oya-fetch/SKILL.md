---
name: oya-fetch
description: Fetch the Oya global precipitation nowcast product (Google Earth Engine, 30-minute cadence aggregated to daily) for a date range and write a Rhiza Envelope Zarr. Use when a task needs the Oya rainfall product as ground truth.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Oya is sourced from Google Earth Engine (sheerwater initializes EE internally with project='sheerwater'); set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# oya-fetch

Oya is a global precipitation nowcast product served from the Google Earth Engine asset `projects/global-precipitation-nowcast/assets/global_estimation`. The native cadence is 30 minutes; sheerwater aggregates to daily totals (mm).

The single registered dataset name is `oya`.

The loader filters out infinities and daily totals exceeding 1000 mm as bad data.

## Cache vs live fetch

- **Cache hit**: anonymous, fast.
- **Cache miss**: live fetch goes to Google Earth Engine via `ee.Initialize(project='sheerwater', ...)`. This requires Earth Engine access registered against the sheerwater GCP project, which means GCP credentials with that role. End users without sheerwater EE access cannot fill cache misses; they can only read pre-computed aggregations from the public bucket.

## When to use

- A task needs the Oya satellite-derived rainfall product as observations.

## Usage

```
uvx sheerwater@latest data fetch oya \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip] [--agg-days 1] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — required; only `precip` is supported (daily mm).
- `--agg-days` — required; rolling-mean window in days. Pass `--agg-days 1` for daily.
- `--grid` — required; pass `source` to keep the native Earth Engine projection, otherwise a sheerwater grid name (e.g. `global0_25`) for conservative regridding.

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with `precip` (mm/day), dims `(time, lat, lon)`, stamped with `rhiza_source=oya`.

## Example

```bash
uvx sheerwater@latest data fetch oya --start 2024-01-01 --end 2024-03-31 \
    --region africa --output /tmp/oya_africa.zarr
```
