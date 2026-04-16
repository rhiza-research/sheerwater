---
name: gencast-fetch
description: Fetch DeepMind GenCast AI ensemble forecasts (precipitation only, deterministic mean or probabilistic ensemble) for a date range and write a Rhiza Envelope Zarr.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying data is read from public WeatherNext buckets; set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# gencast-fetch

GenCast is DeepMind's diffusion-based ensemble AI weather model. Sheerwater reads the WeatherNext archive (`gs://weathernext/126478713_1_0/zarr/...`) and concatenates the 2020, 2021, and 2022 init-year archives. Initialisation dates outside that span (including 2023, which exists in the source repo but is NOT included by sheerwater's loader) will produce no data.

The single registered forecast name is `gencast`. Currently only `precip` is implemented; the loader raises on other variables (a known data quality issue with non-precip GenCast variables in the sheerwater cache).

## When to use

- A task needs probabilistic precipitation forecasts (e.g. for CRPS/Brier-type metrics).
- Comparing ensemble AI models against ECMWF ENS or other ensembles.

## Usage

```
uvx sheerwater@latest forecast fetch gencast \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    --variable precip [--agg-days 1] \
    [--prob-type deterministic|probabilistic] \
    [--grid global1_5] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — only `precip` is supported.
- `--agg-days` — rolling-mean window over the lead-time dimension (default 1).
- `--prob-type` — `deterministic` (averages over the ensemble members) or `probabilistic` (keeps all members; output stamped `prob_type=ensemble`).
- `--grid` — `global1_5` is the top-level default; the underlying daily fetch is on `global0_25` and regrids conservatively to other grids.

See `uvx sheerwater@latest forecast fetch --help` for the full flag list.

### Output

Envelope Zarr with `precip`, dims `(init_time, prediction_timedelta, lat, lon)` plus `member` for `--prob-type probabilistic`. Stamped with `rhiza_source=gencast`.

## Example

```bash
uvx sheerwater@latest forecast fetch gencast --start 2021-01-01 --end 2021-03-31 \
    --variable precip --region africa --output /tmp/gencast_africa.zarr
```
