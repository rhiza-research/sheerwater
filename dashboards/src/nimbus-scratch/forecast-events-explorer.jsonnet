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
          "displayModeBar": "true,         // ⬅️ shows zoom tools",
          "responsive": "true,",
          "scrollZoom": "true              // ⬅️ enables mouse wheel zoom"
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
        "script": "const fields = data.series[0].fields;\n\n// --- Find fields ---\nconst latField = fields.find(f => f.name === \"lat\");\nconst lonField = fields.find(f => f.name === \"lon\");\nconst valueField = fields.find(f => f.name === \"value\");\n\nif (!latField || !lonField || !valueField) {\n  throw new Error(\"Missing lat, lon, or value field\");\n}\n\n// --- Extract values safely ---\nconst lats = Array.from(latField.values || latField.values.buffer || []);\nconst lons = Array.from(lonField.values || lonField.values.buffer || []);\nconst values = Array.from(valueField.values || valueField.values.buffer || []);\n\n// --- Safe variable getter ---\nconst getVar = (name) => {\n  return (\n    variables?.[name]?.current?.value ??\n    variables?.[name]?.value ??\n    null\n  );\n};\n\n// --- Dashboard variables ---\nconst lat1 = parseFloat(getVar(\"lat\"));\nconst lon1 = parseFloat(getVar(\"lon\"));\n\nconst mapZoom = parseFloat(getVar(\"map_zoom\")) || 1.5;\nconst mapCenterLat = parseFloat(getVar(\"map_center_lat\")) || 10;\nconst mapCenterLon = parseFloat(getVar(\"map_center_lon\")) || 30;\n\n// ======================================================\n// MAIN TRACE\n// ======================================================\n\nconst traces = [{\n  type: 'scattermapbox',\n  lat: lats,\n  lon: lons,\n  mode: 'markers',\n  marker: {\n    size: 7,\n    color: values,\n    colorscale: 'Viridis',\n    cmin: Math.min(...values),\n    cmax: Math.max(...values),\n    opacity: 0.8,\n    showscale: true,\n    colorbar: { title: getVar(\"metric_name\") }\n  },\n  text: values.map(v => `Value: ${v}`),\n  hovertemplate:\n    'Lat: %{lat:.2f}<br>' +\n    'Lon: %{lon:.2f}<br>' +\n    '%{text}<extra></extra>',\n  showlegend: false\n}];\n\n// ======================================================\n// SELECTED POINT\n// ======================================================\n\nif (!isNaN(lat1) && !isNaN(lon1)) {\n  traces.push({\n    type: 'scattermapbox',\n    lat: [lat1],\n    lon: [lon1],\n    mode: 'markers',\n    marker: {\n      size: 14,\n      color: 'gold',\n      line: {\n        width: 2,\n        color: 'black'\n      }\n    },\n    text: [`Selected point<br>Lat: ${lat1}<br>Lon: ${lon1}`],\n    hovertemplate: '%{text}<extra></extra>',\n    showlegend: false\n  });\n}\n\n// ======================================================\n// RETURN FIGURE\n// ======================================================\n\nreturn {\n  data: traces,\n  layout: {\n    mapbox: {\n      style: 'open-street-map',\n      center: {\n        lat: mapCenterLat,\n        lon: mapCenterLon\n      },\n      zoom: mapZoom,\n      dragmode: 'zoom'\n    },\n    margin: { t: 0, b: 0, l: 0, r: 0 },\n    paper_bgcolor: 'rgba(0,0,0,0)',\n    plot_bgcolor: 'rgba(0,0,0,0)'\n  },\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true\n  }\n};",
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "cegueq2crd3wge"
          },
          "editorMode": "code",
          "format": "table",
          "hide": false,
          "rawQuery": true,
          "rawSql": "SELECT lat, lon, value FROM \"${fcst_points_table_west}\"\nUNION ALL\nSELECT lat, lon, value FROM \"${fcst_points_table_east}\"",
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
        "config": {},
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
        "onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n  const { type: eventType, data: eventData } = event;\n  const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n  switch (eventType) {\n    case 'click':\n      console.log('Click event:', eventData.points);\n      break;\n    case 'select':\n      console.log('Selection event:', eventData.range);\n      break;\n    case 'zoom':\n      console.log('Zoom event:', eventData);\n      break;\n    default:\n      console.log('Unhandled event type:', eventType, eventData);\n  }\n\n  console.log('Current time zone:', timeZone);\n  console.log('From time:', dayjs(variables.__from).format());\n  console.log('To time:', dayjs(variables.__to).format());\n\n  // Example of using locationService\n  // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n  console.error('Error in onclick handler:', error);\n}\n*/\n  ",
        "resScale": 2,
        "script": "// --- Safe variable getter ---\nconst getVar = (name) => {\n  return (\n    variables?.[name]?.current?.value ??\n    variables?.[name]?.value ??\n    null\n  );\n};\n\nfunction formatDateUTC(t) {\n  const d = new Date(t);\n  const yyyy = d.getUTCFullYear();\n  const mm = String(d.getUTCMonth() + 1).padStart(2, '0');\n  const dd = String(d.getUTCDate()).padStart(2, '0');\n  return `${yyyy}-${mm}-${dd}`;\n}\n\n// --- List each query's position in data.series + styling here ---\nconst SERIES_CONFIG = [\n  { index: 0, label: 'IMERG (observed)', color: '#1f77b4', width: 2.5 },\n  { index: 1, label: 'ECMWF IFS-ER', color: '#ff7f0e', width: 2 },\n  { index: 2, label: 'ERA5', color: '#2ca02c', width: 2 },\n  { index: 3, label: 'Cumulus AI', color: '#d62728', width: 2 },\n];\n\nfunction lighten(hex, amount) {\n  const col = hex.replace('#', '');\n  const num = parseInt(col, 16);\n  const r = (num >> 16) & 0xFF;\n  const g = (num >> 8) & 0xFF;\n  const b = num & 0xFF;\n  const lr = Math.round(r + (255 - r) * amount);\n  const lg = Math.round(g + (255 - g) * amount);\n  const lb = Math.round(b + (255 - b) * amount);\n  return `rgb(${lr}, ${lg}, ${lb})`;\n}\n\nfunction buildTrace(series, { label, color, width }) {\n  const fields = series.fields;\n  const timeField = fields.find(f => f.name === 'time');\n  const valueField = fields.find(f => f.name !== 'time');\n\n  if (!timeField || !valueField || timeField.values.length === 0) {\n    return null; // no data for this series — skip it, don't crash the panel\n  }\n\n  const times = Array.from(timeField.values || timeField.values.buffer || []);\n  const values = Array.from(valueField.values || valueField.values.buffer || []);\n  const dateLabels = times.map(formatDateUTC);\n\n  return {\n    type: 'scatter',\n    mode: 'lines+markers',\n    x: times,\n    y: values,\n    customdata: dateLabels,\n    name: label,\n    line: { color: lighten(color, 0.45), width },\n    marker: { color, size: width * 2.5 },\n    hovertemplate: '%{customdata}<br>%{y:.2f}<extra>' + label + '</extra>'\n  };\n}\n\nconst traces = SERIES_CONFIG\n  .map(cfg => {\n    const series = data.series[cfg.index];\n    if (!series) return null;\n    return buildTrace(series, cfg);\n  })\n  .filter(Boolean);\n\n// --- Shaded band centered on the event date: -1 day before, +1 day after ---\nconst eventDate = new Date(getVar(\"event_date\"));\nconst dayMs = 24 * 60 * 60 * 1000;\nconst eventShape = isNaN(eventDate.getTime()) ? [] : [{\n  type: 'rect',\n  xref: 'x',\n  yref: 'paper',\n  x0: eventDate.getTime() - dayMs,\n  x1: eventDate.getTime() + dayMs,\n  y0: 0,\n  y1: 1,\n  fillcolor: 'rgba(128, 128, 128, 0.2)',\n  line: { width: 0 },\n  layer: 'below'\n}];\n\nreturn {\n  data: traces,\n  layout: {\n    font: { family: 'Inter, Helvetica, Arial, sans-serif' },\n    xaxis: { type: 'date', autorange: true, automargin: true },\n    yaxis: { autorange: true, automargin: true, title: { text: 'Precipitation (mm)' } },\n    title: { automargin: true },\n    margin: { l: 50, r: 20, b: 40, t: 20 },\n    legend: { orientation: 'h', y: -0.25 },\n    plot_bgcolor: 'rgba(0,0,0,0)',\n    paper_bgcolor: 'rgba(0,0,0,0)',\n    shapes: eventShape\n  },\n  config: {\n    responsive: true,\n    displayModeBar: false\n  }\n};",
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
          "rawSql": "WITH filtered AS (\n    SELECT\n        t.time,\n        t.precip\n    FROM (\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_india\"\n        UNION ALL\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_eastern_africa\"\n        UNION ALL\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_western_africa\"\n    ) t\n    WHERE t.lat = ${lat}\n      AND t.lon = ${lon}\n      AND t.time BETWEEN '${event_date}'::date - INTERVAL '${event_window} days' AND '${event_date}'::date + INTERVAL '${event_window} days'\n)\n\nSELECT\n    time,\n    AVG(precip) OVER (\n        ORDER BY time\n        ROWS BETWEEN ${agg_days}-1 PRECEDING AND CURRENT ROW\n    ) AS precip\nFROM filtered\nORDER BY time;",
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
          "rawSql": "SELECT\n    t.time,\n    t.precip / ${agg_days} AS precip\nFROM (\n    SELECT * FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_western_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_india\"\n) t\nWHERE t.lat = ${lat}\n  AND t.lon = ${lon}\n  AND t.time BETWEEN '${event_date}'::date - INTERVAL '${event_window} days'\n                  AND '${event_date}'::date + INTERVAL '${event_window} days'\nORDER BY t.time;",
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
          "rawSql": "WITH source_tables AS (\n    SELECT * FROM \"full_rainfall/era5_${grid}_india\"\n    UNION ALL\n    SELECT * FROM \"full_rainfall/era5_${grid}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"full_rainfall/era5_${grid}_western_africa\"\n),\n\ncombined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM source_tables\n),\n\nnearest_point AS (\n    SELECT\n        lat,\n        lon,\n        SQRT(\n            POWER(lat - ${lat}, 2) +\n            POWER(lon - ${lon}, 2)\n        ) AS distance_deg\n    FROM combined_points\n    ORDER BY distance_deg\n    LIMIT 1\n),\n\nfiltered AS (\n    SELECT\n        t.time,\n        t.precip\n    FROM source_tables t\n    JOIN nearest_point n\n      ON t.lat = n.lat\n     AND t.lon = n.lon\n    WHERE n.distance_deg <= (200.0 / 111.0)\n      AND t.time BETWEEN '${event_date}'::date - INTERVAL '${event_window} days'\n                      AND '${event_date}'::date + INTERVAL '${event_window} days'\n)\n\nSELECT\n    time,\n    AVG(precip) OVER (\n        ORDER BY time\n        ROWS BETWEEN ${agg_days}-1 PRECEDING AND CURRENT ROW\n    ) AS precip\nFROM filtered\nORDER BY time;",
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
          "rawSql": "WITH combined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_eastern_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_western_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_india\"\n),\n\nnearest_point AS (\n    SELECT\n        lat,\n        lon,\n        SQRT(\n            POWER(lat - ${lat}, 2) +\n            POWER(lon - ${lon}, 2)\n        ) AS distance_deg\n    FROM combined_points\n    ORDER BY distance_deg\n    LIMIT 1\n)\n\nSELECT\n    t.time,\n    t.precip / ${agg_days} AS precip\nFROM (\n    SELECT * FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_western_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_india\"\n) t\nJOIN nearest_point n\n  ON t.lat = n.lat\n AND t.lon = n.lon\nWHERE n.distance_deg <= (200 / 111.0)\n  AND t.time BETWEEN '${event_date}'::date - INTERVAL '${event_window} days'\n                  AND '${event_date}'::date + INTERVAL '${event_window} days'\nORDER BY t.time;",
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
        "config": {},
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
        "onclick": "try {\n  const { type: eventType, data: eventData } = event;\n\n  if (eventType === 'click') {\n    const clickedPoint = eventData?.points?.[0];\n\n    if (clickedPoint) {\n      const currentUrl = new URL(window.location.href);\n      currentUrl.searchParams.set('var-event_date', clickedPoint.customdata);\n      window.location.href = currentUrl.toString();\n    }\n  }\n} catch (error) {\n  console.error('Error in bar click handler:', error);\n}",
        "resScale": 2,
        "script": "// --- Safe variable getter ---\nconst getVar = (name) => {\n  return (\n    variables?.[name]?.current?.value ??\n    variables?.[name]?.value ??\n    null\n  );\n};\n\nconst fields = data.series[0].fields;\nconst timeField = fields.find(f => f.name === \"time\");\nconst valueField = fields.find(f => f.name === \"value\");\n\nif (!timeField || !valueField) {\n  throw new Error(\"Missing time or value field\");\n}\n\nconst times = Array.from(timeField.values || timeField.values.buffer || []);\nconst values = Array.from(valueField.values || valueField.values.buffer || []);\n\n// --- Threshold for \"good\" events ---\nconst GOOD_THRESHOLD = parseFloat(getVar(\"good_thresh\"));\nconst GOOD_COLOR = 'rgba(0, 170, 0, 0.8)';\nconst BAD_COLOR = 'rgba(200, 0, 0, 0.8)';\n\nfunction formatDate(t) {\n  const d = new Date(t);\n  const yyyy = d.getUTCFullYear();\n  const mm = String(d.getUTCMonth() + 1).padStart(2, '0');\n  const dd = String(d.getUTCDate()).padStart(2, '0');\n  return `${yyyy}-${mm}-${dd}`;\n}\n\nconst dateLabels = times.map(formatDate);\nconst colors = values.map(v => (v <= GOOD_THRESHOLD ? GOOD_COLOR : BAD_COLOR));\n\nconst traces = [{\n  type: 'bar',\n  x: times,\n  y: values,\n  customdata: dateLabels,\n  marker: { color: colors },\n  width: 4 * 24 * 60 * 60 * 1000, // 2 days wide (±1 day), in ms\n  hovertemplate: 'Date: %{customdata}<br>Value: %{y}<extra></extra>'\n}];\n\n// --- Shaded band centered on the event date: -1 day before, +1 day after ---\nconst dayMs = 5 * 24 * 60 * 60 * 1000;\nconst eventDate = new Date(getVar(\"event_date\"));\nconst eventShape = isNaN(eventDate.getTime()) ? [] : [{\n  type: 'rect',\n  xref: 'x',\n  yref: 'paper',\n  x0: eventDate.getTime() - dayMs,\n  x1: eventDate.getTime() + dayMs,\n  y0: 0,\n  y1: 1,\n  fillcolor: 'rgba(128, 128, 128, 0.2)',\n  line: { width: 0 },\n  layer: 'below'\n}];\n\n// --- Good/bad event counts ---\nconst totalEvents = values.length;\nconst goodCount = values.filter(v => v <= GOOD_THRESHOLD).length;\nconst badCount = totalEvents - goodCount;\n\nreturn {\n  data: traces,\n  layout: {\n    font: { family: 'Inter, Helvetica, Arial, sans-serif' },\n    xaxis: {\n      type: 'date',\n      autorange: true,\n      automargin: true,\n      range: [times[0], times[times.length - 1]]\n    },\n    yaxis: { autorange: true, automargin: true, title: { text: getVar(\"metric_name\") } },\n    title: {\n      text: `Total: ${totalEvents}  |  Good: ${goodCount}  |  Bad: ${badCount}`,\n      font: { size: 12 },\n      automargin: true\n    },\n    margin: { l: 50, r: 20, b: 40, t: 30 },\n    shapes: [\n      {\n        type: 'line',\n        xref: 'paper',\n        x0: 0,\n        x1: 1,\n        yref: 'y',\n        y0: GOOD_THRESHOLD,\n        y1: GOOD_THRESHOLD,\n        line: { color: 'rgba(0,0,0,0.6)', width: 1.5, dash: 'dash' }\n      },\n      ...eventShape\n    ]\n  },\n  config: {\n    responsive: true,\n    displayModeBar: false\n  }\n};",
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT time, value FROM (\n    SELECT lat, lon, time, value FROM \"${event_list_table_west}\"\n    UNION ALL\n    SELECT lat, lon, time, value FROM \"${event_list_table_east}\"\n) combined\nWHERE lat = ${lat} AND lon = ${lon}\nORDER BY value DESC",
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
      "title": "Events",
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
          "text": "9",
          "value": "9"
        },
        "label": "lat",
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
        "label": "lon",
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
          "text": "global1_5",
          "value": "global1_5"
        },
        "description": "",
        "label": "grid",
        "name": "grid",
        "options": [
          {
            "selected": false,
            "text": "global0_25",
            "value": "global0_25"
          },
          {
            "selected": true,
            "text": "global1_5",
            "value": "global1_5"
          }
        ],
        "query": "global0_25, global1_5",
        "type": "custom"
      },
      {
        "current": {
          "text": "1",
          "value": "1"
        },
        "label": "weeks lead",
        "name": "lead",
        "options": [
          {
            "selected": true,
            "text": "1",
            "value": "1"
          },
          {
            "selected": false,
            "text": "2",
            "value": "7"
          },
          {
            "selected": false,
            "text": "3",
            "value": "14"
          },
          {
            "selected": false,
            "text": "4",
            "value": "21"
          }
        ],
        "query": "1 : 1, 2 : 7, 3 : 14, 4 : 21",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "1",
          "value": "1"
        },
        "hide": 2,
        "label": "agg days",
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
        "current": {
          "text": "b64d14cf1cc685d648d771138ea192e7",
          "value": "b64d14cf1cc685d648d771138ea192e7"
        },
        "definition": "SELECT md5(\n    'forecast_metric_points/1_2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_western_africa_2016-01-01_None_imerg_final_precip'\n)",
        "hide": 2,
        "name": "fcst_points_table_west",
        "options": [],
        "query": "SELECT md5(\n    'forecast_metric_points/1_2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_western_africa_2016-01-01_None_imerg_final_precip'\n)",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "8d260c3d04cfc207f254f02803f87370",
          "value": "8d260c3d04cfc207f254f02803f87370"
        },
        "definition": "SELECT md5(\n    'forecast_metric_points/1_2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_eastern_africa_2016-01-01_None_imerg_final_precip'\n)",
        "hide": 2,
        "name": "fcst_points_table_east",
        "options": [],
        "query": "SELECT md5(\n    'forecast_metric_points/1_2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_eastern_africa_2016-01-01_None_imerg_final_precip'\n)",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "05abb8da89f52f19cb6824e420d8825d",
          "value": "05abb8da89f52f19cb6824e420d8825d"
        },
        "definition": "select * from md5('event_list/2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_western_africa_2016-01-01_None_imerg_final_precip')",
        "hide": 2,
        "name": "event_list_table_west",
        "options": [],
        "query": "select * from md5('event_list/2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_western_africa_2016-01-01_None_imerg_final_precip')",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "d310ebc217848ad1c78399c9d812fbc0",
          "value": "d310ebc217848ad1c78399c9d812fbc0"
        },
        "definition": "select * from md5('event_list/2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_eastern_africa_2016-01-01_None_imerg_final_precip')",
        "hide": 2,
        "name": "event_list_table_east",
        "options": [],
        "query": "select * from md5('event_list/2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-${fcst_filter}_obs_filter-${obs_filter}_${event_type}_eastern_africa_2016-01-01_None_imerg_final_precip')",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "2021-04-14",
          "value": "2021-04-14"
        },
        "includeAll": false,
        "label": "event_date",
        "name": "event_date",
        "options": [
          {
            "selected": false,
            "text": "2020-01-01",
            "value": "2020-01-01"
          }
        ],
        "query": "2020-01-01",
        "type": "custom"
      },
      {
        "current": {
          "text": "10",
          "value": "10"
        },
        "description": "",
        "hide": 2,
        "name": "event_window",
        "query": "10",
        "skipUrlSync": true,
        "type": "constant"
      },
      {
        "current": {
          "text": "smape",
          "value": "smape"
        },
        "definition": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 'smape'\n    WHEN 'in_season_dry_spell' THEN 'mm'\n    WHEN 'early_season_accumulation' THEN 'mae'\nEND AS metric;\n",
        "hide": 2,
        "name": "metric_name",
        "options": [],
        "query": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 'smape'\n    WHEN 'in_season_dry_spell' THEN 'mm'\n    WHEN 'early_season_accumulation' THEN 'mae'\nEND AS metric;\n",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "big_rain_days",
          "value": "big_rain_days"
        },
        "label": "event",
        "name": "event_type",
        "options": [
          {
            "selected": true,
            "text": "big_rain_days",
            "value": "big_rain_days"
          },
          {
            "selected": false,
            "text": "in_season_dry_spell",
            "value": "in_season_dry_spell"
          }
        ],
        "query": "big_rain_days, in_season_dry_spell",
        "type": "custom"
      },
      {
        "current": {
          "text": "0.3",
          "value": "0.3"
        },
        "definition": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 0.3\n    WHEN 'in_season_dry_spell' THEN 30\n    WHEN 'early_season_accumulation' THEN 30\nEND AS thresh;",
        "label": "good <",
        "name": "good_thresh",
        "options": [],
        "query": "SELECT CASE '${event_type}'\n    WHEN 'big_rain_days' THEN 0.3\n    WHEN 'in_season_dry_spell' THEN 30\n    WHEN 'early_season_accumulation' THEN 30\nEND AS thresh;",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "True",
          "value": "True"
        },
        "label": "observed events",
        "name": "obs_filter",
        "options": [
          {
            "selected": true,
            "text": "True",
            "value": "True"
          },
          {
            "selected": false,
            "text": "False",
            "value": "False"
          }
        ],
        "query": "True, False",
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
        "refresh": 1,
        "regex": "",
        "type": "query"
      }
    ]
  },
  "time": {
    "from": "1904-01-01T00:00:00.000Z",
    "to": "1904-12-31T00:00:00.000Z"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "Forecast Events Explorer",
  "uid": "efspqenm2yj9ce",
  "version": 1,
  "weekStart": ""
}
