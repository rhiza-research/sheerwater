# test_estimate_query_time

**Timestamp:** 2026-02-11T16:02:25.063491

## Prompt

Using sheerwater, estimate how long it would take to compare ECMWF and FuXi for Kenya precipitation

## Response

Based on my exploration of the sheerwater codebase, here's an estimate for comparing ECMWF and FuXi for Kenya precipitation:

## Time Estimate Summary

| Scenario | Estimated Time |
|----------|---------------|
| **Cached (Kenya is pre-cached)** | **< 1 minute** |
| **First run (1 year, e.g., 2020)** | ~3-5 minutes |
| **Full overlap period (2016-2022)** | ~35-40 minutes |

## Key Parameters

- **Region**: Kenya (~500 grid cells - small, fast to compute)
- **Common period**: 2016-01-03 to 2022-02-02 (FuXi's limit)
- **Aggregation**: Must use 7-day (FuXi's only option)
- **Grid**: global1_5 (1.5° resolution)
- **Ground truth**: CHIRPS v3 recommended

## How to Run

The comparison uses `compare_models()` from `sheerwater/mcp/tools/evaluation.py`:

```python
result = await compare_models(
    forecasts=["ecmwf_ifs_er", "fuxi"],
    truth="chirps_v3",
    metric="mae",  # or "rmse", "bias"
    region="Kenya",
    start_time="2020-01-01",
    end_time="2020-12-31",
    agg_days=7
)
```

## Computation Basis

The time estimate comes from `sheerwater/mcp/tools/evaluation.py:273-299`:
- Base rate: 30 seconds per 10,000 grid cells
- Kenya: ~500 cells → ~1.5 minutes per model per metric
- Two models (ECMWF + FuXi) → ~3 minutes + data loading overhead

## Note on Caching

Kenya precipitation comparisons are listed as "common queries" in the test configuration (`sheerwater/tests/test_mcp/conftest.py:93-112`), so cached results may already exist in the Nuthatch cache system, making subsequent runs nearly instant.

