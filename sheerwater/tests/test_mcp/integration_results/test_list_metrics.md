# test_list_metrics

**Timestamp:** 2026-02-11T16:00:22.572844

## Prompt

List available evaluation metrics using sheerwater

## Response

Based on the exploration, here are the available evaluation metrics in sheerwater:

## Continuous Metrics (deterministic, non-categorical)
| Metric | Full Name | Description |
|--------|-----------|-------------|
| `mae` | Mean Absolute Error | Average absolute difference between forecast and truth |
| `mse` | Mean Squared Error | Average squared difference |
| `rmse` | Root Mean Squared Error | Square root of MSE |
| `bias` | Bias | Systematic over/under-prediction |
| `smape` | Symmetric Mean Absolute Percentage Error | Percentage-based error |
| `mape` | Mean Absolute Percentage Error | Percentage-based absolute error |
| `acc` | Anomaly Correlation Coefficient | Correlation of anomalies |
| `pearson` | Pearson Correlation Coefficient | Linear correlation |
| `seeps` | Stable Equitable Error in Probability Space | Precipitation-specific metric |

## Categorical Metrics (threshold-based)
| Metric | Full Name | Description |
|--------|-----------|-------------|
| `heidke` | Heidke Skill Score | Skill relative to random chance |
| `pod` | Probability of Detection | Hit rate for events |
| `far` | False Alarm Rate | Fraction of false alarms |
| `ets` | Equitable Threat Score | Threat score adjusted for random hits |
| `csi` | Critical Success Index | Fraction of correct event forecasts |
| `frequencybias` | Frequency Bias | Ratio of forecast to observed events |

## Probabilistic Metrics (ensemble/probabilistic)
| Metric | Full Name | Description |
|--------|-----------|-------------|
| `crps` | Continuous Ranked Probability Score | Full distribution accuracy |
| `brier` | Brier Score | Probability forecast accuracy |

You can list these programmatically via:
```python
from sheerwater.metrics_library import list_metrics
metrics = list_metrics()
```

Or through the MCP server's `list_metrics` tool.

