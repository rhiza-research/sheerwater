---
name: tahmo-fetch
description: Fetch TAHMO weather-station precipitation observations across Africa, gridded onto a regular lat/lon grid with a choice of one-station-per-cell or per-cell averaging. Use when a task needs African station-level rainfall as ground truth.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying TAHMO station data is pre-cleaned in the sheerwater cache; reads work against the public bucket anonymously, set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# tahmo-fetch

TAHMO (Trans-African Hydro-Meteorological Observatory) operates a network of automatic weather stations across Africa. Sheerwater consumes pre-cleaned TAHMO station files (QC-filtered to `precip_quality_flag > 0.9`) and snaps stations to the requested grid, either keeping one station per cell (`first`) or averaging all stations in a cell (`avg`).

## Cache vs live fetch

**TAHMO is cache-only in sheerwater.** Unlike CHIRPS or IMERG, sheerwater does NOT have a live-fetch path to the TAHMO API. The underlying `tahmo_deployment` and `tahmo_station_cleaned` functions are stubs that raise `RuntimeError("Processing not implemented...")` whenever the cache misses. A separate ingest pipeline (run by sheerwater operators with TAHMO API credentials) populates these caches out-of-band.

Practically:
- **Cache hit**: anonymous read from the public bucket, works without credentials.
- **Cache miss**: the call FAILS. There is no fallback. Either the date range / station ID hasn't been ingested yet, or the cache was rotated.

### Need data not in the sheerwater cache?

Use the `tahmo-fetch-live` skill in the forecasting-skills repo. It calls the TAHMO REST API directly via the tahmo-api SDK and works for any date range, but requires your own TAHMO_API_USERNAME / TAHMO_API_PASSWORD. That skill is the only working live-TAHMO path today. Once sheerwater implements its live TAHMO path (TODO in `sheerwater.data.tahmo`), this skill will cover both cached and fresh fetches and the forecasting-skills version becomes redundant.

## Variants

The CLI accepts these dataset names:

| Name | Per-cell aggregation |
|---|---|
| `tahmo` | first station only |
| `tahmo_avg` | mean of all stations in the cell |

## When to use

- A task needs African in-situ rainfall observations.
- Comparing a gridded product or forecast against station measurements over Africa.

## Usage

```
uvx sheerwater@latest data fetch <name> \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip] [--agg-days 1] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — only `precip` is supported (daily mm).
- `--agg-days` — rolling-mean window in days (default 1).
- `--grid` — output grid (default `global0_25`).

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with `precip` (mm/day) plus a companion `precip_count` (number of valid station-days in each cell). Stamped with `rhiza_source=<name>` and `sparse=True`.

## Example

```bash
uvx sheerwater@latest data fetch tahmo --start 2024-01-01 --end 2024-12-31 \
    --variable precip --output /tmp/tahmo_2024.zarr
```
