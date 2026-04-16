---
name: evaluate-forecast
description: Compute a single verification metric (MAE, RMSE, bias, ACC, CRPS, Brier, Heidke, ETS, CSI, FAR, POD, frequency bias, MAPE/SMAPE, SEEPS, Pearson, MSE) for a forecast vs a truth dataset over a date range. Use when assessing how well one forecast model performs against a chosen ground-truth source.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI. Most metrics complete fast against the public sheerwater cache; cache misses require GOOGLE_APPLICATION_CREDENTIALS and may be slow (Dask cluster recommended).
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
    primaryEnv: GOOGLE_APPLICATION_CREDENTIALS
---

# evaluate-forecast

Compute a verification metric for a forecast against a truth dataset. Backed by `sheerwater.metrics.metric` — most queries hit pre-computed results in the public sheerwater cache, returning in seconds.

## Available metrics

Pick `--metric <name>` from this catalog. The "valid variables" column says which forecast variables a metric will run on; passing an unsupported variable raises.

| Metric | Type | Valid variables | Notes |
|---|---|---|---|
| `mae` | deterministic | all | Mean Absolute Error |
| `mse` | deterministic | all | Mean Squared Error |
| `rmse` | deterministic | all | sqrt of MSE |
| `bias` | deterministic | all | Mean error (forecast − truth) |
| `acc` | deterministic | all | Anomaly Correlation Coefficient vs ERA5 climatology (1990-2019) |
| `crps` | probabilistic | all | Continuous Ranked Probability Score; requires probabilistic forecast |
| `pearson` | deterministic | precip only | Pearson correlation (rewritten for grouped streaming) |
| `mape` | deterministic | precip only | Mean Absolute Percentage Error |
| `smape` | deterministic | precip only | Symmetric Mean Absolute Percentage Error |
| `seeps` | deterministic | precip only | Stable Equitable Error in Probability Space; uses 1991-2020 climatology |
| `brier` | probabilistic | precip only | Categorical Brier score; requires bins (see below) |
| `heidke` | deterministic | precip only | Heidke Skill Score; categorical, requires bins |
| `pod` | deterministic | precip only | Probability of Detection; categorical, requires bins |
| `far` | deterministic | precip only | False Alarm Rate; categorical, requires bins |
| `csi` | deterministic | precip only | Critical Success Index; categorical, requires bins |
| `ets` | deterministic | precip only | Equitable Threat Score; categorical, requires bins |
| `frequencybias` | deterministic | precip only | Frequency Bias; categorical, requires bins |

### Categorical metrics: bin syntax

For `brier`, `heidke`, `pod`, `far`, `csi`, `ets`, and `frequencybias`, the metric name needs bin thresholds appended with hyphens. For example, to compute Heidke with bins at 1, 5, and 10 mm:

```
--metric heidke-1-5-10
```

Bins are interpreted as the boundaries of the categories (with `-inf` and `+inf` automatically added at the ends). Up to 10 bins maximum.

### Probabilistic vs deterministic

`crps` and `brier` only run on probabilistic forecasts (the metric checks the forecast's `prob_type` attribute and raises on a mismatch). All other metrics require a deterministic forecast.

## When to use

- Quantifying forecast skill against a chosen truth source for a window/region.
- Producing a JSON metric value to feed into a report or dashboard.
- Producing a gridded residual field for downstream visualization.

## Usage

```
uvx sheerwater@latest eval metric \
    --forecast NAME --truth NAME --metric NAME \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    [-v precip] [--agg-days 1] [--grid global1_5] [--mask lsm] [--region global] \
    [--time-grouping NAME] [--space-grouping NAME] \
    [--spatial | --zarr-output PATH] \
    [-o output.json]
```

### Key flags

- `--forecast` — forecast model name (see `sheerwater forecast list`).
- `--truth` — truth dataset name (see `sheerwater data list`). Note: the metric framework also accepts forecast names here when comparing two forecasts.
- `--metric` — metric name plus optional bin suffix for categorical metrics.
- `--time-grouping` — group results by month/year/etc. (mapped through `groupby_time`).
- `--space-grouping` — group results by a spatial subdivision name (e.g. `country`, `continent`, `admin_1`, `agroecological_zone`); default is `country`.
- `--region` — clip the evaluation to a region NAME (e.g. `kenya`, `africa`, `nimbus_east_africa`). Sheerwater auto-detects which subdivision level the name belongs to.
- `--spatial` — return a gridded result instead of grouped scalar/table.
- `--zarr-output` — write gridded result as envelope Zarr (implies `--spatial`).
- `-o` / `--output` — JSON output path (default: stdout).

### Output

JSON of the form:
```json
{
  "forecast": "graphcast", "truth": "chirps", "metric": "mae",
  "variable": "precip", "agg_days": 1, "grid": "global1_5", "region": "global",
  "start_time": "2024-01-01", "end_time": "2024-03-31",
  "values": { "precip": 1.234 }
}
```

Or, with `--zarr-output`, an envelope Zarr of the gridded residuals.

## Examples

```bash
# Scalar MAE for GraphCast vs CHIRPS over Q1 2024 in Kenya
uvx sheerwater@latest eval metric --forecast graphcast --truth chirps --metric mae \
    --start 2024-01-01 --end 2024-03-31 --region kenya
```

```bash
# Heidke Skill Score with bins at 1, 5, 10 mm
uvx sheerwater@latest eval metric --forecast ecmwf_ifs_er_debiased --truth chirps \
    --metric heidke-1-5-10 --start 2024-01-01 --end 2024-03-31 --region africa
```

```bash
# Gridded RMSE residuals
uvx sheerwater@latest eval metric --forecast fuxi --truth era5 --metric rmse \
    --start 2024-01-01 --end 2024-03-31 --region africa \
    --zarr-output /tmp/fuxi_rmse.zarr
```
