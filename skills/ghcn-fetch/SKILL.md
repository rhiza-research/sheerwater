---
name: ghcn-fetch
description: Fetch NOAA GHCN-Daily station observations gridded onto a regular lat/lon grid, with a choice of one-station-per-cell or per-cell averaging. Use when a task needs station-level historical precipitation or temperature as ground truth.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying data is read anonymously from NOAA's public S3 bucket (s3://noaa-ghcn-pds); set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# ghcn-fetch

The Global Historical Climatology Network – Daily (NOAA GHCN-D) is a long-record source of in-situ daily precipitation and temperature observations worldwide. Sheerwater reads station inventories from the GHCN public S3 bucket, snaps stations to the requested grid, and either keeps one representative station per cell (`first`) or averages all stations in a cell (`avg`).

The underlying loader pulls these GHCN measurement codes: `TMAX`, `TMIN`, `TAVG`, `PRCP`. Sheerwater's exposed variables map onto:

- `precip` — daily total precipitation (mm)
- `tmp2m` (also accepted as `temp`) — daily mean temperature (°C). When `TAVG` is missing, sheerwater computes it as `(TMIN + TMAX) / 2`.

Other temperature variables in the variable map (`tmax2m`, `tmin2m`) are NOT registered for GHCN — pass `tmp2m` for daily mean.

## Variants

The CLI accepts these dataset names:

| Name | Per-cell aggregation |
|---|---|
| `ghcn` | first station only |
| `ghcn_avg` | mean of all stations in the cell |

Pick `ghcn` when you want one consistent station's record per cell. Pick `ghcn_avg` when you want a smoothed cell-level signal that uses every available station.

## Cache vs live fetch

Every sheerwater fetch first checks the configured nuthatch caches; on a miss it computes from the live source.

For GHCN:
- **Cache hit (typical)**: anonymous, fast.
- **Cache miss**: live fetch reads `s3://noaa-ghcn-pds/csv/by_year/{year}.csv` with `storage_options={"anon": True}`. NOAA's S3 bucket is public, so no credentials are needed for the live source either. Long date ranges may be slow.

GHCN is fully self-serve regardless of cache state.

## When to use

- A task needs station-level historical observations gridded for comparison with forecasts or reanalyses.
- Verifying a long-record reanalysis against in-situ measurements.

## Usage

```
uvx sheerwater@latest data fetch <name> \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip|tmp2m] [--agg-days 1] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — `precip` (mm) or `tmp2m` (°C, accepts `temp` as an alias).
- `--agg-days` — rolling-mean window in days (default 1). The loader applies a sufficient-coverage threshold of 90% (`missing_thresh=0.9`) by default.
- `--grid` — output grid (default `global0_25`).

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with the requested variable plus a companion `<variable>_count` (count of valid station-days in each cell). Stamped with `rhiza_source=<name>` and `sparse=True` (most cells have no stations).

## Example

```bash
uvx sheerwater@latest data fetch ghcn --start 1990-01-01 --end 2024-12-31 \
    --variable tmp2m --output /tmp/ghcn_tmp.zarr
```
