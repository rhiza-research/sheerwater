---
name: knust-fetch
description: Fetch KNUST West-African rain-gauge station observations (Ashanti, DACCIWA, FuriFlood/Kumasi networks combined) gridded onto a regular lat/lon grid, with a choice of one-station-per-cell or per-cell averaging. Use when a task needs West-African in-situ rainfall as ground truth.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Underlying KNUST data lives at gs://sheerwater-datalake/knust_stations/; set GOOGLE_APPLICATION_CREDENTIALS only if accessing the private cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# knust-fetch

KNUST is a combined rain-gauge dataset assembled by Kwame Nkrumah University of Science and Technology (Ghana), built from three station collections:

- Ashanti Region network (Ghana)
- DACCIWA project rain gauges (West Africa multi-country research network)
- FuriFlood Kumasi rain gauges (Ghana)

Sheerwater merges them, snaps stations to the requested grid, and either keeps one representative station per cell (`first`) or averages all stations in a cell (`avg`).

## Cache vs live fetch

**There is no live API for KNUST.** The underlying loaders read NetCDF files directly from `gs://sheerwater-datalake/knust_stations/` (Ashanti, DACCIWA, FuriFlood subdirectories). Coverage is whatever those files contain.

- **Cache hit**: anonymous read from the public bucket if the result has been computed and mirrored, works without credentials.
- **Cache miss**: the loader needs read access to `gs://sheerwater-datalake/knust_stations/` to ingest the source files. If that path isn't readable for your GCP identity (it's the private datalake), the call will fail.

In practice this means cached aggregates work for everyone; first-time computations on un-cached date ranges need sheerwater GCP credentials.

## Variants

The CLI accepts these dataset names:

| Name | Per-cell aggregation |
|---|---|
| `knust` | first station only |
| `knust_avg` | mean of all stations in the cell |

## When to use

- A task needs West-African station-level rainfall as ground truth, especially in Ghana.
- Comparing forecasts or satellite products against the KNUST station network.

## Usage

```
uvx sheerwater@latest data fetch <name> \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [--variable precip] [--agg-days 1] \
    [--grid global0_25] [--mask lsm] [--region global] \
    --output <path.zarr>
```

### Key flags

- `--variable` — only `precip` is supported (daily mm).
- `--agg-days` — rolling-mean window in days (default 1).
- `--grid` — output grid (default `global0_25`).

See `uvx sheerwater@latest data fetch --help` for the full flag list.

### Output

Envelope Zarr with `precip` (mm/day) plus a companion `precip_count` (number of valid station-days in each cell). Stamped with `rhiza_source=<name>` and `sparse=True`.

## Example

```bash
uvx sheerwater@latest data fetch knust --start 2018-01-01 --end 2019-12-31 \
    --region ghana --output /tmp/knust_ghana.zarr
```
