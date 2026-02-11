# test_get_metric_info

**Timestamp:** 2026-02-11T16:00:47.918501

## Prompt

Tell me about the MAE metric using sheerwater tools

## Response

Here's the information about the **MAE (Mean Absolute Error)** metric from sheerwater:

## MAE - Mean Absolute Error

| Attribute | Value |
|-----------|-------|
| **Full Name** | Mean Absolute Error |
| **Description** | Measures the average magnitude of errors without considering direction |
| **Formula** | `MAE = (1/n) * sum(\|forecast - observed\|)` |
| **Range** | [0, infinity) |
| **Direction** | Lower is better |
| **Interpretation** | Lower values indicate better forecast accuracy. Units match the variable being evaluated |

### Key Properties

- **Type**: Deterministic metric (`prob_type = 'deterministic'`)
- **Categorical**: No - it's a continuous metric
- **Sparse**: No - does not induce NaNs
- **Valid Variables**: All variables (no restrictions)
- **Statistics Used**: `['mae']`

### How It Works

MAE is one of the simplest error metrics. It calculates the absolute difference between each forecast and observation, then averages these differences. Because it uses absolute values, it:

1. Treats over-predictions and under-predictions equally
2. Does not penalize large errors more than small ones (unlike RMSE)
3. Produces results in the same units as the input variable

### Example Usage

```python
run_metric(
    forecast='ecmwf_ifs_er',
    truth='chirps_v3',
    metric='mae',
    region='Kenya'
)
```

### Comparison to Related Metrics

| Metric | Sensitivity to Outliers | Units |
|--------|------------------------|-------|
| **MAE** | Low | Same as variable |
| **MSE** | High | Squared units |
| **RMSE** | High | Same as variable |
| **Bias** | N/A (can cancel out) | Same as variable |

MAE is often preferred when you want a simple, interpretable error measure that's robust to outliers.

