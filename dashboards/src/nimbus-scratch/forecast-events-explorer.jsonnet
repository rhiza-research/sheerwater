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
  "description": "Explore forecast performance across specific impactful events. ",
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "links": [],
  "panels": [
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "status"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "last_quality_flag"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 9,
        "w": 8,
        "x": 0,
        "y": 0
      },
      "id": 3,
      "options": {
        "allData": {},
        "config": {
          "config": {
            "displayModeBar": true,
            "responsive": true,
            "scrollZoom": true
          },
          "displayModeBar": "true,         // \u2b05\ufe0f shows zoom tools",
          "responsive": "true,",
          "scrollZoom": "true              // \u2b05\ufe0f enables mouse wheel zoom"
        },
        "data": [],
        "imgFormat": "png",
        "layout": {
          "font": {
            "family": "Inter, Helvetica, Arial, sans-serif"
          },
          "margin": {
            "b": 0,
            "l": 0,
            "r": 0,
            "t": 0
          },
          "options": {
            "config": {
              "displayModeBar": true,
              "responsive": true,
              "scrollZoom": true
            },
            "layout": {
              "mapbox": {
                "center": {
                  "lat": 0,
                  "lon": 20
                },
                "dragmode": "zoom",
                "scrollZoom": false,
                "style": "open-street-map",
                "zoom": 2
              },
              "margin": {
                "b": 0,
                "l": 0,
                "r": 0,
                "t": 0
              },
              "paper_bgcolor": "rgba(0,0,0,0)",
              "plot_bgcolor": "rgba(0,0,0,0)",
              "showlegend": false
            }
          },
          "title": {
            "automargin": true
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
        "onclick": "try {\n  const { type: eventType, data: eventData } = event;\n\n  if (eventType === 'click') {\n    const clickedPoint = eventData?.points?.[0];\n\n    if (clickedPoint) {\n      const currentUrl = new URL(window.location.href);\n\n      currentUrl.searchParams.set('var-lat', clickedPoint.lat);\n      currentUrl.searchParams.set('var-lon', clickedPoint.lon);\n\n      currentUrl.searchParams.set('var-filter_space', true);\n\n      const plots = document.querySelectorAll('.js-plotly-plot');\n      const plotEl = Array.from(plots).find(p => p._fullLayout?.mapbox);\n      const mapSubplot = plotEl._fullLayout.mapbox._subplot;\n\n      console.log(plotEl._fullLayout.mapbox);\n\n      \n      const center = mapSubplot.map.getCenter();\n      const zoom = mapSubplot.map.getZoom();\n\n      currentUrl.searchParams.set('var-map_zoom', zoom.toFixed(2));\n      currentUrl.searchParams.set('var-map_center_lat', center.lat.toFixed(4));\n      currentUrl.searchParams.set('var-map_center_lon', center.lng.toFixed(4));\n\n      window.location.href = currentUrl.toString();\n    }\n  }\n} catch (error) {\n  console.error('Error in map click handler:', error);\n}",
        "resScale": 2,
        "script": "const getVar = (name) => (\n  variables?.[name]?.current?.value ??\n  variables?.[name]?.value ??\n  null\n);\n\nfunction emptyMap(message) {\n  return {\n    data: [{\n      type: \"scatter\",\n      x: [0],\n      y: [0],\n      mode: \"text\",\n      text: [message],\n      textposition: \"middle center\",\n      hoverinfo: \"skip\",\n      marker: { opacity: 0 },\n    }],\n    layout: {\n      xaxis: { visible: false, fixedrange: true },\n      yaxis: { visible: false, fixedrange: true },\n      margin: { t: 20, b: 20, l: 20, r: 20 },\n      paper_bgcolor: \"rgba(0,0,0,0)\",\n      plot_bgcolor: \"rgba(0,0,0,0)\",\n    },\n    config: { responsive: true, displayModeBar: false },\n  };\n}\n\nif (!data.series || !data.series.length || !data.series[0].fields) {\n  return emptyMap(\"No map data for this selection.\");\n}\n\nconst fields = data.series[0].fields;\nconst latField = fields.find(f => f.name === \"lat\");\nconst lonField = fields.find(f => f.name === \"lon\");\nconst valueField = fields.find(f => f.name === \"value\");\n\nif (!latField || !lonField || !valueField) {\n  return emptyMap(\"No map data for this selection.\");\n}\n\nconst lats = Array.from(latField.values || latField.values.buffer || []);\nconst lons = Array.from(lonField.values || lonField.values.buffer || []);\nconst values = Array.from(valueField.values || valueField.values.buffer || []);\n\nif (!lats.length) {\n  return emptyMap(\"No map data for this selection.\");\n}\n\nconst lat1 = parseFloat(getVar(\"lat\"));\nconst lon1 = parseFloat(getVar(\"lon\"));\nconst mapZoom = parseFloat(getVar(\"map_zoom\")) || 1.5;\nconst mapCenterLat = parseFloat(getVar(\"map_center_lat\")) || 10;\nconst mapCenterLon = parseFloat(getVar(\"map_center_lon\")) || 30;\n\nconst traces = [{\n  type: \"scattermapbox\",\n  lat: lats,\n  lon: lons,\n  mode: \"markers\",\n  marker: {\n    size: 7,\n    color: values,\n    colorscale: \"Viridis\",\n    cmin: Math.min(...values),\n    cmax: Math.max(...values),\n    opacity: 0.8,\n    showscale: true,\n    colorbar: { title: getVar(\"metric_name\") },\n  },\n  text: values.map(v => `Value: ${v}`),\n  hovertemplate:\n    \"Lat: %{lat:.2f}<br>\" +\n    \"Lon: %{lon:.2f}<br>\" +\n    \"%{text}<extra></extra>\",\n  showlegend: false,\n}];\n\nif (!isNaN(lat1) && !isNaN(lon1)) {\n  traces.push({\n    type: \"scattermapbox\",\n    lat: [lat1],\n    lon: [lon1],\n    mode: \"markers\",\n    marker: {\n      size: 14,\n      color: \"gold\",\n      line: { width: 2, color: \"black\" },\n    },\n    text: [`Selected point<br>Lat: ${lat1}<br>Lon: ${lon1}`],\n    hovertemplate: \"%{text}<extra></extra>\",\n    showlegend: false,\n  });\n}\n\nreturn {\n  data: traces,\n  layout: {\n    mapbox: {\n      style: \"open-street-map\",\n      center: { lat: mapCenterLat, lon: mapCenterLon },\n      zoom: mapZoom,\n      dragmode: \"zoom\",\n    },\n    margin: { t: 0, b: 0, l: 0, r: 0 },\n    paper_bgcolor: \"rgba(0,0,0,0)\",\n    plot_bgcolor: \"rgba(0,0,0,0)\",\n  },\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true,\n  },\n};\n",
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
          "hide": false,
          "rawQuery": true,
          "rawSql": "SELECT lat, lon, value FROM \"${fcst_points_table_west}\"\nUNION ALL\nSELECT lat, lon, value FROM \"${fcst_points_table_east}\"\n",
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
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "description": "Climatology & Annual Series",
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 16,
        "x": 8,
        "y": 0
      },
      "id": 6,
      "options": {
        "allData": {},
        "config": {
          "config": {
            "displayModeBar": true,
            "responsive": true,
            "scrollZoom": true,
            "doubleClick": "autosize"
          }
        },
        "data": [],
        "imgFormat": "png",
        "layout": {
          "font": {
            "family": "Inter, Helvetica, Arial, sans-serif"
          },
          "legend": {
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.15,
            "yanchor": "top"
          },
          "margin": {
            "b": 0,
            "l": 0,
            "r": 0,
            "t": 0
          },
          "title": {
            "automargin": true
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
        "onclick": "// Plotly zoom/pan only \u2014 no Grafana time picker\n",
        "resScale": 2,
        "script": "// --- Safe variable getter ---\nconst getVar = (name) => {\n  return (\n    variables?.[name]?.current?.value ??\n    variables?.[name]?.value ??\n    null\n  );\n};\n\nfunction formatDateUTC(t) {\n  const d = new Date(t);\n  const yyyy = d.getUTCFullYear();\n  const mm = String(d.getUTCMonth() + 1).padStart(2, '0');\n  const dd = String(d.getUTCDate()).padStart(2, '0');\n  return `${yyyy}-${mm}-${dd}`;\n}\n\nconst selectedSourcesRaw = getVar(\"models\");\nconst selectedSources = Array.isArray(selectedSourcesRaw)\n  ? selectedSourcesRaw.map(String)\n  : (selectedSourcesRaw == null || selectedSourcesRaw === \"\"\n      ? []\n      : [String(selectedSourcesRaw)]);\nconst hasSource = (name) => selectedSources.includes(name);\n\n// data.series index must match panel target order\nconst SERIES_CONFIG = [\n  { index: 0, key: \"imerg\", label: \"IMERG (observed)\", color: \"#1f77b4\", width: 2.5 },\n  { index: 1, key: \"ecmwf-ifs-er\", label: \"ECMWF IFS-ER\", color: \"#ff7f0e\", width: 2 },\n  { index: 2, key: \"era5\", label: \"ERA5\", color: \"#2ca02c\", width: 2 },\n  { index: 3, key: \"cumulus\", label: \"Cumulus AI\", color: \"#d62728\", width: 2 },\n];\n\nfunction lighten(hex, amount) {\n  const col = hex.replace(\"#\", \"\");\n  const num = parseInt(col, 16);\n  const r = (num >> 16) & 0xFF;\n  const g = (num >> 8) & 0xFF;\n  const b = num & 0xFF;\n  const lr = Math.round(r + (255 - r) * amount);\n  const lg = Math.round(g + (255 - g) * amount);\n  const lb = Math.round(b + (255 - b) * amount);\n  return `rgb(${lr}, ${lg}, ${lb})`;\n}\n\nfunction buildTrace(series, { label, color, width }) {\n  const fields = series.fields;\n  const timeField = fields.find(f => f.name === \"time\");\n  const valueField = fields.find(f => f.name !== \"time\");\n\n  if (!timeField || !valueField || timeField.values.length === 0) {\n    return null;\n  }\n\n  const times = Array.from(timeField.values || timeField.values.buffer || []);\n  const values = Array.from(valueField.values || valueField.values.buffer || []);\n  const dateLabels = times.map(formatDateUTC);\n\n  return {\n    type: \"scatter\",\n    mode: \"lines+markers\",\n    x: times,\n    y: values,\n    customdata: dateLabels,\n    name: label,\n    line: { color: lighten(color, 0.45), width },\n    marker: { color, size: width * 2.5 },\n    hovertemplate: \"%{customdata}<br>%{y:.2f}<extra>\" + label + \"</extra>\",\n  };\n}\n\nconst traces = SERIES_CONFIG\n  .filter(cfg => hasSource(cfg.key))\n  .map(cfg => {\n    const series = data.series[cfg.index];\n    if (!series) return null;\n    return buildTrace(series, cfg);\n  })\n  .filter(Boolean);\n\n// --- Grey band: true scored-event duration (align + duration from event_type) ---\nfunction eventDurationShape() {\n    const eventDate = new Date(getVar(\"event_date\"));\n    if (isNaN(eventDate.getTime())) return [];\n    const duration = parseInt(getVar(\"event_duration\"), 10);\n    const align = String(getVar(\"event_align\") || \"center\");\n    const dayMs = 24 * 60 * 60 * 1000;\n    const t = eventDate.getTime();\n    const d = (Number.isFinite(duration) && duration > 0) ? duration : 1;\n    let x0, x1;\n    if (align === \"right\") {\n        x0 = t - (d - 1) * dayMs;\n        x1 = t + dayMs;\n    } else if (align === \"left\") {\n        x0 = t;\n        x1 = t + d * dayMs;\n    } else {\n        const left = Math.floor((d - 1) / 2);\n        x0 = t - left * dayMs;\n        x1 = t + (d - left) * dayMs;\n    }\n    return [{\n        type: \"rect\",\n        xref: \"x\",\n        yref: \"paper\",\n        x0, x1, y0: 0, y1: 1,\n        fillcolor: \"rgba(128, 128, 128, 0.25)\",\n        line: { width: 0 },\n        layer: \"below\",\n    }];\n}\n\n// Initial view: event_date \u00b1 event_window; double-click autosizes to full series\nfunction eventViewRange() {\n  const eventDate = new Date(getVar(\"event_date\"));\n  if (isNaN(eventDate.getTime())) return null;\n  const windowDays = Math.max(parseInt(getVar(\"event_window\"), 10) || 14, 7);\n  const dayMs = 24 * 60 * 60 * 1000;\n  const t = eventDate.getTime();\n  // numeric ms ranges are more reliable for Plotly double-click / zoom\n  return [t - windowDays * dayMs, t + windowDays * dayMs];\n}\n\nconst eventShape = eventDurationShape();\nconst viewRange = eventViewRange();\nconst eventType = String(getVar(\"event_type\") || \"\");\nconst uiRevision = [\n  \"precip\",\n  getVar(\"event_date\"),\n  getVar(\"lat\"),\n  getVar(\"lon\"),\n  eventType,\n].join(\":\");\n\n// Y-axis calibrated to event type using values inside the current x-window\nfunction precipYRange(traces, xRange) {\n  let maxInView = 0;\n  for (const tr of traces) {\n    const xs = tr.x || [];\n    const ys = tr.y || [];\n    for (let i = 0; i < xs.length; i++) {\n      const t = +new Date(xs[i]);\n      if (xRange && (t < xRange[0] || t > xRange[1])) continue;\n      const v = ys[i];\n      if (Number.isFinite(v) && v > maxInView) maxInView = v;\n    }\n  }\n\n  if (eventType === \"in_season_dry_spell\") {\n    // Tight low range so dryness is readable (cap even if a wet spike sits nearby)\n    const top = Math.max(3, maxInView * 1.25);\n    return [0, Math.min(8, Math.max(top, 3))];\n  }\n  if (eventType.indexOf(\"early_season\") !== -1) {\n    return [0, Math.max(25, maxInView * 1.15)];\n  }\n  // big_rain_days (and default): leave headroom for peaks\n  return [0, Math.max(40, maxInView * 1.2)];\n}\n\nif (!traces.length) {\n  return {\n    data: [],\n    layout: {\n      title: { text: \"No precip for this selection.\", font: { size: 13 } },\n      xaxis: { visible: false },\n      yaxis: { visible: false },\n      paper_bgcolor: \"rgba(0,0,0,0)\",\n      plot_bgcolor: \"rgba(0,0,0,0)\",\n    },\n    config: { responsive: true, displayModeBar: false },\n  };\n}\n\nconst yRange = precipYRange(traces, viewRange);\n\nreturn {\n  data: traces,\n  layout: {\n    font: { family: \"Inter, Helvetica, Arial, sans-serif\" },\n    dragmode: \"zoom\",\n    hovermode: \"closest\",\n    // Preserve zoom across Plotly.react; change when event/location/type changes\n    uirevision: uiRevision,\n    xaxis: {\n      type: \"date\",\n      autorange: !viewRange,\n      range: viewRange || undefined,\n      automargin: true,\n      fixedrange: false,\n    },\n    yaxis: {\n      autorange: false,\n      range: yRange,\n      automargin: true,\n      fixedrange: false,\n      title: { text: \"Precipitation (mm)\" },\n    },\n    title: { automargin: true },\n    margin: { l: 50, r: 20, b: 40, t: 20 },\n    legend: { orientation: \"h\", y: 1.12 },\n    plot_bgcolor: \"rgba(0,0,0,0)\",\n    paper_bgcolor: \"rgba(0,0,0,0)\",\n    shapes: eventShape,\n  },\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true,\n    doubleClick: \"autosize\",\n    modeBarButtonsToAdd: [\"pan2d\", \"zoomIn2d\", \"zoomOut2d\", \"autoScale2d\", \"resetScale2d\"],\n  },\n};\n",
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
          "hide": false,
          "rawQuery": true,
          "rawSql": "WITH filtered AS (\n    SELECT\n        t.time,\n        t.precip\n    FROM (\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_india\"\n        UNION ALL\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_eastern_africa\"\n        UNION ALL\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_western_africa\"\n    ) t\n    WHERE t.lat = ${lat}\n      AND t.lon = ${lon}\n)\n\nSELECT\n    time,\n    AVG(precip) OVER (\n        ORDER BY time\n        ROWS BETWEEN ${agg_days}-1 PRECEDING AND CURRENT ROW\n    ) AS precip\nFROM filtered\nORDER BY time;",
          "refId": "annual_series_imerg",
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
          "rawSql": "SELECT\n    t.time,\n    t.precip / ${agg_days} AS precip\nFROM (\n    SELECT * FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_western_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_india\"\n) t\nWHERE t.lat = ${lat}\n  AND t.lon = ${lon}\nORDER BY t.time;",
          "refId": "annual_series_ecmwf_ifs_er_fcst",
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
          "rawSql": "WITH source_tables AS (\n    SELECT * FROM \"full_rainfall/era5_${grid}_india\"\n    UNION ALL\n    SELECT * FROM \"full_rainfall/era5_${grid}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"full_rainfall/era5_${grid}_western_africa\"\n),\n\ncombined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM source_tables\n),\n\nnearest_point AS (\n    SELECT\n        lat,\n        lon,\n        SQRT(\n            POWER(lat - ${lat}, 2) +\n            POWER(lon - ${lon}, 2)\n        ) AS distance_deg\n    FROM combined_points\n    ORDER BY distance_deg\n    LIMIT 1\n),\n\nfiltered AS (\n    SELECT\n        t.time,\n        t.precip\n    FROM source_tables t\n    JOIN nearest_point n\n      ON t.lat = n.lat\n     AND t.lon = n.lon\n    WHERE n.distance_deg <= (200.0 / 111.0)\n)\n\nSELECT\n    time,\n    AVG(precip) OVER (\n        ORDER BY time\n        ROWS BETWEEN ${agg_days}-1 PRECEDING AND CURRENT ROW\n    ) AS precip\nFROM filtered\nORDER BY time;",
          "refId": "annual_series_era5",
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
          "rawSql": "WITH combined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_eastern_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_western_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_india\"\n),\n\nnearest_point AS (\n    SELECT\n        lat,\n        lon,\n        SQRT(\n            POWER(lat - ${lat}, 2) +\n            POWER(lon - ${lon}, 2)\n        ) AS distance_deg\n    FROM combined_points\n    ORDER BY distance_deg\n    LIMIT 1\n)\n\nSELECT\n    t.time,\n    t.precip / ${agg_days} AS precip\nFROM (\n    SELECT * FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_western_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_india\"\n) t\nJOIN nearest_point n\n  ON t.lat = n.lat\n AND t.lon = n.lon\nWHERE n.distance_deg <= (200 / 111.0)\nORDER BY t.time;",
          "refId": "annual_series_cumulus_fcst",
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
      "title": "Precipitation",
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
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
        "y": 9
      },
      "id": 7,
      "options": {
        "allData": {},
        "config": {
          "config": {
            "displayModeBar": true,
            "responsive": true,
            "scrollZoom": true
          }
        },
        "data": [],
        "imgFormat": "png",
        "layout": {
          "font": {
            "family": "Inter, Helvetica, Arial, sans-serif"
          },
          "margin": {
            "b": 0,
            "l": 0,
            "r": 0,
            "t": 0
          },
          "title": {
            "automargin": true
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
        "onclick": "try {\n  const { type: eventType, data: eventData } = event;\n  if (eventType !== 'click') return;\n\n  const points = eventData?.points || [];\n  const barPoint = points.find(p => p.data && p.data.type === 'bar') || points[0];\n  if (!barPoint) return;\n\n  let eventDateStr = barPoint.customdata;\n  if (Array.isArray(eventDateStr)) eventDateStr = eventDateStr[0];\n  if (eventDateStr == null || eventDateStr === '') eventDateStr = barPoint.x;\n\n  const eventDate = new Date(eventDateStr);\n  if (isNaN(eventDate.getTime())) {\n    console.error('Could not parse event date:', eventDateStr);\n    return;\n  }\n\n  const yyyy = eventDate.getUTCFullYear();\n  const mm = String(eventDate.getUTCMonth() + 1).padStart(2, '0');\n  const dd = String(eventDate.getUTCDate()).padStart(2, '0');\n  const eventDateISO = `${yyyy}-${mm}-${dd}`;\n\n  const currentUrl = new URL(window.location.href);\n  currentUrl.searchParams.set('var-event_date', eventDateISO);\n  // Drop any leftover Grafana time-picker params\n  currentUrl.searchParams.delete('from');\n  currentUrl.searchParams.delete('to');\n  window.location.href = currentUrl.toString();\n} catch (error) {\n  console.error('Error in bar click handler:', error);\n}\n",
        "resScale": 2,
        "script": "// --- Safe variable getter ---\nconst getVar = (name) => {\n  return (\n    variables?.[name]?.current?.value ??\n    variables?.[name]?.value ??\n    null\n  );\n};\n\nfunction emptyEvents(message) {\n  return {\n    data: [{\n      type: \"scatter\",\n      x: [0],\n      y: [0],\n      mode: \"text\",\n      text: [message],\n      textposition: \"middle center\",\n      hoverinfo: \"skip\",\n      marker: { opacity: 0 },\n    }],\n    layout: {\n      xaxis: { visible: false, fixedrange: true },\n      yaxis: { visible: false, fixedrange: true },\n      margin: { t: 20, b: 20, l: 20, r: 20 },\n      paper_bgcolor: \"rgba(0,0,0,0)\",\n      plot_bgcolor: \"rgba(0,0,0,0)\",\n    },\n    config: { responsive: true, displayModeBar: false },\n  };\n}\n\nfunction formatDate(t) {\n  const d = new Date(t);\n  const yyyy = d.getUTCFullYear();\n  const mm = String(d.getUTCMonth() + 1).padStart(2, '0');\n  const dd = String(d.getUTCDate()).padStart(2, '0');\n  return `${yyyy}-${mm}-${dd}`;\n}\n\n// --- Event data (bars) ---\nconst eventSeries = data.series.find(s => s.refId === 'event_times');\nif (!eventSeries || !eventSeries.fields || !eventSeries.fields.length) {\n  return emptyEvents(\"No events for this selection.\");\n}\n\nconst timeField = eventSeries.fields.find(f => f.name === \"time\" || f.name === \"Time\");\nconst valueField = eventSeries.fields.find(f => f.name === \"value\" || f.name === \"Value\");\n\nif (!timeField || !valueField || !timeField.values || timeField.values.length === 0) {\n  return emptyEvents(\"No events for this selection.\");\n}\n\nconst times = Array.from(timeField.values || timeField.values.buffer || []);\nconst values = Array.from(valueField.values || valueField.values.buffer || []);\n\nconst minEventTime = Math.min(...times);\nconst maxEventTime = Math.max(...times);\n\n// --- Threshold for \"good\" events ---\nconst GOOD_THRESHOLD = parseFloat(getVar(\"good_thresh\"));\nconst GOOD_COLOR = 'rgba(0, 170, 0, 0.8)';\nconst BAD_COLOR = 'rgba(200, 0, 0, 0.8)';\n\nconst dateLabels = times.map(formatDate);\nconst selectedDateStr = formatDate(getVar(\"event_date\"));\nconst dayMs = 24 * 60 * 60 * 1000;\nconst BAR_WIDTH = 4 * dayMs;\n\nconst colors = [];\nlet selectedIdx = -1;\nfor (let i = 0; i < values.length; i++) {\n  const isSelected = dateLabels[i] === selectedDateStr;\n  if (isSelected) selectedIdx = i;\n  const base = values[i] <= GOOD_THRESHOLD ? GOOD_COLOR : BAD_COLOR;\n  colors.push(isSelected ? base : base.replace('0.8', '0.4'));\n}\n\nconst eventTrace = {\n  type: 'bar',\n  x: times,\n  y: values,\n  yaxis: 'y',\n  customdata: dateLabels,\n  marker: { color: colors },\n  width: BAR_WIDTH,\n  hovertemplate: 'Date: %{customdata}<br>Value: %{y}<extra></extra>'\n};\n\n// Wide gold bar + diamond so the selected event reads clearly\nconst selectedBarTrace = selectedIdx >= 0 ? {\n  type: 'bar',\n  x: [times[selectedIdx]],\n  y: [values[selectedIdx]],\n  yaxis: 'y',\n  width: 10 * dayMs,\n  marker: {\n    color: 'rgba(255, 200, 0, 0.35)',\n    line: { color: 'rgba(0,0,0,0.95)', width: 2 },\n  },\n  hoverinfo: 'skip',\n  showlegend: false,\n} : null;\n\nconst selectedMarkerTrace = selectedIdx >= 0 ? {\n  type: 'scatter',\n  mode: 'markers',\n  x: [times[selectedIdx]],\n  y: [values[selectedIdx]],\n  yaxis: 'y',\n  name: 'Selected',\n  marker: {\n    symbol: 'diamond',\n    size: 13,\n    color: 'rgba(255, 210, 0, 1)',\n    line: { color: 'rgba(0,0,0,0.9)', width: 1.5 },\n  },\n  hovertemplate: 'Selected<br>%{customdata}<br>Value: %{y}<extra></extra>',\n  customdata: [selectedDateStr],\n} : null;\n\n// --- IMERG data (line, on secondary axis, drawn behind, clipped to event range) ---\nconst imergSeries = data.series.find(s => s.refId === 'imerg');\nlet imergTrace = null;\n\nif (imergSeries) {\n  const iTimeField = imergSeries.fields.find(f => f.name === 'time');\n  const iValueField = imergSeries.fields.find(f => f.name !== 'time');\n\n  if (iTimeField && iValueField && iTimeField.values.length > 0) {\n    const rawTimes = Array.from(iTimeField.values || iTimeField.values.buffer || []);\n    const rawValues = Array.from(iValueField.values || iValueField.values.buffer || []);\n\n    const iTimes = [];\n    const iValues = [];\n    for (let i = 0; i < rawTimes.length; i++) {\n      if (rawTimes[i] >= minEventTime && rawTimes[i] <= maxEventTime) {\n        iTimes.push(rawTimes[i]);\n        iValues.push(rawValues[i]);\n      }\n    }\n\n    if (iTimes.length > 0) {\n      imergTrace = {\n        type: 'scatter',\n        mode: 'lines',\n        x: iTimes,\n        y: iValues,\n        yaxis: 'y2',\n        name: 'IMERG precip',\n        line: { color: 'rgba(31, 119, 180, 0.2)', width: 1.5 },\n        hoverinfo: 'skip' // no tooltip box for imerg \u2014 only events should show one\n      };\n    }\n  }\n}\n\n// imerg first so it renders behind the event bars\nconst traces = [...(imergTrace ? [imergTrace] : []), ...(selectedBarTrace ? [selectedBarTrace] : []), eventTrace, ...(selectedMarkerTrace ? [selectedMarkerTrace] : [])];\n\n// --- Grey band: true scored-event duration (align + duration from event_type) ---\n\nfunction eventDurationShape() {\n    const eventDate = new Date(getVar(\"event_date\"));\n    if (isNaN(eventDate.getTime())) return { shapes: [], annotations: [] };\n    const duration = parseInt(getVar(\"event_duration\"), 10);\n    const align = String(getVar(\"event_align\") || \"center\");\n    const t = eventDate.getTime();\n    const d = (Number.isFinite(duration) && duration > 0) ? duration : 1;\n    let x0, x1;\n    if (align === \"right\") {\n        x0 = t - (d - 1) * dayMs;\n        x1 = t + dayMs;\n    } else if (align === \"left\") {\n        x0 = t;\n        x1 = t + d * dayMs;\n    } else {\n        const left = Math.floor((d - 1) / 2);\n        x0 = t - left * dayMs;\n        x1 = t + (d - left) * dayMs;\n    }\n    const shapes = [\n      {\n        type: \"rect\",\n        xref: \"x\",\n        yref: \"paper\",\n        x0, x1, y0: 0, y1: 1,\n        fillcolor: \"rgba(255, 196, 0, 0.28)\",\n        line: { color: \"rgba(180, 120, 0, 0.9)\", width: 2 },\n        layer: \"below\",\n      },\n      // center line on the event date\n      {\n        type: \"line\",\n        xref: \"x\",\n        yref: \"paper\",\n        x0: t, x1: t, y0: 0, y1: 1,\n        line: { color: \"rgba(0, 0, 0, 0.75)\", width: 2, dash: \"dot\" },\n        layer: \"above\",\n      },\n    ];\n    const annotations = [{\n      x: t,\n      y: 1,\n      xref: \"x\",\n      yref: \"paper\",\n      text: \"Selected \" + formatDate(t),\n      showarrow: false,\n      yanchor: \"bottom\",\n      xanchor: \"center\",\n      font: { size: 11, color: \"rgba(60, 40, 0, 1)\", family: \"Inter, Helvetica, Arial, sans-serif\" },\n      bgcolor: \"rgba(255, 220, 80, 0.9)\",\n      bordercolor: \"rgba(120, 80, 0, 0.8)\",\n      borderwidth: 1,\n      borderpad: 3,\n    }];\n    return { shapes, annotations };\n}\n\nconst { shapes: eventShape, annotations: eventAnnotations } = eventDurationShape();\n\n// --- Good/bad event counts ---\nconst totalEvents = values.length;\nconst goodCount = values.filter(v => v <= GOOD_THRESHOLD).length;\nconst badCount = totalEvents - goodCount;\n\nconst maxEventValue = Math.max(...values);\nconst maxImergValue = imergTrace ? Math.max(...imergTrace.y) : 1;\n\nreturn {\n  data: traces,\n  layout: {\n    dragmode: 'zoom',\n    hovermode: 'closest',\n    font: { family: 'Inter, Helvetica, Arial, sans-serif' },\n    xaxis: {\n      type: 'date',\n      autorange: true,\n      automargin: true,\n      range: [minEventTime, maxEventTime]\n    },\n    showlegend: false,\n    yaxis: {\n      range: [0, maxEventValue * 1.05],\n      automargin: true,\n      title: { text: getVar(\"metric_name\") }\n    },\n    yaxis2: {\n      overlaying: 'y',\n      side: 'right',\n      range: [0, maxImergValue * 1.05],\n      automargin: true,\n      showgrid: false,\n      title: { text: 'IMERG precip (mm)' }\n    },\n    title: {\n      text: `Selected: ${selectedDateStr}  |  Total: ${totalEvents}  |  Good: ${goodCount}  |  Bad: ${badCount}`,\n      font: { size: 12 },\n      automargin: true\n    },\n    margin: { l: 50, r: 50, b: 40, t: 30 },\n    shapes: [\n      {\n        type: 'line',\n        xref: 'paper',\n        x0: 0,\n        x1: 1,\n        yref: 'y',\n        y0: GOOD_THRESHOLD,\n        y1: GOOD_THRESHOLD,\n        line: { color: 'rgba(0,0,0,0.6)', width: 1.5, dash: 'dash' }\n      },\n      ...eventShape\n    ],\n    annotations: eventAnnotations,\n  },\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true,\n    doubleClick: \"reset\"\n  }\n};",
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT time, value FROM (\n    SELECT lat, lon, time, value FROM \"${event_list_table_west}\"\n    UNION ALL\n    SELECT lat, lon, time, value FROM \"${event_list_table_east}\"\n) combined\nWHERE lat = ${lat} AND lon = ${lon}\nORDER BY value DESC\n",
          "refId": "event_times",
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
          },
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "bdz3m3xs99p1cf"
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
          "rawSql": "WITH filtered AS (\n    SELECT\n        t.time,\n        t.precip\n    FROM (\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_india\"\n        UNION ALL\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_eastern_africa\"\n        UNION ALL\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_western_africa\"\n    ) t\n    WHERE t.lat = ${lat}\n      AND t.lon = ${lon}\n)\n\nSELECT\n    time,\n    AVG(precip) OVER (\n        ORDER BY time\n        ROWS BETWEEN ${agg_days}-1 PRECEDING AND CURRENT ROW\n    ) AS precip\nFROM filtered\nORDER BY time;",
          "refId": "imerg",
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
      "title": "Events",
      "type": "nline-plotlyjs-panel",
      "timeFrom": null,
      "timeShift": null,
      "hideTimeOverride": true
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
          "text": "9",
          "value": "9"
        },
        "label": "Latitude",
        "name": "lat",
        "options": [
          {
            "selected": true,
            "text": "9",
            "value": "9"
          }
        ],
        "query": "9",
        "type": "textbox"
      },
      {
        "current": {
          "text": "-7.5",
          "value": "-7.5"
        },
        "label": "Longitude",
        "name": "lon",
        "options": [
          {
            "selected": true,
            "text": "-7.5",
            "value": "-7.5"
          }
        ],
        "query": "-7.5",
        "type": "textbox"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "1.5\u00b0",
          "value": "global1_5"
        },
        "description": "",
        "label": "Grid",
        "name": "grid",
        "options": [
          {
            "selected": false,
            "text": "0.25\u00b0",
            "value": "global0_25"
          },
          {
            "selected": true,
            "text": "1.5\u00b0",
            "value": "global1_5"
          }
        ],
        "query": "0.25\u00b0 : global0_25, 1.5\u00b0 : global1_5",
        "type": "custom"
      },
      {
        "allValue": null,
        "allowCustomValue": false,
        "current": {
          "text": "ECMWF IFS-ER",
          "value": "ecmwf_ifs_er"
        },
        "description": "Forecast used for map metrics and event scores (not the precip display lines).",
        "hide": 0,
        "includeAll": false,
        "label": "Eval Forecast",
        "multi": false,
        "name": "eval_forecast",
        "options": [
          {
            "selected": true,
            "text": "ECMWF IFS-ER",
            "value": "ecmwf_ifs_er"
          },
          {
            "selected": false,
            "text": "ECMWF IFS-ER debiased",
            "value": "ecmwf_ifs_er_debiased"
          },
          {
            "selected": false,
            "text": "ECMWF AIFS",
            "value": "ecmwf_aifs"
          },
          {
            "selected": false,
            "text": "ECMWF IFS ENS",
            "value": "ecmwf_ifs_ens"
          },
          {
            "selected": false,
            "text": "ECMWF HRES",
            "value": "ecmwf_hres"
          },
          {
            "selected": false,
            "text": "Cumulus AI",
            "value": "cumulus_ai"
          },
          {
            "selected": false,
            "text": "FuXi",
            "value": "fuxi"
          },
          {
            "selected": false,
            "text": "GFS",
            "value": "gfs"
          },
          {
            "selected": false,
            "text": "GenCast",
            "value": "gencast"
          },
          {
            "selected": false,
            "text": "GraphCast",
            "value": "graphcast"
          },
          {
            "selected": false,
            "text": "Climatology ERA5",
            "value": "climatology_era5_1985_2015"
          },
          {
            "selected": false,
            "text": "Climatology IMERG",
            "value": "climatology_imerg_1998_2016"
          }
        ],
        "query": "ECMWF IFS-ER : ecmwf_ifs_er, ECMWF IFS-ER debiased : ecmwf_ifs_er_debiased, ECMWF AIFS : ecmwf_aifs, ECMWF IFS ENS : ecmwf_ifs_ens, ECMWF HRES : ecmwf_hres, Cumulus AI : cumulus_ai, FuXi : fuxi, GFS : gfs, GenCast : gencast, GraphCast : graphcast, Climatology ERA5 : climatology_era5_1985_2015, Climatology IMERG : climatology_imerg_1998_2016",
        "refresh": 0,
        "regex": "",
        "skipUrlSync": false,
        "sort": 0,
        "type": "custom"
      },
      {
        "allValue": null,
        "allowCustomValue": false,
        "current": {
          "text": "IMERG Final",
          "value": "imerg_final"
        },
        "description": "Observational truth used for evaluation (map + Events). Must match a cached job truth.",
        "hide": 0,
        "includeAll": false,
        "label": "Eval Ground Truth",
        "multi": false,
        "name": "eval_truth",
        "options": [
          {
            "selected": true,
            "text": "IMERG Final",
            "value": "imerg_final"
          },
          {
            "selected": false,
            "text": "ERA5",
            "value": "era5"
          }
        ],
        "query": "IMERG Final : imerg_final, ERA5 : era5",
        "refresh": 0,
        "regex": "",
        "skipUrlSync": false,
        "sort": 0,
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "Big rain",
          "value": "big_rain_days"
        },
        "label": "Event type",
        "name": "event_type",
        "options": [
          {
            "selected": true,
            "text": "Big rain",
            "value": "big_rain_days"
          },
          {
            "selected": false,
            "text": "Dry spell",
            "value": "in_season_dry_spell"
          },
          {
            "selected": false,
            "text": "Early season",
            "value": "early_season_accumulation-30d"
          }
        ],
        "query": "Big rain : big_rain_days, Dry spell : in_season_dry_spell, Early season : early_season_accumulation-30d",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "2021-05-02",
          "value": "2021-05-02"
        },
        "includeAll": false,
        "label": "Event date",
        "name": "event_date",
        "options": [
          {
            "selected": false,
            "text": "2020-01-01",
            "value": "2020-01-01"
          }
        ],
        "query": "2020-01-01",
        "type": "custom",
        "description": "Selected event date (set by clicking an event bar). Centers the precip view."
      },
      {
        "current": {
          "text": "1 week",
          "value": "7"
        },
        "label": "Precip lead",
        "name": "lead",
        "options": [
          {
            "selected": true,
            "text": "1 week",
            "value": "7"
          },
          {
            "selected": false,
            "text": "2 weeks",
            "value": "14"
          },
          {
            "selected": false,
            "text": "3 weeks",
            "value": "21"
          }
        ],
        "query": "1 week : 7, 2 weeks : 14, 3 weeks : 21",
        "type": "custom",
        "description": "Lead for the precipitation timeseries only. Map and Events always use 1 week (lead 7)."
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": [
            "IMERG",
            "ERA5",
            "ECMWF IFS-ER",
            "Cumulus AI"
          ],
          "value": [
            "imerg",
            "era5",
            "ecmwf-ifs-er",
            "cumulus"
          ]
        },
        "description": "Which series to show on the Precipitation chart.",
        "includeAll": false,
        "label": "Models",
        "multi": true,
        "name": "models",
        "options": [
          {
            "selected": true,
            "text": "IMERG",
            "value": "imerg"
          },
          {
            "selected": true,
            "text": "ERA5",
            "value": "era5"
          },
          {
            "selected": true,
            "text": "ECMWF IFS-ER",
            "value": "ecmwf-ifs-er"
          },
          {
            "selected": true,
            "text": "Cumulus AI",
            "value": "cumulus"
          }
        ],
        "query": "IMERG : imerg, ERA5 : era5, ECMWF IFS-ER : ecmwf-ifs-er, Cumulus AI : cumulus",
        "skipUrlSync": false,
        "type": "custom"
      },
      {
        "current": {
          "text": "0.3",
          "value": "0.3"
        },
        "definition": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 0.3\n    WHEN 'in_season_dry_spell' THEN 30\n    WHEN 'early_season_accumulation-30d' THEN 30\nEND AS thresh;",
        "label": "Good if <",
        "name": "good_thresh",
        "options": [],
        "query": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 0.3\n    WHEN 'in_season_dry_spell' THEN 30\n    WHEN 'early_season_accumulation-30d' THEN 30\nEND AS thresh;",
        "refresh": 2,
        "regex": "",
        "type": "query",
        "includeAll": false
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "Yes",
          "value": "True"
        },
        "label": "Observed events",
        "name": "obs_filter",
        "options": [
          {
            "selected": true,
            "text": "Yes",
            "value": "True"
          },
          {
            "selected": false,
            "text": "No",
            "value": "False"
          }
        ],
        "query": "Yes : True, No : False",
        "type": "custom",
        "description": "If Yes, score observed events (forecast_filter=False). If No, score forecast-triggered events."
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "1",
          "value": "1"
        },
        "hide": 2,
        "label": "Agg days",
        "name": "agg_days",
        "options": [
          {
            "selected": true,
            "text": "1",
            "value": "1"
          },
          {
            "selected": false,
            "text": "7",
            "value": "7"
          }
        ],
        "query": "1, 7",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "False",
          "value": "False"
        },
        "definition": "SELECT CASE '${obs_filter}'\n    WHEN 'True' THEN 'False'\n    WHEN 'False' THEN 'True'\nEND",
        "description": "",
        "hide": 2,
        "name": "fcst_filter",
        "options": [],
        "query": "SELECT CASE '${obs_filter}'\n    WHEN 'True' THEN 'False'\n    WHEN 'False' THEN 'True'\nEND",
        "refresh": 2,
        "regex": "",
        "type": "query",
        "includeAll": false
      },
      {
        "current": {},
        "definition": "SELECT md5(\n    'forecast_metric_points/1_2024-12-31_${eval_forecast}_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_western_africa_2016-01-01_None_${eval_truth}_precip'\n)",
        "hide": 2,
        "name": "fcst_points_table_west",
        "options": [],
        "query": "SELECT md5(\n    'forecast_metric_points/1_2024-12-31_${eval_forecast}_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_western_africa_2016-01-01_None_${eval_truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query",
        "includeAll": false,
        "description": "Pinned to lead 7 (1 week); Lead dropdown only affects precip timeseries."
      },
      {
        "current": {},
        "definition": "SELECT md5(\n    'forecast_metric_points/1_2024-12-31_${eval_forecast}_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_eastern_africa_2016-01-01_None_${eval_truth}_precip'\n)",
        "hide": 2,
        "name": "fcst_points_table_east",
        "options": [],
        "query": "SELECT md5(\n    'forecast_metric_points/1_2024-12-31_${eval_forecast}_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_eastern_africa_2016-01-01_None_${eval_truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query",
        "includeAll": false,
        "description": "Pinned to lead 7 (1 week); Lead dropdown only affects precip timeseries."
      },
      {
        "current": {},
        "definition": "SELECT md5('event_list/2024-12-31_${eval_forecast}_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_western_africa_2016-01-01_None_${eval_truth}_precip')",
        "hide": 2,
        "name": "event_list_table_west",
        "options": [],
        "query": "SELECT md5('event_list/2024-12-31_${eval_forecast}_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_western_africa_2016-01-01_None_${eval_truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query",
        "includeAll": false,
        "description": "Pinned to lead 7 (1 week); Lead dropdown only affects precip timeseries."
      },
      {
        "current": {},
        "definition": "SELECT md5('event_list/2024-12-31_${eval_forecast}_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_eastern_africa_2016-01-01_None_${eval_truth}_precip')",
        "hide": 2,
        "name": "event_list_table_east",
        "options": [],
        "query": "SELECT md5('event_list/2024-12-31_${eval_forecast}_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_eastern_africa_2016-01-01_None_${eval_truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query",
        "includeAll": false,
        "description": "Pinned to lead 7 (1 week); Lead dropdown only affects precip timeseries."
      },
      {
        "current": {},
        "description": "Half-width (days) for the initial precip zoom window around event_date.",
        "hide": 2,
        "name": "event_window",
        "query": "SELECT GREATEST(\n    10,\n    CASE '${event_type}'\n        WHEN 'big_rain_days' THEN 5\n        WHEN 'in_season_dry_spell' THEN 10\n        WHEN 'early_season_accumulation-30d' THEN 30\n        ELSE 10\n    END\n) AS window;",
        "skipUrlSync": true,
        "type": "query",
        "definition": "SELECT GREATEST(\n    10,\n    CASE '${event_type}'\n        WHEN 'big_rain_days' THEN 5\n        WHEN 'in_season_dry_spell' THEN 10\n        WHEN 'early_season_accumulation-30d' THEN 30\n        ELSE 10\n    END\n) AS window;",
        "refresh": 2,
        "regex": "",
        "includeAll": false,
        "multi": false,
        "options": []
      },
      {
        "current": {},
        "definition": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 5\n    WHEN 'in_season_dry_spell' THEN 10\n    WHEN 'early_season_accumulation-30d' THEN 30\nEND AS duration;",
        "description": "True scored-event window length (accumulated_rain agg_days) for the selected event type.",
        "hide": 2,
        "includeAll": false,
        "label": "Event duration (days)",
        "multi": false,
        "name": "event_duration",
        "options": [],
        "query": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 5\n    WHEN 'in_season_dry_spell' THEN 10\n    WHEN 'early_season_accumulation-30d' THEN 30\nEND AS duration;",
        "refresh": 2,
        "regex": "",
        "skipUrlSync": false,
        "sort": 0,
        "type": "query"
      },
      {
        "current": {},
        "definition": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 'center'\n    WHEN 'in_season_dry_spell' THEN 'right'\n    WHEN 'early_season_accumulation-30d' THEN 'right'\nEND AS align;",
        "description": "Window alignment relative to event_date: center or right (matches roll_and_agg).",
        "hide": 2,
        "includeAll": false,
        "label": "Event align",
        "multi": false,
        "name": "event_align",
        "options": [],
        "query": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 'center'\n    WHEN 'in_season_dry_spell' THEN 'right'\n    WHEN 'early_season_accumulation-30d' THEN 'right'\nEND AS align;",
        "refresh": 2,
        "regex": "",
        "skipUrlSync": false,
        "sort": 0,
        "type": "query"
      },
      {
        "current": {
          "text": "smape",
          "value": "smape"
        },
        "definition": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 'smape'\n    WHEN 'in_season_dry_spell' THEN 'mm'\n    WHEN 'early_season_accumulation-30d' THEN 'mae'\nEND AS metric;\n",
        "hide": 2,
        "name": "metric_name",
        "options": [],
        "query": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 'smape'\n    WHEN 'in_season_dry_spell' THEN 'mm'\n    WHEN 'early_season_accumulation-30d' THEN 'mae'\nEND AS metric;\n",
        "refresh": 2,
        "regex": "",
        "type": "query",
        "includeAll": false
      }
    ]
  },
  "time": {
    "from": "2016-01-01T00:00:00.000Z",
    "to": "2024-12-31T23:59:59.000Z"
  },
  "timepicker": {
    "hidden": true,
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ]
  },
  "timezone": "utc",
  "title": "Forecast Events Explorer",
  "uid": "efspqenm2yj9ce",
  "version": 1,
  "weekStart": ""
}
