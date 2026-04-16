---
name: ecmwf-ifs-fetch
description: Fetch ECMWF IFS extended-range (sub-seasonal) forecast data for a date range and write a Rhiza Envelope Zarr. Covers the raw IFS-ER product and a sheerwater bias-corrected variant. Use when a task needs ECMWF S2S forecasts as a verification baseline.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying data is read from WeatherBench2's public bucket (gs://weatherbench2/datasets/ifs_extended_range); set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# ecmwf-ifs-fetch

ECMWF IFS-ER (Integrated Forecasting System Extended Range) is the operational sub-seasonal global forecast (46-day lead time). Sheerwater serves it from the WeatherBench2 mirror.

## Variants

The CLI accepts these dataset names:

| Name | Bias-corrected? | Notes |
|---|---|---|
| `ecmwf_ifs_er` | no | Raw IFS-ER, ensemble-mean (`--prob-type deterministic`) or all 50 perturbed members (`--prob-type probabilistic`). |
| `ecmwf_ifs_er_debiased` | yes | Reforecast-based bias correction with `margin_in_days=6`, computed against the 20-year reforecast hindcast and ERA5. |

For verification against truth, prefer `ecmwf_ifs_er_debiased`. For the unmodified operational signal, use `ecmwf_ifs_er`.

## When to use

- A task needs ECMWF sub-seasonal forecasts as a baseline.
- Comparing AI weather models (GraphCast, FuXi, GenCast) against the operational physical-model baseline.

## Usage

```
uvx sheerwater@latest forecast fetch <name> \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip|tmp2m|tmax2m|tmin2m|ssrd] [--agg-days 1] \
    [--prob-type deterministic|probabilistic] \
    [--grid global1_5] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — variables with explicit unit handling: `precip` (mm), `tmp2m`/`tmax2m`/`tmin2m` (°C), `ssrd` (J/m²). Other variables in the variable map may pass through but won't get unit conversion.
- `--agg-days` — rolling-mean window over the lead-time dimension (default 1).
- `--prob-type` — `deterministic` (ensemble mean) or `probabilistic` (all 50 perturbed members).
- `--grid` — `global1_5` (native; default). The loader can regrid to coarser grids (`>=1.5°`) but raises on finer grids. Reforecast regridding has a separate "use with care" warning in the source.

See `uvx sheerwater@latest forecast fetch --help` for the full flag list.

### Output

Envelope Zarr with the requested variable, dims `(init_time, prediction_timedelta, lat, lon)` plus `member` for `--prob-type probabilistic`. Stamped with `rhiza_source=<name>` and `prob_type` attribute (`deterministic` or `ensemble`).

## Example

```bash
uvx sheerwater@latest forecast fetch ecmwf_ifs_er --start 2024-01-01 --end 2024-03-31 \
    --variable precip --region kenya --output /tmp/ecmwf_kenya.zarr
```
