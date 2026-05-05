local afl21x2g76a68a_16_script_js = importstr './assets/afl21x2g76a68a-16-script.js';
local afl21x2g76a68a_17_script_js = importstr './assets/afl21x2g76a68a-17-script.js';
local grid_size_sql = importstr './assets/grid_size.sql';
local paired_histogram_js = importstr './assets/paired_histogram.js';

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
        "target": {
          "limit": 100,
          "matchAny": false,
          "tags": [],
          "type": "dashboard"
        },
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "links": [
    {
      "asDropdown": false,
      "icon": "external link",
      "includeVars": false,
      "keepTime": false,
      "tags": [
        "Home"
      ],
      "targetBlank": false,
      "title": "Home",
      "tooltip": "",
      "type": "dashboards",
      "url": ""
    },
    {
      "asDropdown": false,
      "icon": "external link",
      "includeVars": false,
      "keepTime": false,
      "tags": [
        "Other QC"
      ],
      "targetBlank": false,
      "title": "New link",
      "tooltip": "",
      "type": "dashboards",
      "url": ""
    }
  ],
  "panels": [
    {
      "datasource": {
        "type": "datasource",
        "uid": "-- Mixed --"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "imerg_precip"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "chirps_precip"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "roa_precip"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byFrameRefID",
              "options": "TAHMO"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "smap_soil_moisture"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Event Threshold"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 12,
        "w": 14,
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
        "script": afl21x2g76a68a_17_script_js,
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
          "rawSql": "WITH\n-- -------------------------------------------------\n-- HISTOGRAM (joint distribution)\n-- -------------------------------------------------\nhist AS (\n    SELECT\n        estimate,\n        truth,\n        SUM(precip) AS count\n    FROM \"hist_df/5_imerg_final_${grid}_kenya_tahmo_avg\"\n    GROUP BY estimate, truth\n),\n\n-- -------------------------------------------------\n-- DRY REGIME: truth <= dry\n-- -------------------------------------------------\ndry_hist AS (\n    SELECT *\n    FROM hist\n    WHERE truth <= (${dry})::real\n),\n\ndry_totals AS (\n    SELECT\n        SUM(count) AS total_count\n    FROM dry_hist\n),\n\ndry_prob AS (\n    SELECT\n        d.estimate,\n        SUM(d.count) / NULLIF(t.total_count, 0) AS p_estimate_given_dry\n    FROM dry_hist d\n    CROSS JOIN dry_totals t\n    GROUP BY d.estimate, t.total_count\n),\n\n-- -------------------------------------------------\n-- WET REGIME: truth >= wet\n-- -------------------------------------------------\nwet_hist AS (\n    SELECT *\n    FROM hist\n    WHERE truth >= (${wet})::real\n),\n\nwet_totals AS (\n    SELECT\n        SUM(count) AS total_count\n    FROM wet_hist\n),\n\nwet_prob AS (\n    SELECT\n        w.estimate,\n        SUM(w.count) / NULLIF(t.total_count, 0) AS p_estimate_given_wet\n    FROM wet_hist w\n    CROSS JOIN wet_totals t\n    GROUP BY w.estimate, t.total_count\n),\n\n-- -------------------------------------------------\n-- MERGE PROBABILITIES\n-- -------------------------------------------------\nprob AS (\n    SELECT\n        COALESCE(d.estimate, w.estimate) AS estimate,\n        d.p_estimate_given_dry,\n        w.p_estimate_given_wet\n    FROM dry_prob d\n    FULL OUTER JOIN wet_prob w USING (estimate)\n),\n\n-- -------------------------------------------------\n-- IMERG TIME SERIES\n-- -------------------------------------------------\nimerg AS (\n    SELECT\n        time,\n        precip AS imerg_val\n    FROM \"data_at_stations/1_imerg_final_${grid}_tahmo_precip\"\n    WHERE time $__timeFilter()\n      AND ABS(lat - (${lat:raw})::real) <= ${grid_size}\n      AND ABS(lon - (${lon:raw})::real) <= ${grid_size}\n),\n\n-- -------------------------------------------------\n-- TAHMO TIME SERIES\n-- -------------------------------------------------\ntahmo AS (\n    SELECT\n        time,\n        precip AS tahmo_val\n    FROM \"data_at_stations/1_tahmo_source_stations_precip\"\n    WHERE time $__timeFilter()\n      AND ABS(lat - (${lat:raw})::real) <= ${grid_size}\n      AND ABS(lon - (${lon:raw})::real) <= ${grid_size}\n),\n\n-- -------------------------------------------------\n-- MAP IMERG → PROBABILITY DISTRIBUTION\n-- -------------------------------------------------\nimerg_prob AS (\n    SELECT\n        i.time,\n        i.imerg_val,\n\n        -- P(estimate | dry regime)\n        (\n            SELECT p.p_estimate_given_dry\n            FROM prob p\n            ORDER BY ABS(i.imerg_val - p.estimate)\n            LIMIT 1\n        ) AS imerg_prob_given_dry,\n\n        -- P(estimate | wet regime)\n        (\n            SELECT p.p_estimate_given_wet\n            FROM prob p\n            ORDER BY ABS(i.imerg_val - p.estimate)\n            LIMIT 1\n        ) AS imerg_prob_given_wet\n\n    FROM imerg i\n)\n\n-- -------------------------------------------------\n-- FINAL OUTPUT\n-- -------------------------------------------------\nSELECT\n    ip.time,\n    ip.imerg_val,\n    ip.imerg_prob_given_dry,\n    ip.imerg_prob_given_wet,\n    t.tahmo_val\nFROM imerg_prob ip\nLEFT JOIN tahmo t USING (time)\nORDER BY ip.time;",
          "refId": "TAHMO",
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
      "title": "Daily Precipitation vs Satellites",
      "transformations": [
        {
          "id": "prepareTimeSeries",
          "options": {
            "format": "multi"
          }
        }
      ],
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
        "h": 14,
        "w": 10,
        "x": 14,
        "y": 0
      },
      "id": 15,
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
        "script": "const fields = data.series[0].fields;\n\nconst lats = fields[0].values.toArray();\nconst lons = fields[1].values.toArray();\nconsole.log(\"lats\", lats);\n\nconst lat1 = parseFloat(variables.lat.query);\nconst lon1 = parseFloat(variables.lon.query);\n\nconst mapZoom = parseFloat(variables.map_zoom.query);\nconst mapCenterLat = parseFloat(variables.map_center_lat.query);\nconst mapCenterLon = parseFloat(variables.map_center_lon.query);\n\nconst traces = [{\n  type: 'scattermapbox',\n  lat: lats,\n  lon: lons,\n  mode: 'markers',\n  marker: {\n    size: 7,\n    color: '#4A90D9',\n    opacity: 0.85,\n  },\n  hoverinfo: 'lat+lon',\n  hoverlabel: { bgcolor: '#333333' }\n}];\n\nif (!isNaN(lat1) && !isNaN(lon1)) {\n  traces.push({\n    type: 'scattermapbox',\n    lat: [lat1],\n    lon: [lon1],\n    mode: 'markers',\n    marker: { size: 10, color: 'gold' },\n    text: [`Point 1: ${lat1}, ${lon1}`],\n    hoverinfo: 'text',\n    hoverlabel: { bgcolor: '#333333' }\n  });\n}\n\nreturn {\n  data: traces,\n  layout: {\n    mapbox: {\n      style: 'open-street-map',\n      center: { lat: mapCenterLat, lon: mapCenterLon },\n      zoom: mapZoom,\n      dragmode: 'zoom'\n    },\n    margin: { t: 0, b: 0, l: 0, r: 0 },\n    paper_bgcolor: 'rgba(0,0,0,0)',\n    plot_bgcolor: 'rgba(0,0,0,0)',\n    showlegend: false\n  },\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true\n  }\n};",
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
          "rawSql": "SELECT DISTINCT lat, lon\nFROM \"data_at_stations/1_imerg_final_${grid}_tahmo_precip\"",
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
      "title": "Sensor Status Map",
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
        "type": "datasource",
        "uid": "-- Mixed --"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "imerg_precip"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "chirps_precip"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "roa_precip"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byFrameRefID",
              "options": "TAHMO"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "smap_soil_moisture"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Event Threshold"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 14,
        "w": 14,
        "x": 0,
        "y": 12
      },
      "id": 13,
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
        "script": "// 'data', 'variables', 'options', and 'utils' are passed as arguments\nconsole.log(data)\nlet seriesImerg = data.series[0];\nlet seriesTahmo = data.series[1];\n\n// Extract fields\nlet timeImerg = seriesImerg.fields.find(f => f.name === 'time').values;\nlet imerg = seriesImerg.fields.find(f => f.name === 'imerg').values;\n\nlet timeTahmo = seriesTahmo.fields.find(f => f.name === 'time').values;\nlet tahmo = seriesTahmo.fields.find(f => f.name === 'tahmo').values;\n\n// Handle Grafana value containers\ntimeImerg = timeImerg || timeImerg.buffer;\nimerg = imerg || imerg.buffer;\n\ntimeTahmo = timeTahmo || timeTahmo.buffer;\ntahmo = tahmo || tahmo.buffer;\n\nreturn {\n  data: [\n    {\n      x: timeImerg,\n      y: imerg,\n      type: 'scatter',\n      mode: 'lines',\n      name: 'IMERG'\n    },\n    {\n      x: timeTahmo,\n      y: tahmo,\n      type: 'scatter',\n      mode: 'lines',\n      name: 'TAHMO'\n    }\n  ],\n  layout: {\n    title: 'IMERG vs TAHMO',\n    xaxis: { title: 'Time' },\n    yaxis: { title: 'Value' },\n    hovermode: 'x unified'\n  }\n};",
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
          "rawSql": "SELECT\n  time,\n  AVG(imerg) OVER (\n    ORDER BY time\n    ROWS BETWEEN ${agg_days} PRECEDING AND CURRENT ROW\n  ) AS imerg,\n  AVG(tahmo) OVER (\n    ORDER BY time\n    ROWS BETWEEN ${agg_days} PRECEDING AND CURRENT ROW\n  ) AS tahmo\nFROM \"station_satellite_climatology/global0_25_africa\"\nWHERE lat = $lat AND lon = $lon\nORDER BY time;",
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
      "title": "Daily Precipitation vs Satellites",
      "transformations": [
        {
          "id": "prepareTimeSeries",
          "options": {
            "format": "multi"
          }
        }
      ],
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
        "h": 4,
        "w": 6,
        "x": 18,
        "y": 14
      },
      "id": 14,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "percentChangeColorMode": "standard",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "showPercentChange": false,
        "textMode": "auto",
        "wideLayout": true
      },
      "pluginVersion": "11.5.0-pre",
      "targets": [
        {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT COUNT(DISTINCT station_id) AS unique_stations\nFROM \"data_at_stations/1_tahmo_source_stations_precip\"\nWHERE time $__timeFilter()\n  AND ABS(lat - (${lat:raw})::real) <= ${grid_size}\n  AND ABS(lon - (${lon:raw})::real) <= ${grid_size}",
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
      "title": "Number of TAHMO Stations ",
      "type": "stat"
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
        "h": 11,
        "w": 14,
        "x": 0,
        "y": 26
      },
      "id": 16,
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
            "range": [
              0,
              10
            ],
            "type": "linear"
          },
          "yaxis": {
            "automargin": true,
            "autorange": true,
            "range": [
              0,
              20
            ]
          }
        },
        "onclick": paired_histogram_js,
        "resScale": 2,
        "script": afl21x2g76a68a_16_script_js,
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT estimate, truth, SUM(precip) as precip\nFROM \"hist_df/${agg_days}_imerg_final_${grid}_kenya_tahmo_avg\"\nWHERE region_id = (\n    SELECT region_id\n    FROM \"spacegrouping_category_codes/${grid}_global_country\"\n    WHERE region = 'kenya'\n)\nGROUP BY estimate, truth\nORDER BY estimate, truth;",
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
      "title": "measurement model",
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
          "text": "-1.75",
          "value": "-1.75"
        },
        "label": "Latitude",
        "name": "lat",
        "options": [
          {
            "selected": true,
            "text": "-1.75",
            "value": "-1.75"
          }
        ],
        "query": "-1.75",
        "type": "textbox"
      },
      {
        "current": {
          "text": "37.5",
          "value": "37.5"
        },
        "label": "Longitude",
        "name": "lon",
        "options": [
          {
            "selected": true,
            "text": "37.5",
            "value": "37.5"
          }
        ],
        "query": "37.5",
        "type": "textbox"
      },
      {
        "current": {
          "text": "c02fd8f15cf116b1a44a29e1cc5a39e3",
          "value": "c02fd8f15cf116b1a44a29e1cc5a39e3"
        },
        "definition": "select * from md5('tahmo_deployment/')",
        "hide": 2,
        "name": "tahmo_deployment_name",
        "options": [],
        "query": "select * from md5('tahmo_deployment/')",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "global0_25",
          "value": "global0_25"
        },
        "label": "Grid",
        "name": "grid",
        "options": [
          {
            "selected": false,
            "text": "1.5",
            "value": "global1_5"
          },
          {
            "selected": true,
            "text": "0.25",
            "value": "global0_25"
          },
          {
            "selected": false,
            "text": "0.10",
            "value": "global0_1"
          }
        ],
        "query": "1.5 : global1_5, 0.25 : global0_25, 0.10 : global0_1",
        "type": "custom"
      },
      {
        "current": {
          "text": "0.125001",
          "value": "0.125001"
        },
        "definition": grid_size_sql,
        "description": "",
        "hide": 2,
        "name": "grid_size",
        "options": [],
        "query": grid_size_sql,
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "5",
          "value": "5"
        },
        "label": "Agg Days",
        "name": "agg_days",
        "options": [
          {
            "selected": true,
            "text": "5",
            "value": "5"
          }
        ],
        "query": "5",
        "type": "textbox"
      },
      {
        "current": {
          "text": "20",
          "value": "20"
        },
        "label": "Event mm",
        "name": "event",
        "options": [
          {
            "selected": true,
            "text": "20",
            "value": "20"
          }
        ],
        "query": "20",
        "type": "textbox"
      },
      {
        "current": {
          "text": "4.61",
          "value": "4.61"
        },
        "hide": 2,
        "name": "map_zoom",
        "options": [
          {
            "selected": true,
            "text": "4.61",
            "value": "4.61"
          }
        ],
        "query": "4.61",
        "type": "textbox"
      },
      {
        "current": {
          "text": "-0.6425",
          "value": "-0.6425"
        },
        "hide": 2,
        "name": "map_center_lat",
        "options": [
          {
            "selected": true,
            "text": "-0.6425",
            "value": "-0.6425"
          }
        ],
        "query": "-0.6425",
        "type": "textbox"
      },
      {
        "current": {
          "text": "34.7440",
          "value": "34.7440"
        },
        "description": "",
        "hide": 2,
        "name": "map_center_lon",
        "options": [
          {
            "selected": true,
            "text": "34.7440",
            "value": "34.7440"
          }
        ],
        "query": "34.7440",
        "type": "textbox"
      },
      {
        "current": {
          "text": "1",
          "value": "1"
        },
        "label": "dry <",
        "name": "dry",
        "options": [
          {
            "selected": true,
            "text": "1",
            "value": "1"
          }
        ],
        "query": "1",
        "type": "custom"
      },
      {
        "current": {
          "text": "5",
          "value": "5"
        },
        "description": "lower wet threshold",
        "label": "wet >",
        "name": "wet",
        "options": [
          {
            "selected": true,
            "text": "5",
            "value": "5"
          }
        ],
        "query": "5",
        "type": "custom"
      }
    ]
  },
  "time": {
    "from": "now-10y",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "Climatologies",
  "uid": "afl21x2g76a68a",
  "version": 1,
  "weekStart": ""
}
