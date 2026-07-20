local click_precip_pt_js = importstr '../assets/click_precip_pt.js';
local grid_size_sql = importstr '../assets/grid_size.sql';
local precip_event_pie_js = importstr '../assets/precip_event_pie.js';
local precip_scatter_js = importstr '../assets/precip_scatter.js';
local station_codes_sql = importstr '../assets/station_codes.sql';

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
  "description": "Compare different sources of precipitation estimates in a scatter. ",
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
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 9,
        "x": 0,
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
            "autorange": false,
            "type": "date"
          },
          "yaxis": {
            "automargin": true,
            "autorange": false
          }
        },
        "onclick": click_precip_pt_js,
        "resScale": 2,
        "script": precip_scatter_js,
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
          "rawSql": "SELECT\n  lat, lon, time, ${satellite}_precip, ${station}_precip\nFROM \"scatter_data/${agg_days}_${grid}_lsm_${region1}\"\nWHERE EXTRACT(MONTH FROM time) IN (${months:csv})\n  AND (\n    NOT ${filter_space:raw}\n    OR ABS(lat - ${lat1}::real) <= ${grid_size}\n  )\n  AND (\n    NOT ${filter_space:raw}\n    OR ABS(lon - ${lon1}::real) <= ${grid_size}\n  );",
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
      "title": "precip comparison for ${region1}",
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
        "h": 9,
        "w": 9,
        "x": 9,
        "y": 0
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
            "autorange": false,
            "type": "date"
          },
          "yaxis": {
            "automargin": true,
            "autorange": false
          }
        },
        "onclick": click_precip_pt_js,
        "resScale": 2,
        "script": precip_scatter_js,
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
          "rawSql": "SELECT\n  lat, lon, time, ${satellite}_precip, ${station}_precip\nFROM \"scatter_data/${agg_days}_${grid}_lsm_${region2}\"\nWHERE EXTRACT(MONTH FROM time) IN (${months:csv})\n  AND (\n    NOT ${filter_space:raw}\n    OR ABS(lat - ${lat2}::real) <= 1e-4\n  )\n  AND (\n    NOT ${filter_space:raw}\n    OR ABS(lon - ${lon2}::real) <= 1e-4\n  );\n",
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
      "title": "precip comparison for ${region2}",
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
        "h": 18,
        "w": 6,
        "x": 18,
        "y": 0
      },
      "id": 8,
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
        "onclick": "try {\n  const { type: eventType, data: eventData } = event;\n\n  if (eventType === 'click') {\n    const clickedPoint = eventData?.points?.[0];\n\n    if (clickedPoint) {\n      const useSecond = eventData.event?.shiftKey;\n      const currentUrl = new URL(window.location.href);\n\n      if (useSecond) {\n        currentUrl.searchParams.set('var-lat2', clickedPoint.lat);\n        currentUrl.searchParams.set('var-lon2', clickedPoint.lon);\n      } else {\n        currentUrl.searchParams.set('var-lat1', clickedPoint.lat);\n        currentUrl.searchParams.set('var-lon1', clickedPoint.lon);\n      }\n\n      currentUrl.searchParams.set('var-filter_space', true);\n\n      const plots = document.querySelectorAll('.js-plotly-plot');\n      const plotEl = Array.from(plots).find(p => p._fullLayout?.mapbox);\n      const mapSubplot = plotEl._fullLayout.mapbox._subplot;\n\n      console.log(plotEl._fullLayout.mapbox);\n\n      \n      const center = mapSubplot.map.getCenter();\n      const zoom = mapSubplot.map.getZoom();\n      console.log(\"Testing\")\n      console.log(center)\n      console.log(zoom)\n      console.log(mapSubplot)\n\n      currentUrl.searchParams.set('var-map_zoom', zoom.toFixed(2));\n      currentUrl.searchParams.set('var-map_center_lat', center.lat.toFixed(4));\n      currentUrl.searchParams.set('var-map_center_lon', center.lng.toFixed(4));\n\n      window.location.href = currentUrl.toString();\n    }\n  }\n} catch (error) {\n  console.error('Error in map click handler:', error);\n}",
        "resScale": 2,
        "script": "const fields = data.series[0].fields;\n\nconst lats = fields[0].values.toArray();\nconst lons = fields[1].values.toArray();\nconsole.log(\"lats\", lats);\n\nconst lat1 = parseFloat(variables.lat1.query);\nconst lon1 = parseFloat(variables.lon1.query);\nconst lat2 = parseFloat(variables.lat2.query);\nconst lon2 = parseFloat(variables.lon2.query);\n\nconst mapZoom = parseFloat(variables.map_zoom.query);\nconst mapCenterLat = parseFloat(variables.map_center_lat.query);\nconst mapCenterLon = parseFloat(variables.map_center_lon.query);\n\n// console.log(mapZoom, mapCenterLat, mapCenterLon);\nconst traces = [{\n  type: 'scattermapbox',\n  lat: lats,\n  lon: lons,\n  mode: 'markers',\n  marker: {\n    size: 7,\n    color: '#4A90D9',\n    opacity: 0.85,\n  },\n  hoverinfo: 'lat+lon',\n  hoverlabel: { bgcolor: '#333333' }\n}];\n\nif (!isNaN(lat1) && !isNaN(lon1)) {\n  traces.push({\n    type: 'scattermapbox',\n    lat: [lat1],\n    lon: [lon1],\n    mode: 'markers',\n    marker: { size: 10, color: 'gold' },\n    text: [`Point 1: ${lat1}, ${lon1}`],\n    hoverinfo: 'text',\n    hoverlabel: { bgcolor: '#333333' }\n  });\n}\n\nif (!isNaN(lat2) && !isNaN(lon2)) {\n  traces.push({\n    type: 'scattermapbox',\n    lat: [lat2],\n    lon: [lon2],\n    mode: 'markers',\n    marker: { size: 10, color: 'red' },\n    text: [`Point 2: ${lat2}, ${lon2}`],\n    hoverinfo: 'text',\n    hoverlabel: { bgcolor: '#333333' }\n  });\n}\n\nreturn {\n  data: traces,\n  layout: {\n    mapbox: {\n      style: 'open-street-map',\n      center: { lat: mapCenterLat, lon: mapCenterLon },\n      zoom: mapZoom,\n      dragmode: 'zoom'\n    },\n    margin: { t: 0, b: 0, l: 0, r: 0 },\n    paper_bgcolor: 'rgba(0,0,0,0)',\n    plot_bgcolor: 'rgba(0,0,0,0)',\n    showlegend: false\n  },\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true\n  }\n};",
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
          "rawSql": "SELECT DISTINCT lat, lon\nFROM (\n  SELECT lat, lon FROM \"scatter_data/${agg_days}_${grid}_lsm_${region1}\"\n  UNION\n  SELECT lat, lon FROM \"scatter_data/${agg_days}_${grid}_lsm_${region2}\"\n) p",
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
        "uid": "-- Dashboard --"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 9,
        "x": 0,
        "y": 9
      },
      "id": 3,
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
        "script": precip_event_pie_js,
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "datasource": {
            "type": "datasource",
            "uid": "-- Dashboard --"
          },
          "panelId": 1,
          "refId": "A"
        }
      ],
      "title": "Counts for event in ${region1}",
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
        "type": "datasource",
        "uid": "-- Dashboard --"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 9,
        "x": 9,
        "y": 9
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
        "script": precip_event_pie_js,
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "datasource": {
            "type": "datasource",
            "uid": "-- Dashboard --"
          },
          "panelId": 7,
          "refId": "A"
        }
      ],
      "title": "Counts for event in ${region2}",
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
        "allowCustomValue": false,
        "current": {
          "text": "imerg_final",
          "value": "imerg_final"
        },
        "description": "precip satellite data source",
        "label": "Satellite Product",
        "name": "satellite",
        "options": [
          {
            "selected": true,
            "text": "IMERG",
            "value": "imerg_final"
          },
          {
            "selected": false,
            "text": "CHIRPS",
            "value": "chirps_v3"
          },
          {
            "selected": false,
            "text": "Rain over Africa",
            "value": "rain_over_africa"
          }
        ],
        "query": "IMERG : imerg_final, CHIRPS : chirps_v3, Rain over Africa : rain_over_africa",
        "type": "custom"
      },
      {
        "current": {
          "text": "global0_25",
          "value": "global0_25"
        },
        "description": "",
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
        "allowCustomValue": false,
        "current": {
          "text": "1",
          "value": "1"
        },
        "label": "agg_days",
        "name": "agg_days",
        "options": [
          {
            "selected": true,
            "text": "1",
            "value": "1"
          },
          {
            "selected": false,
            "text": "5",
            "value": "5"
          },
          {
            "selected": false,
            "text": "10",
            "value": "10"
          }
        ],
        "query": "1, 5, 10",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "tahmo_avg",
          "value": "tahmo_avg"
        },
        "description": "",
        "label": "stations",
        "name": "station",
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
        "allowCustomValue": false,
        "current": {
          "text": [
            "5",
            "6",
            "7"
          ],
          "value": [
            "5",
            "6",
            "7"
          ]
        },
        "description": "",
        "includeAll": true,
        "label": "months",
        "multi": true,
        "name": "months",
        "options": [
          {
            "selected": false,
            "text": "1",
            "value": "1"
          },
          {
            "selected": false,
            "text": "2",
            "value": "2"
          },
          {
            "selected": false,
            "text": "3",
            "value": "3"
          },
          {
            "selected": false,
            "text": "4",
            "value": "4"
          },
          {
            "selected": true,
            "text": "5",
            "value": "5"
          },
          {
            "selected": true,
            "text": "6",
            "value": "6"
          },
          {
            "selected": true,
            "text": "7",
            "value": "7"
          },
          {
            "selected": false,
            "text": "8",
            "value": "8"
          },
          {
            "selected": false,
            "text": "9",
            "value": "9"
          },
          {
            "selected": false,
            "text": "10",
            "value": "10"
          },
          {
            "selected": false,
            "text": "11",
            "value": "11"
          },
          {
            "selected": false,
            "text": "12",
            "value": "12"
          }
        ],
        "query": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "ghana",
          "value": "ghana"
        },
        "description": "",
        "label": "region A",
        "name": "region1",
        "options": [
          {
            "selected": true,
            "text": "ghana",
            "value": "ghana"
          },
          {
            "selected": false,
            "text": "kenya",
            "value": "kenya"
          }
        ],
        "query": "ghana, kenya",
        "type": "custom"
      },
      {
        "current": {
          "text": "kenya",
          "value": "kenya"
        },
        "label": "region B",
        "name": "region2",
        "options": [
          {
            "selected": false,
            "text": "ghana",
            "value": "ghana"
          },
          {
            "selected": true,
            "text": "kenya",
            "value": "kenya"
          }
        ],
        "query": "ghana, kenya",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "",
          "value": ""
        },
        "label": "Filter Lat/Lon",
        "name": "filter_space",
        "options": [
          {
            "selected": false,
            "text": "Yes",
            "value": "true"
          },
          {
            "selected": false,
            "text": "No",
            "value": "false"
          }
        ],
        "query": "Yes : true, No : false",
        "type": "custom"
      },
      {
        "current": {
          "text": "false",
          "value": "false"
        },
        "label": "Agg Time",
        "name": "agg_time",
        "options": [
          {
            "selected": false,
            "text": "Yes",
            "value": "true"
          },
          {
            "selected": true,
            "text": "No",
            "value": "false"
          }
        ],
        "query": "Yes : true, No : false",
        "type": "custom"
      },
      {
        "current": {
          "text": "9.5",
          "value": "9.5"
        },
        "label": "Lat A",
        "name": "lat1",
        "options": [
          {
            "selected": true,
            "text": "9.5",
            "value": "9.5"
          }
        ],
        "query": "9.5",
        "type": "textbox"
      },
      {
        "current": {
          "text": "-1",
          "value": "-1"
        },
        "label": "Lon A",
        "name": "lon1",
        "options": [
          {
            "selected": true,
            "text": "-1",
            "value": "-1"
          }
        ],
        "query": "-1",
        "type": "textbox"
      },
      {
        "current": {
          "text": "0.5",
          "value": "0.5"
        },
        "label": "Lat B",
        "name": "lat2",
        "options": [
          {
            "selected": true,
            "text": "0.5",
            "value": "0.5"
          }
        ],
        "query": "0.5",
        "type": "textbox"
      },
      {
        "current": {
          "text": "35.75",
          "value": "35.75"
        },
        "label": "Lon B",
        "name": "lon2",
        "options": [
          {
            "selected": true,
            "text": "35.75",
            "value": "35.75"
          }
        ],
        "query": "35.75",
        "type": "textbox"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "none",
          "value": "none"
        },
        "description": "parameter to color points by",
        "label": "color by",
        "name": "colorby",
        "options": [
          {
            "selected": true,
            "text": "None",
            "value": "none"
          },
          {
            "selected": false,
            "text": "Humidity",
            "value": "humidity"
          },
          {
            "selected": false,
            "text": "Temperature",
            "value": "temperature"
          },
          {
            "selected": false,
            "text": "Admin 1",
            "value": "admin1"
          },
          {
            "selected": false,
            "text": "Agroecological",
            "value": "agroecological"
          },
          {
            "selected": false,
            "text": "Latitude",
            "value": "latitude"
          },
          {
            "selected": false,
            "text": "Longitude",
            "value": "longitude"
          },
          {
            "selected": false,
            "text": "Location",
            "value": "location"
          }
        ],
        "query": "None : none, Humidity : humidity, Temperature : temperature, Admin 1 : admin1, Agroecological : agroecological, Latitude : latitude, Longitude : longitude, Location : location",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "False",
          "value": "False"
        },
        "description": "whether to plot points as density",
        "label": "density",
        "name": "density",
        "options": [
          {
            "selected": false,
            "text": "True",
            "value": "True"
          },
          {
            "selected": true,
            "text": "False",
            "value": "False"
          }
        ],
        "query": "True, False",
        "type": "custom"
      },
      {
        "current": {
          "text": "2.2",
          "value": "2.2"
        },
        "label": "event threshold (mm / day)",
        "name": "event_thresh",
        "options": [
          {
            "selected": true,
            "text": "2.2",
            "value": "2.2"
          }
        ],
        "query": "2.2",
        "type": "textbox"
      },
      {
        "current": {
          "text": "20",
          "value": "20"
        },
        "description": "set limits on all axes",
        "label": "axis limit",
        "name": "axis_lim",
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
        "allowCustomValue": false,
        "current": {
          "text": "All",
          "value": [
            "$__all"
          ]
        },
        "definition": "SELECT \n  country_name\nFROM \n  \"country_codes/\"",
        "description": "",
        "hide": 2,
        "includeAll": true,
        "label": "Country",
        "multi": true,
        "name": "country_name",
        "options": [],
        "query": "SELECT \n  country_name\nFROM \n  \"country_codes/\"",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "All",
          "value": [
            "$__all"
          ]
        },
        "definition": station_codes_sql,
        "description": "",
        "hide": 2,
        "includeAll": true,
        "label": "Station ID",
        "multi": true,
        "name": "station_id",
        "options": [],
        "query": station_codes_sql,
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "5.16",
          "value": "5.16"
        },
        "hide": 2,
        "name": "map_zoom",
        "options": [
          {
            "selected": true,
            "text": "5.16",
            "value": "5.16"
          }
        ],
        "query": "5.16",
        "type": "textbox"
      },
      {
        "current": {
          "text": "4.7074",
          "value": "4.7074"
        },
        "hide": 2,
        "name": "map_center_lat",
        "options": [
          {
            "selected": true,
            "text": "4.7074",
            "value": "4.7074"
          }
        ],
        "query": "4.7074",
        "type": "textbox"
      },
      {
        "current": {
          "text": "0.3752",
          "value": "0.3752"
        },
        "hide": 2,
        "name": "map_center_lon",
        "options": [
          {
            "selected": true,
            "text": "0.3752",
            "value": "0.3752"
          }
        ],
        "query": "0.3752",
        "type": "textbox"
      },
      {
        "current": {
          "text": "0.125001",
          "value": "0.125001"
        },
        "definition": grid_size_sql,
        "hide": 2,
        "name": "grid_size",
        "options": [],
        "query": grid_size_sql,
        "refresh": 1,
        "regex": "",
        "type": "query"
      }
    ]
  },
  "time": {
    "from": "now-10y",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "Precipitation Scatter Plots",
  "uid": "ffc28h1tj93b4e",
  "version": 1,
  "weekStart": ""
}
