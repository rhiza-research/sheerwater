---
name: imerg-fetch
description: Fetch GPM IMERG satellite-derived daily precipitation and write a Rhiza Envelope Zarr. Covers the late (near-realtime) and final (research-quality) runs, plus a canonical `imerg` alias. Use when a task needs IMERG rainfall as gridded ground truth.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Public data reads anonymously; GOOGLE_APPLICATION_CREDENTIALS only needed for the private cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# imerg-fetch

GPM IMERG (Integrated Multi-satellitE Retrievals for GPM) is NASA's satellite-derived global precipitation product. Sheerwater serves the daily-aggregated form on a 0.1° native grid (regridded as requested).

## Variants

The CLI accepts these dataset names:

| Name | Underlying product | Latency | Notes |
|---|---|---|---|
| `imerg` | GPM_3IMERGDF | ~3.5 months | Alias for `imerg_final` |
| `imerg_final` | GPM_3IMERGDF | ~3.5 months | Research-quality run, gauge-corrected |
| `imerg_late` | GPM_3IMERGDL | ~half day | Near-realtime, no gauge correction |

Pick `imerg_final` for retrospective verification work; pick `imerg_late` when recency matters and reduced accuracy is acceptable.

## Cache vs live fetch

Every sheerwater fetch first checks the configured nuthatch caches; on a miss it computes from the live source.

For IMERG:
- **Cache hit (typical)**: anonymous, fast. Works without any credentials against the public bucket.
- **Cache miss**: live fetch goes through NASA Earthaccess. Sheerwater pulls EARTHDATA credentials from its own secret manager — which means filling a cache miss requires GCP credentials with read access to sheerwater's secret manager (i.e. `GOOGLE_APPLICATION_CREDENTIALS` set to a service account on the sheerwater project, or `gcloud auth application-default login` as a sheerwater-authorized user). End users do NOT need their own EARTHDATA account.

If you want to verify against a recent date range that may not be cached yet (especially `imerg_late`), expect to need sheerwater GCP credentials.

### Need data fresher than the cache?

This skill always reads from the year-aggregated cache first. For a per-fetch live earthaccess path that bypasses the cache (`recompute=True`, `cache_mode="local_overwrite"` — useful for realtime monitoring of `imerg_late` within the last few days), use the `imerg-fetch-live` skill in the forecasting-skills repo. That skill needs your own EARTHDATA_USERNAME / EARTHDATA_PASSWORD instead of routing through sheerwater's secret manager. Once sheerwater registers the live accessor (TODO in `sheerwater.data.imerg`), this skill will cover both paths and the forecasting-skills version becomes redundant.

## When to use

- A task needs IMERG rainfall as gridded observations.
- Verifying a global or African forecast against a satellite-derived truth.

## Usage

```
uvx sheerwater@latest data fetch <name> \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip] [--agg-days 1] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — only `precip` is supported.
- `--agg-days` — rolling-mean window in days (default 1).
- `--grid` — output grid (default `global0_25`). Native is `global0_1`.

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with `precip` (mm/day), dims `(time, lat, lon)`, stamped with `rhiza_source=<name>`.

## Example

```bash
uvx sheerwater@latest data fetch imerg --start 2024-01-01 --end 2024-03-31 \
    --region ethiopia --output /tmp/imerg_ethiopia.zarr
```
