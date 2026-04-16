---
name: salient-fetch
description: Fetch Salient Predictions sub-seasonal to seasonal (S2S) forecasts and write a Rhiza Envelope Zarr. Covers the global Salient blend and the East-Africa-only GEM v2 variant. Use when a task needs S2S/seasonal probabilistic forecasts.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying Salient data is in the sheerwater datalake / Salient-managed object stores; set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# salient-fetch

Salient Predictions is a commercial sub-seasonal to seasonal (S2S) forecast provider focused on weeks-to-months horizons. Sheerwater serves Salient forecasts in two registered forms:

## Variants

The CLI accepts these forecast names:

| Name | Coverage | Default region | Default grid | Probabilistic? | Notes |
|---|---|---|---|---|---|
| `salient` | Global blend | africa | global0_25 | yes (quantile members) | `--agg-days` controls timescale: 7 = sub-seasonal, 30 = seasonal, 90 = long-range. Other agg_days values raise. |
| `salient_gem` | East Africa | eastern_africa | global1_5 | no (deterministic only) | GEM v2 product from `s3://nimbus-gemv2/east_africa.zarr`; loader raises on probabilistic. 126-day forecast horizon. |

## When to use

- A task needs S2S/seasonal forecasts (weeks-to-months lead).
- Comparing sub-seasonal forecast skill across providers.

## Usage

```
uvx sheerwater@latest forecast fetch <name> \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip|tmp2m] [--agg-days 7|30|90] \
    [--prob-type deterministic|probabilistic] \
    [--grid global0_25|global1_5] [--mask lsm] [--region africa] \
    --output <path.zarr>
```

### Key flags

- `--variable` — `precip` and `tmp2m` are the variables Salient supports through sheerwater's variable map.
- `--agg-days` — for `salient`: must be 7 (sub-seasonal weekly leads), 30 (seasonal monthly leads), or 90 (long-range quarterly leads). For `salient_gem`: any window over the 126-day forecast.
- `--prob-type` — `salient` supports `deterministic` (selects the 0.5 quantile) or `probabilistic` (keeps all quantile members; output stamped `prob_type=quantile`). `salient_gem` is deterministic only.
- `--grid` — `salient` defaults to `global0_25`; `salient_gem` defaults to `global1_5`.
- `--region` — `salient` defaults to `africa`; `salient_gem` defaults to `eastern_africa` and is restricted to East Africa by the underlying data.

See `uvx sheerwater@latest forecast fetch --help` for the full flag list.

### Output

Envelope Zarr with the requested variable, dims `(init_time, prediction_timedelta, lat, lon)` plus `member` for probabilistic. Stamped with `rhiza_source=<name>` and `prob_type` attribute (`deterministic` for the median, `quantile` for `salient` probabilistic, `ensemble` for `salient_gem` probabilistic — note `salient_gem` actually raises before reaching the probabilistic path).

## Example

```bash
uvx sheerwater@latest forecast fetch salient --start 2024-01-01 --end 2024-12-31 \
    --variable precip --agg-days 7 --region africa --output /tmp/salient_africa.zarr
```
