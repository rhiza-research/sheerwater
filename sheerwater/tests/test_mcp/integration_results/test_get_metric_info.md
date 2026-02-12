# test_get_metric_info

**Timestamp:** 2026-02-12T10:56:53.550473

## Prompt

Tell me about the MAE metric using sheerwater tools

## Response

## Mean Absolute Error (MAE)

**Full Name:** Mean Absolute Error

**Description:** Measures the average magnitude of errors without considering direction.

**Formula:** 
```
MAE = (1/n) * sum(|forecast - observed|)
```

**Key Properties:**
- **Range:** [0, ∞)
- **Direction:** Lower is better
- **Units:** Match the variable being evaluated (e.g., mm for precipitation, °C for temperature)
- **Type:** Deterministic (not probabilistic)
- **Categorical:** No

**Interpretation:** MAE gives you the average absolute difference between forecasted and observed values. A MAE of 5mm for precipitation means the forecast is off by 5mm on average. Unlike RMSE, MAE treats all errors equally and doesn't penalize large errors more heavily.

**Example Usage:**
```
run_metric(forecast='ecmwf_ifs_er', truth='chirps_v3', metric='mae', region='Kenya')
```

