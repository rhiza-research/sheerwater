---
name: stations-fetch
description: Fetch a unified station-observation dataset that merges GHCN, TAHMO, and KNUST into a single per-cell averaged grid, weighting each source by station count per cell. Use when a task needs the most complete station-derived ground truth available across Africa and globally.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying station data is read from public bucket; set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# stations-fetch

`stations` is sheerwater's unified station-observation accessor. Behavior depends on the grid:

- For a regular grid (e.g. `--grid global0_25`): pulls per-cell averages from `ghcn_avg`, `tahmo_avg`, and `knust_avg`, then combines them in a station-count-weighted average per (time, lat, lon) cell. Cells with more contributing stations dominate, but cells covered by only one source still get values.
- For `--grid source`: concatenates the raw per-station observations from `ghcn`, `tahmo`, and `knust` along the `station_id` dimension (no weighting; just the union).

The single registered dataset name is `stations`.

This is generally the right pick if you want "the best station-derived ground truth available for this place" without having to choose between GHCN, TAHMO, or KNUST. If you need to know which source contributed, fetch them individually instead.

## When to use

- A task needs broad station-derived ground truth and you don't care which network the value came from.
- Verifying a forecast against in-situ data with the widest station coverage available.

## Usage

```
uvx sheerwater@latest data fetch stations \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip|tmp2m|temp] [--agg-days 1] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — `precip` (all three sources support it). Temperature variables are only contributed by GHCN among the three sources, so `--variable tmp2m`/`temp` will reflect GHCN coverage only.
- `--agg-days` — rolling-mean window in days (default 1).
- `--grid` — output grid (default `global0_25`).

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with the requested variable plus a companion `<variable>_count`. Stamped with `rhiza_source=stations` and `sparse=True`.

## Example

```bash
uvx sheerwater@latest data fetch stations --start 2024-01-01 --end 2024-12-31 \
    --variable precip --region africa --output /tmp/stations_africa.zarr
```
