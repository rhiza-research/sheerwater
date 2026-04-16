---
name: smap-fetch
description: Fetch NASA SMAP soil-moisture observations (L3 passive radiometer or L4 surface+rootzone assimilated) for a date range and write a Rhiza Envelope Zarr. Use when a task needs satellite-derived soil moisture as ground truth or as input to a downstream analysis.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. SMAP data is fetched via NASA Earthaccess (sheerwater holds the credentials internally); set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# smap-fetch

NASA SMAP (Soil Moisture Active Passive) provides global soil-moisture observations on the EASE Grid. Sheerwater serves two products:

## Variants

The CLI accepts these dataset names:

| Name | Underlying product | Notes |
|---|---|---|
| `smap_l3` | SPL3SMP_E | Level-3 enhanced passive retrieval, AM and PM passes averaged. ~1-2 day pass rate per location. |
| `smap_l4` | SPL4SMGP | Level-4 model-assimilated product, includes both `sm_surface` and `sm_rootzone`. |

Pick `smap_l3` when you want direct satellite measurements; pick `smap_l4` for the model-assimilated product with rootzone information.

## Cache vs live fetch

- **Cache hit**: anonymous, fast.
- **Cache miss**: live fetch goes through NASA Earthaccess (same path as IMERG). Sheerwater pulls EARTHDATA credentials from its own secret manager, so filling a cache miss requires GCP credentials with read access to sheerwater's secret manager. End users do NOT need their own EARTHDATA account.

## When to use

- A task needs satellite-derived soil moisture as observations.
- Using soil moisture as predictor or evaluation context for forecasts.

## Usage

```
uvx sheerwater@latest data fetch <name> \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable soil_moisture] [--agg-days 1] \
    [--grid source] \
    --output <path.zarr>
```

### Key flags

- `--variable` — must be `soil_moisture` (the loader raises on anything else). For `smap_l4` this is essentially a sanity check; the actual output contains the underlying L4 variables.
- `--agg-days` — rolling-mean window in days (default 1).
- `--grid` — must be `source` (the EASE Grid). Regridding to standard lat/lon grids is not currently supported (the loader raises if you ask for one).

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr indexed by EASE-Grid `(y, x)` with `lat(y, x)` and `lon(y, x)` 2D coordinates. Variable contents differ by product:

- `smap_l3`: a single `soil_moisture` variable, computed as the mean of the AM and PM passes.
- `smap_l4`: two variables, `sm_surface` and `sm_rootzone` (the L4 product's surface and rootzone fields, both retained).

Stamped with `rhiza_source=<name>`.

## Example

```bash
uvx sheerwater@latest data fetch smap_l3 --start 2024-01-01 --end 2024-03-31 \
    --grid source --output /tmp/smap_l3.zarr
```
