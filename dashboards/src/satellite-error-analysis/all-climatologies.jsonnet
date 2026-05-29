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
        "h": 13,
        "w": 12,
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
        "script": "const fields = data.series[0].fields;\n\n// --- Find fields ---\nconst latField = fields.find(f => f.name === \"lat\");\nconst lonField = fields.find(f => f.name === \"lon\");\nconst regionField = fields.find(f => f.name === \"region\");\n\nif (!latField || !lonField || !regionField) {\n  throw new Error(\"Missing lat, lon, or region field\");\n}\n\n// --- Extract values safely ---\nconst lats = Array.from(latField.values || latField.values.buffer || []);\nconst lons = Array.from(lonField.values || lonField.values.buffer || []);\nconst regions = Array.from(regionField.values || regionField.values.buffer || []);\n\n// --- Safe variable getter ---\nconst getVar = (name) => {\n  return (\n    variables?.[name]?.current?.value ??\n    variables?.[name]?.value ??\n    null\n  );\n};\n\n// --- Dashboard variables ---\nconst lat1 = parseFloat(getVar(\"lat\"));\nconst lon1 = parseFloat(getVar(\"lon\"));\n\nconst mapZoom = parseFloat(getVar(\"map_zoom\")) || 1.5;\nconst mapCenterLat = parseFloat(getVar(\"map_center_lat\")) || 10;\nconst mapCenterLon = parseFloat(getVar(\"map_center_lon\")) || 30;\n\n// ======================================================\n// UNIQUE REGIONS\n// ======================================================\n\nconst uniqueRegions = [\n  ...new Set(\n    regions.filter(r => r != null && r !== \"\")\n  )\n];\n\n// ======================================================\n// GENERATE COLORS FROM HSV COLORMAP\n// ======================================================\n\nfunction hsvToRgb(h, s, v) {\n\n  let r, g, b;\n\n  let i = Math.floor(h * 6);\n  let f = h * 6 - i;\n\n  let p = v * (1 - s);\n  let q = v * (1 - f * s);\n  let t = v * (1 - (1 - f) * s);\n\n  switch (i % 6) {\n    case 0:\n      r = v; g = t; b = p;\n      break;\n    case 1:\n      r = q; g = v; b = p;\n      break;\n    case 2:\n      r = p; g = v; b = t;\n      break;\n    case 3:\n      r = p; g = q; b = v;\n      break;\n    case 4:\n      r = t; g = p; b = v;\n      break;\n    case 5:\n      r = v; g = p; b = q;\n      break;\n  }\n\n  return `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`;\n}\n\n// ======================================================\n// DYNAMIC REGION → COLOR MAP\n// ======================================================\n\nconst regionColorMap = {};\n\nuniqueRegions.forEach((region, i) => {\n\n  // evenly spaced hues\n  const hue = i / uniqueRegions.length;\n\n  regionColorMap[region] =\n    hsvToRgb(hue, 0.85, 0.95);\n});\n\n// Default for unlabeled points\nconst defaultColor = \"#2c7fb8\";\n\n// ======================================================\n// POINT COLORS\n// ======================================================\n\nconst colors = regions.map(r => {\n\n  if (r == null || r === \"\") {\n    return defaultColor;\n  }\n\n  return regionColorMap[r];\n});\n\n// ======================================================\n// MAIN TRACE\n// ======================================================\n\nconst traces = [{\n  type: 'scattermapbox',\n\n  lat: lats,\n  lon: lons,\n\n  mode: 'markers',\n\n  marker: {\n    size: 7,\n\n    color: colors,\n\n    opacity: 0.1\n  },\n\n  text: regions.map(r =>\n    r\n      ? `Region: ${r}`\n      : `No region label`\n  ),\n\n  hovertemplate:\n    'Lat: %{lat:.2f}<br>' +\n    'Lon: %{lon:.2f}<br>' +\n    '%{text}<extra></extra>',\n\n  showlegend: false\n}];\n\n// ======================================================\n// LEGEND TRACES\n// ======================================================\n\nuniqueRegions.forEach(region => {\n\n  traces.push({\n\n    type: 'scattermapbox',\n\n    lat: [null],\n    lon: [null],\n\n    mode: 'markers',\n\n    marker: {\n      size: 10,\n      color: regionColorMap[region]\n    },\n\n    name: region,\n\n    showlegend: true,\n\n    hoverinfo: 'skip'\n  });\n});\n\n// unlabeled legend\n\ntraces.push({\n\n  type: 'scattermapbox',\n\n  lat: [null],\n  lon: [null],\n\n  mode: 'markers',\n\n  marker: {\n    size: 10,\n    color: defaultColor\n  },\n\n  name: 'unlabeled',\n\n  showlegend: true,\n\n  hoverinfo: 'skip'\n});\n\n// ======================================================\n// SELECTED POINT\n// ======================================================\n\nif (!isNaN(lat1) && !isNaN(lon1)) {\n\n  traces.push({\n\n    type: 'scattermapbox',\n\n    lat: [lat1],\n    lon: [lon1],\n\n    mode: 'markers',\n\n    marker: {\n      size: 14,\n\n      color: 'gold',\n\n      line: {\n        width: 2,\n        color: 'black'\n      }\n    },\n\n    text: [\n      `Selected point<br>Lat: ${lat1}<br>Lon: ${lon1}`\n    ],\n\n    hovertemplate:\n      '%{text}<extra></extra>',\n\n    showlegend: false\n  });\n}\n\n// ======================================================\n// RETURN FIGURE\n// ======================================================\n\nreturn {\n\n  data: traces,\n\n  layout: {\n\n    mapbox: {\n      style: 'open-street-map',\n\n      center: {\n        lat: mapCenterLat,\n        lon: mapCenterLon\n      },\n\n      zoom: mapZoom,\n\n      dragmode: 'zoom'\n    },\n\n    margin: {\n      t: 0,\n      b: 0,\n      l: 0,\n      r: 0\n    },\n\n    legend: {\n      bgcolor: 'rgba(255,255,255,0.85)'\n    },\n\n    paper_bgcolor: 'rgba(0,0,0,0)',\n    plot_bgcolor: 'rgba(0,0,0,0)'\n  },\n\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true\n  }\n};",
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
          "rawSql": "WITH precip AS (\n\n    SELECT\n        lat,\n        lon,\n        AVG(precip) AS mean_precip\n    FROM (\n\n        SELECT lat, lon, precip\n        FROM \"get_precip_climatology/imerg_final_global0_25_india\"\n\n        UNION ALL\n\n        SELECT lat, lon, precip\n        FROM \"get_precip_climatology/imerg_final_global0_25_eastern_africa\"\n\n        UNION ALL\n\n        SELECT lat, lon, precip\n        FROM \"get_precip_climatology/imerg_final_global0_25_western_africa\"\n\n    ) t\n\n    GROUP BY lat, lon\n)\n\nSELECT\n    p.lat,\n    p.lon,\n    p.mean_precip,\n    r.region\nFROM precip p\n\nLEFT JOIN \"rainfall_region_labels/global0_25\" r\nON p.lat = r.lat\nAND p.lon = r.lon\n\nORDER BY p.lat, p.lon",
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
      "description": "Precipitation & Soil Moisture",
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "gridPos": {
        "h": 13,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 1,
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
        "onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n  const { type: eventType, data: eventData } = event;\n  const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n  switch (eventType) {\n    case 'click':\n      console.log('Click event:', eventData.points);\n      break;\n    case 'select':\n      console.log('Selection event:', eventData.range);\n      break;\n    case 'zoom':\n      console.log('Zoom event:', eventData);\n      break;\n    default:\n      console.log('Unhandled event type:', eventType, eventData);\n  }\n\n  console.log('Current time zone:', timeZone);\n  console.log('From time:', dayjs(variables.__from).format());\n  console.log('To time:', dayjs(variables.__to).format());\n\n  // Example of using locationService\n  // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n  console.error('Error in onclick handler:', error);\n}\n*/\n  ",
        "resScale": 2,
        "script": " // --- Get series ---\nlet series = data.series[0];\n\n// --- Find fields ---\nlet xField = series.fields.find(f => f.name === \"dayofyear\");\nlet yField = series.fields.find(f => f.name === \"precip\");\n\nif (!xField || !yField) {\n    throw new Error(\"Could not find dayofyear or precip fields\");\n}\n\n// --- Extract values safely ---\nlet rawDates = Array.from(xField.values || xField.values.buffer || []);\nlet yValues = Array.from(yField.values || yField.values.buffer || []);\n\n// --- Convert dates to MM-DD strings ---\nlet xValues = rawDates.map(d => {\n    let dt = new Date(d);\n\n    let month = String(dt.getUTCMonth() + 1).padStart(2, '0');\n    let day = String(dt.getUTCDate()).padStart(2, '0');\n\n    return `${month}-${day}`;\n});\n\n// --- Month tick positions ---\nconst monthStarts = [\n    \"01-01\",\"02-01\",\"03-01\",\"04-01\",\n    \"05-01\",\"06-01\",\"07-01\",\"08-01\",\n    \"09-01\",\"10-01\",\"11-01\",\"12-01\"\n];\n\nconst monthLabels = [\n    \"Jan\",\"Feb\",\"Mar\",\"Apr\",\n    \"May\",\"Jun\",\"Jul\",\"Aug\",\n    \"Sep\",\"Oct\",\"Nov\",\"Dec\"\n];\n\n// --- Wet blue color (matches map palette) ---\nconst wetBlue = '#80cdc1';\n\n// --- Build trace ---\nlet traces = [\n    {\n        x: xValues,\n        y: yValues,\n        type: 'scatter',\n        mode: 'lines',\n        line: {\n            color: wetBlue,\n            width: 2.5\n        },\n        hovertemplate:\n            'Day: %{x}<br>' +\n            'Precip: %{y:.2f}<extra></extra>'\n    }\n];\n\n// --- Return Plotly object ---\nreturn {\n    data: traces,\n\n    layout: {\n        xaxis: {\n            title: 'Month',\n            type: 'category',\n            tickmode: 'array',\n            tickvals: monthStarts,\n            ticktext: monthLabels\n        },\n\n        yaxis: {\n            title: 'Precipitation (mm/day)'\n        },\n\n        margin: {\n            l: 60,\n            r: 20,\n            t: 40,\n            b: 60\n        },\n\n        hovermode: 'closest'\n    }\n};",
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
          "rawSql": "WITH combined_points AS (\n    SELECT DISTINCT lat, lon\n    FROM \"get_precip_climatology/imerg_final_global0_25_india\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"get_precip_climatology/imerg_final_global0_25_eastern_africa\"\n\n    UNION\n\n    SELECT DISTINCT lat, lon\n    FROM \"get_precip_climatology/imerg_final_global0_25_western_africa\"\n),\n\nnearest_point AS (\n    SELECT\n        lat,\n        lon,\n        POWER(lat - ${lat}, 2) + POWER(lon - ${lon}, 2) AS distance\n    FROM combined_points\n    ORDER BY distance\n    LIMIT 1\n)\n\nSELECT\n    t.dayofyear,\n    t.precip\nFROM (\n    SELECT * FROM \"get_precip_climatology/imerg_final_global0_25_india\"\n    UNION ALL\n    SELECT * FROM \"get_precip_climatology/imerg_final_global0_25_eastern_africa\"\n    UNION ALL\n    SELECT * FROM \"get_precip_climatology/imerg_final_global0_25_western_africa\"\n) t\nJOIN nearest_point n\n  ON t.lat = n.lat\n AND t.lon = n.lon\nORDER BY t.dayofyear",
          "refId": "india_imerg",
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
      "title": "Climatology",
      "type": "nline-plotlyjs-panel"
    },
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
        "h": 12,
        "w": 12,
        "x": 0,
        "y": 13
      },
      "id": 2,
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
        "script": "const fields = data.series[0].fields;\n\n// --- Find fields ---\nconst latField = fields.find(f => f.name === \"lat\");\nconst lonField = fields.find(f => f.name === \"lon\");\nconst meanField = fields.find(f => f.name === \"mean_precip\");\n\nif (!latField || !lonField || !meanField) {\n  throw new Error(\"Missing lat, lon, or mean_precip field\");\n}\n\n// --- Extract values safely ---\nconst lats = Array.from(latField.values || latField.values.buffer || []);\nconst lons = Array.from(lonField.values || lonField.values.buffer || []);\nconst means = Array.from(meanField.values || meanField.values.buffer || []);\n\n// --- Safe variable getter ---\nconst getVar = (name) => {\n  return (\n    variables?.[name]?.current?.value ??\n    variables?.[name]?.value ??\n    null\n  );\n};\n\n// --- Dashboard variables ---\nconst lat1 = parseFloat(getVar(\"lat\"));\nconst lon1 = parseFloat(getVar(\"lon\"));\n\nconst mapZoom = parseFloat(getVar(\"map_zoom\"));\nconst mapCenterLat = parseFloat(getVar(\"map_center_lat\"));\nconst mapCenterLon = parseFloat(getVar(\"map_center_lon\"));\n\n// --- Brown → Blue colormap (dry → wet) ---\nconst brownBlueScale = [\n  [0.0, '#8c510a'],  // dry brown\n  [0.05, '#bf812d'],\n  [0.1, '#dfc27d'],\n  [0.4, '#80cdc1'],\n  [0.8, '#35978f'],\n  [1.0, '#2c7fb8']   // wet blue\n];\n\n// --- Main scatter map ---\nconst traces = [{\n  type: 'scattermapbox',\n\n  lat: lats,\n  lon: lons,\n\n  mode: 'markers',\n\n  marker: {\n    size: 7,\n\n    color: means,\n    colorscale: brownBlueScale,\n\n    cmin: Math.min(...means),\n    cmax: Math.max(...means),\n\n    colorbar: {\n      title: 'Mean Precip'\n    },\n\n    opacity: 0.5\n  },\n\n  text: means.map(v => `Mean precip: ${Number(v).toFixed(2)}`),\n\n  hovertemplate:\n    'Lat: %{lat:.2f}<br>' +\n    'Lon: %{lon:.2f}<br>' +\n    '%{text}<extra></extra>'\n}];\n\n// --- Highlight selected point ---\nif (!isNaN(lat1) && !isNaN(lon1)) {\n  traces.push({\n    type: 'scattermapbox',\n\n    lat: [lat1],\n    lon: [lon1],\n\n    mode: 'markers',\n\n    marker: {\n      size: 14,\n      color: 'gold',\n      line: {\n        width: 2,\n        color: 'black'\n      }\n    },\n\n    text: [`Selected point<br>Lat: ${lat1}<br>Lon: ${lon1}`],\n\n    hovertemplate: '%{text}<extra></extra>'\n  });\n}\n\n// --- Return Plotly figure ---\nreturn {\n  data: traces,\n\n  layout: {\n    mapbox: {\n      style: 'open-street-map',\n\n      center: {\n        lat: 10,\n        lon: 30\n      },\n\n      zoom: 1.5,\n\n      dragmode: 'zoom'\n    },\n\n    margin: {\n      t: 0,\n      b: 0,\n      l: 0,\n      r: 0\n    },\n\n    paper_bgcolor: 'rgba(0,0,0,0)',\n    plot_bgcolor: 'rgba(0,0,0,0)',\n\n    showlegend: false\n  },\n\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true\n  }\n};",
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
          "rawSql": "WITH precip AS (\n\n    SELECT\n        lat,\n        lon,\n        AVG(precip) AS mean_precip\n    FROM (\n\n        SELECT lat, lon, precip\n        FROM \"get_precip_climatology/imerg_final_global0_25_india\"\n\n        UNION ALL\n\n        SELECT lat, lon, precip\n        FROM \"get_precip_climatology/imerg_final_global0_25_eastern_africa\"\n\n        UNION ALL\n\n        SELECT lat, lon, precip\n        FROM \"get_precip_climatology/imerg_final_global0_25_western_africa\"\n\n    ) t\n\n    GROUP BY lat, lon\n)\n\nSELECT\n    p.lat,\n    p.lon,\n    p.mean_precip,\n    r.region\nFROM precip p\n\nLEFT JOIN \"rainfall_region_labels/global0_25\" r\nON p.lat = r.lat\nAND p.lon = r.lon\n\nORDER BY p.lat, p.lon",
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
      "title": "Average Rainfall",
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
          "text": "4",
          "value": "4"
        },
        "label": "lat",
        "name": "lat",
        "options": [],
        "query": "",
        "type": "custom"
      },
      {
        "current": {
          "text": "40.5",
          "value": "40.5"
        },
        "label": "lon",
        "name": "lon",
        "options": [
          {
            "selected": false,
            "text": "80",
            "value": "80"
          }
        ],
        "query": "80",
        "type": "custom"
      }
    ]
  },
  "time": {
    "from": "1904-01-01T00:00:00.000Z",
    "to": "1904-12-31T00:00:00.000Z"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "All Climatologies",
  "uid": "afn9r6y0z14hsb",
  "version": 1,
  "weekStart": ""
}
