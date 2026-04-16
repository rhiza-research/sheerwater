---
name: rain-over-africa-fetch
description: Fetch the Rain Over Africa (rainoverafrica.ai) daily precipitation product, derived from MSG geostationary satellite imagery, for a date range and write a Rhiza Envelope Zarr. Use when a task needs the ROA Africa rainfall product as ground truth.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying ROA data is in the sheerwater datalake; set GOOGLE_APPLICATION_CREDENTIALS for private access.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# rain-over-africa-fetch

Rain Over Africa (ROA) is a satellite-derived daily rainfall product over Africa, produced from MSG geostationary observations at 15-minute cadence and aggregated to daily totals. See [rainoverafrica.ai](https://rainoverafrica.ai/).

The single registered dataset name is `rain_over_africa`.

The loader treats any day where the spatial-max precip exceeds 350 mm/day as bad — that whole day is set to NaN across the grid (per the source comment, the threshold catches a class of corrupted values).

## Cache vs live fetch

**There is no public live source for ROA in sheerwater.** The loader reads per-day MSG files directly from `gs://sheerwater-datalake/rain_over_africa/`, the sheerwater private datalake.

- **Cache hit**: anonymous read from the public bucket if the requested aggregation has been computed and mirrored, works without credentials.
- **Cache miss**: needs read access to the sheerwater private datalake. Set `GOOGLE_APPLICATION_CREDENTIALS` to a service account with that access.

## When to use

- A task needs an African satellite-derived rainfall product as observations.
- Comparing forecasts and other rainfall products against a continent-specific truth.

## Usage

```
uvx sheerwater@latest data fetch rain_over_africa \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip] [--agg-days 1] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — only `precip` is supported (daily mm).
- `--agg-days` — rolling-mean window in days (default 1).
- `--grid` — output grid (default `global0_25`); regridded conservatively from the source.

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with `precip` (mm/day), dims `(time, lat, lon)`, stamped with `rhiza_source=rain_over_africa`. The underlying source also produces `max_probability_precip` per day; only `precip` is exposed by the standard fetch.

## Example

```bash
uvx sheerwater@latest data fetch rain_over_africa --start 2024-01-01 --end 2024-03-31 \
    --region africa --output /tmp/roa_africa.zarr
```
