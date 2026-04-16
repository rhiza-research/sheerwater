---
name: era5-fetch
description: Fetch ECMWF ERA5 reanalysis (precipitation, 2m temperature, radiation, humidity, ...) and write a Rhiza Envelope Zarr. Covers the global ARCO ERA5 product and the higher-resolution ERA5-Land. Use when a task needs the long-record reanalysis as gridded ground truth or a verification baseline.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. ERA5 reads from Google ARCO (gs://gcp-public-data-arco-era5) anonymously; ERA5-Land reads from Earth Data Hub via a sheerwater-managed token. GOOGLE_APPLICATION_CREDENTIALS is only needed for the sheerwater private cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# era5-fetch

ERA5 is ECMWF's flagship global reanalysis (hourly from 1940 onward). Sheerwater serves daily-aggregated ERA5 from the Google ARCO mirror, plus the higher-resolution land-only ERA5-Land variant from Earth Data Hub.

## Variants

The CLI accepts these dataset names:

| Name | Source | Native grid | Coverage |
|---|---|---|---|
| `era5` | Google ARCO ERA5 | 0.25° | Global, full atmospheric column |
| `era5_land` | Earth Data Hub ERA5-Land | 0.1° | Land-only, finer detail |

`era5_daily` and `era5_cds` exist in the codebase but are internal helpers, not registered for fetching.

Pick `era5` for global comparisons or non-land variables. Pick `era5_land` when the question is land-focused and 0.1° detail matters; note `era5_land` cannot be regridded finer than 0.1°.

## Cache vs live fetch

For `era5`:
- **Cache hit**: anonymous, fast.
- **Cache miss**: live fetch reads from `gs://gcp-public-data-arco-era5/...` (Google ARCO public mirror). No credentials needed for the live source. Fully self-serve.

For `era5_land`:
- **Cache hit**: anonymous, fast.
- **Cache miss**: live fetch goes to Earth Data Hub (`data.earthdatahub.destine.eu`) using a token sheerwater pulls from its own secret manager. Filling a cache miss requires GCP credentials with read access to sheerwater's secret manager. End users do not need their own Earth Data Hub token.

## When to use

- A task needs long-record gridded reanalysis truth.
- Establishing a verification baseline against a forecast.

## Usage

```
uvx sheerwater@latest data fetch <name> \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip|tmp2m|tmax2m|tmin2m|rh2m|ssrd|tcwv] [--agg-days 1] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — for `era5`: `precip` (mm), `tmp2m` (mean), `tmax2m`, `tmin2m` (all °C), `rh2m` (%, derived from `d2m` + `tmp2m` via Magnus formula), `ssrd` (J/m², downward solar radiation), `tcwv` (kg/m², column water vapour). For `era5_land`: `precip`, `tmp2m`, `tmax2m`, `tmin2m`, `ssrd` only (no `rh2m`, no `tcwv`). Other variables raise. **For `era5_land`, --variable and --agg-days are required (no function-level defaults).**
- `--agg-days` — rolling-mean window in days (default 1 for `era5`; required for `era5_land`).
- `--grid` — output grid. ERA5 cannot regrid finer than 0.25°; ERA5-Land cannot regrid finer than 0.1°.

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with the requested variable, dims `(time, lat, lon)`, stamped with `rhiza_source=<name>`.

## Example

```bash
uvx sheerwater@latest data fetch era5 --start 2024-01-01 --end 2024-03-31 \
    --variable precip --region kenya --output /tmp/era5_kenya.zarr
```
