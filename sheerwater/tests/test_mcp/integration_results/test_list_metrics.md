# test_list_metrics

**Timestamp:** 2026-02-12T10:56:41.616006

## Prompt

List available evaluation metrics using sheerwater

## Response

Here are the available evaluation metrics from Sheerwater:

## Continuous Metrics

| Metric | Full Name | Interpretation |
|--------|-----------|----------------|
| **acc** | Anomaly Correlation Coefficient | Higher is better (1.0 = perfect, 0.0 = no skill) |
| **bias** | Bias | Closer to 0 is better; positive = over-prediction |
| **mae** | Mean Absolute Error | Lower is better |
| **mse** | Mean Squared Error | Lower is better; more sensitive to outliers |
| **rmse** | Root Mean Squared Error | Lower is better; more sensitive to outliers |
| **mape** | Mean Absolute Percentage Error | Lower is better (precip only) |
| **smape** | Symmetric Mean Absolute Percentage Error | Lower is better (precip only) |
| **pearson** | Pearson Correlation Coefficient | Higher is better (-1 to 1) |
| **seeps** | Stable Equitable Error in Probability Space | Lower is better; designed for rainfall verification |

## Categorical Metrics

| Metric | Full Name | Interpretation |
|--------|-----------|----------------|
| **heidke** | Heidke Skill Score | Higher is better (0 = no skill, 1 = perfect) |
| **pod** | Probability of Detection | Higher is better (hit rate) |
| **far** | False Alarm Rate | Lower is better |
| **ets** | Equitable Threat Score | Higher is better; balanced skill measure |
| **csi** | Critical Success Index | Higher is better (Threat Score) |
| **frequencybias** | Frequency Bias | 1.0 is ideal; >1 = over-forecasting |

## Probabilistic Metrics

| Metric | Full Name | Interpretation |
|--------|-----------|----------------|
| **crps** | Continuous Ranked Probability Score | Lower is better; measures calibration and sharpness |
| **brier** | Brier Score | Lower is better (0 = perfect, 1 = worst) |

Use `tool_get_metric_info` with a specific metric name for detailed formulas and usage guidance.

