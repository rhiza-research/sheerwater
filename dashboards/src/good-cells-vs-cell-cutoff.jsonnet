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
  "description": "Good Enough Cells table and threshold curve, summed over a multiselect of regions.",
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "links": [
    {
      "asDropdown": false,
      "icon": "dashboard",
      "includeVars": true,
      "keepTime": true,
      "tags": [],
      "targetBlank": false,
      "title": "Advanced Forecast Evaluation Tables",
      "tooltip": "",
      "type": "link",
      "url": "/d/cfoumv7uu5xq8f/advanced-forecast-evaluation-tables?var-table_view=metric"
    }
  ],
  "panels": [
    {
      "collapsed": true,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 3,
      "panels": [
        {
          "datasource": {
            "uid": "bdz3m3xs99p1cf"
          },
          "fieldConfig": {
            "defaults": {},
            "overrides": []
          },
          "gridPos": {
            "h": 8,
            "w": 24,
            "x": 0,
            "y": 1
          },
          "id": 4,
          "options": {
            "content": "### Days Beyond Baseline\n\nEach cell is **cell-days** of expected good cells relative to the selected **Baseline forecast**.\n\nFor a forecast F and baseline B, at each lead day L in {7, 14, 21, 28} **where both F and B have usable cells** (`points_total > 0`, i.e. at least one non-null `percent_good`):\n\n1. Compute **expected actionable** (or **informative**) cells for F and B \u2014 the average number of good cells when sweeping the cutoff uniformly over the green (actionable) or teal (informative) band on the curve below.\n2. Take the difference `(cells_F \u2212 cells_B)` and weight by lead day L.\n\nLeads with no usable `percent_good` are **skipped** \u2014 they are not treated as zero. In **Events = Both** mode, a lead only counts when both the observation-triggered and forecast-triggered tables have `percent_good` for that forecast (so models like ECMWF IFS ENS are not scored on weeks they do not produce).\n\n**Actionable days** = sum over available leads of `(act[F,L] \u2212 act[B,L]) \u00d7 L`\n\n**Informative days** = sum over available leads of `(info[F,L] \u2212 info[B,L]) \u00d7 L`\n\nPositive values mean more expected good cells than the baseline, with later leads weighted more heavily. The baseline row is always `0`. \u2605 marks the best (highest) value in each column.\n\nOther **View** options show expected cells by lead day instead of these summary KPIs.\n",
            "contentPartials": [],
            "defaultContent": "",
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
              "rawSql": "select 1 as ok",
              "refId": "A"
            }
          ],
          "title": "",
          "transparent": true,
          "type": "marcusolsson-dynamictext-panel"
        }
      ],
      "title": "How Days Beyond Baseline is calculated",
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
        "h": 7,
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
          "plot_bgcolor": "#F4F5F5",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            },
            "text": "Good Enough Cells",
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
        "script": "function getThresholdColor(ratio) {\n    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';\n    const t = Math.min(1, Math.max(0, ratio));\n    const mid = 0.5;\n    let r, g, b;\n    if (t <= mid) {\n        const s = t / mid;\n        r = Math.round(220 + s * (255 - 220));\n        g = Math.round(50  + s * (253 - 50));\n        b = Math.round(50  + s * (220 - 50));\n    } else {\n        const s = (t - mid) / (1 - mid);\n        r = Math.round(255 + s * (56  - 255));\n        g = Math.round(253 + s * (168 - 253));\n        b = Math.round(220 + s * (83  - 220));\n    }\n    return `rgba(${r}, ${g}, ${b}, 0.5)`;\n}\n\nconst renameDict = {\n    \"Ecmwf Ifs Er\": \"ECMWF IFS ER\",\n    \"Ecmwf Ifs Ens\": \"ECMWF IFS ENS\",\n    \"Ecmwf Ifs Er Debiased\": \"ECMWF IFS ER Debiased\",\n    \"Ecmwf Aifs\": \"ECMWF AIFS\",\n    \"Ecmwf Hres\": \"ECMWF HRES\",\n    \"Gfs\": \"GFS\",\n    \"Salient\": \"AI-Enhanced NWP\",\n    \"Fuxi\": \"FuXi S2S\",\n    \"Climatology 2015\": \"Climatology 1985-2014\",\n    \"Climatology Trend 2015\": \"Climatology 1985-2014 w/Trend\",\n    \"Climatology Era5 1985 2015\": \"Climatology ERA5 1985-2014\",\n    \"Climatology Imerg 1998 2016\": \"Climatology IMERG 1998-2015\",\n    \"Cumulus Ai\": \"Cumulus AI v0.0.0\",\n};\n\nfunction titleCase(str) {\n    let name = str.replaceAll('_', ' ')\n        .split(' ')\n        .map(w => w[0].toUpperCase() + w.substring(1))\n        .join(' ');\n    return renameDict[name] || name;\n}\n\nfunction getVar(name) {\n    const v = variables?.[name];\n    if (!v) return null;\n    return v.current?.value ?? v.value ?? v.query ?? null;\n}\n\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst VIEW_CONFIG = {\n    auc: {\n        title: 'Expected Cells',\n        mode: 'value',\n        field: 'auc',\n        higherIsBetter: true,\n        filterNullForecasts: true,\n        asPercent: false,\n        decimals: 1,\n        // Color heatmap as fraction of max cells (points_total).\n        colorByFractionOfTotal: true,\n    },\n    auc_informative: {\n        title: 'Expected Informative',\n        mode: 'value',\n        field: 'auc_informative',\n        higherIsBetter: true,\n        filterNullForecasts: true,\n        asPercent: false,\n        decimals: 1,\n        colorByFractionOfTotal: true,\n    },\n    auc_actionable: {\n        title: 'Expected Actionable',\n        mode: 'value',\n        field: 'auc_actionable',\n        higherIsBetter: true,\n        filterNullForecasts: true,\n        asPercent: false,\n        decimals: 1,\n        colorByFractionOfTotal: true,\n    },\n    days_beyond_baseline: {\n        title: 'Days Beyond Baseline',\n        mode: 'days_beyond',\n        higherIsBetter: true,\n        filterNullForecasts: false,\n        asPercent: false,\n        decimals: 0,\n    },\n};\n\nfunction resolveTableView(series) {\n    const aliases = {\n        auc: 'auc',\n        'Area Under Curve': 'auc',\n        'Total AUC': 'auc',\n        'AUC': 'auc',\n        'Expected Cells': 'auc',\n        'Expected cells': 'auc',\n        auc_informative: 'auc_informative',\n        'AUC Informative': 'auc_informative',\n        'Area Under Curve Informative': 'auc_informative',\n        'Expected Informative': 'auc_informative',\n        auc_actionable: 'auc_actionable',\n        'AUC Actionable': 'auc_actionable',\n        'Area Under Curve Actionable': 'auc_actionable',\n        'Expected Actionable': 'auc_actionable',\n        days_beyond_baseline: 'days_beyond_baseline',\n        'Days Beyond Baseline': 'days_beyond_baseline',\n        'Actionable days': 'days_beyond_baseline',\n        'Informative days': 'days_beyond_baseline',\n        // Legacy aliases from older View values\n        good_enough_cells: 'auc',\n        'Good Enough Cells': 'auc',\n    };\n    const fromSql = getField(series?.fields || [], 'table_view');\n    const sqlVal = fromSql.length ? fromSql[0] : null;\n    const raw = sqlVal || getVar('gc_view') || 'auc';\n    return aliases[raw] || 'auc';\n}\n\nfunction metricActionableThreshold() {\n    const m = String(getVar('metric') ?? '');\n    const parts = m.split('-thresh-');\n    if (parts.length < 2) return 1;\n    const t = parseFloat(parts[parts.length - 1]);\n    return (t != null && !isNaN(t) && t > 0) ? t : 1;\n}\n\nfunction skillScore(rawVal, tableView, actionableThresh) {\n    if (rawVal == null || isNaN(rawVal)) return null;\n    if (tableView === 'metric') {\n        if (rawVal <= actionableThresh) return 1;\n        return Math.max(0, 1 - (rawVal - actionableThresh) / (0.5 * actionableThresh));\n    }\n    return Math.min(1, Math.max(0, rawVal));\n}\n\nfunction isClimatology(forecast) {\n    return String(forecast).toLowerCase().startsWith('climatology');\n}\n\nfunction pickClimatologyForecast(forecasts, truth) {\n    const clims = forecasts.filter(isClimatology);\n    if (!clims.length) return null;\n    const t = String(truth || '').toLowerCase();\n    if (t.includes('imerg')) {\n        const hit = clims.find(f => f.toLowerCase().includes('imerg'));\n        if (hit) return hit;\n    }\n    if (t.includes('era5') || t.includes('chirps')) {\n        const hit = clims.find(f => f.toLowerCase().includes('era5'));\n        if (hit) return hit;\n    }\n    const nonTrend = clims.find(f => !f.toLowerCase().includes('trend'));\n    return nonTrend || clims[0];\n}\n\nfunction formatDelta(raw, climRaw, { asPercent = false } = {}) {\n    if (raw == null || isNaN(raw) || climRaw == null || isNaN(climRaw)) return null;\n    const d = raw - climRaw;\n    const sign = d > 0 ? '+' : '';\n    if (asPercent) {\n        return `${sign}${(d * 100).toFixed(0)}%`;\n    }\n    return `${sign}${d.toFixed(2)}`;\n}\n\nfunction formatDaysBeyond(v) {\n    if (v == null || !Number.isFinite(v)) return '\u2014';\n    const sign = v > 0 ? '+' : '';\n    return `${sign}${v.toFixed(0)}`;\n}\n\nfunction resolveBaselineForecast(knownForecasts, series) {\n    const fromSql = getField(series?.fields || [], 'baseline_forecast');\n    const raw = (fromSql.length ? fromSql[0] : null) ?? getVar('baseline_forecast');\n    const candidate = Array.isArray(raw) ? (raw[0] ?? null) : (raw || null);\n    if (candidate == null || candidate === '') {\n        return pickClimatologyForecast(knownForecasts, getVar('truth'));\n    }\n    const s = String(candidate);\n    if (knownForecasts.includes(s)) return s;\n    const lower = s.toLowerCase();\n    for (const f of knownForecasts) {\n        if (titleCase(f).toLowerCase() === lower) return f;\n        if (f.toLowerCase() === lower) return f;\n    }\n    return s;\n}\n\n/** \u03a3 (forecast \u2212 baseline) \u00d7 lead_day over leads with usable data for both.\n * Leads with no non-null percent_good cells (points_total == 0) are omitted from\n * the maps below, so they drop out \u2014 no zero-fill penalty (e.g. ENS weeks 3\u20134).\n */\nfunction daysBeyondForForecast(bandByLead, baseByLead, leads) {\n    let sum = 0;\n    let n = 0;\n    for (const lead of leads) {\n        const ev = bandByLead?.[lead];\n        const base = baseByLead?.[lead];\n        if (ev == null || !Number.isFinite(ev) || base == null || !Number.isFinite(base)) {\n            continue;\n        }\n        sum += (ev - base) * lead;\n        n += 1;\n    }\n    return n > 0 ? sum : null;\n}\n\nfunction buildDaysBeyondTable(series, regionLabel, domain) {\n    const fieldNames = series.fields.map(f => f.name);\n    if (fieldNames.indexOf('forecast') < 0 || fieldNames.indexOf('lead_day') < 0) {\n        return null;\n    }\n\n    const forecastField = series.fields[fieldNames.indexOf('forecast')].values;\n    const leadDayField = series.fields[fieldNames.indexOf('lead_day')].values;\n    const actField = getField(series.fields, 'auc_actionable');\n    const infoField = getField(series.fields, 'auc_informative');\n    const pointsTotalField = getField(series.fields, 'points_total');\n\n    const actMap = {};\n    const infoMap = {};\n    for (let i = 0; i < forecastField.length; i++) {\n        const f = forecastField[i];\n        const ld = Number(leadDayField[i]);\n        if (!Number.isFinite(ld)) continue;\n        // points_total = COUNT(percent_good). 0/null \u21d2 no forecast eval at this lead\n        // (SQL may still emit auc=0 from an all-null curve \u2014 do not treat as a real score).\n        const pts = pointsTotalField.length ? Number(pointsTotalField[i]) : NaN;\n        if (!(pts > 0)) continue;\n\n        if (!actMap[f]) actMap[f] = {};\n        if (!infoMap[f]) infoMap[f] = {};\n        const act = actField[i];\n        const info = infoField[i];\n        if (act != null && Number.isFinite(Number(act))) actMap[f][ld] = Number(act);\n        if (info != null && Number.isFinite(Number(info))) infoMap[f][ld] = Number(info);\n    }\n\n    const allForecasts = [...new Set(forecastField)];\n    const baselineForecast = resolveBaselineForecast(allForecasts, series);\n    if (!baselineForecast || !actMap[baselineForecast]) {\n        return {\n            empty: true,\n            climNote: '',\n            uniqueLeadDays: [],\n        };\n    }\n\n    const allLeads = [7, 14, 21, 28];\n    const baseAct = actMap[baselineForecast] || {};\n    const baseInfo = infoMap[baselineForecast] || {};\n\n    // Rows: selected forecasts (and eval if present); keep baseline labeled.\n    let uniqueForecasts = allForecasts.filter(f => {\n        if (f === baselineForecast) return true;\n        const actDays = daysBeyondForForecast(actMap[f], baseAct, allLeads);\n        const infoDays = daysBeyondForForecast(infoMap[f], baseInfo, allLeads);\n        return actDays != null || infoDays != null;\n    });\n\n    // Prefer showing non-baseline first, baseline last.\n    uniqueForecasts = [\n        ...uniqueForecasts.filter(f => f !== baselineForecast).sort(),\n        ...uniqueForecasts.filter(f => f === baselineForecast),\n    ];\n\n    if (uniqueForecasts.length === 0) {\n        return { empty: true, climNote: '', uniqueLeadDays: [] };\n    }\n\n    const columns = [\n        { key: 'actionable', label: 'Actionable days', leads: allLeads, band: 'act' },\n        { key: 'informative', label: 'Informative days', leads: allLeads, band: 'info' },\n    ];\n\n    const rowValues = {};\n    for (const f of uniqueForecasts) {\n        if (f === baselineForecast) {\n            rowValues[f] = { actionable: 0, informative: 0 };\n        } else {\n            rowValues[f] = {\n                actionable: daysBeyondForForecast(actMap[f], baseAct, allLeads),\n                informative: daysBeyondForForecast(infoMap[f], baseInfo, allLeads),\n            };\n        }\n    }\n\n    const bestIdxByCol = {};\n    for (const col of columns) {\n        let bestIdx = -1;\n        let bestRaw = null;\n        uniqueForecasts.forEach((f, idx) => {\n            if (f === baselineForecast) return;\n            const raw = rowValues[f]?.[col.key];\n            if (raw == null || isNaN(raw)) return;\n            if (bestRaw == null || raw > bestRaw) {\n                bestRaw = raw;\n                bestIdx = idx;\n            }\n        });\n        bestIdxByCol[col.key] = bestIdx;\n    }\n\n    const maxAbsByCol = {};\n    for (const col of columns) {\n        let maxAbs = 0;\n        for (const f of uniqueForecasts) {\n            if (f === baselineForecast) continue;\n            const raw = rowValues[f]?.[col.key];\n            if (raw != null && Number.isFinite(raw)) {\n                maxAbs = Math.max(maxAbs, Math.abs(raw));\n            }\n        }\n        maxAbsByCol[col.key] = maxAbs;\n    }\n\n    const forecastNames = uniqueForecasts.map(f => {\n        const name = titleCase(f);\n        return f === baselineForecast ? `${name} (baseline)` : name;\n    });\n    const values = [forecastNames];\n    const ratios = [];\n    const fontWeights = [uniqueForecasts.map(() => 'normal')];\n    const fontColors = [uniqueForecasts.map(() => 'black')];\n\n    for (const col of columns) {\n        const colVals = [];\n        const ratioCol = [];\n        const weightCol = [];\n        const colorCol = [];\n        uniqueForecasts.forEach((f, idx) => {\n            const raw = rowValues[f]?.[col.key];\n            const isBest = bestIdxByCol[col.key] === idx;\n            weightCol.push(isBest ? 'bold' : 'normal');\n            colorCol.push(isBest ? '#0b3d1f' : 'black');\n\n            if (raw == null || !Number.isFinite(raw)) {\n                colVals.push('\u2014');\n                ratioCol.push(null);\n                return;\n            }\n\n            let label = formatDaysBeyond(raw);\n            if (f === baselineForecast) {\n                label = '0';\n            }\n            if (isBest) label = `\u2605 ${label}`;\n            colVals.push(label);\n\n            const maxAbs = maxAbsByCol[col.key];\n            // Map [-maxAbs, maxAbs] \u2192 [0, 1] with 0.5 at zero for diverging heatmap.\n            ratioCol.push(maxAbs > 0 ? 0.5 + 0.5 * (raw / maxAbs) : 0.5);\n        });\n        values.push(colVals);\n        ratios.push(ratioCol);\n        fontWeights.push(weightCol);\n        fontColors.push(colorCol);\n    }\n\n    const forecast_colors = uniqueForecasts.map(() => 'rgba(0,0,0,0)');\n    const skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(v => (v == null ? 'rgba(255,255,255,0)' : getThresholdColor(v)))\n    );\n\n    const header = [`Forecast \u00b7 ${regionLabel}`, ...columns.map(c => c.label)];\n    const align = ['left', 'center', 'center'];\n    const colWidth = [1.6, 1.0, 1.0];\n    const tableFont = '\"IBM Plex Sans\", \"Source Sans 3\", \"Segoe UI\", system-ui, sans-serif';\n    const climNote = ` \u00b7 vs ${titleCase(baselineForecast)} \u00b7 \u0394\u00d7{7,14,21,28}`;\n\n    return {\n        empty: false,\n        regionLabel,\n        climNote,\n        daysBeyond: true,\n        trace: {\n            type: 'table',\n            domain,\n            header: {\n                values: header,\n                align,\n                line: { width: 0, color: 'rgba(0,0,0,0)' },\n                font: {\n                    family: tableFont,\n                    size: 12,\n                    weight: 600,\n                    color: '#3f3f46',\n                },\n                fill: { color: ['rgba(244,245,245,1)'] },\n                height: 30,\n            },\n            cells: {\n                values,\n                align,\n                line: { width: 0.5, color: 'rgba(219,221,222,0.85)' },\n                font: {\n                    family: tableFont,\n                    size: 12,\n                    color: fontColors,\n                    weight: fontWeights,\n                },\n                fill: { color: [forecast_colors, ...skill_colors] },\n                height: 30,\n            },\n            columnwidth: colWidth,\n            name: regionLabel,\n        },\n    };\n}\n\nfunction buildRegionTable(series, regionLabel, tableView, view, domain, mapLinks) {\n    if (view.mode === 'days_beyond') {\n        return buildDaysBeyondTable(series, regionLabel, domain);\n    }\n    const fieldNames = series.fields.map(f => f.name);\n    if (fieldNames.indexOf('forecast') < 0 || fieldNames.indexOf('lead_day') < 0) {\n        return null;\n    }\n\n    const forecastField = series.fields[fieldNames.indexOf('forecast')].values;\n    const leadDayField = series.fields[fieldNames.indexOf('lead_day')].values;\n    const pointsField = getField(series.fields, 'points_above_threshold');\n    const pointsTotalField = getField(series.fields, 'points_total');\n    const eventCountField = getField(series.fields, 'event_count_mean');\n    const aucRawField = getField(series.fields, 'auc_raw');\n    const valueField = view.mode === 'value' ? getField(series.fields, view.field) : [];\n\n    const dataMap = {};\n    for (let i = 0; i < forecastField.length; i++) {\n        const f = forecastField[i];\n        const ld = leadDayField[i];\n        if (!dataMap[f]) dataMap[f] = {};\n        let raw = null;\n        let display = '-';\n        if (view.mode === 'points') {\n            const num = pointsField[i];\n            const denom = pointsTotalField[i];\n            if (denom != null && denom !== 0) {\n                raw = num / denom;\n                display = `${num} / ${denom}`;\n            }\n        } else if (view.mode === 'auc_points') {\n            // auc_raw = \u222b good_cells d(threshold) over [0,1] \u2192 mean # good cells;\n            // max possible is points_total (all cells good at every threshold).\n            const num = aucRawField[i];\n            const denom = pointsTotalField[i];\n            if (\n                num != null && Number.isFinite(Number(num))\n                && denom != null && denom !== 0 && Number.isFinite(Number(denom))\n            ) {\n                raw = Number(num) / Number(denom);\n                display = `${Math.round(Number(num))} / ${denom}`;\n            }\n        } else {\n            const v = valueField[i];\n            if (v != null && !isNaN(v) && Number.isFinite(Number(v))) {\n                raw = parseFloat(v);\n                const decimals = view.decimals != null ? view.decimals : 2;\n                display = view.asPercent\n                    ? `${(raw * 100).toFixed(0)}%`\n                    : raw.toFixed(decimals);\n            }\n        }\n        const ec = eventCountField[i];\n        const eventCount = (ec != null && !isNaN(ec)) ? Math.round(parseFloat(ec)) : null;\n        const pt = pointsTotalField[i];\n        const pointsTotal = (pt != null && !isNaN(pt) && Number(pt) > 0)\n            ? Number(pt)\n            : null;\n        dataMap[f][ld] = { raw, display, eventCount, pointsTotal };\n    }\n\n    let uniqueForecasts = [...new Set(forecastField)];\n    const uniqueLeadDays = [...new Set(leadDayField)].sort((a, b) => a - b);\n    if (view.filterNullForecasts) {\n        // Hide a forecast if any lead is missing or null (same rule as the curve).\n        uniqueForecasts = uniqueForecasts.filter(f =>\n            uniqueLeadDays.every(ld => {\n                const d = dataMap[f]?.[ld];\n                return d && d.raw != null && !isNaN(d.raw);\n            })\n        );\n    }\n    const actionableThresh = metricActionableThreshold();\n    const truth = getVar('truth');\n    const climForecast = pickClimatologyForecast(uniqueForecasts, truth);\n\n    if (uniqueForecasts.length === 0) return { empty: true, uniqueLeadDays };\n\n    const metric = getVar('metric');\n    const grid = getVar('grid');\n    const region = getVar('region');\n    const time_grouping = getVar('time_grouping') || 'year';\n    const time_filter = getVar('time_option');\n\n    // Best forecast index per lead by raw value (skillScore saturates at the\n    // actionable threshold, so it cannot break ties among \"good enough\" metrics).\n    const bestIdxByLead = {};\n    for (const ld of uniqueLeadDays) {\n        let bestIdx = -1;\n        let bestRaw = null;\n        uniqueForecasts.forEach((f, idx) => {\n            const raw = dataMap[f]?.[ld]?.raw;\n            if (raw == null || isNaN(raw)) return;\n            const better = bestRaw == null\n                || (view.higherIsBetter ? raw > bestRaw : raw < bestRaw);\n            if (better) {\n                bestRaw = raw;\n                bestIdx = idx;\n            }\n        });\n        bestIdxByLead[ld] = bestIdx;\n    }\n\n    const header = [\n        `Forecast \u00b7 ${regionLabel}`,\n        ...uniqueLeadDays.map(ld => `D${ld}`),\n    ];\n    const forecastNames = uniqueForecasts.map(f => {\n        const name = titleCase(f);\n        return (climForecast && f === climForecast) ? `${name} (baseline)` : name;\n    });\n    const values = [forecastNames];\n    const ratios = [];\n    const fontWeights = [uniqueForecasts.map(() => 'normal')];\n    const fontColors = [uniqueForecasts.map(() => 'black')];\n\n    for (const ld of uniqueLeadDays) {\n        const col = [];\n        const ratioCol = [];\n        const weightCol = [];\n        const colorCol = [];\n        const climRaw = climForecast ? dataMap[climForecast]?.[ld]?.raw : null;\n\n        uniqueForecasts.forEach((f, idx) => {\n            const d = dataMap[f]?.[ld];\n            const isBest = bestIdxByLead[ld] === idx;\n            weightCol.push(isBest ? 'bold' : 'normal');\n            colorCol.push(isBest ? '#0b3d1f' : 'black');\n\n            if (!d || d.raw == null) {\n                col.push('-');\n                ratioCol.push(null);\n                return;\n            }\n\n            let label = d.display;\n            const secondary = [];\n            // Delta on a second line so bare clim values stay neat when left-aligned\n            if (climForecast && f !== climForecast) {\n                const delta = formatDelta(d.raw, climRaw, {\n                    asPercent: view.asPercent === true,\n                });\n                if (delta != null) secondary.push(delta);\n            }\n            if (d.eventCount != null) {\n                secondary.push(`n=${d.eventCount}`);\n            }\n            if (secondary.length) {\n                label = `${d.display}<br><span style=\"font-size:10px;opacity:0.72\">${secondary.join(' \u00b7 ')}</span>`;\n            }\n\n            if (isBest) {\n                label = `\u2605 ${label}`;\n            }\n\n            let cell = label;\n            if (mapLinks) {\n                const url = `d/ae39q2k3jv668d/plotly-maps?orgId=1` +\n                    `&var-forecast=${f}` +\n                    `&var-metric=${metric}` +\n                    `&var-lead=lead_${ld}` +\n                    `&var-truth=era5` +\n                    `&var-grid=${grid}` +\n                    `&var-region=${region}` +\n                    `&var-time_grouping=${time_grouping}` +\n                    `&var-time_filter=${time_filter}`;\n                cell = `<a href=\"${url}\">${label}</a>`;\n            }\n            col.push(cell);\n            // Heatmap uses [0,1] skill; expected-cell views normalize by max cells.\n            if (view.colorByFractionOfTotal && d.pointsTotal) {\n                ratioCol.push(d.raw / d.pointsTotal);\n            } else {\n                ratioCol.push(d.raw);\n            }\n        });\n\n        values.push(col);\n        ratios.push(ratioCol);\n        fontWeights.push(weightCol);\n        fontColors.push(colorCol);\n    }\n\n    const forecast_colors = uniqueForecasts.map(() => 'rgba(0,0,0,0)');\n    const skill_colors = ratios.map(ratioCol =>\n        ratioCol.map(v => {\n            const s = skillScore(v, tableView, actionableThresh);\n            return s == null ? 'rgba(255,255,255,0)' : getThresholdColor(s);\n        })\n    );\n\n    const dividerAt = Math.min(2, uniqueLeadDays.length);\n    const headerWithDiv = [\n        ...header.slice(0, dividerAt + 1),\n        '',\n        ...header.slice(dividerAt + 1)\n    ];\n    const valuesWithDiv = [\n        ...values.slice(0, dividerAt + 1),\n        Array(uniqueForecasts.length).fill(''),\n        ...values.slice(dividerAt + 1)\n    ];\n    const colorsWithDiv = [\n        forecast_colors,\n        ...skill_colors.slice(0, dividerAt),\n        Array(uniqueForecasts.length).fill('rgba(200,200,200,0.3)'),\n        ...skill_colors.slice(dividerAt)\n    ];\n    const fontWeightWithDiv = [\n        ...fontWeights.slice(0, dividerAt + 1),\n        Array(uniqueForecasts.length).fill('normal'),\n        ...fontWeights.slice(dividerAt + 1)\n    ];\n    const fontColorWithDiv = [\n        ...fontColors.slice(0, dividerAt + 1),\n        Array(uniqueForecasts.length).fill('black'),\n        ...fontColors.slice(dividerAt + 1)\n    ];\n    const colWidth = [1.35, ...uniqueLeadDays.map(() => 0.48)];\n    colWidth.splice(dividerAt + 1, 0, 0.03);\n\n    // Left-align values so bare clim numbers line up with rows that include \u0394\n    const align = [\n        'left',\n        ...uniqueLeadDays.map(() => 'left'),\n        'left',\n    ];\n    // After divider insert, keep left align with columns\n    const alignWithDiv = [\n        ...align.slice(0, dividerAt + 1),\n        'center',\n        ...align.slice(dividerAt + 1),\n    ];\n    const climNote = climForecast\n        ? ` \u00b7 \u0394 vs ${titleCase(climForecast)}`\n        : '';\n\n    const tableFont = '\"IBM Plex Sans\", \"Source Sans 3\", \"Segoe UI\", system-ui, sans-serif';\n\n    return {\n        empty: false,\n        regionLabel,\n        climNote,\n        trace: {\n            type: 'table',\n            domain: domain,\n            header: {\n                values: headerWithDiv,\n                align: alignWithDiv,\n                line: { width: 0, color: 'rgba(0,0,0,0)' },\n                font: {\n                    family: tableFont,\n                    size: 12,\n                    weight: 600,\n                    color: '#3f3f46',\n                },\n                fill: { color: ['rgba(244,245,245,1)'] },\n                height: 30,\n            },\n            cells: {\n                values: valuesWithDiv,\n                align: alignWithDiv,\n                line: { width: 0.5, color: 'rgba(219,221,222,0.85)' },\n                font: {\n                    family: tableFont,\n                    size: 12,\n                    color: fontColorWithDiv,\n                    weight: fontWeightWithDiv,\n                },\n                fill: { color: colorsWithDiv },\n                height: 30,\n            },\n            columnwidth: colWidth,\n            name: regionLabel,\n        }\n    };\n}\n\n// \u2500\u2500 Main \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\nfunction formatRegions(raw) {\n    const vals = Array.isArray(raw) ? raw : (raw == null || raw === '' ? [] : [raw]);\n    if (!vals.length) return 'selected regions';\n    // Grafana \"All\": $__all, or custom allValue (quoted for SQL: '__all__').\n    const allTokens = new Set(['$__all', '__all__', \"'__all__'\"]);\n    if (vals.length === 1 && allTokens.has(String(vals[0]))) {\n        return 'All regions';\n    }\n    const names = vals.map(v => {\n        const s = String(v).replaceAll('_', ' ');\n        return s.charAt(0).toUpperCase() + s.slice(1);\n    });\n    if (names.length <= 3) return names.join(', ');\n    return `${names.slice(0, 3).join(', ')} +${names.length - 3} more`;\n}\n\nif (!data.series || data.series.length === 0) return { data: [] };\n\nconst seriesA = data.series[0];\nconst tableView = resolveTableView(seriesA);\nconst view = VIEW_CONFIG[tableView] || VIEW_CONFIG.good_enough_cells;\nconst regionTitle = formatRegions(getVar('region_option'));\n\nconst builtA = buildRegionTable(\n    seriesA, regionTitle, tableView, view,\n    { x: [0, 1], y: [0, 1] },\n    true\n);\n\nif (!builtA || builtA.empty) {\n    return {\n        data: [],\n        layout: {\n            title: { text: `${view.title} \u2014 no data`, xanchor: 'left', x: 0 },\n            annotations: [{\n                text: 'No data for this selection',\n                xref: 'paper', yref: 'paper', x: 0.5, y: 0.5,\n                showarrow: false,\n                font: { size: 14, color: '#666' }\n            }]\n        }\n    };\n}\n\nconst climTitleNote = builtA.climNote || '';\n\nreturn {\n    data: [builtA.trace],\n    layout: {\n        title: {\n            text: `${view.title} \u2014 ${regionTitle}${climTitleNote} \u00b7 \u2605 = best in column`,\n            xanchor: 'left',\n            x: 0,\n            font: {\n                size: 14,\n                color: '#18181b',\n                family: '\"IBM Plex Sans\", \"Source Sans 3\", \"Segoe UI\", system-ui, sans-serif',\n                weight: 500,\n            }\n        },\n        margin: { t: 32, b: 6, l: 6, r: 6 },\n        paper_bgcolor: '#F4F5F5',\n        plot_bgcolor: '#F4F5F5',\n        font: {\n            family: '\"IBM Plex Sans\", \"Source Sans 3\", \"Segoe UI\", system-ui, sans-serif',\n            color: '#27272a',\n        },\n    },\n};\n",
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
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    -- In 'both' mode PostgreSQL LEAST() ignores NULLs, so a missing forecast\n    -- side would otherwise fall back to obs-only percent_good and look like a\n    -- real (bad) score. Require both sides; otherwise leave null so the lead drops out.\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    END AS percent_good_avg,\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_members_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    END AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_metric_fcst_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    -- In 'both' mode PostgreSQL LEAST() ignores NULLs, so a missing forecast\n    -- side would otherwise fall back to obs-only percent_good and look like a\n    -- real (bad) score. Require both sides; otherwise leave null so the lead drops out.\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    END AS percent_good_avg,\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_members_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    END AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_shifted_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_shifted_fcst_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    -- In 'both' mode PostgreSQL LEAST() ignores NULLs, so a missing forecast\n    -- side would otherwise fall back to obs-only percent_good and look like a\n    -- real (bad) score. Require both sides; otherwise leave null so the lead drops out.\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    END AS percent_good_avg,\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_members_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    END AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${bimodal_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${bimodal_metric_fcst_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n),\nthresholds AS (\n  SELECT (gs::double precision / 100.0) AS cell_threshold\n  FROM generate_series(0, 100, 5) AS gs\n),\ncurve AS (\n  SELECT\n    t.cell_threshold,\n    c.lead_day,\n    c.forecast,\n    COUNT(*) FILTER (WHERE c.percent_good_avg >= t.cell_threshold) AS good_cells,\n    COUNT(c.percent_good_avg) AS points_total\n  FROM thresholds t\n  CROSS JOIN cell_avgs c\n  GROUP BY t.cell_threshold, c.lead_day, c.forecast\n),\ncurve_auc AS (\n  SELECT\n    forecast,\n    lead_day,\n    SUM(\n      0.5 * (good_cells + next_good_cells) * (next_threshold - cell_threshold)\n    ) AS auc_raw,\n    -- Informative band: [info_lo, act_lo]; actionable band: [act_lo, 1.0]\n    -- (same bands as the threshold-curve subplot shading).\n    SUM(\n      0.5 * (good_cells + next_good_cells)\n        * (LEAST(next_threshold, act_lo) - GREATEST(cell_threshold, info_lo))\n    ) FILTER (\n      WHERE LEAST(next_threshold, act_lo) > GREATEST(cell_threshold, info_lo)\n    ) AS auc_informative_raw,\n    SUM(\n      0.5 * (good_cells + next_good_cells)\n        * (LEAST(next_threshold, 1.0) - GREATEST(cell_threshold, act_lo))\n    ) FILTER (\n      WHERE LEAST(next_threshold, 1.0) > GREATEST(cell_threshold, act_lo)\n    ) AS auc_actionable_raw,\n    MAX(points_total) AS points_total,\n    MAX(info_lo) AS info_lo,\n    MAX(act_lo) AS act_lo\n  FROM (\n    SELECT\n      forecast,\n      lead_day,\n      cell_threshold,\n      good_cells,\n      points_total,\n      LEAD(cell_threshold) OVER (\n        PARTITION BY forecast, lead_day ORDER BY cell_threshold\n      ) AS next_threshold,\n      LEAD(good_cells) OVER (\n        PARTITION BY forecast, lead_day ORDER BY cell_threshold\n      ) AS next_good_cells,\n      LEAST(\n        GREATEST(LEAST('${informative_cutoff}'::float, '${actionable_cutoff}'::float), 0.0),\n        1.0\n      ) AS info_lo,\n      LEAST(\n        GREATEST(GREATEST('${informative_cutoff}'::float, '${actionable_cutoff}'::float), 0.0),\n        1.0\n      ) AS act_lo\n    FROM curve\n  ) steps\n  WHERE next_threshold IS NOT NULL\n  GROUP BY forecast, lead_day\n),\nat_cutoff AS (\n  SELECT\n    forecast,\n    lead_day,\n    COUNT(CASE WHEN percent_good_avg >= '${actionable_cutoff}'::float THEN 1 END) AS points_above_threshold,\n    COUNT(percent_good_avg) AS points_total,\n    AVG(event_count_avg) AS event_count_mean\n  FROM cell_avgs\n  GROUP BY forecast, lead_day\n)\nSELECT\n  a.forecast,\n  a.lead_day,\n  a.points_above_threshold,\n  a.points_total,\n  a.event_count_mean,\n  c.auc_raw::double precision AS auc_raw,\n  -- Expected cells = \u222b good_cells d\u03b8 / band width (\u03b8 ~ Uniform on the band).\n  -- points_total = 0 means no non-null percent_good (no forecast at this lead);\n  -- do not emit a spurious 0 AUC from an all-null curve.\n  CASE\n    WHEN a.points_total IS NULL OR a.points_total = 0 OR c.auc_raw IS NULL THEN NULL\n    ELSE c.auc_raw::double precision\n  END AS auc,\n  CASE\n    WHEN a.points_total IS NULL OR a.points_total = 0\n         OR c.auc_informative_raw IS NULL OR c.info_lo IS NULL OR c.act_lo IS NULL\n         OR c.act_lo <= c.info_lo THEN NULL\n    ELSE (c.auc_informative_raw / (c.act_lo - c.info_lo))::double precision\n  END AS auc_informative,\n  CASE\n    WHEN a.points_total IS NULL OR a.points_total = 0\n         OR c.auc_actionable_raw IS NULL OR c.act_lo IS NULL OR c.act_lo >= 1.0 THEN NULL\n    ELSE (c.auc_actionable_raw / (1.0 - c.act_lo))::double precision\n  END AS auc_actionable,\n  '${gc_view}' AS table_view,\n  'no' AS compare_regions,\n  '${prob_type}' AS prob_type,\n  '${actionable_cutoff}' AS cell_cutoff,\n  '${baseline_forecast}' AS baseline_forecast\nFROM at_cutoff a\nLEFT JOIN curve_auc c\n  ON c.forecast = a.forecast AND c.lead_day = a.lead_day\nORDER BY a.forecast, a.lead_day\n",
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
        "overrides": []
      },
      "gridPos": {
        "h": 28,
        "w": 24,
        "x": 0,
        "y": 8
      },
      "id": 2,
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
            "b": 40,
            "l": 50,
            "r": 20,
            "t": 40
          },
          "paper_bgcolor": "#F4F5F5",
          "plot_bgcolor": "#F4F5F5",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            },
            "text": "Good cells vs cell cutoff",
            "x": 0,
            "xanchor": "left"
          },
          "xaxis": {
            "automargin": true,
            "autorange": false,
            "range": [
              0,
              100
            ],
            "type": "linear"
          },
          "yaxis": {
            "automargin": true,
            "autorange": true,
            "type": "linear"
          }
        },
        "onclick": "",
        "resScale": 2,
        "script": "function getVar(name) {\n    const v = variables?.[name];\n    if (!v) return null;\n    return v.current?.value ?? v.value ?? v.query ?? null;\n}\n\nfunction getField(fields, name) {\n    const idx = fields.map(f => f.name).indexOf(name);\n    return idx >= 0 ? fields[idx].values : [];\n}\n\nconst FORECAST_COLORS = [\n    '#2563eb', '#dc2626', '#16a34a', '#ca8a04', '#7c3aed', '#0891b2',\n    '#db2777', '#4f46e5', '#65a30d', '#b45309', '#0f766e', '#ea580c',\n];\n\n// Stable, high-contrast colors by model family (clim always gray, ECMWF always blue).\nconst FORECAST_COLOR_BY_KEY = {\n    ecmwf_ifs_er: '#1d4ed8',\n    ecmwf_ifs_ens: '#3b82f6',\n    ecmwf_ifs_er_debiased: '#60a5fa',\n    ecmwf_aifs: '#0ea5e9',\n    ecmwf_hres: '#0284c7',\n    fuxi: '#ea580c',\n    graphcast: '#c026d3',\n    gencast: '#a21caf',\n    salient: '#16a34a',\n    gfs: '#ca8a04',\n    cumulus_ai: '#0f766e',\n    climatology_2015: '#57534e',\n    climatology_trend_2015: '#78716c',\n    climatology_era5_1985_2015: '#44403c',\n    climatology_imerg_1998_2016: '#a8a29e',\n};\n\nfunction colorForForecast(forecast, fallbackIndex) {\n    const key = String(forecast).toLowerCase();\n    if (FORECAST_COLOR_BY_KEY[key]) return FORECAST_COLOR_BY_KEY[key];\n    if (key.startsWith('climatology')) return '#57534e';\n    if (key.startsWith('ecmwf')) return '#1d4ed8';\n    return FORECAST_COLORS[fallbackIndex % FORECAST_COLORS.length];\n}\n\nconst LEADS = [7, 14, 21, 28, 35, 42];\n\nconst renameDict = {\n    'Ecmwf Ifs Er': 'ECMWF IFS ER',\n    'Ecmwf Ifs Ens': 'ECMWF IFS ENS',\n    'Ecmwf Ifs Er Debiased': 'ECMWF IFS ER Debiased',\n    'Ecmwf Aifs': 'ECMWF AIFS',\n    'Ecmwf Hres': 'ECMWF HRES',\n    'Gfs': 'GFS',\n    'Salient': 'AI-Enhanced NWP',\n    'Fuxi': 'FuXi S2S',\n    'Graphcast': 'GraphCast',\n    'Gencast': 'GenCast',\n    'Climatology 2015': 'Climatology 1985-2014',\n    'Climatology Trend 2015': 'Climatology 1985-2014 w/Trend',\n    'Climatology Era5 1985 2015': 'Climatology ERA5 1985-2014',\n    'Climatology Imerg 1998 2016': 'Climatology IMERG 1998-2015',\n    'Cumulus Ai': 'Cumulus AI v0.0.0',\n};\n\nfunction titleCase(str) {\n    const name = String(str).replaceAll('_', ' ')\n        .split(' ')\n        .map(w => w[0].toUpperCase() + w.substring(1))\n        .join(' ');\n    return renameDict[name] || name;\n}\n\nfunction weekLabel(leadDay) {\n    return `Week ${Math.round(Number(leadDay) / 7)}`;\n}\n\nfunction toPercent(v) {\n    const n = Number(v);\n    if (!Number.isFinite(n)) return null;\n    return n <= 1.0000001 ? n * 100 : n;\n}\n\nfunction isFiniteNumber(v) {\n    // Number(null) === 0 \u2014 treat null/empty/NaN strings as missing.\n    if (v === null || v === undefined || v === '') return false;\n    if (typeof v === 'string' && ['nan', 'null', 'undefined'].includes(v.toLowerCase())) {\n        return false;\n    }\n    const n = Number(v);\n    return Number.isFinite(n);\n}\n\nfunction formatList(raw, { empty = 'selected', max = 3 } = {}) {\n    const vals = Array.isArray(raw) ? raw : (raw == null || raw === '' ? [] : [raw]);\n    if (!vals.length) return empty;\n    // Grafana \"All\": $__all, or custom allValue (quoted for SQL: '__all__').\n    const allTokens = new Set(['$__all', '__all__', \"'__all__'\"]);\n    if (vals.length === 1 && allTokens.has(String(vals[0]))) {\n        return 'All';\n    }\n    const names = vals.map(titleCase);\n    if (names.length <= max) return names.join(', ');\n    return `${names.slice(0, max).join(', ')} +${names.length - max} more`;\n}\n\nfunction axisId(i, axis) {\n    return i === 0 ? axis : `${axis}${i + 1}`;\n}\n\n/** Trapezoidal \u222b good_cells d\u03b8 over [loPct, hiPct] (\u03b8 as percent 0\u2013100). */\nfunction integrateBand(xPct, y, loPct, hiPct) {\n    if (!(hiPct > loPct)) return null;\n    const pairs = xPct.map((x, i) => [Number(x), Number(y[i])])\n        .filter(([x, yi]) => Number.isFinite(x) && Number.isFinite(yi))\n        .sort((a, b) => a[0] - b[0]);\n    if (pairs.length < 2) return null;\n\n    let area = 0; // in good_cells \u00b7 \u03b8_fraction\n    for (let i = 0; i < pairs.length - 1; i++) {\n        const [x0, y0] = pairs[i];\n        const [x1, y1] = pairs[i + 1];\n        const left = Math.max(x0, loPct);\n        const right = Math.min(x1, hiPct);\n        if (!(right > left)) continue;\n        const t0 = x1 === x0 ? 0 : (left - x0) / (x1 - x0);\n        const t1 = x1 === x0 ? 1 : (right - x0) / (x1 - x0);\n        const yl = y0 + t0 * (y1 - y0);\n        const yr = y0 + t1 * (y1 - y0);\n        // d\u03b8_fraction = d\u03b8_pct / 100\n        area += 0.5 * (yl + yr) * ((right - left) / 100);\n    }\n    const width = (hiPct - loPct) / 100; // \u03b8 fraction\n    return { area, width };\n}\n\nfunction formatExpectedCells(v) {\n    if (v == null || !Number.isFinite(v)) return '\u2014';\n    return v.toFixed(1);\n}\n\nfunction formatDeltaCells(v) {\n    if (v == null || !Number.isFinite(v)) return '\u2014';\n    const sign = v > 0 ? '+' : '';\n    return `${sign}${v.toFixed(1)}`;\n}\n\nfunction deltaOrNull(evalVal, baseVal) {\n    if (evalVal == null || !Number.isFinite(evalVal)\n        || baseVal == null || !Number.isFinite(baseVal)) {\n        return null;\n    }\n    return evalVal - baseVal;\n}\n\nif (!data.series || data.series.length === 0) {\n    return { data: [], layout: { title: { text: 'Good cells vs cell cutoff \u2014 no data' } } };\n}\n\nconst series = data.series[0];\nconst thresh = getField(series.fields, 'cell_threshold');\nconst leads = getField(series.fields, 'lead_day');\nconst forecasts = getField(series.fields, 'forecast');\nconst goods = getField(series.fields, 'good_cells');\nconst pointsTotals = getField(series.fields, 'points_total');\nconst informativeCutoffField = getField(series.fields, 'informative_cutoff');\nconst actionableCutoffField = getField(series.fields, 'actionable_cutoff');\n\nif (!thresh.length) {\n    return { data: [], layout: { title: { text: 'Good cells vs cell cutoff \u2014 no data' } } };\n}\n\n// Keep usable (forecast, lead) curves only. Skip bad rows \u2014 do NOT drop a whole\n// forecast because some leads are missing (ENS / short-range models).\nconst allForecasts = new Set();\nconst byKey = new Map();\nfor (let i = 0; i < thresh.length; i++) {\n    const forecast = String(forecasts[i]);\n    allForecasts.add(forecast);\n    if (!isFiniteNumber(goods[i])) continue;\n    const pts = pointsTotals.length ? pointsTotals[i] : null;\n    // points_total = 0/null \u21d2 no non-null percent_good at this lead (omit lead only).\n    if (pts != null && (!isFiniteNumber(pts) || Number(pts) <= 0)) continue;\n    const xp = toPercent(thresh[i]);\n    if (xp == null) continue;\n    // At 0% cutoff every valid cell counts; 0 good cells \u21d2 unusable point.\n    if (xp <= 0.0001 && Number(goods[i]) <= 0) continue;\n\n    const lead = Number(leads[i]);\n    if (!Number.isFinite(lead)) continue;\n    const key = `${forecast}||${lead}`;\n    if (!byKey.has(key)) {\n        byKey.set(key, {\n            forecast,\n            lead,\n            x: [],\n            y: [],\n            pointsTotal: pointsTotals.length && isFiniteNumber(pointsTotals[i])\n                ? Number(pointsTotals[i])\n                : null,\n        });\n    }\n    const bucket = byKey.get(key);\n    bucket.x.push(xp);\n    bucket.y.push(Number(goods[i]));\n    if (bucket.pointsTotal == null && pointsTotals.length && isFiniteNumber(pointsTotals[i])) {\n        bucket.pointsTotal = Number(pointsTotals[i]);\n    }\n}\n\n// Forecasts that had SQL rows but no usable lead curves (for the title note).\nconst forecastsWithCurves = new Set([...byKey.values()].map(b => b.forecast));\nconst nanForecasts = new Set(\n    [...allForecasts].filter(f => !forecastsWithCurves.has(f))\n);\n\nfunction resolveCutoffPct(fieldVals, varName, fallback) {\n    const fromSql = fieldVals.length ? fieldVals[0] : null;\n    const fromVar = getVar(varName);\n    return toPercent(fromSql ?? fromVar ?? fallback);\n}\n\nlet bandLo = resolveCutoffPct(informativeCutoffField, 'informative_cutoff', 0.50);\nlet mid = resolveCutoffPct(actionableCutoffField, 'actionable_cutoff', 0.75);\nconst bandHi = 100;\n// Keep Informative start \u2264 Actionable start \u2264 100%.\nif (bandLo == null || !Number.isFinite(bandLo)) bandLo = 50;\nif (mid == null || !Number.isFinite(mid)) mid = 75;\nif (mid < bandLo) {\n    const tmp = bandLo;\n    bandLo = mid;\n    mid = tmp;\n}\nbandLo = Math.min(Math.max(bandLo, 0), bandHi);\nmid = Math.min(Math.max(mid, bandLo), bandHi);\n\nfunction leadBandExpectedCells(leadBuckets, forecastFilter) {\n    const buckets = forecastFilter\n        ? leadBuckets.filter(b => b.forecast === String(forecastFilter))\n        : leadBuckets;\n    const infos = [];\n    const acts = [];\n    for (const b of buckets) {\n        const info = integrateBand(b.x, b.y, bandLo, mid);\n        const act = integrateBand(b.x, b.y, mid, bandHi);\n        // Expected cells = \u222b good_cells d\u03b8 / band width.\n        if (info && info.width > 0) infos.push(info.area / info.width);\n        if (act && act.width > 0) acts.push(act.area / act.width);\n    }\n    const mean = arr => (arr.length\n        ? arr.reduce((s, v) => s + v, 0) / arr.length\n        : null);\n    return {\n        info: mean(infos),\n        act: mean(acts),\n        n: buckets.length,\n        forecast: forecastFilter || null,\n    };\n}\n\nconst keysPresentForResolve = [...new Set([...byKey.values()].map(b => b.forecast))];\n\nfunction resolveForecastKey(raw, knownKeys) {\n    if (raw == null || raw === '') return null;\n    const s = String(raw);\n    if (knownKeys.includes(s)) return s;\n    const lower = s.toLowerCase();\n    for (const f of knownKeys) {\n        if (titleCase(f).toLowerCase() === lower) return f;\n        if (f.toLowerCase() === lower) return f;\n    }\n    // Fall back to raw key even if not currently plotted (SQL may still have it).\n    return s;\n}\n\nfunction forecastVarCandidate(sqlFieldName, varName) {\n    const fromSql = getField(series.fields, sqlFieldName);\n    const raw = (fromSql.length ? fromSql[0] : null) ?? getVar(varName);\n    return Array.isArray(raw) ? (raw[0] ?? null) : (raw || null);\n}\n\nconst evalForecast = resolveForecastKey(\n    forecastVarCandidate('eval_forecast', 'eval_forecast'),\n    keysPresentForResolve\n);\nconst baselineForecast = resolveForecastKey(\n    forecastVarCandidate('baseline_forecast', 'baseline_forecast'),\n    keysPresentForResolve\n);\n\nfunction selectedForecastKeys() {\n    const raw = getVar('forecast_option');\n    const vals = Array.isArray(raw) ? raw : (raw == null || raw === '' ? [] : [raw]);\n    // Grafana \"All\" often arrives as a single \"$__all\" token \u2014 treat as unrestricted.\n    if (vals.length === 1 && String(vals[0]) === '$__all') return null;\n    if (!vals.length) return null;\n    return new Set(vals.map(String));\n}\n\nconst plotSelection = selectedForecastKeys();\n\nfunction shouldPlotForecast(forecast) {\n    if (evalForecast && forecast === String(evalForecast)) return true;\n    // Unrestricted (\"All\"): plot everything returned by SQL, including baseline.\n    if (plotSelection == null) return true;\n    return plotSelection.has(forecast);\n}\n\n// Plot each forecast on whichever leads it has; missing leads stay empty.\nconst uniqueForecasts = [...new Set(\n    [...byKey.values()].map(b => b.forecast).filter(shouldPlotForecast)\n)].sort();\nconst colorByForecast = new Map(\n    uniqueForecasts.map((f, i) => [f, colorForForecast(f, i)])\n);\n\nconst presentLeads = LEADS.filter(ld =>\n    [...byKey.values()].some(b => b.lead === ld && shouldPlotForecast(b.forecast))\n);\nconst subplotLeads = presentLeads.length ? presentLeads : LEADS;\n\nconst ncols = 2;\nconst nrows = 3;\nconst xPad = 0.05;\nconst yPadBottom = 0.08;\nconst yPadTop = 0.03;\nconst xGap = 0.03;\nconst yGap = 0.07;\nconst kpiGutter = 0.12; // space to the right of each plot for KPI boxes\nconst slotW = (1 - xPad * 2 - xGap * (ncols - 1)) / ncols;\nconst plotW = Math.max(0.28, slotW - kpiGutter);\nconst cellH = (1 - yPadTop - yPadBottom - yGap * (nrows - 1)) / nrows;\n\nfunction domainFor(i) {\n    const col = i % ncols;\n    const rowFromTop = Math.floor(i / ncols);\n    const rowFromBottom = nrows - 1 - rowFromTop;\n    const slotX0 = xPad + col * (slotW + xGap);\n    const y0 = yPadBottom + rowFromBottom * (cellH + yGap);\n    return {\n        x: [slotX0, slotX0 + plotW],\n        y: [y0, y0 + cellH],\n        kpiX: slotX0 + plotW + 0.012,\n    };\n}\n\nconst traces = [];\nconst shapes = [];\nconst annotations = [];\nconst layoutAxes = {};\nconst legendShown = new Set();\n\nsubplotLeads.forEach((lead, i) => {\n    const xid = axisId(i, 'x');\n    const yid = axisId(i, 'y');\n    const domain = domainFor(i);\n\n    layoutAxes[xid === 'x' ? 'xaxis' : `xaxis${i + 1}`] = {\n        domain: domain.x,\n        anchor: yid,\n        type: 'linear',\n        range: [0, 100],\n        dtick: 50,\n        ticksuffix: '%',\n        gridcolor: 'rgba(0,0,0,0.08)',\n        zeroline: false,\n        autorange: false,\n        title: i >= ncols * (nrows - 1)\n            ? { text: 'Threshold (%)', font: { size: 11 } }\n            : undefined,\n        tickfont: { size: 10 },\n    };\n    layoutAxes[yid === 'y' ? 'yaxis' : `yaxis${i + 1}`] = {\n        domain: domain.y,\n        anchor: xid,\n        type: 'linear',\n        rangemode: 'tozero',\n        gridcolor: 'rgba(0,0,0,0.08)',\n        zeroline: false,\n        title: (i % ncols === 0) ? { text: 'Good cells', font: { size: 11 } } : undefined,\n        tickfont: { size: 10 },\n    };\n\n    const leadBuckets = [...byKey.values()]\n        .filter(b => b.lead === lead && shouldPlotForecast(b.forecast))\n        .sort((a, b) => a.forecast.localeCompare(b.forecast));\n    // KPI boxes: eval \u2212 baseline (baseline may be absent from the plot selection).\n    const allLeadBuckets = [...byKey.values()].filter(b => b.lead === lead);\n    const evalScores = leadBandExpectedCells(allLeadBuckets, evalForecast);\n    const baseScores = leadBandExpectedCells(allLeadBuckets, baselineForecast);\n    const infoDelta = deltaOrNull(evalScores.info, baseScores.info);\n    const actDelta = deltaOrNull(evalScores.act, baseScores.act);\n    const midX = (domain.x[0] + domain.x[1]) / 2;\n    const midY = (domain.y[0] + domain.y[1]) / 2;\n    const deltaCaption = (evalForecast && baselineForecast)\n        ? `${titleCase(evalForecast)} \u2212 ${titleCase(baselineForecast)}`\n        : (evalForecast ? titleCase(evalForecast) : 'selected');\n\n    annotations.push({\n        text: `<b>${weekLabel(lead)}</b> \u00b7 D${lead}`,\n        xref: 'paper',\n        yref: 'paper',\n        x: midX,\n        y: domain.y[1] + 0.012,\n        showarrow: false,\n        xanchor: 'center',\n        yanchor: 'bottom',\n        font: { size: 12, color: '#27272a' },\n    });\n\n    // Final KPIs: expected-cell deltas vs baseline, stacked beside the plot.\n    annotations.push({\n        text:\n            `<span style=\"font-size:9px;letter-spacing:0.04em\">INFORMATIVE \u0394</span><br>`\n            + `<b style=\"font-size:18px\">${formatDeltaCells(infoDelta)}</b>`,\n        xref: 'paper',\n        yref: 'paper',\n        x: domain.kpiX,\n        y: midY + 0.045,\n        showarrow: false,\n        xanchor: 'left',\n        yanchor: 'middle',\n        align: 'center',\n        bgcolor: 'rgba(240, 253, 250, 0.96)',\n        bordercolor: '#0f766e',\n        borderwidth: 2,\n        borderpad: 7,\n        font: {\n            size: 12,\n            family: '\"IBM Plex Sans\", \"Segoe UI\", system-ui, sans-serif',\n            color: '#0f766e',\n        },\n    });\n    annotations.push({\n        text:\n            `<span style=\"font-size:9px;letter-spacing:0.04em\">ACTIONABLE \u0394</span><br>`\n            + `<b style=\"font-size:18px\">${formatDeltaCells(actDelta)}</b>`,\n        xref: 'paper',\n        yref: 'paper',\n        x: domain.kpiX,\n        y: midY - 0.01,\n        showarrow: false,\n        xanchor: 'left',\n        yanchor: 'middle',\n        align: 'center',\n        bgcolor: 'rgba(247, 254, 231, 0.96)',\n        bordercolor: '#4d7c0f',\n        borderwidth: 2,\n        borderpad: 7,\n        font: {\n            size: 12,\n            family: '\"IBM Plex Sans\", \"Segoe UI\", system-ui, sans-serif',\n            color: '#4d7c0f',\n        },\n    });\n    annotations.push({\n        text: deltaCaption,\n        xref: 'paper',\n        yref: 'paper',\n        x: domain.kpiX,\n        y: midY - 0.065,\n        showarrow: false,\n        xanchor: 'left',\n        yanchor: 'top',\n        align: 'left',\n        font: {\n            size: 9,\n            family: '\"IBM Plex Sans\", \"Segoe UI\", system-ui, sans-serif',\n            color: '#57534e',\n        },\n    });\n\n    // Band labels inside the shaded regions\n    if (mid > bandLo + 2) {\n        annotations.push({\n            text: 'informative',\n            xref: xid,\n            yref: `${yid} domain`,\n            x: (bandLo + mid) / 2,\n            y: 0.96,\n            showarrow: false,\n            xanchor: 'center',\n            yanchor: 'top',\n            font: { size: 9, color: '#0f766e', family: '\"IBM Plex Sans\", \"Segoe UI\", system-ui, sans-serif' },\n        });\n    }\n    if (bandHi > mid + 2) {\n        annotations.push({\n            text: 'actionable',\n            xref: xid,\n            yref: `${yid} domain`,\n            x: (mid + bandHi) / 2,\n            y: 0.96,\n            showarrow: false,\n            xanchor: 'center',\n            yanchor: 'top',\n            font: { size: 9, color: '#4d7c0f', family: '\"IBM Plex Sans\", \"Segoe UI\", system-ui, sans-serif' },\n        });\n    }\n\n    shapes.push(\n        {\n            type: 'rect', xref: xid, yref: `${yid} domain`,\n            x0: bandLo, x1: mid, y0: 0, y1: 1,\n            fillcolor: 'rgba(20, 120, 120, 0.14)',\n            line: { width: 0 },\n            layer: 'below',\n        },\n        {\n            type: 'rect', xref: xid, yref: `${yid} domain`,\n            x0: mid, x1: bandHi, y0: 0, y1: 1,\n            fillcolor: 'rgba(100, 110, 40, 0.14)',\n            line: { width: 0 },\n            layer: 'below',\n        },\n        {\n            type: 'line', xref: xid, yref: `${yid} domain`,\n            x0: bandLo, x1: bandLo, y0: 0, y1: 1,\n            line: { color: '#0f766e', width: 1.1, dash: 'dot' },\n            layer: 'above',\n        },\n        {\n            type: 'line', xref: xid, yref: `${yid} domain`,\n            x0: mid, x1: mid, y0: 0, y1: 1,\n            line: { color: '#18181b', width: 1.2, dash: 'dash' },\n            layer: 'above',\n        }\n    );\n\n    leadBuckets.forEach(({ forecast, x, y }) => {\n        const pairs = x.map((xi, j) => [xi, y[j]])\n            .filter(([, yi]) => isFiniteNumber(yi))\n            .sort((p, q) => p[0] - q[0]);\n        if (!pairs.length) return;\n\n        const isEval = evalForecast && forecast === String(evalForecast);\n        const lineColor = colorByForecast.get(forecast) || '#52525b';\n        const showInLegend = !legendShown.has(forecast);\n        if (showInLegend) legendShown.add(forecast);\n\n        traces.push({\n            type: 'scatter',\n            mode: 'lines',\n            name: titleCase(forecast),\n            legendgroup: forecast,\n            showlegend: showInLegend,\n            x: pairs.map(p => p[0]),\n            y: pairs.map(p => p[1]),\n            xaxis: xid,\n            yaxis: yid,\n            connectgaps: false,\n            line: {\n                color: lineColor,\n                width: isEval ? 3.4 : 2.0,\n                dash: 'solid',\n            },\n            hovertemplate:\n                `${weekLabel(lead)} \u00b7 %{fullData.name}` +\n                '<br>threshold=%{x:.0f}%<br>good cells=%{y:.0f}<extra></extra>',\n        });\n    });\n});\n\nconst regionTitle = formatList(getVar('region_option'), { empty: 'selected regions' });\nconst forecastTitle = formatList(\n    uniqueForecasts.length ? uniqueForecasts : getVar('forecast_option'),\n    { empty: 'selected forecasts' }\n);\nconst droppedNote = nanForecasts.size\n    ? ` \u00b7 hidden ${nanForecasts.size} with no usable leads`\n    : '';\n\nreturn {\n    data: traces,\n    layout: {\n        title: {\n            text: `Good cells vs cell cutoff \u2014 ${regionTitle} \u00b7 ${forecastTitle}${droppedNote}`,\n            xanchor: 'left',\n            x: 0,\n            font: {\n                size: 14,\n                color: '#18181b',\n                family: '\"IBM Plex Sans\", \"Source Sans 3\", \"Segoe UI\", system-ui, sans-serif',\n                weight: 500,\n            },\n        },\n        ...layoutAxes,\n        shapes,\n        annotations,\n        legend: {\n            orientation: 'h',\n            y: -0.02,\n            x: 0,\n            font: { size: 11 },\n            title: { text: 'Forecast', font: { size: 11 } },\n        },\n        margin: { t: 44, b: 56, l: 48, r: 8 },\n        paper_bgcolor: '#F4F5F5',\n        plot_bgcolor: '#F4F5F5',\n        font: {\n            family: '\"IBM Plex Sans\", \"Source Sans 3\", \"Segoe UI\", system-ui, sans-serif',\n            color: '#27272a',\n        },\n        hovermode: 'closest',\n    },\n};\n",
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
          "rawSql": "WITH cell_avgs AS (\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    -- In 'both' mode PostgreSQL LEAST() ignores NULLs, so a missing forecast\n    -- side would otherwise fall back to obs-only percent_good and look like a\n    -- real (bad) score. Require both sides; otherwise leave null so the lead drops out.\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    END AS percent_good_avg,\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_members_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    END AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_metric_fcst_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    -- In 'both' mode PostgreSQL LEAST() ignores NULLs, so a missing forecast\n    -- side would otherwise fall back to obs-only percent_good and look like a\n    -- real (bad) score. Require both sides; otherwise leave null so the lead drops out.\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    END AS percent_good_avg,\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_members_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    END AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_shifted_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${unimodal_shifted_fcst_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n\n  UNION ALL\n\n  SELECT\n    forecast,\n    $region,\n    lead_day,\n    lat,\n    lon,\n    COALESCE(\n      GREATEST(\n        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n      ),\n      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),\n      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)\n    ) AS metric_avg,\n    -- In 'both' mode PostgreSQL LEAST() ignores NULLs, so a missing forecast\n    -- side would otherwise fall back to obs-only percent_good and look like a\n    -- real (bad) score. Require both sides; otherwise leave null so the lead drops out.\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)\n    END AS percent_good_avg,\n    CASE\n      WHEN '${source}' = 'both' THEN\n        CASE\n          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END) IS NOT NULL\n           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END) IS NOT NULL\n          THEN LEAST(\n            MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),\n            MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n          )\n          ELSE NULL\n        END\n      WHEN '${source}' = 'obs' THEN\n        MAX(CASE WHEN source = 'obs' THEN percent_good_members_year_avg END)\n      ELSE\n        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)\n    END AS percent_good_members_avg,\n    AVG(event_count_year_sum) AS event_count_avg\n  FROM (\n    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${bimodal_metric_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('obs', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n\n    UNION ALL\n\n    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,\n      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,\n      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,\n      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,\n      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum\n    FROM \"${bimodal_metric_fcst_name}\" t\n    WHERE\n      COALESCE(time_grouping, 'None') IN (${time_option})\n      AND (\n        '$__all' IN (${region_option})\n        OR '__all__' IN (${region_option})\n        OR $region IN (${region_option})\n      )\n      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')\n      AND lead_day IN (7, 14, 21, 28, 35, 42)\n      AND '${source}' IN ('forecast', 'both')\n    GROUP BY forecast, $region, lead_day, lat, lon\n  ) combined\n  GROUP BY forecast, $region, lead_day, lat, lon\n),\nthresholds AS (\n  SELECT (gs::double precision / 100.0) AS cell_threshold\n  FROM generate_series(0, 100, 5) AS gs\n),\nvalid_cells AS (\n  -- Null percent_good cells produce empty/zero curves; exclude them.\n  SELECT *\n  FROM cell_avgs\n  WHERE percent_good_avg IS NOT NULL\n),\nper_forecast AS (\n  SELECT\n    t.cell_threshold,\n    c.lead_day,\n    c.forecast,\n    COUNT(*) FILTER (WHERE c.percent_good_avg >= t.cell_threshold) AS good_cells,\n    COUNT(*) AS points_total\n  FROM thresholds t\n  CROSS JOIN valid_cells c\n  GROUP BY t.cell_threshold, c.lead_day, c.forecast\n  HAVING COUNT(*) > 0\n)\nSELECT\n  cell_threshold,\n  lead_day,\n  forecast,\n  good_cells::double precision AS good_cells,\n  points_total::double precision AS points_total,\n  '${informative_cutoff}'::double precision AS informative_cutoff,\n  '${actionable_cutoff}'::double precision AS actionable_cutoff,\n  -- Forces panel refresh when Eval/Baseline forecast changes; also read by Plotly script.\n  '${eval_forecast}' AS eval_forecast,\n  '${baseline_forecast}' AS baseline_forecast\nFROM per_forecast\nORDER BY forecast, lead_day, cell_threshold\n",
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
  "tags": [
    "advanced",
    "evaluation"
  ],
  "templating": {
    "list": [
      {
        "current": {
          "text": "big_rain_days-thresh-0.30",
          "value": "big_rain_days-thresh-0.30"
        },
        "description": "Advanced event metric. percent_good is computed against the -thresh- actionable bar in the metric name.",
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
            "selected": true,
            "text": "Large rain days",
            "value": "big_rain_days-thresh-0.30"
          },
          {
            "selected": false,
            "text": "90th percentile rain",
            "value": "extreme_rain_days-thresh-0.30"
          },
          {
            "selected": false,
            "text": "In season dry spells",
            "value": "in_season_dry_spell-thresh-20"
          }
        ],
        "query": "Early season accumulation : early_season_accumulation-30d-thresh-30, Large rain days : big_rain_days-thresh-0.30, 90th percentile rain : extreme_rain_days-thresh-0.30, In season dry spells : in_season_dry_spell-thresh-20",
        "type": "custom"
      },
      {
        "current": {
          "text": "big_rain_days",
          "value": "big_rain_days"
        },
        "definition": "SELECT split_part('${metric}', '-thresh-', 1)",
        "description": "SQL column name for the selected metric (metric name with the -thresh-\u2026 suffix removed).",
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
          "text": "Days Beyond Baseline",
          "value": "days_beyond_baseline"
        },
        "description": "Expected cells by lead, or days beyond baseline (actionable and informative cell-days summed over weeks 1\u20134).",
        "includeAll": false,
        "label": "View",
        "name": "gc_view",
        "options": [
          {
            "selected": false,
            "text": "Expected Cells",
            "value": "auc"
          },
          {
            "selected": false,
            "text": "Expected Informative",
            "value": "auc_informative"
          },
          {
            "selected": false,
            "text": "Expected Actionable",
            "value": "auc_actionable"
          },
          {
            "selected": true,
            "text": "Days Beyond Baseline",
            "value": "days_beyond_baseline"
          }
        ],
        "query": "Expected Cells : auc, Expected Informative : auc_informative, Expected Actionable : auc_actionable, Days Beyond Baseline : days_beyond_baseline",
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
            "Y2023"
          ],
          "value": [
            "Y2016",
            "Y2017",
            "Y2018",
            "Y2019",
            "Y2020",
            "Y2021",
            "Y2022",
            "Y2023"
          ]
        },
        "definition": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"\nWHERE lead_day IN (7, 14, 21, 28, 35, 42)\n",
        "description": "Which years (or other time groups) to include when averaging cell scores.",
        "label": "Years",
        "multi": true,
        "name": "time_option",
        "options": [],
        "query": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"\nWHERE lead_day IN (7, 14, 21, 28, 35, 42)\n",
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
          "text": "probabilistic",
          "value": "probabilistic"
        },
        "description": "Deterministic vs probabilistic forecast tables.",
        "includeAll": false,
        "label": "Prob",
        "name": "prob_type",
        "options": [
          {
            "selected": false,
            "text": "Deterministic",
            "value": "deterministic"
          },
          {
            "selected": true,
            "text": "Probabilistic",
            "value": "probabilistic"
          }
        ],
        "query": "Deterministic : deterministic, Probabilistic : probabilistic",
        "type": "custom"
      },
      {
        "current": {
          "text": "_prob_type-probabilistic",
          "value": "_prob_type-probabilistic"
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
        "description": "Spatial grid resolution of the metric tables (1.5\u00b0 or 0.25\u00b0).",
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
        "description": "Region typology used for the region multiselect (country, rainfall region, etc.).",
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
          "text": [
            "Kenya"
          ],
          "value": [
            "kenya"
          ]
        },
        "definition": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n",
        "description": "One or more regions to include. Table counts and the curve sum cells across the selection.",
        "includeAll": true,
        "label": "Regions",
        "multi": true,
        "name": "region_option",
        "options": [],
        "query": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\n",
        "refresh": 1,
        "regex": "",
        "type": "query",
        "allValue": "'__all__'"
      },
      {
        "current": {
          "text": [
            "Climatology ERA5 1985-2014",
            "Climatology IMERG 1998-2015",
            "Cumulus AI v0.0.0",
            "ECMWF IFS ENS",
            "ECMWF IFS ER"
          ],
          "value": [
            "climatology_era5_1985_2015",
            "climatology_imerg_1998_2016",
            "cumulus_ai",
            "ecmwf_ifs_ens",
            "ecmwf_ifs_er"
          ]
        },
        "definition": "SELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nORDER BY 1",
        "description": "One or more forecasts to include. Curve uses color for week and line style for forecast.",
        "includeAll": true,
        "label": "Forecasts",
        "multi": true,
        "name": "forecast_option",
        "options": [],
        "query": "SELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nORDER BY 1",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "Cumulus AI v0.0.0",
          "value": "cumulus_ai"
        },
        "definition": "SELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nORDER BY 1",
        "description": "Forecast for per-lead Informative/Actionable expected-cell boxes and as the numerator in days-beyond-baseline KPIs.",
        "includeAll": false,
        "label": "Eval forecast",
        "name": "eval_forecast",
        "options": [],
        "query": "SELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nORDER BY 1",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "Climatology IMERG 1998-2015",
          "value": "climatology_imerg_1998_2016"
        },
        "definition": "SELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nORDER BY 1",
        "description": "Comparator for days-beyond-baseline KPIs: actionable and informative cell-days summed over weeks 1\u20134 (leads 7, 14, 21, 28).",
        "includeAll": false,
        "label": "Baseline forecast",
        "name": "baseline_forecast",
        "options": [],
        "query": "SELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\nSELECT DISTINCT CASE forecast\n  WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'\n  WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'\n  WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'\n  WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'\n  WHEN 'ecmwf_hres' THEN 'ECMWF HRES'\n  WHEN 'gfs' THEN 'GFS'\n  WHEN 'salient' THEN 'AI-Enhanced NWP'\n  WHEN 'fuxi' THEN 'FuXi S2S'\n  WHEN 'graphcast' THEN 'GraphCast'\n  WHEN 'gencast' THEN 'GenCast'\n  WHEN 'climatology_2015' THEN 'Climatology 1985-2014'\n  WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'\n  WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'\n  WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'\n  WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'\n  ELSE initcap(replace(forecast, '_', ' '))\nEND\n AS __text, forecast AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nORDER BY 1",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "3fa7ab60a8aacaa9ce3a4fd7fdb34205",
          "value": "3fa7ab60a8aacaa9ce3a4fd7fdb34205"
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
          "text": "0511e70c4f418962ad27245a5ae5548f",
          "value": "0511e70c4f418962ad27245a5ae5548f"
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
          "text": "848aef143449b15e482017e8c98df6b3",
          "value": "848aef143449b15e482017e8c98df6b3"
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
          "text": "536f59461b4e1effcdfe014232b1dac0",
          "value": "536f59461b4e1effcdfe014232b1dac0"
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
          "text": "37ced1cadfa826aa3502d3426b21d617",
          "value": "37ced1cadfa826aa3502d3426b21d617"
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
          "text": "71aabe373b3d47fcda107b9c18bd2ae4",
          "value": "71aabe373b3d47fcda107b9c18bd2ae4"
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
          "text": "0.50",
          "value": "0.50"
        },
        "description": "Lower edge of the teal Informative band (0\u20131). Informative expected cells average over this cutoff up to the Actionable cutoff.",
        "label": "Informative cutoff",
        "name": "informative_cutoff",
        "options": [
          {
            "selected": true,
            "text": "0.50",
            "value": "0.50"
          }
        ],
        "query": "0.50",
        "type": "textbox"
      },
      {
        "current": {
          "text": "0.75",
          "value": "0.75"
        },
        "description": "Start of the green Actionable band (0\u20131). Also used as the table cell-count cutoff and dashed line on the curve. Actionable expected cells average from here to 100%.",
        "label": "Actionable cutoff",
        "name": "actionable_cutoff",
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
  "title": "Good Cells vs Cell Cutoff",
  "uid": "sw-good-cells-cutoff",
  "version": 1,
  "weekStart": ""
}
