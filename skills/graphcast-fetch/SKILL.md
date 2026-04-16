---
name: graphcast-fetch
description: Fetch DeepMind GraphCast AI weather model forecasts (precipitation or 2m temperature, deterministic only) for a date range and write a Rhiza Envelope Zarr. Use when a task needs GraphCast as a baseline AI model for verification.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying data is read from public WeatherBench2 buckets; set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# graphcast-fetch

GraphCast is DeepMind's graph-neural-network medium-range global weather model. Sheerwater serves it from the WeatherBench2 mirror (`gs://weatherbench2/datasets/graphcast/`). The underlying source covers initialisation dates in the range 2017-11-16 through 2021-02-01.

The single registered forecast name is `graphcast`. Only deterministic forecasts are implemented (the loader raises on `--prob-type probabilistic`).

## When to use

- A task needs GraphCast as a baseline AI model.
- Building a multi-model verification that includes GraphCast.

## Usage

```
uvx sheerwater@latest forecast fetch graphcast \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip|tmp2m] [--agg-days 1] \
    [--prob-type deterministic] \
    [--grid global0_25|global1_5] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — only `precip` (mm) or `tmp2m` (°C). Other variables raise.
- `--agg-days` — rolling-mean window over the lead-time dimension (default 1).
- `--prob-type` — must be `deterministic`.
- `--grid` — `global0_25` (native) or `global1_5` (regridded conservatively at the source). Other grids raise.

See `uvx sheerwater@latest forecast fetch --help` for the full flag list.

### Output

Envelope Zarr with the requested variable, dims `(init_time, prediction_timedelta, lat, lon)`. Stamped with `rhiza_source=graphcast` and `prob_type=deterministic`.

## Example

```bash
uvx sheerwater@latest forecast fetch graphcast --start 2020-01-01 --end 2020-12-31 \
    --variable precip --region kenya --output /tmp/graphcast_kenya.zarr
```
