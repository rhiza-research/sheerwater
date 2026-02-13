local click_precip_pt_js = importstr './assets/click_precip_pt.js';
local precip_event_pie_js = importstr './assets/precip_event_pie.js';
local precip_scatter_js = importstr './assets/precip_scatter.js';
local station_codes_sql = importstr './assets/station_codes.sql';

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
        "h": 7,
        "w": 22,
        "x": 0,
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
        "onclick": "try {\n  const { type: eventType, data: eventData } = event;\n\n  if (eventType === 'click') {\n    const clickedPoint = eventData?.points?.[0];\n    if (clickedPoint) {\n      const lat = (Math.round(clickedPoint.lat / 0.05) * 0.05).toFixed(2);\n      const lon = (Math.round(clickedPoint.lon / 0.05) * 0.05).toFixed(2);\n\n      if (eventData.event?.ctrlKey) {\n        locationService.partial({ 'var-lat2': lat, 'var-lon2': lon });\n      } else {\n        locationService.partial({ 'var-lat1': lat, 'var-lon1': lon });\n      }\n    }\n  }\n} catch (error) {\n  console.error('Error in map click handler:', error);\n}",
        "resScale": 2,
        "script": "const fields = data.series[0].fields;\n\nconst lats = fields[1].values.toArray();\nconst lons = fields[2].values.toArray();\n\nconst lat1 = parseFloat(variables.lat1.query);\nconst lon1 = parseFloat(variables.lon1.query);\nconst lat2 = parseFloat(variables.lat2.query);\nconst lon2 = parseFloat(variables.lon2.query);\n\n// console.log(variables.lat1.query)\n\nconst traces = [{\n  type: 'scattermapbox',\n  lat: lats,\n  lon: lons,\n  mode: 'markers',\n  marker: {\n    size: 7,\n    color: '#4A90D9',\n    opacity: 0.85,\n  },\n  hoverinfo: 'lat+lon',\n  hoverlabel: { bgcolor: '#333333' }\n}];\n\nif (!isNaN(lat1) && !isNaN(lon1)) {\n  traces.push({\n    type: 'scattermapbox',\n    lat: [lat1],\n    lon: [lon1],\n    mode: 'markers',\n    marker: { size: 10, color: 'gold' },\n    text: [`Point 1: ${lat1}, ${lon1}`],\n    hoverinfo: 'text',\n    hoverlabel: { bgcolor: '#333333' }\n  });\n}\n\nif (!isNaN(lat2) && !isNaN(lon2)) {\n  traces.push({\n    type: 'scattermapbox',\n    lat: [lat2],\n    lon: [lon2],\n    mode: 'markers',\n    marker: { size: 10, color: 'red' },\n    text: [`Point 2: ${lat2}, ${lon2}`],\n    hoverinfo: 'text',\n    hoverlabel: { bgcolor: '#333333' }\n  });\n}\n\nreturn {\n  data: traces,\n  layout: {\n    mapbox: {\n      style: 'open-street-map',\n      center: { lat: 0, lon: 20 },\n      zoom: 2,\n      dragmode: 'zoom'\n    },\n    margin: { t: 0, b: 0, l: 0, r: 0 },\n    paper_bgcolor: 'rgba(0,0,0,0)',\n    plot_bgcolor: 'rgba(0,0,0,0)',\n    showlegend: false\n  },\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true\n  }\n};",
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
          "rawSql": "SELECT station_ids, lat, lon\nFROM \"tahmo_grid_counts/global0_25\"",
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
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 11,
        "x": 0,
        "y": 7
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
          "rawSql": "SELECT\n  *,\n  rh2m * 100 AS rh2m_pct\nFROM \"pairwise_precip/${agg_days}_global0_25_${satellite}_${station}_${region1}\"\nWHERE EXTRACT(MONTH FROM time) IN (${months:csv})\n  AND (\n    NOT ${filter_space:raw}\n    OR ABS(lat - ${lat1}::real) <= 1e-6\n  )\n  AND (\n    NOT ${filter_space:raw}\n    OR ABS(lon - ${lon1}::real) <= 1e-6\n  );\n",
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
        "w": 11,
        "x": 11,
        "y": 7
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
          "rawSql": "SELECT\n  *,\n  rh2m * 100 AS rh2m_pct\nFROM \"pairwise_precip/${agg_days}_global0_25_${satellite}_${station}_${region2}\"\nWHERE EXTRACT(MONTH FROM time) IN (${months:csv})\n  AND (\n    NOT ${filter_space:raw}\n    OR ABS(lat - ${lat2}::real) <= 1e-6\n  )\n  AND (\n    NOT ${filter_space:raw}\n    OR ABS(lon - ${lon2}::real) <= 1e-6\n  );\n",
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
        "type": "datasource",
        "uid": "-- Dashboard --"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 11,
        "x": 0,
        "y": 16
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
        "h": 8,
        "w": 11,
        "x": 11,
        "y": 16
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
          "text": "imerg",
          "value": "imerg"
        },
        "description": "precip satellite data source",
        "label": "Satellite Product",
        "name": "satellite",
        "options": [
          {
            "selected": true,
            "text": "imerg",
            "value": "imerg"
          },
          {
            "selected": false,
            "text": "chirps",
            "value": "chirps"
          }
        ],
        "query": "imerg, chirps",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "10",
          "value": "10"
        },
        "label": "agg_days",
        "name": "agg_days",
        "options": [
          {
            "selected": false,
            "text": "1",
            "value": "1"
          },
          {
            "selected": false,
            "text": "5",
            "value": "5"
          },
          {
            "selected": true,
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
            "4",
            "5",
            "6"
          ],
          "value": [
            "4",
            "5",
            "6"
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
            "selected": true,
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
            "selected": false,
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
          "text": "6.75",
          "value": "6.75"
        },
        "label": "Lat A",
        "name": "lat1",
        "options": [
          {
            "selected": true,
            "text": "6.75",
            "value": "6.75"
          }
        ],
        "query": "6.75",
        "type": "textbox"
      },
      {
        "current": {
          "text": "-1.5",
          "value": "-1.5"
        },
        "label": "Lon A",
        "name": "lon1",
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
        "current": {
          "text": "-1.25",
          "value": "-1.25"
        },
        "label": "Lat B",
        "name": "lat2",
        "options": [
          {
            "selected": true,
            "text": "-1.25",
            "value": "-1.25"
          }
        ],
        "query": "-1.25",
        "type": "textbox"
      },
      {
        "current": {
          "text": "36.75",
          "value": "36.75"
        },
        "label": "Lon B",
        "name": "lon2",
        "options": [
          {
            "selected": true,
            "text": "36.75",
            "value": "36.75"
          }
        ],
        "query": "36.75",
        "type": "textbox"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "humidity",
          "value": "humidity"
        },
        "description": "parameter to color points by",
        "label": "color by",
        "name": "colorby",
        "options": [
          {
            "selected": true,
            "text": "humidity",
            "value": "humidity"
          },
          {
            "selected": false,
            "text": "temperature",
            "value": "temperature"
          },
          {
            "selected": false,
            "text": "admin1",
            "value": "admin1"
          },
          {
            "selected": false,
            "text": "agroecological",
            "value": "agroecological"
          },
          {
            "selected": false,
            "text": "latitude",
            "value": "latitude"
          },
          {
            "selected": false,
            "text": "longitude",
            "value": "longitude"
          },
          {
            "selected": false,
            "text": "location",
            "value": "location"
          }
        ],
        "query": "humidity, temperature, admin1, agroecological, latitude, longitude, location",
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
          "text": "40",
          "value": "40"
        },
        "description": "set limits on all axes",
        "label": "axis limit",
        "name": "axis_lim",
        "options": [
          {
            "selected": true,
            "text": "40",
            "value": "40"
          }
        ],
        "query": "40",
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
          "text": "",
          "value": ""
        },
        "name": "query0",
        "options": [],
        "query": "",
        "refresh": 1,
        "regex": "",
        "type": "query"
      }
    ]
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "Precipitation Scatter Plots",
  "uid": "ffc28h1tj93b4e",
  "version": 1,
  "weekStart": ""
}
