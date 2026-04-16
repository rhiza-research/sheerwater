---
name: compare-forecasts
description: Compute a matrix of metrics for multiple forecasts against a single truth dataset. Use when you need to compare how several models perform on the same metrics over the same window/region.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Most cells of the matrix hit pre-computed results in the public sheerwater cache.
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# compare-forecasts

Compute a forecast × metric matrix against one truth source — produces a JSON table you can drop into a report or feed into a comparison plot.

For the catalog of available metrics and their constraints (probabilistic vs deterministic, valid variables, categorical bin syntax), see the `evaluate-forecast` skill.

## When to use

- Benchmarking AI models (GraphCast / FuXi / GenCast) against an operational baseline (ECMWF IFS).
- Producing a side-by-side skill comparison for a region/season.

## Usage

```
uvx sheerwater@latest eval compare \
    --forecasts NAME1,NAME2,... \
    --truth NAME \
    --metrics NAME1,NAME2,... \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [-v precip] [--agg-days 1] [--grid global1_5] [--mask lsm] [--region global] \
    [-o matrix.json]
```

### Key flags

- `--forecasts` — comma-separated forecast names.
- `--truth` — truth dataset name.
- `--metrics` — comma-separated metric names. Use the bin-suffix syntax (`heidke-1-5-10`) for categorical metrics.
- `-o` / `--output` — JSON output path (default: stdout).

Each cell of the matrix is computed via the same `sheerwater.metrics.metric` call as `eval metric`, so probabilistic-only metrics (`crps`, `brier`) require the corresponding forecast to be probabilistic, and metrics with `valid_variables=['precip']` will fail on non-precip evaluations.

### Output

JSON of the form:
```json
{
  "truth": "chirps", "variable": "precip", "agg_days": 1, "grid": "global1_5", "region": "kenya",
  "start_time": "2024-01-01", "end_time": "2024-03-31",
  "matrix": {
    "graphcast": { "mae": { ... }, "rmse": { ... } },
    "fuxi":      { "mae": { ... }, "rmse": { ... } },
    "ecmwf_ifs_er": { "mae": { ... }, "rmse": { ... } }
  }
}
```

## Example

```bash
uvx sheerwater@latest eval compare \
    --forecasts graphcast,fuxi,ecmwf_ifs_er \
    --truth chirps \
    --metrics mae,rmse,bias \
    --start 2024-01-01 --end 2024-03-31 \
    --region kenya \
    --output /tmp/compare_kenya.json
```
