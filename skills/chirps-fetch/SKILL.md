---
name: chirps-fetch
description: Fetch CHIRPS / CHIRP gridded precipitation observations from the Climate Hazards Center (UCSB) and write a Rhiza Envelope Zarr. Covers 5 dataset variants (CHIRPS v2/v3 with stations blended, CHIRP v2/v3 satellite-only, plus the canonical `chirps` alias). Use when a task needs CHIRPS rainfall as gridded ground truth.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Public CHIRPS data is read from the sheerwater public bucket anonymously; set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# chirps-fetch

CHIRPS (Climate Hazards Center InfraRed Precipitation with Stations) is a quasi-global rainfall dataset combining satellite IR and station gauges, widely used as gridded precipitation truth in Africa. CHIRP (no S) is the satellite-only version of the same family.

## Variants

The CLI accepts these dataset names:

| Name | Stations blended? | Version | Notes |
|---|---|---|---|
| `chirps` | yes | v3 | Alias for `chirps_v3` — the canonical pick |
| `chirps_v3` | yes | v3 | Latest with-stations product. Valid from year 2000 onward |
| `chirps_v2` | yes | v2 | Older with-stations product, longer historical record |
| `chirp_v3` | no | v3 | Satellite-only v3. Valid from year 2000 onward |
| `chirp_v2` | no | v2 | Satellite-only v2 |

If you don't have a reason to pick a specific variant, use `chirps`.

## Cache vs live fetch

Every sheerwater fetch first checks the configured nuthatch caches (your local cache, the sheerwater datalake, and any configured mirrors including the public bucket). If a hit is found, the data comes from there. On a miss, sheerwater computes the result by hitting the live source.

For CHIRPS:
- **Cache hit (typical)**: anonymous, fast. Works without any credentials.
- **Cache miss**: live fetch goes directly to UCSB's public HTTPS endpoint (`data.chc.ucsb.edu/products/CHIRPS/...` or `CHIRP/...`). No credentials needed for the live source either, but the network round-trips can be slow for long date ranges.

So CHIRPS is fully self-serve regardless of cache state.

### Need the current calendar year prelim file?

This skill does NOT currently expose the CHIRPS v3 prelim file (`chirps_raw_live` in sheerwater) — only finalized historical CHIRPS. For prelim data within the current calendar year, use the `chirps-fetch-live` skill in the forecasting-skills repo. Once sheerwater registers the live accessor (TODO in `sheerwater.data.chirps`), this skill will cover both paths and the forecasting-skills version becomes redundant.

## When to use

- A task needs CHIRPS rainfall as gridded observations.
- A downstream skill will clip, aggregate, regrid, or compare CHIRPS against another source.

## Usage

```
uvx sheerwater@latest data fetch <name> \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip] [--agg-days 5] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--start`, `--end` — inclusive date range. CHIRPS v3 variants only support dates from 2000 onward.
- `--variable` — only `precip` is supported by CHIRPS / CHIRP.
- `--agg-days` — rolling-mean window in days (default 5 for CHIRPS).
- `--grid` — output grid (default `global0_25`). Native grid is `chirps` (~0.05° irregular); the underlying loader regrids onto your chosen grid using conservative regridding.
- `--region` — named sheerwater region (default `global`).

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with `precip` (mm/day), dims `(time, lat, lon)`, stamped with `rhiza_source=<name>`.

## Example

```bash
uvx sheerwater@latest data fetch chirps \
    --start 2024-01-01 --end 2024-03-31 \
    --region kenya --output /tmp/chirps_kenya.zarr
```
