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
        "Battery QC"
      ],
      "targetBlank": false,
      "title": "New link",
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
        "Rain QC"
      ],
      "targetBlank": false,
      "title": "New link",
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
    },
    {
      "asDropdown": false,
      "icon": "external link",
      "includeVars": false,
      "keepTime": false,
      "tags": [
        "Battery Timeseries"
      ],
      "targetBlank": true,
      "title": "Battery Timeseries",
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
        "Precip Timeseries"
      ],
      "targetBlank": true,
      "title": "Precipitation Timeseries",
      "tooltip": "",
      "type": "dashboards",
      "url": ""
    }
  ],
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
        "h": 18,
        "w": 11,
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
        "onclick": "try {\n  const { type: eventType, data: eventData } = event;\n\n  if (eventType === 'click') {\n    const clickedPoint = eventData?.points?.[0];\n    const urlFragment = clickedPoint?.customdata;\n    const pointIndex = clickedPoint?.pointIndex;\n\n    if (urlFragment && pointIndex != null) {\n      const fields = data.series[0].fields;\n      const stationId = fields[0].values.get(pointIndex);  // Station ID\n      const startStr = fields[6].values.get(pointIndex);   // Start time string\n\n      let fromTimestamp = null;\n      const toTimestamp = Date.now();\n\n      if (startStr) {\n        const startDate = new Date(startStr);\n        const sixMonthsAgo = new Date(startDate);\n        sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);\n        fromTimestamp = sixMonthsAgo.getTime();\n      }\n\n      // Fallback to 1 year if no start time\n      const from_time = fromTimestamp || toTimestamp - 1000 * 60 * 60 * 24 * 365;\n\n      // const fullUrl = `d/${urlFragment}?from=${from_time}&to=${toTimestamp}&timezone=utc&var-station=${stationId}`;\n      // window.location.href = fullUrl;\n      const fullUrl = `d/${urlFragment}?from=${from_time}&to=${toTimestamp}&timezone=utc&var-station=${stationId}`;\n      window.open(fullUrl, '_blank');      \n    }\n  }\n} catch (error) {\n  console.error('Error in map click handler:', error);\n}\n",
        "resScale": 2,
        "script": "const fields = data.series[0].fields;\n\nconst stationIds = fields[0].values.toArray();\nconst names = fields[1].values.toArray();\n// skip installation date (fields[2])\nconst lat = fields[3].values.toArray();\nconst lon = fields[4].values.toArray();\n\nconst baseUrl = 'https://your-constant-url.com'; // ← set your URL here\n\nconst tooltips = names.map((name, i) =>\n  `<b>${name || 'Unknown'}</b><br>` +\n  `Station: ${stationIds[i]}`\n);\n\nreturn {\n  data: [{\n    type: 'scattermapbox',\n    lat: lat,\n    lon: lon,\n    mode: 'markers',\n    customdata: stationIds.map(() => baseUrl),\n    marker: {\n      size: 7,\n      color: '#4A90D9',\n      opacity: 0.85,\n    },\n    text: tooltips,\n    hoverinfo: 'text',\n    hoverlabel: {\n      bgcolor: '#333333'\n    }\n  }],\n  layout: {\n    mapbox: {\n      style: 'open-street-map',\n      center: { lat: 0, lon: 20 },\n      zoom: 2,\n      dragmode: 'zoom'\n    },\n    margin: { t: 0, b: 0, l: 0, r: 0 },\n    paper_bgcolor: 'rgba(0,0,0,0)',\n    plot_bgcolor: 'rgba(0,0,0,0)',\n    showlegend: false\n  },\n  config: {\n    responsive: true,\n    displayModeBar: true,\n    scrollZoom: true\n  }\n};",
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
          "rawSql": "SELECT \n  d.code AS \"Station ID\",\n  d.location_name,\n  d.installationdate,\n  d.location_latitude,\n  d.location_longitude\nFROM \n  ${tahmo_deployment_name} d\nLEFT JOIN \n  \"country_codes/\" cc \n  ON d.location_countrycode = cc.country_code\nWHERE \n  d.code || ' - ' || d.location_name IN (${station_id})\n  AND cc.country_name IN (${country_name});",
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
    }
  ],
  "preload": false,
  "refresh": "",
  "schemaVersion": 40,
  "tags": [
    "Home"
  ],
  "templating": {
    "list": [
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
          "text": "e40289e05ff47b91c7710c248e7bd903",
          "value": "e40289e05ff47b91c7710c248e7bd903"
        },
        "definition": "select * from md5('single_station_wideish/TA00003_controlled')",
        "hide": 2,
        "name": "single_station_name",
        "options": [],
        "query": "select * from md5('single_station_wideish/TA00003_controlled')",
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
      }
    ]
  },
  "time": {
    "from": "2020-12-11T09:32:39.669Z",
    "to": "2028-12-09T09:32:39.669Z"
  },
  "timepicker": {
    "hidden": true
  },
  "timezone": "utc",
  "title": "TAHMO Fleet Status Home",
  "uid": "feokoc2whs000d",
  "version": 1,
  "weekStart": ""
}
