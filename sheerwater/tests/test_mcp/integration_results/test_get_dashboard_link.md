# test_get_dashboard_link

**Timestamp:** 2026-02-11T16:02:41.140370

## Prompt

Using sheerwater tools, get me a Grafana dashboard link for Kenya precipitation forecasts

## Response

I found the `get_dashboard_link` tool in the sheerwater MCP tools. Let me construct the URL for Kenya precipitation forecasts:

Based on the `get_dashboard_link` function in `sheerwater/mcp/tools/visualization.py:23`, here's the Grafana dashboard link for Kenya precipitation forecasts:

**URL:** https://dashboards.rhizaresearch.org/d/ee2jzeymn1o8wf/forecast-evaluation?var-region=Kenya&var-variable=precip

This links to the Forecast Evaluation dashboard with:
- **Region:** Kenya
- **Variable:** precip (precipitation)

You can also add additional filters:
- `var-forecast=<model>` - to pre-select a specific forecast model
- `var-metric=<metric>` - to pre-select a specific metric (e.g., mae, rmse)

**Other available dashboards:**
- `forecast-eval-maps` (ID: ae39q2k3jv668d)
- `ground-truth` (ID: bf5u4y7w1vv28b)  
- `reanalysis` (ID: ce6tgp4j3d9fkf)

