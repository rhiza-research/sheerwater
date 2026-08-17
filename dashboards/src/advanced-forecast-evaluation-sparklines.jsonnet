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
        "h": 19,
        "w": 16,
        "x": 0,
        "y": 0
      },
      "id": 17,
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
        "script": "function getThresholdColor(ratio, colorThreshold) {\n    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';\n    const t = Math.min(1, Math.max(0, ratio));\n    let r, g, b;\n    if (t <= colorThreshold) {\n        const s = t / colorThreshold;\n        r = Math.round(220 + s * (255 - 220));\n        g = Math.round(50  + s * (253 - 50));\n        b = Math.round(50  + s * (220 - 50));\n    } else {\n        const s = (t - colorThreshold) / (1 - colorThreshold);\n        r = Math.round(255 + s * (56  - 255));\n        g = Math.round(253 + s * (168 - 253));\n        b = Math.round(220 + s * (83  - 220));\n    }\n    return `rgba(${r}, ${g}, ${b}, 0.5)`;\n}\n\nconst renameDict = {\n    \"Ecmwf Ifs Er\": \"ECMWF IFS ER\",\n    \"Ecmwf Ifs Ens\": \"ECMWF IFS ENS\",\n    \"Ecmwf Ifs Er Debiased\": \"ECMWF IFS ER Debiased\",\n    \"Ecmwf Aifs\": \"ECMWF AIFS\",\n    \"Ecmwf Hres\": \"ECMWF HRES\",\n    \"Gfs\": \"GFS\",\n    \"Salient\": \"AI-Enhanced NWP\",\n    \"Fuxi\": \"FuXi S2S\",\n    \"Climatology 2015\": \"Climatology 1985-2014\",\n    \"Climatology Trend 2015\": \"Climatology 1985-2014 w/Trend\",\n    \"Climatology Era5 1985 2015\": \"Climatology ERA5 1985-2014\",\n    \"Climatology Imerg 1998 2016\": \"Climatology IMERG 1998-2015\",\n    \"Cumulus Ai\": \"Cumulus AI v0.0.0\",\n};\n\nfunction titleCase(str) {\n    let name = str.replaceAll('_', ' ').split(' ').map(w => w[0].toUpperCase() + w.substring(1)).join(' ');\n    return renameDict[name] || name;\n}\n\n// ── Data check ────────────────────────────────────────────────────────────────\nlet series = data.series[0];\nif (!series || series.fields.length === 0) return { data: [] };\n\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst fieldNames       = series.fields.map(f => f.name);\nconst forecastField    = series.fields[fieldNames.indexOf('forecast')].values;\nconst leadDayField     = series.fields[fieldNames.indexOf('lead_day')].values;\nconst yearField        = getField(series.fields, 'time_grouping');\nconst p0Field          = getField(series.fields, 'p0');\nconst q1Field          = getField(series.fields, 'q1');\nconst medianField      = getField(series.fields, 'median');\nconst q3Field          = getField(series.fields, 'q3');\nconst p100Field        = getField(series.fields, 'p100');\nconst pointsField      = getField(series.fields, 'points_above_threshold');\nconst pointsTotalField = getField(series.fields, 'points_total');\n\n// ── Build lookup: forecast -> lead_day -> year -> {...} ───────────────────────\nconst dataMap = {};\nfor (let i = 0; i < forecastField.length; i++) {\n    const f  = forecastField[i];\n    const ld = leadDayField[i];\n    const yr = yearField[i];\n    if (!dataMap[f])     dataMap[f]     = {};\n    if (!dataMap[f][ld]) dataMap[f][ld] = {};\n    dataMap[f][ld][yr] = {\n        p0:          p0Field[i],\n        q1:          q1Field[i],\n        median:      medianField[i],\n        q3:          q3Field[i],\n        p100:        p100Field[i],\n        points:      pointsField[i],\n        pointsTotal: pointsTotalField[i],\n    };\n}\n\nconst uniqueForecasts = [...new Set(forecastField)];\nconst uniqueLeadDays  = [...new Set(leadDayField)].sort((a, b) => a - b);\nconst uniqueYears     = [...new Set(yearField)].sort();\n\nconst threshold      = parseFloat(variables?.threshold?.current?.value) || 0;\nconst colorThreshold = parseFloat(variables?.color_threshold?.current?.value) || 0.8;\n\nconst nF  = uniqueForecasts.length;\nconst nLD = uniqueLeadDays.length;\n\n// ── Layout constants ──────────────────────────────────────────────────────────\nconst LEFT   = 0.20;\nconst RIGHT  = 0.01;\nconst TOP    = 0.05;\nconst BOTTOM = 0.08;\nconst PAD    = 0.003;\n\nconst cellW = (1 - LEFT - RIGHT) / nLD;\nconst cellH = (1 - TOP - BOTTOM) / nF;\n\nconst traces = [];\nconst layout = {\n    paper_bgcolor: '#F4F5F5',\n    plot_bgcolor:  '#F4F5F5',\n    showlegend: false,\n    margin: { l: 5, r: 10, t: 10, b: 10 },\n    annotations: [],\n    shapes: [],\n    font: { family: 'Inter, sans-serif', size: 11 }\n};\n\n// ── Column headers ────────────────────────────────────────────────────────────\nfor (let j = 0; j < nLD; j++) {\n    layout.annotations.push({\n        xref: 'paper', yref: 'paper',\n        x: LEFT + (j + 0.5) * cellW,\n        y: 1 - TOP * 0.25,\n        text: `<b>Day ${uniqueLeadDays[j]}</b>`,\n        showarrow: false,\n        xanchor: 'center', yanchor: 'middle',\n        font: { size: 12 }\n    });\n}\n\n// ── Forecast name labels ──────────────────────────────────────────────────────\nfor (let i = 0; i < nF; i++) {\n    layout.annotations.push({\n        xref: 'paper', yref: 'paper',\n        x: LEFT - 0.01,\n        y: 1 - TOP - (i + 0.5) * cellH,\n        text: titleCase(uniqueForecasts[i]),\n        showarrow: false,\n        xanchor: 'right', yanchor: 'middle',\n        font: { size: 11 }\n    });\n}\n\n// ── Cells ─────────────────────────────────────────────────────────────────────\nlet axIdx = 1;\nfor (let i = 0; i < nF; i++) {\n    for (let j = 0; j < nLD; j++) {\n        const f  = uniqueForecasts[i];\n        const ld = uniqueLeadDays[j];\n\n        const x0 = LEFT + j * cellW + PAD;\n        const x1 = LEFT + (j + 1) * cellW - PAD;\n        const y1 = 1 - TOP - i * cellH - PAD;\n        const y0 = 1 - TOP - (i + 1) * cellH + PAD;\n\n        const xAxisKey = axIdx === 1 ? 'xaxis' : `xaxis${axIdx}`;\n        const yAxisKey = axIdx === 1 ? 'yaxis' : `yaxis${axIdx}`;\n        const xRef     = axIdx === 1 ? 'x'     : `x${axIdx}`;\n        const yRef     = axIdx === 1 ? 'y'     : `y${axIdx}`;\n\n        layout[xAxisKey] = {\n            domain: [x0, x1],\n            showticklabels: false, showgrid: false,\n            zeroline: false, fixedrange: true,\n            range: [-0.5, uniqueYears.length - 0.5]\n        };\n        layout[yAxisKey] = {\n            domain: [y0, y1],\n            showticklabels: false, showgrid: false,\n            zeroline: false, fixedrange: true,\n            range: [0, threshold * 2]\n        };\n        const byYear = dataMap[f]?.[ld];\n\n        // KPI ratio per year, averaged across years for background color\n        const ratios = byYear\n            ? uniqueYears.map(yr => {\n                const d = byYear[yr];\n                return (d && d.pointsTotal > 0) ? d.points / d.pointsTotal : null;\n              }).filter(v => v != null)\n            : [];\n        const avgRatio = ratios.length ? ratios.reduce((a, b) => a + b, 0) / ratios.length : null;\n\n        layout.shapes.push({\n            type: 'rect', xref: 'paper', yref: 'paper',\n            x0, y0, x1, y1,\n            fillcolor: byYear ? getThresholdColor(avgRatio, colorThreshold) : 'rgba(255,255,255,0)',\n            line: { width: 0.5, color: '#DBDDDE' }\n        });\n\n        if (!byYear) {\n            layout.annotations.push({\n                xref: 'paper', yref: 'paper',\n                x: (x0 + x1) / 2, y: (y0 + y1) / 2,\n                text: '–', showarrow: false,\n                xanchor: 'center', yanchor: 'middle',\n                font: { color: '#aaa', size: 13 }\n            });\n        } else {\n            const lineColor = (avgRatio ?? 0) >= colorThreshold ? '#38a853' : '#dc3232';\n\n            const xs         = [];\n            const lowers     = [];\n            const q1s        = [];\n            const meds       = [];\n            const q3s        = [];\n            const uppers     = [];\n            const hoverTexts = [];\n\n            uniqueYears.forEach((yr, idx) => {\n                const d = byYear[yr];\n                console.log(yr);\n                if (!d || d.p0 == null) return;\n                // const yearLabel = String(yr).slice(0, 5);\n                xs.push(idx);\n                lowers.push(d.p0);\n                q1s.push(d.q1);\n                meds.push(d.median);\n                q3s.push(d.q3);\n                uppers.push(d.p100);\n                hoverTexts.push(\n                    `<b>${yr}</b><br>` +\n                    `Min: ${d.p0?.toFixed(2)}<br>` +\n                    `Q1: ${d.q1?.toFixed(2)}<br>` +\n                    `Median: ${d.median?.toFixed(2)}<br>` +\n                    `Q3: ${d.q3?.toFixed(2)}<br>` +\n                    `Max: ${d.p100?.toFixed(2)}<br>` +\n                    `Cells meeting threshold: ${d.pointsTotal > 0 ? ((d.points / d.pointsTotal) * 100).toFixed(0) : '–'}%`\n                );\n            });\n\n            // Threshold line at actual metric value\n            traces.push({\n                type: 'scatter',\n                x: [-0.5, uniqueYears.length - 0.5],\n                y: [threshold, threshold],\n                mode: 'lines',\n                line: { color: 'rgba(80,80,80,0.5)', width: 1, dash: 'dot' },\n                xaxis: xRef, yaxis: yRef,\n                hoverinfo: 'skip'\n            });\n\n            // Box plot\n            traces.push({\n                type: 'box',\n                x: xs,\n                lowerfence: lowers,\n                q1: q1s,\n                median: meds,\n                q3: q3s,\n                upperfence: uppers,\n                boxpoints: false,\n                xaxis: xRef, yaxis: yRef,\n                marker:     { color: lineColor },\n                line:       { color: lineColor, width: 1 },\n                fillcolor:  lineColor.replace('rgb(', 'rgba(').replace(')', ', 0.2)'),\n                customdata: hoverTexts,\n                hovertemplate: '%{customdata}<extra></extra>'\n            });\n        }\n\n        axIdx++;\n    }\n}\n\nreturn { data: traces, layout };",
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
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    time_grouping,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    time_grouping,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_fcst_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    time_grouping,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n)\nSELECT\n  forecast,\n  $region,\n  lead_day,\n  time_grouping,\n  PERCENTILE_CONT(0.0)  WITHIN GROUP (ORDER BY metric_avg) AS p0,\n  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY metric_avg) AS q1,\n  PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY metric_avg) AS median,\n  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY metric_avg) AS q3,\n  PERCENTILE_CONT(1.0)  WITHIN GROUP (ORDER BY metric_avg) AS p100,\n  COUNT(CASE WHEN metric_avg < ${threshold}::float THEN 1 END) AS points_above_threshold,\n  COUNT(metric_avg)                                             AS points_total\nFROM cell_avgs\nGROUP BY forecast, $region, lead_day, time_grouping\nORDER BY forecast, $region, lead_day, time_grouping",
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
        "h": 18,
        "w": 7,
        "x": 17,
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
        "h": 12,
        "w": 24,
        "x": 0,
        "y": 19
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
        "script": "function getThresholdColor(ratio, colorThreshold) {\n    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';\n    const t = Math.min(1, Math.max(0, ratio));\n    let r, g, b;\n    if (t <= colorThreshold) {\n        const s = t / colorThreshold;\n        r = Math.round(220 + s * (255 - 220));\n        g = Math.round(50  + s * (253 - 50));\n        b = Math.round(50  + s * (220 - 50));\n    } else {\n        const s = (t - colorThreshold) / (1 - colorThreshold);\n        r = Math.round(255 + s * (56  - 255));\n        g = Math.round(253 + s * (168 - 253));\n        b = Math.round(220 + s * (83  - 220));\n    }\n    return `rgba(${r}, ${g}, ${b}, 0.5)`;\n}\n\nconst renameDict = {\n    \"Ecmwf Ifs Er\": \"ECMWF IFS ER\",\n    \"Ecmwf Ifs Ens\": \"ECMWF IFS ENS\",\n    \"Ecmwf Ifs Er Debiased\": \"ECMWF IFS ER Debiased\",\n    \"Ecmwf Aifs\": \"ECMWF AIFS\",\n    \"Ecmwf Hres\": \"ECMWF HRES\",\n    \"Gfs\": \"GFS\",\n    \"Salient\": \"AI-Enhanced NWP\",\n    \"Fuxi\": \"FuXi S2S\",\n    \"Climatology 2015\": \"Climatology 1985-2014\",\n    \"Climatology Trend 2015\": \"Climatology 1985-2014 w/Trend\",\n    \"Climatology Era5 1985 2015\": \"Climatology ERA5 1985-2014\",\n    \"Climatology Imerg 1998 2016\": \"Climatology IMERG 1998-2015\",\n    \"Cumulus Ai\": \"Cumulus AI v0.0.0\",\n};\n\nfunction titleCase(str) {\n    let name = str.replaceAll('_', ' ').split(' ').map(w => w[0].toUpperCase() + w.substring(1)).join(' ');\n    return renameDict[name] || name;\n}\n\n// ── Data check ────────────────────────────────────────────────────────────────\nlet series = data.series[0];\nif (!series || series.fields.length === 0) return { data: [] };\n\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst fieldNames       = series.fields.map(f => f.name);\nconst forecastField    = series.fields[fieldNames.indexOf('forecast')].values;\nconst leadDayField     = series.fields[fieldNames.indexOf('lead_day')].values;\nconst yearField        = getField(series.fields, 'time_grouping');\nconst pointsField      = getField(series.fields, 'points_above_threshold');\nconst pointsTotalField = getField(series.fields, 'points_total');\nconst metricMeanField  = getField(series.fields, 'metric_mean');\n\n// ── Build lookup: forecast -> lead_day -> year -> {...} ───────────────────────\nconst dataMap = {};\nfor (let i = 0; i < forecastField.length; i++) {\n    const f  = forecastField[i];\n    const ld = leadDayField[i];\n    const yr = yearField[i];\n    if (!dataMap[f])     dataMap[f]     = {};\n    if (!dataMap[f][ld]) dataMap[f][ld] = {};\n    dataMap[f][ld][yr] = {\n        points:      pointsField[i],\n        pointsTotal: pointsTotalField[i],\n        metricMean:  metricMeanField[i]\n    };\n}\n\nconst uniqueForecasts = [...new Set(forecastField)];\nconst uniqueLeadDays  = [...new Set(leadDayField)].sort((a, b) => a - b);\nconst uniqueYears     = [...new Set(yearField)].sort();\n\nconst displayMetric  = variables?.display_metric?.current?.value || 'points';\nconst colorThreshold = parseFloat(variables?.color_threshold?.current?.value) || 0.8;\n\nconst nF  = uniqueForecasts.length;\nconst nLD = uniqueLeadDays.length;\n\n// ── Layout constants ──────────────────────────────────────────────────────────\nconst LEFT   = 0.20;   // space for forecast name labels\nconst RIGHT  = 0.01;\nconst TOP    = 0.07;   // space for column headers\nconst BOTTOM = 0.02;\nconst PAD    = 0.003;  // padding between cells\n\nconst cellW = (1 - LEFT - RIGHT) / nLD;\nconst cellH = (1 - TOP - BOTTOM) / nF;\n\nconst traces = [];\nconst layout = {\n    paper_bgcolor: '#F4F5F5',\n    plot_bgcolor:  '#F4F5F5',\n    showlegend: false,\n    margin: { l: 5, r: 10, t: 10, b: 10 },\n    annotations: [],\n    shapes: [],\n    font: { family: 'Inter, sans-serif', size: 11 }\n};\n\n// ── Column headers ────────────────────────────────────────────────────────────\nfor (let j = 0; j < nLD; j++) {\n    layout.annotations.push({\n        xref: 'paper', yref: 'paper',\n        x: LEFT + (j + 0.5) * cellW,\n        y: 1 - TOP * 0.25,\n        text: `<b>Day ${uniqueLeadDays[j]}</b>`,\n        showarrow: false,\n        xanchor: 'center', yanchor: 'middle',\n        font: { size: 12 }\n    });\n}\n\n// ── Forecast name labels ──────────────────────────────────────────────────────\nfor (let i = 0; i < nF; i++) {\n    layout.annotations.push({\n        xref: 'paper', yref: 'paper',\n        x: LEFT - 0.01,\n        y: 1 - TOP - (i + 0.5) * cellH,\n        text: titleCase(uniqueForecasts[i]),\n        showarrow: false,\n        xanchor: 'right', yanchor: 'middle',\n        font: { size: 11 }\n    });\n}\n\n// ── Cells ─────────────────────────────────────────────────────────────────────\nlet axIdx = 1;\nfor (let i = 0; i < nF; i++) {\n    for (let j = 0; j < nLD; j++) {\n        const f  = uniqueForecasts[i];\n        const ld = uniqueLeadDays[j];\n\n        const x0 = LEFT + j * cellW + PAD;\n        const x1 = LEFT + (j + 1) * cellW - PAD;\n        const y1 = 1 - TOP - i * cellH - PAD;\n        const y0 = 1 - TOP - (i + 1) * cellH + PAD;\n\n        const xAxisKey = axIdx === 1 ? 'xaxis' : `xaxis${axIdx}`;\n        const yAxisKey = axIdx === 1 ? 'yaxis' : `yaxis${axIdx}`;\n        const xRef     = axIdx === 1 ? 'x'     : `x${axIdx}`;\n        const yRef     = axIdx === 1 ? 'y'     : `y${axIdx}`;\n\n        layout[xAxisKey] = {\n            domain: [x0, x1],\n            showticklabels: false, showgrid: false,\n            zeroline: false, fixedrange: true,\n            range: [-0.5, uniqueYears.length - 0.5]\n        };\n        layout[yAxisKey] = {\n            domain: [y0, y1],\n            showticklabels: false, showgrid: false,\n            zeroline: false, fixedrange: true,\n            range: [-0.05, 1.05]\n        };\n\n        const byYear = dataMap[f]?.[ld];\n\n        // Background rectangle (always drawn)\n        const yearData = byYear\n            ? uniqueYears.map(yr => {\n                const d = byYear[yr];\n                if (!d) return null;\n                return displayMetric === 'value'\n                    ? d.metricMean\n                    : (d.pointsTotal > 0 ? d.points / d.pointsTotal : null);\n              })\n            : null;\n\n        const valid    = yearData ? yearData.filter(v => v != null && !isNaN(v)) : [];\n        const avgRatio = valid.length ? valid.reduce((a, b) => a + b, 0) / valid.length : null;\n\n        layout.shapes.push({\n            type: 'rect', xref: 'paper', yref: 'paper',\n            x0, y0, x1, y1,\n            fillcolor: byYear ? getThresholdColor(avgRatio, colorThreshold) : 'rgba(255,255,255,0)',\n            line: { width: 0.5, color: '#DBDDDE' }\n        });\n\n        if (!byYear) {\n            layout.annotations.push({\n                xref: 'paper', yref: 'paper',\n                x: (x0 + x1) / 2, y: (y0 + y1) / 2,\n                text: '–', showarrow: false,\n                xanchor: 'center', yanchor: 'middle',\n                font: { color: '#aaa', size: 13 }\n            });\n        } else {\n            const lineColor = (avgRatio ?? 0) >= colorThreshold ? '#38a853' : '#dc3232';\n\n            // Threshold dashed line\n            traces.push({\n                type: 'scatter',\n                x: [-0.5, uniqueYears.length - 0.5],\n                y: [colorThreshold, colorThreshold],\n                mode: 'lines',\n                line: { color: 'rgba(80,80,80,0.4)', width: 1, dash: 'dot' },\n                xaxis: xRef, yaxis: yRef,\n                hoverinfo: 'skip'\n            });\n\n            // Sparkline\n            traces.push({\n                type: 'scatter',\n                x: uniqueYears.map((_, idx) => idx),\n                y: yearData,\n                mode: 'lines+markers',\n                line: { color: lineColor, width: 1.5 },\n                marker: { size: 3.5, color: lineColor },\n                xaxis: xRef, yaxis: yRef,\n                text: uniqueYears.map((yr, idx) =>\n                    `${titleCase(f)}<br>Day ${ld} — ${yr}<br>${yearData[idx]?.toFixed(2) ?? 'N/A'}`\n                ),\n                hoverinfo: 'text'\n            });\n        }\n\n        axIdx++;\n    }\n}\n\nreturn { data: traces, layout };",
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
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    time_grouping,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    time_grouping,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${unimodal_shifted_fcst_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    time_grouping,\n    lat,\n    lon,\n    GREATEST(\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg\n  FROM (\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'obs' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, time_grouping, lat, lon, 'fcst' AS source, AVG(\"${metric}\") AS metric_year_avg\n    FROM \"${bimodal_metric_fcst_name}\"\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, time_grouping, lat, lon\n)\nSELECT\n  forecast,\n  $region,\n  lead_day,\n  time_grouping,\n  COUNT(CASE WHEN metric_avg < ${threshold}::float THEN 1 END) AS points_above_threshold,\n  COUNT(metric_avg)                                             AS points_total,\n  AVG(metric_avg)                                               AS metric_mean\nFROM cell_avgs\nGROUP BY forecast, $region, lead_day, time_grouping\nORDER BY forecast, $region, lead_day, time_grouping",
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
        "hide": 2,
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
          }
        ],
        "query": "1.5 : global1_5",
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
            "value": "region"
          }
        ],
        "query": "Countries : country, Rainfall Region : rainfall_region, Rainfall Region+Country : region",
        "type": "custom"
      },
      {
        "current": {
          "text": "Kenya",
          "value": "kenya"
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
  "title": "Advanced Forecast Evaluation Sparklines",
  "uid": "efp26wakjhw5cf",
  "version": 1,
  "weekStart": ""
}
