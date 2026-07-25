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
      "collapsed": true,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 16,
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
            "h": 5,
            "w": 24,
            "x": 0,
            "y": 0
          },
          "id": 17,
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
        }
      ],
      "title": "Metric description",
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
        "overrides": []
      },
      "gridPos": {
        "h": 18,
        "w": 24,
        "x": 0,
        "y": 1
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
        "script": "function getThresholdColor(ratio) {\n    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';\n    const t = Math.min(1, Math.max(0, ratio));\n    const mid = 0.5;\n    let r, g, b;\n    if (t <= mid) {\n        const s = t / mid;\n        r = Math.round(220 + s * (255 - 220));\n        g = Math.round(50  + s * (253 - 50));\n        b = Math.round(50  + s * (220 - 50));\n    } else {\n        const s = (t - mid) / (1 - mid);\n        r = Math.round(255 + s * (56  - 255));\n        g = Math.round(253 + s * (168 - 253));\n        b = Math.round(220 + s * (83  - 220));\n    }\n    return `rgba(${r}, ${g}, ${b}, 0.5)`;\n}\n\nconst renameDict = {\n    \"Ecmwf Ifs Er\": \"ECMWF IFS ER\",\n    \"Ecmwf Ifs Ens\": \"ECMWF IFS ENS\",\n    \"Ecmwf Ifs Er Debiased\": \"ECMWF IFS ER Debiased\",\n    \"Ecmwf Aifs\": \"ECMWF AIFS\",\n    \"Ecmwf Hres\": \"ECMWF HRES\",\n    \"Gfs\": \"GFS\",\n    \"Salient\": \"AI-Enhanced NWP\",\n    \"Fuxi\": \"FuXi S2S\",\n    \"Climatology 2015\": \"Climatology 1985-2014\",\n    \"Climatology Trend 2015\": \"Climatology 1985-2014 w/Trend\",\n    \"Climatology Era5 1985 2015\": \"Climatology ERA5 1985-2014\",\n    \"Climatology Imerg 1998 2016\": \"Climatology IMERG 1998-2015\",\n    \"Cumulus Ai\": \"Cumulus AI v0.0.0\",\n};\n\nfunction titleCase(str) {\n    let name = str.replaceAll('_', ' ')\n        .split(' ')\n        .map(w => w[0].toUpperCase() + w.substring(1))\n        .join(' ');\n    return renameDict[name] || name;\n}\n\nfunction getVar(name) {\n    const v = variables?.[name];\n    if (!v) return null;\n    return v.current?.value ?? v.value ?? v.query ?? null;\n}\n\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst VIEW_CONFIG = {\n    good_enough_cells: {\n        title: 'Good Enough Cells',\n        mode: 'points',\n        higherIsBetter: true,\n        filterNullForecasts: false,\n    },\n    metric: {\n        title: 'Average Metric',\n        mode: 'value',\n        field: 'metric_mean',\n        higherIsBetter: false,\n        filterNullForecasts: false,\n    },\n    percent_good: {\n        title: 'Percent Good Enough',\n        mode: 'value',\n        field: 'percent_good_mean',\n        higherIsBetter: true,\n        filterNullForecasts: false,\n    },\n    percent_good_members: {\n        title: 'Percent Good Enough Members',\n        mode: 'value',\n        field: 'percent_good_members_mean',\n        higherIsBetter: true,\n        filterNullForecasts: true,\n    },\n};\n\nfunction resolveTableView(series) {\n    const aliases = {\n        good_enough_cells: 'good_enough_cells',\n        'Good Enough Cells': 'good_enough_cells',\n        metric: 'metric',\n        'Average Metric': 'metric',\n        percent_good: 'percent_good',\n        'Average Good Enough': 'percent_good',\n        'Average Good Enough Percent': 'percent_good',\n        'Percent Good Enough': 'percent_good',\n        percent_good_members: 'percent_good_members',\n        'Average Good Enough Members': 'percent_good_members',\n        'Average Good Enough Members Percent': 'percent_good_members',\n        'Percent Good Enough Members': 'percent_good_members',\n    };\n    const fromSql = getField(series?.fields || [], 'table_view');\n    const sqlVal = fromSql.length ? fromSql[0] : null;\n    const raw = sqlVal || getVar('table_view') || 'percent_good';\n    return aliases[raw] || 'percent_good';\n}\n\nfunction metricActionableThreshold() {\n    const m = String(getVar('metric') ?? '');\n    const parts = m.split('-thresh-');\n    if (parts.length < 2) return 1;\n    const t = parseFloat(parts[parts.length - 1]);\n    return (t != null && !isNaN(t) && t > 0) ? t : 1;\n}\n\nfunction skillScore(rawVal, tableView, actionableThresh) {\n    if (rawVal == null || isNaN(rawVal)) return null;\n    if (tableView === 'metric') {\n        if (rawVal <= actionableThresh) return 1;\n        return Math.max(0, 1 - (rawVal - actionableThresh) / (0.5 * actionableThresh));\n    }\n    return Math.min(1, Math.max(0, rawVal));\n}\n\nfunction isClimatology(forecast) {\n    return String(forecast).toLowerCase().startsWith('climatology');\n}\n\nfunction pickClimatologyForecast(forecasts, truth) {\n    const clims = forecasts.filter(isClimatology);\n    if (!clims.length) return null;\n    const t = String(truth || '').toLowerCase();\n    if (t.includes('imerg')) {\n        const hit = clims.find(f => f.toLowerCase().includes('imerg'));\n        if (hit) return hit;\n    }\n    if (t.includes('era5') || t.includes('chirps')) {\n        const hit = clims.find(f => f.toLowerCase().includes('era5'));\n        if (hit) return hit;\n    }\n    const nonTrend = clims.find(f => !f.toLowerCase().includes('trend'));\n    return nonTrend || clims[0];\n}\n\nfunction formatDelta(raw, climRaw, { asPercent = false } = {}) {\n    if (raw == null || isNaN(raw) || climRaw == null || isNaN(climRaw)) return null;\n    const d = raw - climRaw;\n    const sign = d > 0 ? '+' : '';\n    if (asPercent) {\n        return `${sign}${(d * 100).toFixed(0)}%`;\n    }\n    return `${sign}${d.toFixed(2)}`;\n}\n\nfunction buildRegionTable(series, regionLabel, tableView, view, domain, mapLinks) {\n    const fieldNames = series.fields.map(f => f.name);\n    if (fieldNames.indexOf('forecast') < 0 || fieldNames.indexOf('lead_day') < 0) {\n        return null;\n    }\n\n    const forecastField = series.fields[fieldNames.indexOf('forecast')].values;\n    const leadDayField = series.fields[fieldNames.indexOf('lead_day')].values;\n    const pointsField = getField(series.fields, 'points_above_threshold');\n    const pointsTotalField = getField(series.fields, 'points_total');\n    const eventCountField = getField(series.fields, 'event_count_mean');\n    const valueField = view.mode === 'value' ? getField(series.fields, view.field) : [];\n\n    const dataMap = {};\n    for (let i = 0; i < forecastField.length; i++) {\n        const f = forecastField[i];\n        const ld = leadDayField[i];\n        if (!dataMap[f]) dataMap[f] = {};\n        let raw = null;\n        let display = '-';\n        if (view.mode === 'points') {\n            const num = pointsField[i];\n            const denom = pointsTotalField[i];\n            if (denom != null && denom !== 0) {\n                raw = num / denom;\n                display = `${num} / ${denom}`;\n            }\n        } else {\n            const v = valueField[i];\n            if (v != null && !isNaN(v)) {\n                raw = parseFloat(v);\n                display = raw.toFixed(2);\n            }\n        }\n        const ec = eventCountField[i];\n        const eventCount = (ec != null && !isNaN(ec)) ? Math.round(parseFloat(ec)) : null;\n        dataMap[f][ld] = { raw, display, eventCount };\n    }\n\n    let uniqueForecasts = [...new Set(forecastField)];\n    if (view.filterNullForecasts) {\n        uniqueForecasts = uniqueForecasts.filter(f =>\n            Object.values(dataMap[f] || {}).some(d => d.raw != null && !isNaN(d.raw))\n        );\n    }\n    const uniqueLeadDays = [...new Set(leadDayField)].sort((a, b) => a - b);\n    const actionableThresh = metricActionableThreshold();\n    const truth = getVar('truth');\n    const climForecast = pickClimatologyForecast(uniqueForecasts, truth);\n\n    if (uniqueForecasts.length === 0) return { empty: true, uniqueLeadDays };\n\n    const metric = getVar('metric');\n    const grid = getVar('grid');\n    const region = getVar('region');\n    const time_grouping = getVar('time_grouping') || 'year';\n    const time_filter = getVar('time_option');\n\n    // Best forecast index per lead by raw value (skillScore saturates at the\n    // actionable threshold, so it cannot break ties among \"good enough\" metrics).\n    const bestIdxByLead = {};\n    for (const ld of uniqueLeadDays) {\n        let bestIdx = -1;\n        let bestRaw = null;\n        uniqueForecasts.forEach((f, idx) => {\n            const raw = dataMap[f]?.[ld]?.raw;\n            if (raw == null || isNaN(raw)) return;\n            const better = bestRaw == null\n                || (view.higherIsBetter ? raw > bestRaw : raw < bestRaw);\n            if (better) {\n                bestRaw = raw;\n                bestIdx = idx;\n            }\n        });\n        bestIdxByLead[ld] = bestIdx;\n    }\n\n    const header = [\n        `Forecast · ${regionLabel}`,\n        ...uniqueLeadDays.map(ld => `D${ld}`),\n    ];\n    const forecastNames = uniqueForecasts.map(f => {\n        const name = titleCase(f);\n        return (climForecast && f === climForecast) ? `${name} (baseline)` : name;\n    });\n    const values = [forecastNames];\n    const ratios = [];\n    const fontWeights = [uniqueForecasts.map(() => 'normal')];\n    const fontColors = [uniqueForecasts.map(() => 'black')];\n\n    for (const ld of uniqueLeadDays) {\n        const col = [];\n        const ratioCol = [];\n        const weightCol = [];\n        const colorCol = [];\n        const climRaw = climForecast ? dataMap[climForecast]?.[ld]?.raw : null;\n\n        uniqueForecasts.forEach((f, idx) => {\n            const d = dataMap[f]?.[ld];\n            const isBest = bestIdxByLead[ld] === idx;\n            weightCol.push(isBest ? 'bold' : 'normal');\n            colorCol.push(isBest ? '#0b3d1f' : 'black');\n\n            if (!d || d.raw == null) {\n                col.push('-');\n                ratioCol.push(null);\n                return;\n            }\n\n            let label = d.display;\n            const secondary = [];\n            // Delta on a second line so bare clim values stay neat when left-aligned\n            if (climForecast && f !== climForecast) {\n                const delta = formatDelta(d.raw, climRaw, {\n                    asPercent: view.mode !== 'value' || view.higherIsBetter,\n                });\n                if (delta != null) secondary.push(delta);\n            }\n            if (d.eventCount != null) {\n                secondary.push(`n=${d.eventCount}`);\n            }\n            if (secondary.length) {\n                label = `${d.display}<br><span style=\"font-size:10px;opacity:0.72\">${secondary.join(' · ')}</span>`;\n            }\n\n            if (isBest) {\n                label = `★ ${label}`;\n            }\n\n            let cell = label;\n            if (mapLinks) {\n                const url = `d/ae39q2k3jv668d/plotly-maps?orgId=1` +\n                    `&var-forecast=${f}` +\n                    `&var-metric=${metric}` +\n                    `&var-lead=lead_${ld}` +\n                    `&var-truth=era5` +\n                    `&var-grid=${grid}` +\n                    `&var-region=${region}` +\n                    `&var-time_grouping=${time_grouping}` +\n                    `&var-time_filter=${time_filter}`;\n                cell = `<a href=\"${url}\">${label}</a>`;\n            }\n            col.push(cell);\n            ratioCol.push(d.raw);\n        });\n\n        values.push(col);\n        ratios.push(ratioCol);\n        fontWeights.push(weightCol);\n        fontColors.push(colorCol);\n    }\n\n    const forecast_colors = uniqueForecasts.map(() => 'rgba(0,0,0,0)');\n    const skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(v => {\n            const s = skillScore(v, tableView, actionableThresh);\n            return s == null ? 'rgba(255,255,255,0)' : getThresholdColor(s);\n        })\n    );\n\n    const dividerAt = Math.min(2, uniqueLeadDays.length);\n    const headerWithDiv = [\n        ...header.slice(0, dividerAt + 1),\n        '',\n        ...header.slice(dividerAt + 1)\n    ];\n    const valuesWithDiv = [\n        ...values.slice(0, dividerAt + 1),\n        Array(uniqueForecasts.length).fill(''),\n        ...values.slice(dividerAt + 1)\n    ];\n    const colorsWithDiv = [\n        forecast_colors,\n        ...skill_colors.slice(0, dividerAt),\n        Array(uniqueForecasts.length).fill('rgba(200,200,200,0.3)'),\n        ...skill_colors.slice(dividerAt)\n    ];\n    const fontWeightWithDiv = [\n        ...fontWeights.slice(0, dividerAt + 1),\n        Array(uniqueForecasts.length).fill('normal'),\n        ...fontWeights.slice(dividerAt + 1)\n    ];\n    const fontColorWithDiv = [\n        ...fontColors.slice(0, dividerAt + 1),\n        Array(uniqueForecasts.length).fill('black'),\n        ...fontColors.slice(dividerAt + 1)\n    ];\n    const colWidth = [1.35, ...uniqueLeadDays.map(() => 0.48)];\n    colWidth.splice(dividerAt + 1, 0, 0.03);\n\n    // Left-align values so bare clim numbers line up with rows that include Δ\n    const align = [\n        'left',\n        ...uniqueLeadDays.map(() => 'left'),\n        'left',\n    ];\n    // After divider insert, keep left align with columns\n    const alignWithDiv = [\n        ...align.slice(0, dividerAt + 1),\n        'center',\n        ...align.slice(dividerAt + 1),\n    ];\n    const climNote = climForecast\n        ? ` · Δ vs ${titleCase(climForecast)}`\n        : '';\n\n    const tableFont = '\"IBM Plex Sans\", \"Source Sans 3\", \"Segoe UI\", system-ui, sans-serif';\n\n    return {\n        empty: false,\n        regionLabel,\n        climNote,\n        trace: {\n            type: 'table',\n            domain: domain,\n            header: {\n                values: headerWithDiv,\n                align: alignWithDiv,\n                line: { width: 0, color: 'rgba(0,0,0,0)' },\n                font: {\n                    family: tableFont,\n                    size: 12,\n                    weight: 600,\n                    color: '#3f3f46',\n                },\n                fill: { color: ['rgba(244,245,245,1)'] },\n                height: 30,\n            },\n            cells: {\n                values: valuesWithDiv,\n                align: alignWithDiv,\n                line: { width: 0.5, color: 'rgba(219,221,222,0.85)' },\n                font: {\n                    family: tableFont,\n                    size: 12,\n                    color: fontColorWithDiv,\n                    weight: fontWeightWithDiv,\n                },\n                fill: { color: colorsWithDiv },\n                height: 42,\n            },\n            columnwidth: colWidth,\n            name: regionLabel,\n        }\n    };\n}\n\n// ── Main ─────────────────────────────────────────────────────────────────────\nif (!data.series || data.series.length === 0) return { data: [] };\n\nconst seriesA = data.series[0];\nconst tableView = resolveTableView(seriesA);\nconst view = VIEW_CONFIG[tableView];\n\nconst probType = String(\n    getField(seriesA.fields, 'prob_type')[0] || getVar('prob_type') || 'deterministic'\n).toLowerCase();\nconst compareRaw = String(\n    getField(seriesA.fields, 'compare_regions')[0] || getVar('compare_regions') || 'yes'\n).toLowerCase();\nconst compareOn = compareRaw === 'yes' || compareRaw === 'true';\n\nconst region1 = String(getVar('region_option') || 'region 1');\nconst region2 = String(getVar('region_option2') || 'region 2');\nconst label1 = region1.charAt(0).toUpperCase() + region1.slice(1);\nconst label2 = region2.charAt(0).toUpperCase() + region2.slice(1);\n\n// Probabilistic-only view with deterministic data selected\nif (tableView === 'percent_good_members' && probType !== 'probabilistic') {\n    return {\n        data: [],\n        layout: {\n            title: {\n                text: `${view.title} — switch Prob Type to Probabilistic`,\n                xanchor: 'left', x: 0,\n                font: { size: 14, color: '#b45309' }\n            },\n            annotations: [{\n                text: 'Percent Good Enough Members needs probabilistic metric tables.<br>Set <b>Prob Type</b> to <b>Probabilistic</b>, or choose another View.',\n                xref: 'paper', yref: 'paper', x: 0.5, y: 0.5,\n                showarrow: false,\n                font: { size: 15, color: '#666' },\n                align: 'center'\n            }],\n            paper_bgcolor: '#F4F5F5',\n            plot_bgcolor: '#F4F5F5',\n            margin: { t: 40, b: 20, l: 20, r: 20 },\n        }\n    };\n}\n\nconst domainSingle = { x: [0, 1], y: [0, 1] };\nconst domainLeft = { x: [0, 0.495], y: [0, 1] };\nconst domainRight = { x: [0.505, 1], y: [0, 1] };\n\nconst builtA = buildRegionTable(\n    seriesA, label1, tableView, view,\n    compareOn ? domainLeft : domainSingle,\n    true\n);\n\nlet builtB = null;\nif (compareOn && data.series.length > 1) {\n    builtB = buildRegionTable(data.series[1], label2, tableView, view, domainRight, true);\n}\n\nif ((!builtA || builtA.empty) && (!builtB || builtB.empty)) {\n    const msg = view.filterNullForecasts\n        ? 'percent_good_members is only available for probabilistic forecasts'\n        : 'No data for this selection';\n    return {\n        data: [],\n        layout: {\n            title: { text: `${view.title} — no data`, xanchor: 'left', x: 0 },\n            annotations: [{\n                text: msg,\n                xref: 'paper', yref: 'paper', x: 0.5, y: 0.5,\n                showarrow: false,\n                font: { size: 14, color: '#666' }\n            }]\n        }\n    };\n}\n\nconst traces = [];\nconst climNotes = [];\nif (builtA && !builtA.empty) {\n    traces.push(builtA.trace);\n    if (builtA.climNote) climNotes.push(builtA.climNote);\n}\nif (builtB && !builtB.empty) {\n    traces.push(builtB.trace);\n    if (builtB.climNote) climNotes.push(builtB.climNote);\n}\n\nconst regionTitle = compareOn\n    ? `${label1} vs ${label2}`\n    : label1;\nconst climTitleNote = climNotes[0] || '';\n\nreturn {\n    data: traces,\n    layout: {\n        title: {\n            text: `${view.title} — ${regionTitle}${climTitleNote} · ★ = best in column`,\n            xanchor: 'left',\n            x: 0,\n            font: {\n                size: 14,\n                color: '#18181b',\n                family: '\"IBM Plex Sans\", \"Source Sans 3\", \"Segoe UI\", system-ui, sans-serif',\n                weight: 500,\n            }\n        },\n        margin: { t: 40, b: 10, l: 6, r: 6 },\n        paper_bgcolor: '#F4F5F5',\n        plot_bgcolor: '#F4F5F5',\n        font: {\n            family: '\"IBM Plex Sans\", \"Source Sans 3\", \"Segoe UI\", system-ui, sans-serif',\n            color: '#27272a',\n        },\n    },\n};\n",
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
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    ) AS percent_good_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    ) AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_metric_fcst_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    ) AS percent_good_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    ) AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_shifted_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_shifted_fcst_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    ) AS percent_good_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    ) AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${bimodal_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${bimodal_metric_fcst_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n)\nSELECT\n  forecast,\n  $region,\n  lead_day,\n      COUNT(CASE WHEN percent_good_avg > ${threshold}::float THEN 1 END) AS points_above_threshold,\n  COUNT(percent_good_avg) AS points_total,\n  AVG(metric_avg) AS metric_mean,\n  AVG(percent_good_avg) AS percent_good_mean,\n  AVG(percent_good_members_avg) AS percent_good_members_mean,\n  AVG(event_count_avg) AS event_count_mean,\n  -- forces panel refresh when View changes; also read by Plotly scripts\n  '${table_view}' AS table_view,\n  '${compare_regions}' AS compare_regions,\n  '${prob_type}' AS prob_type\nFROM cell_avgs\nGROUP BY forecast, $region, lead_day\nORDER BY forecast, $region, lead_day\n",
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
          "rawQuery": true,
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    ) AS percent_good_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    ) AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_metric_fcst_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    ) AS percent_good_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    ) AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_shifted_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_shifted_fcst_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    ) AS percent_good_avg,\n    COALESCE(\n      LEAST(\n        MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    ) AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${bimodal_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${bimodal_metric_fcst_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND $region = '$region_option2'\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n)\nSELECT\n  forecast,\n  $region,\n  lead_day,\n      COUNT(CASE WHEN percent_good_avg > ${threshold}::float THEN 1 END) AS points_above_threshold,\n  COUNT(percent_good_avg) AS points_total,\n  AVG(metric_avg) AS metric_mean,\n  AVG(percent_good_avg) AS percent_good_mean,\n  AVG(percent_good_members_avg) AS percent_good_members_mean,\n  AVG(event_count_avg) AS event_count_mean,\n  -- forces panel refresh when View changes; also read by Plotly scripts\n  '${table_view}' AS table_view,\n  '${compare_regions}' AS compare_regions,\n  '${prob_type}' AS prob_type\nFROM cell_avgs\nGROUP BY forecast, $region, lead_day\nORDER BY forecast, $region, lead_day\n",
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
      "collapsed": true,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 19
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
          "text": "in_season_dry_spell-thresh-20",
          "value": "in_season_dry_spell-thresh-20"
        },
        "description": "Advanced event metric to evaluate. The -thresh- value in the name is the actionable bar used for percent_good and for Average Metric cell coloring.",
        "includeAll": false,
        "label": "Metric",
        "name": "metric",
        "options": [
          {
            "selected": false,
            "text": "Early season accumulation",
            "value": "early_season_accumulation-30d-thresh-30"
          },
          {
            "selected": false,
            "text": "Large rain days",
            "value": "big_rain_days-thresh-0.30"
          },
          {
            "selected": false,
            "text": "90th percentile rain",
            "value": "extreme_rain_days-thresh-0.30"
          },
          {
            "selected": true,
            "text": "In season dry spells",
            "value": "in_season_dry_spell-thresh-20"
          }
        ],
        "query": "Early season accumulation : early_season_accumulation-30d-thresh-30, Large rain days : big_rain_days-thresh-0.30, 90th percentile rain : extreme_rain_days-thresh-0.30, In season dry spells : in_season_dry_spell-thresh-20",
        "type": "custom"
      },
      {
        "current": {
          "text": "in_season_dry_spell",
          "value": "in_season_dry_spell"
        },
        "definition": "SELECT split_part('${metric}', '-thresh-', 1)",
        "description": "SQL column name for the selected metric (metric name with the -thresh-… suffix removed).",
        "hide": 2,
        "name": "metric_column",
        "options": [],
        "query": "SELECT split_part('${metric}', '-thresh-', 1)",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "percent_good",
          "value": "percent_good"
        },
        "description": "Which table summary to show. Percent Good Enough Members requires Prob Type = Probabilistic.",
        "includeAll": false,
        "label": "View",
        "name": "table_view",
        "options": [
          {
            "selected": true,
            "text": "Percent Good Enough",
            "value": "percent_good"
          },
          {
            "selected": false,
            "text": "Percent Good Enough Members",
            "value": "percent_good_members"
          },
          {
            "selected": false,
            "text": "Good Enough Cells",
            "value": "good_enough_cells"
          },
          {
            "selected": false,
            "text": "Average Metric",
            "value": "metric"
          }
        ],
        "query": "Percent Good Enough : percent_good, Percent Good Enough Members : percent_good_members, Good Enough Cells : good_enough_cells, Average Metric : metric",
        "type": "custom"
      },
      {
        "current": {
          "text": "yes",
          "value": "yes"
        },
        "description": "When Yes, stack Region 1 and Region 2 vertically (full width each). When No, show only Region 1.",
        "includeAll": false,
        "label": "Compare",
        "name": "compare_regions",
        "options": [
          {
            "selected": true,
            "text": "Yes",
            "value": "yes"
          },
          {
            "selected": false,
            "text": "No",
            "value": "no"
          }
        ],
        "query": "Yes : yes, No : no",
        "type": "custom"
      },
      {
        "current": {
          "text": "year",
          "value": "year"
        },
        "description": "How rows are grouped in time in the underlying tables (currently year).",
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
        "definition": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"\nWHERE lead_day IN (7, 14, 21, 28, 35, 42)",
        "description": "Which years (or other time groups) to include when averaging cell scores.",
        "label": "Years",
        "multi": true,
        "name": "time_option",
        "options": [],
        "query": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"\nWHERE lead_day IN (7, 14, 21, 28, 35, 42)",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "imerg_final",
          "value": "imerg_final"
        },
        "description": "Observational rainfall product used as ground truth when the metric tables were built.",
        "includeAll": false,
        "label": "Truth",
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
          "text": "deterministic",
          "value": "deterministic"
        },
        "description": "Deterministic vs probabilistic forecast tables. Probabilistic is required for Percent Good Enough Members.",
        "includeAll": false,
        "label": "Prob",
        "name": "prob_type",
        "options": [
          {
            "selected": true,
            "text": "Deterministic",
            "value": "deterministic"
          },
          {
            "selected": false,
            "text": "Probabilistic",
            "value": "probabilistic"
          }
        ],
        "query": "Deterministic : deterministic, Probabilistic : probabilistic",
        "type": "custom"
      },
      {
        "current": {
          "text": "",
          "value": ""
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT CASE WHEN '${prob_type}' = 'probabilistic' THEN '_prob_type-probabilistic' ELSE '' END",
        "description": "Internal: cache-key suffix for probabilistic metric tables.",
        "hide": 2,
        "includeAll": false,
        "name": "prob_type_suffix",
        "options": [],
        "query": "SELECT CASE WHEN '${prob_type}' = 'probabilistic' THEN '_prob_type-probabilistic' ELSE '' END",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "global1_5",
          "value": "global1_5"
        },
        "description": "Spatial grid resolution of the metric tables (1.5° or 0.25°).",
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
        "description": "Region typology used for the left/right region pickers (country, rainfall region, etc.).",
        "includeAll": false,
        "label": "Region type",
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
        "definition": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)",
        "description": "Region shown in the left-hand table.",
        "label": "Region 1",
        "name": "region_option",
        "options": [],
        "query": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)",
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
        "definition": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)",
        "description": "Second region for side-by-side comparison (used when Compare Regions is Yes).",
        "label": "Region 2",
        "name": "region_option2",
        "options": [],
        "query": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "d895ce4377dcf6ec5ba8f80d5cd55f61",
          "value": "d895ce4377dcf6ec5ba8f80d5cd55f61"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "description": "Internal: hashed SQL table for unimodal-season, observation-filtered events.",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_metric_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "a369a9403e7c860156c83a478b34dd2b",
          "value": "a369a9403e7c860156c83a478b34dd2b"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "description": "Internal: hashed SQL table for unimodal-season, forecast-filtered events.",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_metric_fcst_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "44f18c546cd12ab880c9787b8f270672",
          "value": "44f18c546cd12ab880c9787b8f270672"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "description": "Internal: hashed SQL table for shifted unimodal-season, observation-filtered events.",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_shifted_metric_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "de1b63ba78330d2ce9ed07ebe35e0b43",
          "value": "de1b63ba78330d2ce9ed07ebe35e0b43"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "description": "Internal: hashed SQL table for shifted unimodal-season, forecast-filtered events.",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_shifted_fcst_metric_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "096cdc8d670093f61356985dcb64dce9",
          "value": "096cdc8d670093f61356985dcb64dce9"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "description": "Internal: hashed SQL table for bimodal-season, observation-filtered events.",
        "hide": 2,
        "includeAll": false,
        "name": "bimodal_metric_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "8ca6ee76f6d1f4441f647a8a0c174062",
          "value": "8ca6ee76f6d1f4441f647a8a0c174062"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "description": "Internal: hashed SQL table for bimodal-season, forecast-filtered events.",
        "hide": 2,
        "includeAll": false,
        "name": "bimodal_metric_fcst_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "0.75",
          "value": "0.75"
        },
        "description": "Only used by the Good Enough Cells view: a grid cell counts when its average percent_good is above this cutoff (0–1). Does not change Percent Good Enough or Average Metric.",
        "label": "Cell cutoff",
        "name": "threshold",
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
          "text": "both",
          "value": "both"
        },
        "description": "Which event filter to include: forecast-defined events, observation-defined events, or both (combined).",
        "label": "Events",
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
  "title": "Advanced Forecast Evaluation Tables",
  "uid": "cfoumv7uu5xq8f",
  "version": 1,
  "weekStart": ""
}
