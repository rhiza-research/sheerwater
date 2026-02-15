# test_list_forecasts

**Timestamp:** 2026-02-12T10:56:27.216538

## Prompt

List available forecast models using the sheerwater MCP tools

## Response

Here are the available forecast models:

**Climatology Baselines:**
| Name | Description |
|------|-------------|
| climatology_2015 | 30-year climatology baseline (1985-2014) |
| climatology_2020 | 30-year climatology baseline (1990-2019) |
| climatology_rolling | Rolling 30-year climatology baseline |
| climatology_trend_2015 | 30-year climatology with trend adjustment (1985-2014) |

**Physics-Based Models:**
| Name | Description |
|------|-------------|
| ecmwf_ifs_er | ECMWF IFS Extended Range - Operational physics-based model |
| ecmwf_ifs_er_debiased | ECMWF IFS Extended Range with reforecast-based bias correction |

**ML-Based Models:**
| Name | Description | Type |
|------|-------------|------|
| fuxi | FuXi S2S - ML subseasonal model from Fudan University | deterministic |
| gencast | GenCast - Google DeepMind's ensemble ML weather model | ensemble |
| graphcast | GraphCast - Google DeepMind's ML weather model | deterministic |
| salient | Salient - Commercial ML subseasonal forecasts | probabilistic |
| salient_gem | Salient GEM - Generative ensemble model for East Africa | ensemble |

All models support both precipitation (`precip`) and 2-meter temperature (`tmp2m`) variables.

