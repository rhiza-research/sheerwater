# test_list_forecasts

**Timestamp:** 2026-02-11T15:59:30.163291

## Prompt

List available forecast models using the sheerwater MCP tools

## Response

Based on my exploration of the codebase, here are the **available forecast models** in the Sheerwater MCP server:

## Operational Forecasts

| Model | Description | Type | Variables |
|-------|-------------|------|-----------|
| `ecmwf_ifs_er` | ECMWF IFS Extended Range - Operational physics-based model | deterministic | precip, tmp2m |
| `ecmwf_ifs_er_debiased` | ECMWF IFS Extended Range with reforecast-based bias correction | deterministic | precip, tmp2m |
| `fuxi` | FuXi S2S - ML-based subseasonal model from Fudan University | deterministic | precip, tmp2m |
| `graphcast` | GraphCast - Google DeepMind's ML weather model | deterministic | precip, tmp2m |
| `gencast` | GenCast - Google DeepMind's ensemble ML weather model | ensemble | precip, tmp2m |
| `salient` | Salient - Commercial ML subseasonal forecasts | probabilistic | precip, tmp2m |
| `salient_gem` | Salient GEM - Generative ensemble model for East Africa | ensemble | precip, tmp2m |

## Climatology Baselines

| Model | Description | Type | Variables |
|-------|-------------|------|-----------|
| `climatology_2015` | 30-year climatology baseline (1985-2014) | deterministic | precip, tmp2m |
| `climatology_2020` | 30-year climatology baseline (1990-2019) | deterministic | precip, tmp2m |
| `climatology_trend_2015` | 30-year climatology with trend adjustment (1985-2014) | deterministic | precip, tmp2m |
| `climatology_rolling` | Rolling 30-year climatology baseline | deterministic | precip, tmp2m |

These are registered in the `FORECAST_REGISTRY` via the `@sheerwater_forecast` decorator and can be used with the MCP tools like `tool_run_metric` and `tool_compare_models`.

