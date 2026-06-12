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
        "h": 4,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 5,
      "options": {
        "afterRender": "// window.onload = function () {\n//     renderMathInElement(document.body, {\n//         delimiters: [\n//             { left: \"$$\", right: \"$$\", display: true },\n//             { left: \"\\\\(\", right: \"\\\\)\", display: false }\n//         ]\n//     });\n// };\n",
        "content": "### Selected Metric: {{#if (eq metric \"mae\")}}MAE {{/if}} {{#if (eq metric \"rmse\")}}RMSE{{/if}} {{#if (eq metric \"crps\")}}CRPS{{/if}} {{#if (eq metric \"bias\")}}Bias{{/if}} {{#if (eq metric \"smape\")}}SMAPE{{/if}} {{#if (eq metric \"seeps\")}}SEEPS{{/if}} {{#if (eq metric \"acc\")}}ACC{{/if}}  {{#if (eq metric \"heidke-1-5-10-20\")}}Heidke 1/5/10/20mm{{/if}} {{#if (eq metric \"far-1\")}}FAR 1mm{{/if}} {{#if (eq metric \"far-5\")}}FAR 5mm{{/if}} {{#if (eq metric \"far-10\")}}FAR 10mm{{/if}} {{#if (eq metric \"pod-1\")}}POD 1mm{{/if}} {{#if (eq metric \"pod-5\")}}POD 5mm{{/if}} {{#if (eq metric \"pod-10\")}}POD 10mm{{/if}} {{#if (eq metric \"ets-1\")}}ETS 1mm{{/if}} {{#if (eq metric \"ets-5\")}}ETS 5mm{{/if}} {{#if (eq metric \"ets-10\")}}ETS 10mm{{/if}}\n\n{{#if (eq metric \"mae\")}}\nMean absolute error (MAE) measures the average magnitude of the errors in a set of predictions, without considering\ntheir direction.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower MAE means better predictions.</span> \n\n{{else if (eq metric \"crps\")}}\nContinuous ranked probability score (CRPS) assesses the accuracy of probabilistic forecasts by comparing the cumulative\ndistribution function of forecasts to the observed values.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower CRPS indicates better probabilistic forecasting skill.</span>\n\n{{else if (eq metric \"rmse\")}}\nRoot mean squared error (RMSE) gives higher weight to large errors, making it more sensitive to outliers.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower RMSE means better predictions.</span>\n\n{{else if (eq metric \"acc\")}}\nAnomaly correlation coefficient (ACC) ACC is a measure of how well the forecast anomalies have represented the observed anomalies\nrelative to climatology. We used 1991-2020 climatology (years inclusive) for our ACC calculation.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — higher ACC means better predictions. Range [-1, 1].</span>\n\n{{else if (eq metric \"bias\")}}\nBias measures the signed magnitude of errors in a set of predictions. \\\n<span style=\"color: gray; font-weight: bold;\">⚪ Ideal value = 0.0 — Bias should be close to 0.0 for an unbiased forecast.</span>\n\n{{else if (eq metric \"smape\")}}\nSymmetric mean absolute percentage error (SMAPE) is a normalized version of Mean Absolute Percentage Error (MAPE) and calculate sthe error as a percentage of the total value. We only calculate SMAPE for precipitation.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower SMAPE indicates better forecasting accuracy. Range [0, 1].</span>\n\n{{else if (eq metric \"seeps\")}}\nStable equitable error in probability space (SEEPS) is a score designed for evaluating rainfall forecasts while taking into account climactic difference in rainfall. Areas that are too dry or wet are exclued. \nWe include all cells with a 3-93% non-dry day frequency to ensure inclusion of relevant parts of Africa. We only calculate SEEPS for precipitation.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower SEEPS indicates better forecasting accuracy. Good SEEPS for short term forecasts on cells that have 10-85% non-dry days are considered between 0-1.</span>\n\n{{else if (eq metric \"heidke-1-5-10-20\")}}\nHeidke skill score (HSS) compares the accuracy of a forecast to random chance for a set of predetermined rainfall thresholds—in this case, 1, 5, 10, and 20mm. We only calculate Heidke for precipitation.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — a higher HSS indicates better skill. Range [-&infin;, 1]</span>\n\n{{else if (or (eq metric \"pod-1\") (or (eq metric \"pod-5\") (eq metric \"pod-10\")))}}\nProbability of detection (POD) measures the fraction of observed rainfall events that were correctly predicted—in this case, a weekly average daily rainfall of over 1, 5, or 10mm. We only calculate POD for precipitation. \\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — higher probability of detection is better. Range [0, 1]. </span>\n\n{{else if (or (eq metric \"far-1\") (or (eq metric \"far-5\") (eq metric \"far-10\")))}}\nFalse alarm rate (FAR) quantifies the fraction of predicted rainfall events that were not observed—in this case, a weekly average daily rainfall of over 1, 5, or 10mm. We only calculate FAR for precipitation.\\ \n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower false alarm rate is better. Range [0, 1].</span>\n\n{{else if (or (eq metric \"ets-1\") (or (eq metric \"ets-5\") (eq metric \"ets-10\")))}}\nEquitable threat score (ETS) measures a combination of POD and FAR while accounting for random chance on a specific event—in this case, a weekly average daily rainfall of over 1, 5, or 10mm. We only calculate ETS for precipitation. \\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — higher ETS indicates better skill. Range [-1/3, 1].</span>\n\n{{else}}\n_no description available for this metric._\n{{/if}}\n",
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
        "y": 4
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
      "collapsed": false,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 5
      },
      "id": 9,
      "panels": [],
      "title": "Metrics",
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
        "script": "// Returns green if ratio >= colorThreshold, red gradient otherwise\nfunction getThresholdColor(ratio, colorThreshold) {\n    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';\n    if (ratio >= colorThreshold) {\n        return 'rgba(56, 168, 83, 0.5)'; // green\n    }\n    // Red gradient: 0 -> deep red, approaching threshold -> light red\n    const t = ratio / colorThreshold;\n    const r = 220;\n    const g = Math.round(50 + t * 140);\n    const b = Math.round(50 + t * 140);\n    return `rgba(${r}, ${g}, ${b}, 0.5)`;\n}\n\nconst renameDict = {\n    \"Ecmwf Ifs Er\": \"ECMWF IFS ER\",\n    \"Ecmwf Ifs Ens\": \"ECMWF IFS ENS\",\n    \"Ecmwf Ifs Er Debiased\": \"ECMWF IFS ER Debiased\",\n    \"Ecmwf Aifs\": \"ECMWF AIFS\",\n    \"Ecmwf Hres\": \"ECMWF HRES\",\n    \"Gfs\": \"GFS\",\n    \"Salient\": \"AI-Enhanced NWP\",\n    \"Fuxi\": \"FuXi S2S\",\n    \"Climatology 2015\": \"Climatology 1985-2014\",\n    \"Climatology Trend 2015\": \"Climatology 1985-2014 w/Trend\"\n};\n\nfunction titleCase(str) {\n    let name = str.replaceAll('_', ' ')\n        .split(' ')\n        .map(w => w[0].toUpperCase() + w.substring(1))\n        .join(' ');\n    return renameDict[name] || name;\n}\n\n// ── Data check ───────────────────────────────────────────────────────────────\nlet series = data.series[0];\nif (!series || series.fields.length === 0) return { data: [] };\n\n// ── Parse long-format fields ─────────────────────────────────────────────────\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst fieldNames       = series.fields.map(f => f.name);\nconst forecastField    = series.fields[fieldNames.indexOf('forecast')].values;\nconst leadDayField     = series.fields[fieldNames.indexOf('lead_day')].values;\nconst pointsField      = getField(series.fields, 'points_above_threshold');\nconst pointsTotalField = getField(series.fields, 'points_total');\nconst metricMeanField  = getField(series.fields, 'metric_mean');\n\n// ── Build lookup: forecast -> lead_day -> { points, pointsTotal, metricMean } ──\nconst dataMap = {};\nfor (let i = 0; i < forecastField.length; i++) {\n    const f  = forecastField[i];\n    const ld = leadDayField[i];\n    if (!dataMap[f]) dataMap[f] = {};\n    dataMap[f][ld] = {\n        points:      pointsField[i],\n        pointsTotal: pointsTotalField[i],\n        metricMean:  metricMeanField[i]\n    };\n}\n\nconst uniqueForecasts = [...new Set(forecastField)];\nconst uniqueLeadDays  = [...new Set(leadDayField)].sort((a, b) => a - b);\n\n// display_metric: 'points' (default) shows X / Y count, 'value' shows mean\nconst displayMetric = variables?.display_metric?.current?.value || 'points';\nconst metricLabel = displayMetric === 'value' ? 'Mean value' : 'Points (avg < threshold)';\n\n// Color threshold — driven by Grafana variable color_threshold (e.g. 0.8), defaults to 0.8\nconst colorThreshold = parseFloat(variables?.color_threshold?.current?.value) || 0.8;\n\n// ── Build header and value columns ───────────────────────────────────────────\nconst header      = [\"Forecast\", ...uniqueLeadDays.map(ld => `Day ${ld}`)];\nconst orig_header = [\"forecast\", ...uniqueLeadDays.map(ld => `lead_${ld}`)];\n\nconst forecastNames = uniqueForecasts.map(titleCase);\nconst values  = [forecastNames];  // values[0] = forecast names, values[1..] = lead_day columns\nconst ratios  = [];               // numeric ratios for coloring, parallel to values[1..]\n\nfor (const ld of uniqueLeadDays) {\n    const col      = [];\n    const ratioCol = [];\n    for (const f of uniqueForecasts) {\n        const d = dataMap[f]?.[ld];\n        if (!d) {\n            col.push('-');\n            ratioCol.push(null);\n        } else if (displayMetric === 'value') {\n            const v = d.metricMean;\n            if (v == null) {\n                col.push('-');\n                ratioCol.push(null);\n            } else {\n                col.push(parseFloat(v).toFixed(3));\n                ratioCol.push(parseFloat(v));\n            }\n        } else {\n            const num   = d.points;\n            const denom = d.pointsTotal;\n            if (denom === 0 || denom == null) {\n                col.push('-');\n                ratioCol.push(null);\n            } else {\n                const ratio = num / denom;\n                col.push(`${num} / ${denom}`);\n                ratioCol.push(ratio);\n            }\n        }\n    }\n    values.push(col);\n    ratios.push(ratioCol);\n}\n\n// ── Colors ───────────────────────────────────────────────────────────────────\nconst forecast_colors = uniqueForecasts.map(() => 'rgba(0,0,0,0)');\n\nlet skill_colors;\nif (displayMetric === 'value') {\n    // Scale color across the observed min/max range\n    const allRatios = ratios.flat().filter(v => v != null && !isNaN(v));\n    const minVal = Math.min(...allRatios);\n    const maxVal = Math.max(...allRatios);\n    const range  = maxVal - minVal || 1;\n    skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(v => {\n            if (v == null || isNaN(v)) return 'rgba(255,255,255,0)';\n            const normalized = (v - minVal) / range;  // 0 = best (low), 1 = worst (high)\n            return getThresholdColor(1 - normalized, colorThreshold);\n        })\n    );\n} else {\n    skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(ratio => getThresholdColor(ratio, colorThreshold))\n    );\n}\n\n// ── Links ────────────────────────────────────────────────────────────────────\nconst metric        = variables.metric.current.value;\nconst grid          = variables.grid.current.value;\nconst region        = variables.region.current.value;\nconst time_grouping = variables.time_grouping.current.value;\nconst time_filter   = variables.time_option.current.value;\n\nfor (let i = 1; i < values.length; i++) {\n    const ld = uniqueLeadDays[i - 1];\n    for (let j = 0; j < values[i].length; j++) {\n        const url = `d/ae39q2k3jv668d/plotly-maps?orgId=1` +\n            `&var-forecast=${uniqueForecasts[j]}` +\n            `&var-metric=${metric}` +\n            `&var-lead=lead_${ld}` +\n            `&var-truth=era5` +\n            `&var-grid=${grid}` +\n            `&var-region=${region}` +\n            `&var-time_grouping=${time_grouping}` +\n            `&var-time_filter=${time_filter}`;\n        values[i][j] = `<a href=\"${url}\">${values[i][j]}</a>`;\n    }\n}\n\n// ── Divider after 2nd lead-day column ────────────────────────────────────────\nconst dividerAt = 2; // insert divider after this many lead-day columns\n\nconst headerWithDiv = [\n    ...header.slice(0, dividerAt + 1),\n    '',\n    ...header.slice(dividerAt + 1)\n];\nconst valuesWithDiv = [\n    ...values.slice(0, dividerAt + 1),\n    Array(uniqueForecasts.length).fill(''),\n    ...values.slice(dividerAt + 1)\n];\nconst colorsWithDiv = [\n    forecast_colors,\n    ...skill_colors.slice(0, dividerAt),\n    Array(uniqueForecasts.length).fill('rgba(200,200,200,0.3)'),\n    ...skill_colors.slice(dividerAt)\n];\n\nconst colWidth = [1.4, ...uniqueLeadDays.map(() => 0.5)];\ncolWidth.splice(dividerAt + 1, 0, 0.05);\n\n// ── Return ────────────────────────────────────────────────────────────────────\nreturn {\n    data: [{\n        type: 'table',\n        header: {\n            values: headerWithDiv,\n            align: ['left', ...uniqueLeadDays.map(() => 'right'), 'right'],\n            line: { width: 0, color: '#DBDDDE' },\n            font: { family: \"Inter, sans-serif\", size: 14, weight: \"bold\" },\n            fill: { color: ['rgba(0,0,0,0)'] }\n        },\n        cells: {\n            values: valuesWithDiv,\n            align: ['left', ...uniqueLeadDays.map(() => 'right'), 'right'],\n            line: { width: 1, color: \"#DBDDDE\" },\n            font: { family: \"Inter, sans-serif\", size: 14, color: [\"black\"] },\n            fill: { color: colorsWithDiv },\n            height: 35\n        },\n        columnwidth: colWidth\n    }],\n    layout: {\n        title: {\n            text: `Cells meeting threshold — ${metricLabel} (above / total)`,\n            xanchor: 'left',\n            x: 0\n        }\n    }\n};",
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
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    AVG(${metric}) AS metric_avg\n  FROM \"$metric_tab_name\"\n  WHERE\n    COALESCE(time_grouping, 'None') IN (${time_option})\n    AND $region = '$region_option'\n    AND lead_day IN (7, 14, 21, 28, 35, 42)\n  GROUP BY forecast, $region, lead_day, lat, lon\n)\nSELECT\n  -- display_metric: $display_metric\n  -- threshold: $threshold\n  forecast,\n  $region,\n  lead_day,\n  COUNT(CASE WHEN metric_avg < ${threshold} THEN 1 END)  AS points_above_threshold,\n  COUNT(metric_avg)                                        AS points_total,\n  AVG(metric_avg)                                          AS metric_mean\nFROM cell_avgs\nGROUP BY forecast, $region, lead_day\nORDER BY forecast, $region, lead_day",
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
      "id": 13,
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
        "script": "// Returns green if ratio >= colorThreshold, red gradient otherwise\nfunction getThresholdColor(ratio, colorThreshold) {\n    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';\n    if (ratio >= colorThreshold) {\n        return 'rgba(56, 168, 83, 0.5)'; // green\n    }\n    // Red gradient: 0 -> deep red, approaching threshold -> light red\n    const t = ratio / colorThreshold;\n    const r = 220;\n    const g = Math.round(50 + t * 140);\n    const b = Math.round(50 + t * 140);\n    return `rgba(${r}, ${g}, ${b}, 0.5)`;\n}\n\nconst renameDict = {\n    \"Ecmwf Ifs Er\": \"ECMWF IFS ER\",\n    \"Ecmwf Ifs Ens\": \"ECMWF IFS ENS\",\n    \"Ecmwf Ifs Er Debiased\": \"ECMWF IFS ER Debiased\",\n    \"Ecmwf Aifs\": \"ECMWF AIFS\",\n    \"Ecmwf Hres\": \"ECMWF HRES\",\n    \"Gfs\": \"GFS\",\n    \"Salient\": \"AI-Enhanced NWP\",\n    \"Fuxi\": \"FuXi S2S\",\n    \"Climatology 2015\": \"Climatology 1985-2014\",\n    \"Climatology Trend 2015\": \"Climatology 1985-2014 w/Trend\"\n};\n\nfunction titleCase(str) {\n    let name = str.replaceAll('_', ' ')\n        .split(' ')\n        .map(w => w[0].toUpperCase() + w.substring(1))\n        .join(' ');\n    return renameDict[name] || name;\n}\n\n// ── Data check ───────────────────────────────────────────────────────────────\nlet series = data.series[0];\nif (!series || series.fields.length === 0) return { data: [] };\n\n// ── Parse long-format fields ─────────────────────────────────────────────────\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst fieldNames       = series.fields.map(f => f.name);\nconst forecastField    = series.fields[fieldNames.indexOf('forecast')].values;\nconst leadDayField     = series.fields[fieldNames.indexOf('lead_day')].values;\nconst pointsField      = getField(series.fields, 'points_above_threshold');\nconst pointsTotalField = getField(series.fields, 'points_total');\nconst metricMeanField  = getField(series.fields, 'metric_mean');\n\n// ── Build lookup: forecast -> lead_day -> { points, pointsTotal, metricMean } ──\nconst dataMap = {};\nfor (let i = 0; i < forecastField.length; i++) {\n    const f  = forecastField[i];\n    const ld = leadDayField[i];\n    if (!dataMap[f]) dataMap[f] = {};\n    dataMap[f][ld] = {\n        points:      pointsField[i],\n        pointsTotal: pointsTotalField[i],\n        metricMean:  metricMeanField[i]\n    };\n}\n\nconst uniqueForecasts = [...new Set(forecastField)];\nconst uniqueLeadDays  = [...new Set(leadDayField)].sort((a, b) => a - b);\n\n// display_metric: 'points' (default) shows X / Y count, 'value' shows mean\nconst displayMetric = variables?.display_metric?.current?.value || 'points';\nconst metricLabel = displayMetric === 'value' ? 'Mean value' : 'Points (avg < threshold)';\n\n// Color threshold — driven by Grafana variable color_threshold (e.g. 0.8), defaults to 0.8\nconst colorThreshold = parseFloat(variables?.color_threshold?.current?.value) || 0.8;\n\n// ── Build header and value columns ───────────────────────────────────────────\nconst header      = [\"Forecast\", ...uniqueLeadDays.map(ld => `Day ${ld}`)];\nconst orig_header = [\"forecast\", ...uniqueLeadDays.map(ld => `lead_${ld}`)];\n\nconst forecastNames = uniqueForecasts.map(titleCase);\nconst values  = [forecastNames];  // values[0] = forecast names, values[1..] = lead_day columns\nconst ratios  = [];               // numeric ratios for coloring, parallel to values[1..]\n\nfor (const ld of uniqueLeadDays) {\n    const col      = [];\n    const ratioCol = [];\n    for (const f of uniqueForecasts) {\n        const d = dataMap[f]?.[ld];\n        if (!d) {\n            col.push('-');\n            ratioCol.push(null);\n        } else if (displayMetric === 'value') {\n            const v = d.metricMean;\n            if (v == null) {\n                col.push('-');\n                ratioCol.push(null);\n            } else {\n                col.push(parseFloat(v).toFixed(3));\n                ratioCol.push(parseFloat(v));\n            }\n        } else {\n            const num   = d.points;\n            const denom = d.pointsTotal;\n            if (denom === 0 || denom == null) {\n                col.push('-');\n                ratioCol.push(null);\n            } else {\n                const ratio = num / denom;\n                col.push(`${num} / ${denom}`);\n                ratioCol.push(ratio);\n            }\n        }\n    }\n    values.push(col);\n    ratios.push(ratioCol);\n}\n\n// ── Colors ───────────────────────────────────────────────────────────────────\nconst forecast_colors = uniqueForecasts.map(() => 'rgba(0,0,0,0)');\n\nlet skill_colors;\nif (displayMetric === 'value') {\n    // Scale color across the observed min/max range\n    const allRatios = ratios.flat().filter(v => v != null && !isNaN(v));\n    const minVal = Math.min(...allRatios);\n    const maxVal = Math.max(...allRatios);\n    const range  = maxVal - minVal || 1;\n    skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(v => {\n            if (v == null || isNaN(v)) return 'rgba(255,255,255,0)';\n            const normalized = (v - minVal) / range;  // 0 = best (low), 1 = worst (high)\n            return getThresholdColor(1 - normalized, colorThreshold);\n        })\n    );\n} else {\n    skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(ratio => getThresholdColor(ratio, colorThreshold))\n    );\n}\n\n// ── Links ────────────────────────────────────────────────────────────────────\nconst metric        = variables.metric.current.value;\nconst grid          = variables.grid.current.value;\nconst region        = variables.region.current.value;\nconst time_grouping = variables.time_grouping.current.value;\nconst time_filter   = variables.time_option.current.value;\n\nfor (let i = 1; i < values.length; i++) {\n    const ld = uniqueLeadDays[i - 1];\n    for (let j = 0; j < values[i].length; j++) {\n        const url = `d/ae39q2k3jv668d/plotly-maps?orgId=1` +\n            `&var-forecast=${uniqueForecasts[j]}` +\n            `&var-metric=${metric}` +\n            `&var-lead=lead_${ld}` +\n            `&var-truth=era5` +\n            `&var-grid=${grid}` +\n            `&var-region=${region}` +\n            `&var-time_grouping=${time_grouping}` +\n            `&var-time_filter=${time_filter}`;\n        values[i][j] = `<a href=\"${url}\">${values[i][j]}</a>`;\n    }\n}\n\n// ── Divider after 2nd lead-day column ────────────────────────────────────────\nconst dividerAt = 2; // insert divider after this many lead-day columns\n\nconst headerWithDiv = [\n    ...header.slice(0, dividerAt + 1),\n    '',\n    ...header.slice(dividerAt + 1)\n];\nconst valuesWithDiv = [\n    ...values.slice(0, dividerAt + 1),\n    Array(uniqueForecasts.length).fill(''),\n    ...values.slice(dividerAt + 1)\n];\nconst colorsWithDiv = [\n    forecast_colors,\n    ...skill_colors.slice(0, dividerAt),\n    Array(uniqueForecasts.length).fill('rgba(200,200,200,0.3)'),\n    ...skill_colors.slice(dividerAt)\n];\n\nconst colWidth = [1.4, ...uniqueLeadDays.map(() => 0.5)];\ncolWidth.splice(dividerAt + 1, 0, 0.05);\n\n// ── Return ────────────────────────────────────────────────────────────────────\nreturn {\n    data: [{\n        type: 'table',\n        header: {\n            values: headerWithDiv,\n            align: ['left', ...uniqueLeadDays.map(() => 'right'), 'right'],\n            line: { width: 0, color: '#DBDDDE' },\n            font: { family: \"Inter, sans-serif\", size: 14, weight: \"bold\" },\n            fill: { color: ['rgba(0,0,0,0)'] }\n        },\n        cells: {\n            values: valuesWithDiv,\n            align: ['left', ...uniqueLeadDays.map(() => 'right'), 'right'],\n            line: { width: 1, color: \"#DBDDDE\" },\n            font: { family: \"Inter, sans-serif\", size: 14, color: [\"black\"] },\n            fill: { color: colorsWithDiv },\n            height: 35\n        },\n        columnwidth: colWidth\n    }],\n    layout: {\n        title: {\n            text: `Cells meeting threshold — ${metricLabel} (above / total)`,\n            xanchor: 'left',\n            x: 0\n        }\n    }\n};",
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
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    AVG(${metric}) AS metric_avg\n  FROM \"$metric_tab_name\"\n  WHERE\n    COALESCE(time_grouping, 'None') IN (${time_option})\n    AND $region = '$region_option2'\n    AND lead_day IN (7, 14, 21, 28, 35, 42)\n  GROUP BY forecast, $region, lead_day, lat, lon\n)\nSELECT\n  -- display_metric: $display_metric\n  -- threshold: $threshold\n  forecast,\n  $region,\n  lead_day,\n  COUNT(CASE WHEN metric_avg < ${threshold} THEN 1 END)  AS points_above_threshold,\n  COUNT(metric_avg)                                        AS points_total,\n  AVG(metric_avg)                                          AS metric_mean\nFROM cell_avgs\nGROUP BY forecast, $region, lead_day\nORDER BY forecast, $region, lead_day",
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
            "Y2018"
          ],
          "value": [
            "Y2018"
          ]
        },
        "definition": "SELECT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"$metric_tab_name\" \nWHERE lead_day = 0;",
        "label": "Time Period",
        "multi": true,
        "name": "time_option",
        "options": [],
        "query": "SELECT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"$metric_tab_name\" \nWHERE lead_day = 0;",
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
            "text": "Rainfall Region+Country",
            "value": "country_rainfall_region"
          }
        ],
        "query": "Countries : country, Rainfall Region : rainfall_region, Rainfall Region+Country : country_rainfall_region",
        "type": "custom"
      },
      {
        "current": {
          "text": "Nigeria",
          "value": "nigeria"
        },
        "definition": "SELECT\n    DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text,\n    \"$region\" AS __value\nFROM \"$metric_tab_name\"\nWHERE lead_day = 0",
        "label": "First Region",
        "name": "region_option",
        "options": [],
        "query": "SELECT\n    DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text,\n    \"$region\" AS __value\nFROM \"$metric_tab_name\"\nWHERE lead_day = 0",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "Burkina Faso",
          "value": "burkina_faso"
        },
        "definition": "SELECT\n    DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text,\n    \"$region\" AS __value\nFROM \"$metric_tab_name\"\nWHERE lead_day = 0",
        "label": "Second Region",
        "name": "region_option2",
        "options": [],
        "query": "SELECT\n    DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text,\n    \"$region\" AS __value\nFROM \"$metric_tab_name\"\nWHERE lead_day = 0",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "27bae4d31fa2ef84983b50999931f9f7",
          "value": "27bae4d31fa2ef84983b50999931f9f7"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "metric_tab_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "0.3",
          "value": "0.3"
        },
        "label": "Good Threshold",
        "name": "threshold",
        "options": [
          {
            "selected": true,
            "text": "0.3",
            "value": "0.3"
          }
        ],
        "query": "0.3",
        "type": "textbox"
      },
      {
        "current": {
          "text": "0.75",
          "value": "0.75"
        },
        "hide": 2,
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
          "text": "value",
          "value": "value"
        },
        "name": "display_metric",
        "options": [
          {
            "selected": false,
            "text": "Points",
            "value": "points"
          },
          {
            "selected": true,
            "text": "Values",
            "value": "value"
          }
        ],
        "query": "Points : points,Values : value",
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
