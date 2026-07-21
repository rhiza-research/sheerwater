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
        "script": "const fields = data.series[0].fields;\n\n// --- Find fields ---\nconst latField = fields.find(f => f.name === \"lat\");\nconst lonField = fields.find(f => f.name === \"lon\");\nconst valueField = fields.find(f => f.name === \"value\");\n\nif (!latField || !lonField || !valueField) {\n  throw new Error(\"Missing lat, lon, or value field\");\n}\n\n// --- Extract values safely ---\nconst lats = Array.from(latField.values || latField.values.buffer || []);\nconst lons = Array.from(lonField.values || lonField.values.buffer || []);\nconst values = Array.from(valueField.values || valueField.values.buffer || []);\n\n// --- Safe variable getter ---\nconst getVar = (name) => {\n  return (\n    variables?.[name]?.current?.value ??\n    variables?.[name]?.value ??\n    null\n  );\n};\n\n// --- Dashboard variables ---\nconst lat1 = parseFloat(getVar(\"lat\"));\nconst lon1 = parseFloat(getVar(\"lon\"));\n\nconst mapZoom = parseFloat(getVar(\"map_zoom\")) || 1.5;\nconst mapCenterLat = parseFloat(getVar(\"map_center_lat\")) || 10;\nconst mapCenterLon = parseFloat(getVar(\"map_center_lon\")) || 30;\n\n// ======================================================\n// MAIN TRACE\n// ======================================================\n\nconst traces = [{\n  type: 'scattermapbox',\n  lat: lats,\n  lon: lons,\n  mode: 'markers',\n  marker: {\n    size: 7,\n    color: values,\n    colorscale: 'Viridis',\n    cmin: Math.min(...values),\n    cmax: Math.max(...values),\n    opacity: 0.8,\n    showscale: true,\n    colorbar: { title: 'Value' }\n  },\n  text: values.map(v => `Value: ${v}`),\n  hovertemplate:\n    'Lat: %{lat:.2f}<br>' +\n    'Lon: %{lon:.2f}<br>' +\n    '%{text}<extra></extra>',\n  showlegend: false\n}];\n\n// ======================================================\n// SELECTED POINT\n// ======================================================\n\nif (!isNaN(lat1) && !isNaN(lon1)) {\n  traces.push({\n    type: 'scattermapbox',\n    lat: [lat1],\n    lon: [lon1],\n    mode: 'markers',\n    marker: {\n      size: 14,\n      color: 'gold',\n      line: {\n        width: 2,\n        color: 'black'\n      }\n    },\n    text: [`Selected point<br>Lat: ${lat1}<br>Lon: ${lon1}`],\n    hovertemplate: '%{text}<extra></extra>',\n    showlegend: false\n  });\n}\n\n// ======================================================\n// RETURN FIGURE\n// ======================================================\n\nreturn {\n  data: traces,\n  layout: {\n    mapbox: {\n      style: 'open-street-map',\n      center: {\n        lat: mapCenterLat,\n        lon: mapCenterLon\n      },\n      zoom: mapZoom,\n      dragmode: 'zoom'\n    },\n    margin: { t: 0, b: 0, l: 0, r: 0 },\n    paper_bgcolor: 'rgba(0,0,0,0)',\n    plot_bgcolor: 'rgba(0,0,0,0)'\n  },\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true\n  }\n};",
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
          "rawSql": "SELECT lat, lon, value FROM ${fcst_points_table}",
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
      "title": "Rainfall Regions",
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
        "w": 15,
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
        "script": "// =====================\n// CONFIG\n// =====================\nconst annualWidth = 2;\nconst annualOpacity = 0.85;\n\nconst climatologyColor = \"#333333\";\nconst climatologyFill = \"rgba(51, 51, 51, 0.1)\";\nconst climatologyLineWidth = 1.5;\n\n// =====================\n// YEAR COLORS\n// =====================\nconst YEAR_COLORS = {\n    2010: \"#4E79A7\", 2011: \"#F28E2B\", 2012: \"#59A14F\", 2013: \"#E15759\",\n    2014: \"#B07AA1\", 2015: \"#9C755F\", 2016: \"#76B7B2\", 2017: \"#EDC948\",\n    2018: \"#FF9DA7\", 2019: \"#86BCB6\",\n    2020: \"#4E79A7\", 2021: \"#F28E2B\", 2022: \"#59A14F\", 2023: \"#E15759\",\n    2024: \"#B07AA1\", 2025: \"#76B7B2\"\n};\n\nfunction getYearColor(year) {\n    return YEAR_COLORS[year] || \"#444444\";\n}\n\nfunction adjustColor(hex, amount) {\n    let usePound = hex[0] === \"#\";\n    let col = usePound ? hex.slice(1) : hex;\n    let num = parseInt(col, 16);\n    let r = Math.min(255, Math.max(0, (num >> 16) + amount));\n    let g = Math.min(255, Math.max(0, ((num >> 8) & 0xFF) + amount));\n    let b = Math.min(255, Math.max(0, (num & 0xFF) + amount));\n    return (\n        (usePound ? \"#\" : \"\") +\n        ((1 << 24) + (r << 16) + (g << 8) + b)\n            .toString(16)\n            .slice(1)\n    );\n}\n\n// =====================\n// HELPERS\n// =====================\nfunction getDOY(dateStr) {\n    const dt = new Date(dateStr);\n    const start = new Date(Date.UTC(dt.getUTCFullYear(), 0, 0));\n    return Math.floor((dt - start) / 86400000);\n}\n\nfunction formatDate(dateStr) {\n    const dt = new Date(dateStr);\n    const months = [\"Jan\",\"Feb\",\"Mar\",\"Apr\",\"May\",\"Jun\",\n                    \"Jul\",\"Aug\",\"Sep\",\"Oct\",\"Nov\",\"Dec\"];\n    return `${dt.getUTCDate()} ${months[dt.getUTCMonth()]} ${dt.getUTCFullYear()}`;\n}\n\n// =====================\n// STORAGE\n// =====================\nlet traces = [];\nlet clim_traces = [];\n\n// ======================================================\n// 1) CLIMATOLOGY (FILLED)\n// ======================================================\nlet climSeries = data.series[0];\n\nif (climSeries) {\n    let tField = climSeries.fields.find(f => f.name === \"dayofyear\");\n    let yField = climSeries.fields.find(f => f.name === \"precip\");\n\n    if (tField && yField) {\n        let pts = [];\n        let times = Array.from(tField.values || []);\n        let vals = Array.from(yField.values || []);\n\n        for (let i = 0; i < times.length; i++) {\n            pts.push({ x: getDOY(times[i]), y: vals[i] });\n        }\n\n        pts.sort((a, b) => a.x - b.x);\n\n        clim_traces.push({\n            x: pts.map(p => p.x),\n            y: pts.map(p => p.y),\n            type: \"scatter\",\n            mode: \"lines\",\n            name: \"mean\",\n            fill: \"tozeroy\",\n            fillcolor: climatologyFill,\n            line: { color: \"rgba(0,0,0,0)\", width: 0 },\n            hovertemplate: \"DOY: %{x}<br>Clim: %{y:.2f} mm/day<extra></extra>\"\n        });\n    }\n}\n\n// ======================================================\n// 2) ANNUAL BUILDER\n// ======================================================\nfunction buildAnnual(series, labelPrefix, dashStyle, colorDelta = 0, width = annualWidth) {\n    if (!series) return;\n\n    let tField = series.fields.find(f => f.name === \"time\");\n    let pField = series.fields.find(f => f.name === \"precip\");\n\n    if (!tField || !pField) return;\n\n    let times = Array.from(tField.values || []);\n    let vals = Array.from(pField.values || []);\n\n    let groups = {};\n\n    for (let i = 0; i < times.length; i++) {\n        let yr = new Date(times[i]).getUTCFullYear();\n        let doy = getDOY(times[i]);\n\n        if (!groups[yr]) groups[yr] = { x: [], y: [], dates: [] };\n\n        groups[yr].x.push(doy);\n        groups[yr].y.push(vals[i]);\n        groups[yr].dates.push(formatDate(times[i]));\n    }\n\n    let years = Object.keys(groups)\n        .map(Number)\n        .sort((a, b) => a - b);\n\n    years.forEach(yr => {\n        let pts = groups[yr].x.map((x, i) => ({\n            x,\n            y: groups[yr].y[i],\n            date: groups[yr].dates[i]\n        })).sort((a, b) => a.x - b.x);\n\n        traces.push({\n            x: pts.map(p => p.x),\n            y: pts.map(p => p.y),\n            customdata: pts.map(p => p.date),\n            type: \"scatter\",\n            mode: \"lines\",\n            name: `${labelPrefix} ${yr}`,\n            hovertemplate: \"%{customdata}<br>%{y:.2f} mm/day<extra>%{fullData.name}</extra>\",\n            line: {\n                color: adjustColor(getYearColor(yr), colorDelta),\n                width: width,\n                dash: dashStyle\n            },\n            opacity: annualOpacity\n        });\n    });\n}\n\nconst selectedSources = Array.isArray(variables.display.current.value)\n    ? variables.display.current.value\n    : [variables.display.current.value];\n\nconst hasSource = (name) => selectedSources.includes(name);\n\n// ======================================================\n// SERIES ORDER (important for layering)\n// ======================================================\nif (hasSource(\"imerg\")) {\n    buildAnnual(data.series[1], \"imerg\", \"solid\", -100, 1.5);\n}\n\nif (hasSource(\"era5\")) {\n    buildAnnual(data.series[3], \"era5\", \"solid\", -20, 1.5);\n}\n\nif (hasSource(\"ecmwf-ifs-er\")) {\n    buildAnnual(data.series[2], \"ecmwf-ifs-er\", \"solid\", 0, 3);\n}\n\nif (hasSource(\"cumulus\")) {\n    buildAnnual(data.series[4], \"cumulus\", \"solid\", -40, 3);\n}\n\n// =====================\n// EMPTY CHECK\n// =====================\nif (traces.length === 0 && clim_traces.length === 0) {\n    return {\n        data: [],\n        layout: {\n            annotations: [{\n                text: \"No data available\",\n                showarrow: false,\n                x: 0.5,\n                y: 0.5\n            }]\n        }\n    };\n}\n\n// =====================\n// AXIS\n// =====================\nconst monthTicks = [1,32,60,91,121,152,182,213,244,274,305,335];\nconst monthLabels = [\n    \"Jan\",\"Feb\",\"Mar\",\"Apr\",\"May\",\"Jun\",\n    \"Jul\",\"Aug\",\"Sep\",\"Oct\",\"Nov\",\"Dec\"\n];\n\nlet vmax = variables.vmax.current.value;\n\n// =====================\n// RETURN\n// =====================\nreturn {\n    data: [...clim_traces, ...traces],\n    layout: {\n        xaxis: {\n            title: \"\",\n            type: \"linear\",\n            range: [1, 366],\n            tickmode: \"array\",\n            tickvals: monthTicks,\n            ticktext: monthLabels\n        },\n        yaxis: {\n            title: \"[mm/day]\",\n            range: [0, vmax]\n        },\n        hovermode: \"closest\",\n        margin: { l: 60, r: 60, t: 40, b: 60 }\n    }\n};",
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
          "rawSql": "WITH combined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM \"get_precip_climatology/imerg_final_${grid}_india\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"get_precip_climatology/imerg_final_${grid}_eastern_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"get_precip_climatology/imerg_final_${grid}_western_africa\"\n),\n\nselected_point AS (\n    SELECT lat, lon\n    FROM combined_points\n    WHERE lat = ${lat}\n      AND lon = ${lon}\n)\n\nSELECT\n    t.dayofyear,\n    t.precip\n    -- display: $display\nFROM (\n    SELECT * FROM \"get_precip_climatology/imerg_final_${grid}_india\"\n    UNION ALL\n    SELECT * FROM \"get_precip_climatology/imerg_final_${grid}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"get_precip_climatology/imerg_final_${grid}_western_africa\"\n) t\nJOIN selected_point s\n  ON t.lat = s.lat\n AND t.lon = s.lon\nWHERE NOT (EXTRACT(MONTH FROM t.dayofyear) = 2 AND EXTRACT(DAY FROM t.dayofyear) = 29)\nORDER BY t.dayofyear;",
          "refId": "climatology",
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
          "rawSql": "WITH combined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM \"full_rainfall/imerg_final_${grid}_india\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_rainfall/imerg_final_${grid}_eastern_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_rainfall/imerg_final_${grid}_western_africa\"\n),\n\nnearest_point AS (\n    SELECT\n        lat,\n        lon,\n        SQRT(\n            POWER(lat - ${lat}, 2) +\n            POWER(lon - ${lon}, 2)\n        ) AS distance_deg\n    FROM combined_points\n    ORDER BY distance_deg\n    LIMIT 1\n),\n\nfiltered AS (\n    SELECT\n        t.time,\n        t.precip\n    FROM (\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_india\"\n        UNION ALL\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_eastern_africa\"\n        UNION ALL\n        SELECT * FROM \"full_rainfall/imerg_final_${grid}_western_africa\"\n    ) t\n    JOIN nearest_point n\n      ON t.lat = n.lat\n     AND t.lon = n.lon\n    WHERE n.distance_deg <= (200 / 111.0)\n      AND EXTRACT(YEAR FROM t.time)::int IN (${year:csv})\n)\n\nSELECT\n    time,\n    AVG(precip) OVER (\n        ORDER BY time\n        ROWS BETWEEN ${agg_days}-1 PRECEDING AND CURRENT ROW\n    ) AS precip\nFROM filtered\nORDER BY time;",
          "refId": "annual_series",
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
          "rawSql": "WITH combined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_eastern_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_western_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_india\"\n),\n\nnearest_point AS (\n    SELECT\n        lat,\n        lon,\n        SQRT(\n            POWER(lat - ${lat}, 2) +\n            POWER(lon - ${lon}, 2)\n        ) AS distance_deg\n    FROM combined_points\n    ORDER BY distance_deg\n    LIMIT 1\n)\n\nSELECT\n    t.time,\n    t.precip / ${agg_days} AS precip\nFROM (\n    SELECT * FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_western_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_ecmwf_ifs_er_global1_5_${lead}_india\"\n) t\nJOIN nearest_point n\n  ON t.lat = n.lat\n AND t.lon = n.lon\nWHERE n.distance_deg <= (200 / 111.0)\n  AND EXTRACT(YEAR FROM t.time)::int IN (${year:csv})\nORDER BY t.time;",
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
          "rawSql": "WITH source_tables AS (\n    SELECT * FROM \"full_rainfall/era5_${grid}_india\"\n    UNION ALL\n    SELECT * FROM \"full_rainfall/era5_${grid}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"full_rainfall/era5_${grid}_western_africa\"\n),\n\ncombined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM source_tables\n),\n\nnearest_point AS (\n    SELECT\n        lat,\n        lon,\n        SQRT(\n            POWER(lat - ${lat}, 2) +\n            POWER(lon - ${lon}, 2)\n        ) AS distance_deg\n    FROM combined_points\n    ORDER BY distance_deg\n    LIMIT 1\n),\n\nfiltered AS (\n    SELECT\n        t.time,\n        t.precip\n    FROM source_tables t\n    JOIN nearest_point n\n      ON t.lat = n.lat\n     AND t.lon = n.lon\n    WHERE n.distance_deg <= (200.0 / 111.0)\n      AND EXTRACT(YEAR FROM t.time) IN (${year:csv})\n)\n\nSELECT\n    time,\n    AVG(precip) OVER (\n        ORDER BY time\n        ROWS BETWEEN ${agg_days}-1 PRECEDING AND CURRENT ROW\n    ) AS precip\nFROM filtered\nORDER BY time;",
          "refId": "era5_annual_series",
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
          "rawSql": "WITH combined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_eastern_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_western_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_india\"\n),\n\nnearest_point AS (\n    SELECT\n        lat,\n        lon,\n        SQRT(\n            POWER(lat - ${lat}, 2) +\n            POWER(lon - ${lon}, 2)\n        ) AS distance_deg\n    FROM combined_points\n    ORDER BY distance_deg\n    LIMIT 1\n)\n\nSELECT\n    t.time,\n    t.precip / ${agg_days} AS precip\nFROM (\n    SELECT * FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_western_africa\"\n    UNION ALL\n    SELECT * FROM \"full_forecast/${agg_days}_cumulus_ai_global1_5_${lead}_india\"\n) t\nJOIN nearest_point n\n  ON t.lat = n.lat\n AND t.lon = n.lon\nWHERE n.distance_deg <= (200 / 111.0)\n  AND EXTRACT(YEAR FROM t.time)::int IN (${year:csv})\nORDER BY t.time;",
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
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "custom": {
            "align": "auto",
            "cellOptions": {
              "type": "auto"
            },
            "inspect": false
          },
          "mappings": [],
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
        "h": 7,
        "w": 8,
        "x": 0,
        "y": 9
      },
      "id": 7,
      "options": {
        "cellHeight": "sm",
        "footer": {
          "countRows": false,
          "fields": "",
          "reducer": [
            "sum"
          ],
          "show": false
        },
        "showHeader": true
      },
      "pluginVersion": "11.5.0-pre",
      "targets": [
        {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT time, value FROM \"${event_list_table}\"\nWHERE lat = ${lat} AND lon = ${lon}\nORDER BY value DESC",
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
      "type": "table"
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
          "text": "12",
          "value": "12"
        },
        "label": "lat",
        "name": "lat",
        "options": [
          {
            "selected": true,
            "text": "12",
            "value": "12"
          }
        ],
        "query": "12",
        "type": "textbox"
      },
      {
        "current": {
          "text": "-1.5",
          "value": "-1.5"
        },
        "label": "lon",
        "name": "lon",
        "options": [
          {
            "selected": true,
            "text": "-1.5",
            "value": "-1.5"
          }
        ],
        "query": "-1.5",
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
        "allowCustomValue": false,
        "current": {
          "text": [
            "2019"
          ],
          "value": [
            "2019"
          ]
        },
        "hide": 1,
        "label": "year",
        "multi": true,
        "name": "year",
        "options": [
          {
            "selected": false,
            "text": "2014",
            "value": "2014"
          },
          {
            "selected": false,
            "text": "2015",
            "value": "2015"
          },
          {
            "selected": false,
            "text": "2016",
            "value": "2016"
          },
          {
            "selected": false,
            "text": "2017",
            "value": "2017"
          },
          {
            "selected": false,
            "text": "2018",
            "value": "2018"
          },
          {
            "selected": true,
            "text": "2019",
            "value": "2019"
          },
          {
            "selected": false,
            "text": "2020",
            "value": "2020"
          },
          {
            "selected": false,
            "text": "2021",
            "value": "2021"
          },
          {
            "selected": false,
            "text": "2022",
            "value": "2022"
          },
          {
            "selected": false,
            "text": "2023",
            "value": "2023"
          },
          {
            "selected": false,
            "text": "2024",
            "value": "2024"
          },
          {
            "selected": false,
            "text": "2025",
            "value": "2025"
          }
        ],
        "query": "2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025",
        "type": "custom"
      },
      {
        "current": {
          "text": "21",
          "value": "21"
        },
        "label": "weeks lead",
        "name": "lead",
        "options": [
          {
            "selected": false,
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
            "selected": true,
            "text": "4",
            "value": "21"
          }
        ],
        "query": "1 : 1, 2 : 7, 3 : 14, 4 : 21",
        "type": "custom"
      },
      {
        "current": {
          "text": "10",
          "value": "10"
        },
        "description": "",
        "name": "vmax",
        "options": [
          {
            "selected": true,
            "text": "10",
            "value": "10"
          }
        ],
        "query": "10",
        "type": "textbox"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": [
            "imerg",
            "cumulus",
            "ecmwf-ifs-er"
          ],
          "value": [
            "imerg",
            "cumulus",
            "ecmwf-ifs-er"
          ]
        },
        "description": "",
        "includeAll": false,
        "label": "display",
        "multi": true,
        "name": "display",
        "options": [
          {
            "selected": true,
            "text": "imerg",
            "value": "imerg"
          },
          {
            "selected": false,
            "text": "era5",
            "value": "era5"
          },
          {
            "selected": true,
            "text": "ecmwf-ifs-er",
            "value": "ecmwf-ifs-er"
          },
          {
            "selected": true,
            "text": "cumulus",
            "value": "cumulus"
          }
        ],
        "query": "imerg, era5, ecmwf-ifs-er, cumulus",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "1",
          "value": "1"
        },
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
        "definition": "select * from md5('forecast_metric_points/1_2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-False_obs_filter-True_big_rain_days_western_africa_2016-01-01_None_imerg_final_precip')",
        "name": "fcst_points_table",
        "options": [],
        "query": "select * from md5('forecast_metric_points/1_2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-False_obs_filter-True_big_rain_days_western_africa_2016-01-01_None_imerg_final_precip')",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "05abb8da89f52f19cb6824e420d8825d",
          "value": "05abb8da89f52f19cb6824e420d8825d"
        },
        "definition": "select * from md5('event_list/2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-False_obs_filter-True_big_rain_days_western_africa_2016-01-01_None_imerg_final_precip')",
        "name": "event_list_table",
        "options": [],
        "query": "select * from md5('event_list/2024-12-31_ecmwf_ifs_er_global1_5_7_forecast_filter-False_obs_filter-True_big_rain_days_western_africa_2016-01-01_None_imerg_final_precip')",
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
