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
        "h": 9,
        "w": 8,
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
        "script": "function getThresholdColor(ratio, colorThreshold) {\n    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';\n    const t = Math.min(1, Math.max(0, ratio));\n    let r, g, b;\n    if (t <= colorThreshold) {\n        const s = t / colorThreshold;\n        r = Math.round(220 + s * (255 - 220));\n        g = Math.round(50  + s * (253 - 50));\n        b = Math.round(50  + s * (220 - 50));\n    } else {\n        const s = (t - colorThreshold) / (1 - colorThreshold);\n        r = Math.round(255 + s * (56  - 255));\n        g = Math.round(253 + s * (168 - 253));\n        b = Math.round(220 + s * (83  - 220));\n    }\n    return `rgba(${r}, ${g}, ${b}, 0.5)`;\n}\n\nconst renameDict = {\n    \"Ecmwf Ifs Er\": \"ECMWF IFS ER\",\n    \"Ecmwf Ifs Ens\": \"ECMWF IFS ENS\",\n    \"Ecmwf Ifs Er Debiased\": \"ECMWF IFS ER Debiased\",\n    \"Ecmwf Aifs\": \"ECMWF AIFS\",\n    \"Ecmwf Hres\": \"ECMWF HRES\",\n    \"Gfs\": \"GFS\",\n    \"Salient\": \"AI-Enhanced NWP\",\n    \"Fuxi\": \"FuXi S2S\",\n    \"Climatology 2015\": \"Climatology 1985-2014\",\n    \"Climatology Trend 2015\": \"Climatology 1985-2014 w/Trend\",\n    \"Climatology Era5 1985 2015\": \"Climatology ERA5 1985-2014\",\n    \"Climatology Imerg 1998 2016\": \"Climatology IMERG 1998-2015\",\n    \"Cumulus Ai\": \"Cumulus AI v0.0.0\",\n};\n\nfunction titleCase(str) {\n    let name = str.replaceAll('_', ' ')\n        .split(' ')\n        .map(w => w[0].toUpperCase() + w.substring(1))\n        .join(' ');\n    return renameDict[name] || name;\n}\n\n// ── Data check ────────────────────────────────────────────────────────────────\nlet series = data.series[0];\nif (!series || series.fields.length === 0) return { data: [] };\n\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst fieldNames       = series.fields.map(f => f.name);\nconst forecastField    = series.fields[fieldNames.indexOf('forecast')].values;\nconst pointsField      = getField(series.fields, 'points_above_threshold');\nconst pointsTotalField = getField(series.fields, 'points_total');\nconst metricMeanField  = getField(series.fields, 'metric_mean');\n\n// ── Build lookup: forecast -> { points, pointsTotal, metricMean } ─────────────\nconst dataMap = {};\nfor (let i = 0; i < forecastField.length; i++) {\n    const f = forecastField[i];\n    dataMap[f] = {\n        points:      pointsField[i],\n        pointsTotal: pointsTotalField[i],\n        metricMean:  metricMeanField[i]\n    };\n}\n\nconst uniqueForecasts = [...new Set(forecastField)];\n\nconst displayMetric  = variables?.display_metric?.current?.value || 'points';\nconst metricLabel    = displayMetric === 'value' ? 'Mean value' : 'Points (avg < threshold)';\nconst colorThreshold = parseFloat(variables?.color_threshold?.current?.value) || 0.8;\n\n// ── Build value and ratio columns ─────────────────────────────────────────────\nconst forecastNames = uniqueForecasts.map(titleCase);\nconst metricCol  = [];\nconst ratioCol   = [];\n\nfor (const f of uniqueForecasts) {\n    const d = dataMap[f];\n    if (!d) {\n        metricCol.push('-');\n        ratioCol.push(null);\n    } else if (displayMetric === 'value') {\n        const v = d.metricMean;\n        if (v == null) {\n            metricCol.push('-');\n            ratioCol.push(null);\n        } else {\n            metricCol.push(parseFloat(v).toFixed(3));\n            ratioCol.push(parseFloat(v));\n        }\n    } else {\n        const num   = d.points;\n        const denom = d.pointsTotal;\n        if (denom === 0 || denom == null) {\n            metricCol.push('-');\n            ratioCol.push(null);\n        } else {\n            const ratio = num / denom;\n            metricCol.push(`${num} / ${denom}`);\n            ratioCol.push(ratio);\n        }\n    }\n}\n\n// ── Colors ────────────────────────────────────────────────────────────────────\nconst forecastColors = uniqueForecasts.map(() => 'rgba(0,0,0,0)');\nlet skillColors;\n\nif (displayMetric === 'value') {\n    const allRatios = ratioCol.filter(v => v != null && !isNaN(v));\n    const minVal = Math.min(...allRatios);\n    const maxVal = Math.max(...allRatios);\n    const range  = maxVal - minVal || 1;\n    skillColors = ratioCol.map(v => {\n        if (v == null || isNaN(v)) return 'rgba(255,255,255,0)';\n        return getThresholdColor(1 - (v - minVal) / range, colorThreshold);\n    });\n} else {\n    skillColors = ratioCol.map(ratio => getThresholdColor(ratio, colorThreshold));\n}\n\n// ── Links ─────────────────────────────────────────────────────────────────────\nconst metric        = variables.metric.current.value;\nconst grid          = variables.grid.current.value;\nconst region        = variables.region.current.value;\nconst time_grouping = variables.time_grouping.current.value;\nconst time_filter   = variables.time_option.current.value;\n\nconst linkedMetricCol = metricCol.map((val, j) => {\n    const url = `d/ae39q2k3jv668d/plotly-maps?orgId=1` +\n        `&var-forecast=${uniqueForecasts[j]}` +\n        `&var-metric=${metric}` +\n        `&var-truth=era5` +\n        `&var-grid=${grid}` +\n        `&var-region=${region}` +\n        `&var-time_grouping=${time_grouping}` +\n        `&var-time_filter=${time_filter}`;\n    return `<a href=\"${url}\">${val}</a>`;\n});\n\n// ── Return ────────────────────────────────────────────────────────────────────\nreturn {\n    data: [{\n        type: 'table',\n        header: {\n            values: ['Forecast', metricLabel],\n            align: ['left', 'right'],\n            line: { width: 0, color: '#DBDDDE' },\n            font: { family: \"Inter, sans-serif\", size: 14, weight: \"bold\" },\n            fill: { color: ['rgba(0,0,0,0)'] }\n        },\n        cells: {\n            values: [forecastNames, linkedMetricCol],\n            align: ['left', 'right'],\n            line: { width: 1, color: \"#DBDDDE\" },\n            font: { family: \"Inter, sans-serif\", size: 14, color: [\"black\"] },\n            fill: { color: [forecastColors, skillColors] },\n            height: 35\n        },\n        columnwidth: [1.4, 1.0]\n    }],\n    layout: {\n        title: {\n            text: `Cells meeting threshold — ${metricLabel} (above / total)`,\n            xanchor: 'left',\n            x: 0\n        }\n    }\n};",
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
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, lat, lon\n  ) combined\n  GROUP BY forecast, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_fcst_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, lat, lon\n  ) combined\n  GROUP BY forecast, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, lat, lon\n  ) combined\n  GROUP BY forecast, lat, lon\n)\nSELECT\n  -- display_metric: $display_metric\n  -- threshold: $threshold\n  -- color_threshold: $color_threshold\n  forecast,\n  COUNT(CASE WHEN metric_avg < ${threshold}::float THEN 1 END)  AS points_above_threshold,\n  COUNT(metric_avg)                                               AS points_total,\n  AVG(metric_avg)                                                 AS metric_mean\nFROM cell_avgs\nGROUP BY forecast\nORDER BY forecast",
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
          "text": "big_rain_days",
          "value": "big_rain_days"
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
            "selected": true,
            "text": "Large rain days",
            "value": "big_rain_days"
          },
          {
            "selected": false,
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
            "Y2019",
            "Y2016",
            "Y2022",
            "Y2017",
            "Y2018",
            "Y2023",
            "Y2021",
            "Y2024",
            "Y2020"
          ],
          "value": [
            "Y2019",
            "Y2016",
            "Y2022",
            "Y2017",
            "Y2018",
            "Y2023",
            "Y2021",
            "Y2024",
            "Y2020"
          ]
        },
        "definition": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"",
        "label": "Time Period",
        "multi": true,
        "name": "time_option",
        "options": [],
        "query": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "tahmo_avg",
          "value": "tahmo_avg"
        },
        "includeAll": false,
        "label": "Ground Truth",
        "name": "truth",
        "options": [
          {
            "selected": true,
            "text": "tahmo_avg",
            "value": "tahmo_avg"
          }
        ],
        "query": "tahmo_avg",
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
        "hide": 2,
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
          "text": "Nigeria",
          "value": "nigeria"
        },
        "definition": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" \n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" \n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\"",
        "hide": 2,
        "label": "First Region",
        "name": "region_option",
        "options": [],
        "query": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" \n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" \n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\"",
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
        "definition": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\"\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\"\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\"",
        "hide": 2,
        "label": "Second Region",
        "name": "region_option2",
        "options": [],
        "query": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\"\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\"\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\"",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "3373253bda65a96f6a4987be5f056179",
          "value": "3373253bda65a96f6a4987be5f056179"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_metric_name",
        "options": [],
        "query": "select * from md5('advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "8846ed0ccac09bd9268d2bef46fbb61b",
          "value": "8846ed0ccac09bd9268d2bef46fbb61b"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_metric_fcst_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "e41f8a25bd14cd115fb725b6a4db2ca5",
          "value": "e41f8a25bd14cd115fb725b6a4db2ca5"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_shifted_metric_name",
        "options": [],
        "query": "select * from md5('advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "fe26a885350b36f644e9fdd1b7328650",
          "value": "fe26a885350b36f644e9fdd1b7328650"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_shifted_fcst_metric_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "dbfd92a08089a83b7c5f69e2f9a922f5",
          "value": "dbfd92a08089a83b7c5f69e2f9a922f5"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "bimodal_metric_name",
        "options": [],
        "query": "select * from md5('advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "4e4cdd86dcf656d1158f7acfa867607e",
          "value": "4e4cdd86dcf656d1158f7acfa867607e"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "hide": 2,
        "includeAll": false,
        "name": "bimodal_metric_fcst_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_ground_truth_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": true,
        "current": {
          "text": "0.3",
          "value": "0.3"
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
            "text": "Forecasted events",
            "value": "forecast"
          },
          {
            "selected": false,
            "text": "Observed events",
            "value": "obs"
          },
          {
            "selected": true,
            "text": "Both",
            "value": "both"
          }
        ],
        "query": "Forecasted events : forecast, Observed events : obs, Both : both",
        "type": "custom"
      },
      {
        "current": {
          "text": "None",
          "value": "None"
        },
        "hide": 2,
        "label": "time_filter",
        "name": "time_filter",
        "options": [
          {
            "selected": true,
            "text": "None",
            "value": "None"
          }
        ],
        "query": "None",
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
  "title": "Advanced Ground Truth Evaluation Tables",
  "uid": "afp4iqj8sm22oe",
  "version": 1,
  "weekStart": ""
}
