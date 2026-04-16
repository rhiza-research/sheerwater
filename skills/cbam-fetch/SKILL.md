---
name: cbam-fetch
description: Fetch CBAM gridded daily precipitation and 2m temperature for a date range and write a Rhiza Envelope Zarr. Use when a task needs the CBAM dataset as gridded ground truth.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Public CBAM data reads from the sheerwater public bucket anonymously; set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# cbam-fetch

CBAM is served from `gs://sheerwater-datalake/cbam-data/gap/cbam_20241021.zarr`. Sheerwater renames `total_rainfall` to `precip` and derives `tmp2m` as the mean of `min_total_temperature` and `max_total_temperature` from the source.

The single registered dataset name is `cbam`.

## Cache vs live fetch

**There is no public live source for CBAM in sheerwater.** The loader reads directly from `gs://sheerwater-datalake/cbam-data/gap/cbam_20241021.zarr`, which lives in the sheerwater private datalake.

- **Cache hit**: anonymous read from the public bucket if the requested aggregation has been computed and mirrored, works without credentials.
- **Cache miss**: needs read access to the sheerwater private datalake (`gs://sheerwater-datalake/cbam-data/`). Set `GOOGLE_APPLICATION_CREDENTIALS` to a service account with that access, or run `gcloud auth application-default login` as a sheerwater-authorized user.

## When to use

- A task needs the CBAM dataset as observation truth.
- Comparing a forecast against CBAM rainfall or temperature.

## Usage

```
uvx sheerwater@latest data fetch cbam \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip|tmp2m] [--agg-days 1] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — required; `precip` (daily mm) or `tmp2m` (°C; mean of source min/max).
- `--agg-days` — required; rolling-mean window in days. Pass `--agg-days 1` for daily.
- `--grid` — output grid (default `global0_25`); regridded conservatively from the source.

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with the requested variable, dims `(time, lat, lon)`, stamped with `rhiza_source=cbam`.

## Example

```bash
uvx sheerwater@latest data fetch cbam --start 2024-01-01 --end 2024-03-31 \
    --variable precip --region kenya --output /tmp/cbam_kenya.zarr
```
