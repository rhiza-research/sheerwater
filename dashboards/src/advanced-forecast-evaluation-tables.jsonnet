local metrics_explainer_md = importstr './assets/metrics_explainer.md';

{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "links": [],
  "panels": [
    {
      "datasource": {
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 5,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 16,
      "options": {
        "afterRender": "// window.onload = function () {\n//     renderMathInElement(document.body, {\n//         delimiters: [\n//             { left: \"$$\", right: \"$$\", display: true },\n//             { left: \"\\\\(\", right: \"\\\\)\", display: false }\n//         ]\n//     });\n// };\n",
        "content": metrics_explainer_md,
        "contentPartials": [],
        "defaultContent": "The query didn't return any results.",
        "editor": {
          "format": "auto",
          "language": "markdown"
        },
        "editors": [],
        "externalStyles": [],
        "helpers": "",
        "renderMode": "everyRow",
        "styles": "",
        "wrap": true
      },
      "pluginVersion": "6.2.3",
      "targets": [
        {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "select '${metric}' as metric\n",
          "refId": "A",
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "",
      "transparent": true,
      "type": "marcusolsson-dynamictext-panel"
    },
    {
      "collapsed": true,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 5
      },
      "id": 7,
      "panels": [
        {
          "datasource": {
            "uid": "bdz3m3xs99p1cf"
          },
          "fieldConfig": {
            "defaults": {
              "thresholds": {
                "mode": "absolute",
                "steps": [
                  {
                    "color": "green"
                  },
                  {
                    "color": "red",
                    "value": 80
                  }
                ]
              }
            },
            "overrides": []
          },
          "gridPos": {
            "h": 12,
            "w": 24,
            "x": 0,
            "y": 5
          },
          "id": 8,
          "options": {
            "afterRender": "// window.onload = function () {\n//     renderMathInElement(document.body, {\n//         delimiters: [\n//             { left: \"$$\", right: \"$$\", display: true },\n//             { left: \"\\\\(\", right: \"\\\\)\", display: false }\n//         ]\n//     });\n// };\n",
            "content": " - Models are evaluated from 2016-01-01 through 2022-12-31\n - All metrics are computed with the ECMWF land-sea mask that includes any cell with non-zero land coverage. \n - Spatial averages use latitude-based weighting.\n\n - Conservative regridding is used for both upscaling and downscaling forecasts. \n \n - ECMWF and FuXi S2S forecasts are native 1.5x1.5. \n \n - Salient, Graphcast, and Gencast are native 0.25x0.25.\n\n - Salient is conservatively regridded from their native 0.125 shifted grid to our round 0.25/1.5 grid. \n\n - All metrics are computed deterministically except for CRPS\n\n - Deterministic forecasts are derived from ensemble forecasts (ECMWF, FuXi, Gencast) through taking the average of the ensemble members\n\n - Deterministic forecasts are derived from quantile forecasts (Salient) by taking the median quantile.\n\n - The source for Gencast temperature forecasts was corrupted so they have been excluded.\n\n - Metrics that cannot be globally computed and then reduced (such as ACC, POD, FAR, ETC) are not available with time groupings.",
            "contentPartials": [],
            "defaultContent": "The query didn't return any results.",
            "editor": {
              "format": "auto",
              "language": "markdown"
            },
            "editors": [],
            "externalStyles": [],
            "helpers": "",
            "renderMode": "everyRow",
            "styles": "",
            "wrap": true
          },
          "pluginVersion": "6.2.3",
          "targets": [
            {
              "editorMode": "code",
              "format": "table",
              "rawQuery": true,
              "rawSql": "select '${metric}' as metric\n",
              "refId": "A",
              "sql": {
                "columns": [
                  {
                    "parameters": [],
                    "type": "function"
                  }
                ],
                "groupBy": [
                  {
                    "property": {
                      "type": "string"
                    },
                    "type": "groupBy"
                  }
                ],
                "limit": 50
              }
            }
          ],
          "title": "",
          "transparent": true,
          "type": "marcusolsson-dynamictext-panel"
        }
      ],
      "title": "Notes and Caveats",
      "type": "row"
    },
    {
      "datasource": {
        "default": true,
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 15,
        "w": 12,
        "x": 0,
        "y": 6
      },
      "id": 1,
      "options": {
        "allData": {},
        "config": {},
        "data": [],
        "imgFormat": "png",
        "layout": {
          "font": {
            "family": "Inter, sans-serif"
          },
          "margin": {
            "b": 4,
            "l": 0,
            "r": 0,
            "t": 0
          },
          "paper_bgcolor": "#F4F5F5",
          "plog_bgcolor": "#F4F5F5",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            },
            "pad": {
              "b": 30
            },
            "text": "Weekly",
            "x": 0,
            "xanchor": "left"
          },
          "xaxis": {
            "automargin": true,
            "autorange": true,
            "type": "date"
          },
          "yaxis": {
            "automargin": true,
            "autorange": true
          }
        },
        "onclick": "",
        "resScale": 2,
        "script": "function getThresholdColor(ratio, colorThreshold) {\n    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';\n\n    const t = Math.min(1, Math.max(0, ratio));\n\n    let r, g, b;\n    if (t <= colorThreshold) {\n        // Red (220,50,50) → Cream (255,253,220)\n        const s = t / colorThreshold;\n        r = Math.round(220 + s * (255 - 220));\n        g = Math.round(50  + s * (253 - 50));\n        b = Math.round(50  + s * (220 - 50));\n    } else {\n        // Cream (255,253,220) → Green (56,168,83)\n        const s = (t - colorThreshold) / (1 - colorThreshold);\n        r = Math.round(255 + s * (56  - 255));\n        g = Math.round(253 + s * (168 - 253));\n        b = Math.round(220 + s * (83  - 220));\n    }\n\n    return `rgba(${r}, ${g}, ${b}, 0.5)`;\n}\nconst renameDict = {\n    \"Ecmwf Ifs Er\": \"ECMWF IFS ER\",\n    \"Ecmwf Ifs Ens\": \"ECMWF IFS ENS\",\n    \"Ecmwf Ifs Er Debiased\": \"ECMWF IFS ER Debiased\",\n    \"Ecmwf Aifs\": \"ECMWF AIFS\",\n    \"Ecmwf Hres\": \"ECMWF HRES\",\n    \"Gfs\": \"GFS\",\n    \"Salient\": \"AI-Enhanced NWP\",\n    \"Fuxi\": \"FuXi S2S\",\n    \"Climatology 2015\": \"Climatology 1985-2014\",\n    \"Climatology Trend 2015\": \"Climatology 1985-2014 w/Trend\",\n    \"Climatology Era5 1985 2015\": \"Climatology ERA5 1985-2014\",\n    \"Climatology Imerg 1998 2016\": \"Climatology IMERG 1998-2015\",\n    \"Cumulus Ai\": \"Cumulus AI v0.0.0\",\n};\n\nfunction titleCase(str) {\n    let name = str.replaceAll('_', ' ')\n        .split(' ')\n        .map(w => w[0].toUpperCase() + w.substring(1))\n        .join(' ');\n    return renameDict[name] || name;\n}\n\n// ── Data check ───────────────────────────────────────────────────────────────\nlet series = data.series[0];\nif (!series || series.fields.length === 0) return { data: [] };\n\n// ── Parse long-format fields ─────────────────────────────────────────────────\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst fieldNames       = series.fields.map(f => f.name);\nconst forecastField    = series.fields[fieldNames.indexOf('forecast')].values;\nconst leadDayField     = series.fields[fieldNames.indexOf('lead_day')].values;\nconst pointsField      = getField(series.fields, 'points_above_threshold');\nconst pointsTotalField = getField(series.fields, 'points_total');\nconst metricMeanField  = getField(series.fields, 'metric_mean');\n\n// ── Build lookup: forecast -> lead_day -> { points, pointsTotal, metricMean } ──\nconst dataMap = {};\nfor (let i = 0; i < forecastField.length; i++) {\n    const f  = forecastField[i];\n    const ld = leadDayField[i];\n    if (!dataMap[f]) dataMap[f] = {};\n    dataMap[f][ld] = {\n        points:      pointsField[i],\n        pointsTotal: pointsTotalField[i],\n        metricMean:  metricMeanField[i]\n    };\n}\n\nconst uniqueForecasts = [...new Set(forecastField)];\nconst uniqueLeadDays  = [...new Set(leadDayField)].sort((a, b) => a - b);\n\n// display_metric: 'points' (default) shows X / Y count, 'value' shows mean\nconst displayMetric = variables?.display_metric?.current?.value || 'points';\nconst metricLabel = displayMetric === 'value' ? 'Mean value' : 'Points (avg < threshold)';\n\n// Color threshold — driven by Grafana variable color_threshold (e.g. 0.8), defaults to 0.8\nconst colorThreshold = parseFloat(variables?.color_threshold?.current?.value) || 0.8;\n\n// ── Build header and value columns ───────────────────────────────────────────\nconst header      = [\"Forecast\", ...uniqueLeadDays.map(ld => `Day ${ld}`)];\nconst orig_header = [\"forecast\", ...uniqueLeadDays.map(ld => `lead_${ld}`)];\n\nconst forecastNames = uniqueForecasts.map(titleCase);\nconst values  = [forecastNames];  // values[0] = forecast names, values[1..] = lead_day columns\nconst ratios  = [];               // numeric ratios for coloring, parallel to values[1..]\n\nfor (const ld of uniqueLeadDays) {\n    const col      = [];\n    const ratioCol = [];\n    for (const f of uniqueForecasts) {\n        const d = dataMap[f]?.[ld];\n        if (!d) {\n            col.push('-');\n            ratioCol.push(null);\n        } else if (displayMetric === 'value') {\n            const v = d.metricMean;\n            if (v == null) {\n                col.push('-');\n                ratioCol.push(null);\n            } else {\n                col.push(parseFloat(v).toFixed(3));\n                ratioCol.push(parseFloat(v));\n            }\n        } else {\n            const num   = d.points;\n            const denom = d.pointsTotal;\n            if (denom === 0 || denom == null) {\n                col.push('-');\n                ratioCol.push(null);\n            } else {\n                const ratio = num / denom;\n                col.push(`${num} / ${denom}`);\n                ratioCol.push(ratio);\n            }\n        }\n    }\n    values.push(col);\n    ratios.push(ratioCol);\n}\n\n// ── Colors ───────────────────────────────────────────────────────────────────\nconst forecast_colors = uniqueForecasts.map(() => 'rgba(0,0,0,0)');\n\nlet skill_colors;\nif (displayMetric === 'value') {\n    // Scale color across the observed min/max range\n    const allRatios = ratios.flat().filter(v => v != null && !isNaN(v));\n    const minVal = Math.min(...allRatios);\n    const maxVal = Math.max(...allRatios);\n    const range  = maxVal - minVal || 1;\n    skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(v => {\n            if (v == null || isNaN(v)) return 'rgba(255,255,255,0)';\n            const normalized = (v - minVal) / range;  // 0 = best (low), 1 = worst (high)\n            return getThresholdColor(1 - normalized, colorThreshold);\n        })\n    );\n} else {\n    skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(ratio => getThresholdColor(ratio, colorThreshold))\n    );\n}\n\n// ── Links ────────────────────────────────────────────────────────────────────\nconst metric        = variables.metric.current.value;\nconst grid          = variables.grid.current.value;\nconst region        = variables.region.current.value;\nconst region_option        = variables.region_option.current.value;\nconst time_grouping = variables.time_grouping.current.value;\nconst time_filter   = variables.time_option.current.value;\n\nfor (let i = 1; i < values.length; i++) {\n    const ld = uniqueLeadDays[i - 1];\n    for (let j = 0; j < values[i].length; j++) {\n        const url = `d/ae39q2k3jv668d/plotly-maps?orgId=1` +\n            `&var-forecast=${uniqueForecasts[j]}` +\n            `&var-metric=${metric}` +\n            `&var-lead=lead_${ld}` +\n            `&var-truth=era5` +\n            `&var-grid=${grid}` +\n            `&var-region=${region}` +\n            `&var-time_grouping=${time_grouping}` +\n            `&var-time_filter=${time_filter}`;\n        values[i][j] = `<a href=\"${url}\">${values[i][j]}</a>`;\n    }\n}\n\n// ── Divider after 2nd lead-day column ────────────────────────────────────────\nconst dividerAt = 2; // insert divider after this many lead-day columns\n\nconst headerWithDiv = [\n    ...header.slice(0, dividerAt + 1),\n    '',\n    ...header.slice(dividerAt + 1)\n];\nconst valuesWithDiv = [\n    ...values.slice(0, dividerAt + 1),\n    Array(uniqueForecasts.length).fill(''),\n    ...values.slice(dividerAt + 1)\n];\nconst colorsWithDiv = [\n    forecast_colors,\n    ...skill_colors.slice(0, dividerAt),\n    Array(uniqueForecasts.length).fill('rgba(200,200,200,0.3)'),\n    ...skill_colors.slice(dividerAt)\n];\n\nconst colWidth = [1.4, ...uniqueLeadDays.map(() => 0.5)];\ncolWidth.splice(dividerAt + 1, 0, 0.05);\n\n// ── Return ────────────────────────────────────────────────────────────────────\nreturn {\n    data: [{\n        type: 'table',\n        header: {\n            values: headerWithDiv,\n            align: ['left', ...uniqueLeadDays.map(() => 'right'), 'right'],\n            line: { width: 0, color: '#DBDDDE' },\n            font: { family: \"Inter, sans-serif\", size: 14, weight: \"bold\" },\n            fill: { color: ['rgba(0,0,0,0)'] }\n        },\n        cells: {\n            values: valuesWithDiv,\n            align: ['left', ...uniqueLeadDays.map(() => 'right'), 'right'],\n            line: { width: 1, color: \"#DBDDDE\" },\n            font: { family: \"Inter, sans-serif\", size: 14, color: [\"black\"] },\n            fill: { color: colorsWithDiv },\n            height: 35\n        },\n        columnwidth: colWidth\n    }],\n    layout: {\n        title: {\n            text: `Actionable Cells — ${region_option.charAt(0).toUpperCase() + region_option.slice(1)}`,            \n            xanchor: 'left',\n            x: 0\n        }\n    }\n};",
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "bdz3m3xs99p1cf"
          },
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_fcst_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n)\nSELECT\n  -- display_metric: $display_metric\n  -- threshold: $threshold\n  -- color_threshold: $color_threshold\n  forecast,\n  $region,\n  lead_day,\n  COUNT(CASE WHEN metric_avg < ${threshold}::float THEN 1 END)  AS points_above_threshold,\n  COUNT(metric_avg)                                               AS points_total,\n  AVG(metric_avg)                                                 AS metric_mean\nFROM cell_avgs\nGROUP BY forecast, $region, lead_day\nORDER BY forecast, $region, lead_day",
          "refId": "A",
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "",
      "transparent": true,
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
        "default": true,
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 15,
        "w": 12,
        "x": 12,
        "y": 6
      },
      "id": 15,
      "options": {
        "allData": {},
        "config": {},
        "data": [],
        "imgFormat": "png",
        "layout": {
          "font": {
            "family": "Inter, sans-serif"
          },
          "margin": {
            "b": 4,
            "l": 0,
            "r": 0,
            "t": 0
          },
          "paper_bgcolor": "#F4F5F5",
          "plog_bgcolor": "#F4F5F5",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            },
            "pad": {
              "b": 30
            },
            "text": "Weekly",
            "x": 0,
            "xanchor": "left"
          },
          "xaxis": {
            "automargin": true,
            "autorange": true,
            "type": "date"
          },
          "yaxis": {
            "automargin": true,
            "autorange": true
          }
        },
        "onclick": "",
        "resScale": 2,
        "script": "function getThresholdColor(ratio, colorThreshold) {\n    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';\n\n    const t = Math.min(1, Math.max(0, ratio));\n\n    let r, g, b;\n    if (t <= colorThreshold) {\n        // Red (220,50,50) → Cream (255,253,220)\n        const s = t / colorThreshold;\n        r = Math.round(220 + s * (255 - 220));\n        g = Math.round(50  + s * (253 - 50));\n        b = Math.round(50  + s * (220 - 50));\n    } else {\n        // Cream (255,253,220) → Green (56,168,83)\n        const s = (t - colorThreshold) / (1 - colorThreshold);\n        r = Math.round(255 + s * (56  - 255));\n        g = Math.round(253 + s * (168 - 253));\n        b = Math.round(220 + s * (83  - 220));\n    }\n\n    return `rgba(${r}, ${g}, ${b}, 0.5)`;\n}\nconst renameDict = {\n    \"Ecmwf Ifs Er\": \"ECMWF IFS ER\",\n    \"Ecmwf Ifs Ens\": \"ECMWF IFS ENS\",\n    \"Ecmwf Ifs Er Debiased\": \"ECMWF IFS ER Debiased\",\n    \"Ecmwf Aifs\": \"ECMWF AIFS\",\n    \"Ecmwf Hres\": \"ECMWF HRES\",\n    \"Gfs\": \"GFS\",\n    \"Salient\": \"AI-Enhanced NWP\",\n    \"Fuxi\": \"FuXi S2S\",\n    \"Climatology 2015\": \"Climatology 1985-2014\",\n    \"Climatology Trend 2015\": \"Climatology 1985-2014 w/Trend\",\n    \"Climatology Era5 1985 2015\": \"Climatology ERA5 1985-2014\",\n    \"Climatology Imerg 1998 2016\": \"Climatology IMERG 1998-2015\",\n    \"Cumulus Ai\": \"Cumulus AI v0.0.0\",\n};\n\nfunction titleCase(str) {\n    let name = str.replaceAll('_', ' ')\n        .split(' ')\n        .map(w => w[0].toUpperCase() + w.substring(1))\n        .join(' ');\n    return renameDict[name] || name;\n}\n\n// ── Data check ───────────────────────────────────────────────────────────────\nlet series = data.series[0];\nif (!series || series.fields.length === 0) return { data: [] };\n\n// ── Parse long-format fields ─────────────────────────────────────────────────\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst fieldNames       = series.fields.map(f => f.name);\nconst forecastField    = series.fields[fieldNames.indexOf('forecast')].values;\nconst leadDayField     = series.fields[fieldNames.indexOf('lead_day')].values;\nconst pointsField      = getField(series.fields, 'points_above_threshold');\nconst pointsTotalField = getField(series.fields, 'points_total');\nconst metricMeanField  = getField(series.fields, 'metric_mean');\n\n// ── Build lookup: forecast -> lead_day -> { points, pointsTotal, metricMean } ──\nconst dataMap = {};\nfor (let i = 0; i < forecastField.length; i++) {\n    const f  = forecastField[i];\n    const ld = leadDayField[i];\n    if (!dataMap[f]) dataMap[f] = {};\n    dataMap[f][ld] = {\n        points:      pointsField[i],\n        pointsTotal: pointsTotalField[i],\n        metricMean:  metricMeanField[i]\n    };\n}\n\nconst uniqueForecasts = [...new Set(forecastField)];\nconst uniqueLeadDays  = [...new Set(leadDayField)].sort((a, b) => a - b);\n\n// display_metric: 'points' (default) shows X / Y count, 'value' shows mean\nconst displayMetric = variables?.display_metric?.current?.value || 'points';\nconst metricLabel = displayMetric === 'value' ? 'Mean value' : 'Points (avg < threshold)';\n\n// Color threshold — driven by Grafana variable color_threshold (e.g. 0.8), defaults to 0.8\nconst colorThreshold = parseFloat(variables?.color_threshold?.current?.value) || 0.8;\n\n// ── Build header and value columns ───────────────────────────────────────────\nconst header      = [\"Forecast\", ...uniqueLeadDays.map(ld => `Day ${ld}`)];\nconst orig_header = [\"forecast\", ...uniqueLeadDays.map(ld => `lead_${ld}`)];\n\nconst forecastNames = uniqueForecasts.map(titleCase);\nconst values  = [forecastNames];  // values[0] = forecast names, values[1..] = lead_day columns\nconst ratios  = [];               // numeric ratios for coloring, parallel to values[1..]\n\nfor (const ld of uniqueLeadDays) {\n    const col      = [];\n    const ratioCol = [];\n    for (const f of uniqueForecasts) {\n        const d = dataMap[f]?.[ld];\n        if (!d) {\n            col.push('-');\n            ratioCol.push(null);\n        } else if (displayMetric === 'value') {\n            const v = d.metricMean;\n            if (v == null) {\n                col.push('-');\n                ratioCol.push(null);\n            } else {\n                col.push(parseFloat(v).toFixed(3));\n                ratioCol.push(parseFloat(v));\n            }\n        } else {\n            const num   = d.points;\n            const denom = d.pointsTotal;\n            if (denom === 0 || denom == null) {\n                col.push('-');\n                ratioCol.push(null);\n            } else {\n                const ratio = num / denom;\n                col.push(`${num} / ${denom}`);\n                ratioCol.push(ratio);\n            }\n        }\n    }\n    values.push(col);\n    ratios.push(ratioCol);\n}\n\n// ── Colors ───────────────────────────────────────────────────────────────────\nconst forecast_colors = uniqueForecasts.map(() => 'rgba(0,0,0,0)');\n\nlet skill_colors;\nif (displayMetric === 'value') {\n    // Scale color across the observed min/max range\n    const allRatios = ratios.flat().filter(v => v != null && !isNaN(v));\n    const minVal = Math.min(...allRatios);\n    const maxVal = Math.max(...allRatios);\n    const range  = maxVal - minVal || 1;\n    skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(v => {\n            if (v == null || isNaN(v)) return 'rgba(255,255,255,0)';\n            const normalized = (v - minVal) / range;  // 0 = best (low), 1 = worst (high)\n            return getThresholdColor(1 - normalized, colorThreshold);\n        })\n    );\n} else {\n    skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(ratio => getThresholdColor(ratio, colorThreshold))\n    );\n}\n\n// ── Links ────────────────────────────────────────────────────────────────────\nconst metric        = variables.metric.current.value;\nconst grid          = variables.grid.current.value;\nconst region        = variables.region.current.value;\nconst region_option        = variables.region_option2.current.value;\nconst time_grouping = variables.time_grouping.current.value;\nconst time_filter   = variables.time_option.current.value;\n\nfor (let i = 1; i < values.length; i++) {\n    const ld = uniqueLeadDays[i - 1];\n    for (let j = 0; j < values[i].length; j++) {\n        const url = `d/ae39q2k3jv668d/plotly-maps?orgId=1` +\n            `&var-forecast=${uniqueForecasts[j]}` +\n            `&var-metric=${metric}` +\n            `&var-lead=lead_${ld}` +\n            `&var-truth=era5` +\n            `&var-grid=${grid}` +\n            `&var-region=${region}` +\n            `&var-time_grouping=${time_grouping}` +\n            `&var-time_filter=${time_filter}`;\n        values[i][j] = `<a href=\"${url}\">${values[i][j]}</a>`;\n    }\n}\n\n// ── Divider after 2nd lead-day column ────────────────────────────────────────\nconst dividerAt = 2; // insert divider after this many lead-day columns\n\nconst headerWithDiv = [\n    ...header.slice(0, dividerAt + 1),\n    '',\n    ...header.slice(dividerAt + 1)\n];\nconst valuesWithDiv = [\n    ...values.slice(0, dividerAt + 1),\n    Array(uniqueForecasts.length).fill(''),\n    ...values.slice(dividerAt + 1)\n];\nconst colorsWithDiv = [\n    forecast_colors,\n    ...skill_colors.slice(0, dividerAt),\n    Array(uniqueForecasts.length).fill('rgba(200,200,200,0.3)'),\n    ...skill_colors.slice(dividerAt)\n];\n\nconst colWidth = [1.4, ...uniqueLeadDays.map(() => 0.5)];\ncolWidth.splice(dividerAt + 1, 0, 0.05);\n\n// ── Return ────────────────────────────────────────────────────────────────────\nreturn {\n    data: [{\n        type: 'table',\n        header: {\n            values: headerWithDiv,\n            align: ['left', ...uniqueLeadDays.map(() => 'right'), 'right'],\n            line: { width: 0, color: '#DBDDDE' },\n            font: { family: \"Inter, sans-serif\", size: 14, weight: \"bold\" },\n            fill: { color: ['rgba(0,0,0,0)'] }\n        },\n        cells: {\n            values: valuesWithDiv,\n            align: ['left', ...uniqueLeadDays.map(() => 'right'), 'right'],\n            line: { width: 1, color: \"#DBDDDE\" },\n            font: { family: \"Inter, sans-serif\", size: 14, color: [\"black\"] },\n            fill: { color: colorsWithDiv },\n            height: 35\n        },\n        columnwidth: colWidth\n    }],\n    layout: {\n        title: {\n            text: `Actionable Cells — ${region_option.charAt(0).toUpperCase() + region_option.slice(1)}`,            \n            xanchor: 'left',\n            x: 0\n        }\n    }\n};",
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "bdz3m3xs99p1cf"
          },
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_fcst_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n)\nSELECT\n  -- display_metric: $display_metric\n  -- threshold: $threshold\n  forecast,\n  $region,\n  lead_day,\n  COUNT(CASE WHEN metric_avg < ${threshold}::float THEN 1 END)  AS points_above_threshold,\n  COUNT(metric_avg)                                               AS points_total,\n  AVG(metric_avg)                                                 AS metric_mean\nFROM cell_avgs\nGROUP BY forecast, $region, lead_day\nORDER BY forecast, $region, lead_day",
          "refId": "A",
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        },
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "bdz3m3xs99p1cf"
          },
          "editorMode": "code",
          "format": "table",
          "hide": false,
          "rawQuery": true,
          "rawSql": "-- select * from (values ('${forecast}${lead}${metric}${region}${standardize_lead_colors}${standardize_forecast_colors}${time_grouping}${time_filter}') ) v(t)\nselect *\nfrom (\n    values (\n        '${region:doublequote}${metric}${truth}${time_grouping}${time_filter}'\n    )\n) v(t);",
          "refId": "B",
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "",
      "transparent": true,
      "type": "nline-plotlyjs-panel"
    },
    {
      "collapsed": false,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 21
      },
      "id": 9,
      "panels": [],
      "title": "Metrics",
      "type": "row"
    }
  ],
  "preload": false,
  "refresh": "",
  "schemaVersion": 40,
  "tags": [],
  "templating": {
    "list": [
      {
        "current": {
          "text": "in_season_dry_spell",
          "value": "in_season_dry_spell"
        },
        "includeAll": false,
        "label": "Metric",
        "name": "metric",
        "options": [
          {
            "selected": false,
            "text": "Early season accumulation",
            "value": "early_season_accumulation-30d"
          },
          {
            "selected": false,
            "text": "Large rain days",
            "value": "big_rain_days"
          },
          {
            "selected": true,
            "text": "In season dry spells",
            "value": "in_season_dry_spell"
          }
        ],
        "query": "Early season accumulation : early_season_accumulation-30d, Large rain days : big_rain_days, In season dry spells : in_season_dry_spell",
        "type": "custom"
      },
      {
        "current": {
          "text": "year",
          "value": "year"
        },
        "includeAll": false,
        "label": "Time Grouping",
        "name": "time_grouping",
        "options": [
          {
            "selected": true,
            "text": "Year",
            "value": "year"
          }
        ],
        "query": "Year : year",
        "type": "custom"
      },
      {
        "current": {
          "text": [
            "Y2016",
            "Y2017",
            "Y2018",
            "Y2019",
            "Y2020",
            "Y2021",
            "Y2022",
            "Y2023",
            "Y2024"
          ],
          "value": [
            "Y2016",
            "Y2017",
            "Y2018",
            "Y2019",
            "Y2020",
            "Y2021",
            "Y2022",
            "Y2023",
            "Y2024"
          ]
        },
        "definition": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"\nWHERE lead_day = 0",
        "label": "Time Period",
        "multi": true,
        "name": "time_option",
        "options": [],
        "query": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"\nWHERE lead_day = 0",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "imerg_final",
          "value": "imerg_final"
        },
        "includeAll": false,
        "label": "Ground Truth",
        "name": "truth",
        "options": [
          {
            "selected": false,
            "text": "ERA5",
            "value": "era5"
          },
          {
            "selected": true,
            "text": "IMERG",
            "value": "imerg_final"
          },
          {
            "selected": false,
            "text": "CHIRPS V3",
            "value": "chirps_v3"
          }
        ],
        "query": "ERA5 : era5, IMERG : imerg_final, CHIRPS V3 : chirps_v3",
        "type": "custom"
      },
      {
        "current": {
          "text": "global1_5",
          "value": "global1_5"
        },
        "includeAll": false,
        "label": "Grid",
        "name": "grid",
        "options": [
          {
            "selected": true,
            "text": "1.5",
            "value": "global1_5"
          },
          {
            "selected": false,
            "text": "0.25",
            "value": "global0_25"
          }
        ],
        "query": "1.5 : global1_5, 0.25 : global0_25",
        "type": "custom"
      },
      {
        "current": {
          "text": "country",
          "value": "country"
        },
        "includeAll": false,
        "label": "Region",
        "name": "region",
        "options": [
          {
            "selected": true,
            "text": "Countries",
            "value": "country"
          },
          {
            "selected": false,
            "text": "Rainfall Region",
            "value": "rainfall_region"
          },
          {
            "selected": false,
            "text": "Subregion",
            "value": "subregion_region"
          },
          {
            "selected": false,
            "text": "Rainfall Region+Country",
            "value": "region"
          }
        ],
        "query": "Countries : country, Rainfall Region : rainfall_region, Subregion : subregion_region, Rainfall Region+Country : region",
        "type": "custom"
      },
      {
        "current": {
          "text": "Ghana",
          "value": "ghana"
        },
        "definition": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day = 0",
        "label": "First Region",
        "name": "region_option",
        "options": [],
        "query": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day = 0",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "Kenya",
          "value": "kenya"
        },
        "definition": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day = 0",
        "label": "Second Region",
        "name": "region_option2",
        "options": [],
        "query": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day = 0",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "6ff92e4dd5349c6a59868964ce479a78",
          "value": "6ff92e4dd5349c6a59868964ce479a78"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_metric_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "84b7eb24707bfdf37a9ca90cd3364d8f",
          "value": "84b7eb24707bfdf37a9ca90cd3364d8f"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_metric_fcst_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "cb67961274c40387afc3ccd3875a70d1",
          "value": "cb67961274c40387afc3ccd3875a70d1"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_shifted_metric_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "e190ca5c9e854e6edbccf8bb61ae9caa",
          "value": "e190ca5c9e854e6edbccf8bb61ae9caa"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_shifted_fcst_metric_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "525c534e50f08f616bcdba6d01630263",
          "value": "525c534e50f08f616bcdba6d01630263"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "bimodal_metric_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "13d2b8ebd4b50a0371a63c2de25610b6",
          "value": "13d2b8ebd4b50a0371a63c2de25610b6"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "hide": 2,
        "includeAll": false,
        "name": "bimodal_metric_fcst_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": true,
        "current": {
          "text": "20.0",
          "value": "20.0"
        },
        "definition": "SELECT\n  CASE '$metric'\n    WHEN 'early_season_accumulation-30d' THEN '30.0'\n    WHEN 'in_season_dry_spell'           THEN '20.0'\n    WHEN 'big_rain_days'                 THEN '0.3'\n    ELSE '0.0'\n  END",
        "description": "",
        "label": "Actionable Threshold",
        "name": "threshold",
        "options": [],
        "query": "SELECT\n  CASE '$metric'\n    WHEN 'early_season_accumulation-30d' THEN '30.0'\n    WHEN 'in_season_dry_spell'           THEN '20.0'\n    WHEN 'big_rain_days'                 THEN '0.3'\n    ELSE '0.0'\n  END",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "0.75",
          "value": "0.75"
        },
        "label": "KPI Threshold",
        "name": "color_threshold",
        "options": [
          {
            "selected": true,
            "text": "0.75",
            "value": "0.75"
          }
        ],
        "query": "0.75",
        "type": "textbox"
      },
      {
        "current": {
          "text": "points",
          "value": "points"
        },
        "hide": 2,
        "name": "display_metric",
        "options": [
          {
            "selected": true,
            "text": "Points",
            "value": "points"
          },
          {
            "selected": false,
            "text": "Values",
            "value": "value"
          }
        ],
        "query": "Points : points,Values : value",
        "type": "custom"
      },
      {
        "current": {
          "text": "both",
          "value": "both"
        },
        "description": "",
        "label": "Events Filter",
        "name": "source",
        "options": [
          {
            "selected": false,
            "text": "True / False Alarm",
            "value": "forecast"
          },
          {
            "selected": false,
            "text": "Detected / Missed Event",
            "value": "obs"
          },
          {
            "selected": true,
            "text": "Both",
            "value": "both"
          }
        ],
        "query": "True / False Alarm : forecast, Detected / Missed Event : obs, Both : both",
        "type": "custom"
      }
    ]
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "hidden": true
  },
  "timezone": "utc",
  "title": "Advanced Forecast Evaluation Tables",
  "uid": "cfoumv7uu5xq8f",
  "version": 1,
  "weekStart": ""
}
