---
name: fuxi-fetch
description: Fetch FuXi AI weather model forecasts (precipitation or 2m temperature, deterministic ensemble mean or probabilistic ensemble) for a date range and write a Rhiza Envelope Zarr.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying data is downloaded from the FudanFuXi/FuXi-S2S Hugging Face dataset; sheerwater handles the Hugging Face token internally. Set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# fuxi-fetch

FuXi is Fudan University's S2S AI weather model. Sheerwater pulls per-day forecasts from the `FudanFuXi/FuXi-S2S` Hugging Face dataset and serves them on the 1.5° global grid.

The single registered forecast name is `fuxi`.

The raw FuXi files contain `tp, t2m, d2m, sst, ttr, 10u, 10v, msl, tcwv` channels, but only `precip` (mm/day, derived from `tp * 24`) and `tmp2m` (°C, derived from `t2m - 273.15`) get unit conversions in sheerwater's pipeline. Use `--variable precip` or `--variable tmp2m`.

## When to use

- A task needs FuXi forecasts for benchmarking against other AI models or operational baselines.
- Building a multi-model comparison that includes FuXi.

## Usage

```
uvx sheerwater@latest forecast fetch fuxi \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip|tmp2m] [--agg-days 1] \
    [--prob-type deterministic|probabilistic] \
    [--grid global1_5] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — `precip` (mm) or `tmp2m` (°C).
- `--agg-days` — rolling-mean window over the lead-time dimension (default 1).
- `--prob-type` — `deterministic` (averages over the 51 members) or `probabilistic` (keeps all members; output stamped `prob_type=ensemble`).
- `--grid` — only `global1_5` is implemented (the loader raises on other grids).

See `uvx sheerwater@latest forecast fetch --help` for the full flag list.

### Output

Envelope Zarr with the requested variable, dims `(init_time, prediction_timedelta, lat, lon)` plus `member` for `--prob-type probabilistic`. Stamped with `rhiza_source=fuxi`.

## Example

```bash
uvx sheerwater@latest forecast fetch fuxi --start 2024-01-01 --end 2024-03-31 \
    --variable tmp2m --region africa --output /tmp/fuxi_africa.zarr
```
