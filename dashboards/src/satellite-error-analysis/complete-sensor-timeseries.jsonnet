local grid_size_sql = importstr './assets/grid_size.sql';

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
      },
      {
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "enable": false,
        "hide": false,
        "iconColor": "green",
        "mappings": {
          "tags": {
            "source": "field",
            "value": "author"
          },
          "text": {
            "source": "field",
            "value": "text"
          },
          "time": {
            "source": "field",
            "value": "time"
          }
        },
        "name": "Issues and Comments",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT time, text, author \nFROM \"issues_and_comments_for_display/\" \nWHERE station_id IN (${station:singlequote})",
          "refId": "Anno",
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
      },
      {
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "enable": false,
        "hide": false,
        "iconColor": "red",
        "name": "Rainfall flagged",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  \"station_id\" || ': Bad rainfall' as \"text\"\nFROM \"classifier_annotation/rainfall_final\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") \n  AND \"station_id\" IN (${station:singlequote})",
          "refId": "Anno",
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
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "Daily Precip (mm)",
            "axisPlacement": "left",
            "axisSoftMax": 250,
            "axisSoftMin": 3,
            "axisWidth": 90,
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "drawStyle": "line",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": 86400000,
            "lineInterpolation": "linear",
            "lineStyle": {
              "fill": "solid"
            },
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "max": 150,
          "min": -2,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          }
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "imerg_precip"
            },
            "properties": [
              {
                "id": "custom.drawStyle",
                "value": "line"
              },
              {
                "id": "custom.barAlignment",
                "value": 0
              },
              {
                "id": "custom.pointSize",
                "value": 5
              },
              {
                "id": "color",
                "value": {
                  "fixedColor": "#b044cc",
                  "mode": "fixed"
                }
              },
              {
                "id": "displayName",
                "value": "IMERG"
              },
              {
                "id": "custom.lineWidth",
                "value": 1
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "chirps_precip"
            },
            "properties": [
              {
                "id": "custom.drawStyle",
                "value": "line"
              },
              {
                "id": "custom.pointSize",
                "value": 5
              },
              {
                "id": "custom.axisWidth",
                "value": 30
              },
              {
                "id": "color",
                "value": {
                  "fixedColor": "#2cb5a0",
                  "mode": "fixed"
                }
              },
              {
                "id": "custom.axisWidth",
                "value": 45
              },
              {
                "id": "displayName",
                "value": "CHIRPS v3"
              },
              {
                "id": "custom.lineWidth",
                "value": 1
              },
              {
                "id": "custom.fillOpacity",
                "value": 0
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "roa_precip"
            },
            "properties": [
              {
                "id": "color",
                "value": {
                  "fixedColor": "#e8409c",
                  "mode": "fixed"
                }
              },
              {
                "id": "displayName",
                "value": "Rain over Africa"
              }
            ]
          },
          {
            "matcher": {
              "id": "byFrameRefID",
              "options": "TAHMO"
            },
            "properties": [
              {
                "id": "color",
                "value": {
                  "fixedColor": "blue",
                  "mode": "fixed"
                }
              },
              {
                "id": "custom.fillOpacity",
                "value": 1
              },
              {
                "id": "custom.drawStyle",
                "value": "line"
              },
              {
                "id": "custom.showPoints",
                "value": "never"
              },
              {
                "id": "custom.lineWidth",
                "value": 1
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "smap_soil_moisture"
            },
            "properties": [
              {
                "id": "custom.axisPlacement",
                "value": "right"
              },
              {
                "id": "custom.scaleDistribution",
                "value": {
                  "type": "linear"
                }
              },
              {
                "id": "custom.axisSoftMax",
                "value": 0.5
              },
              {
                "id": "custom.axisLabel",
                "value": "Soil Moisture"
              },
              {
                "id": "custom.axisSoftMin",
                "value": 0
              },
              {
                "id": "color",
                "value": {
                  "fixedColor": "#d28602",
                  "mode": "fixed"
                }
              },
              {
                "id": "custom.insertNulls",
                "value": 172800000
              },
              {
                "id": "displayName",
                "value": "Soil Moisture"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Event Threshold"
            },
            "properties": [
              {
                "id": "custom.fillOpacity",
                "value": 7
              },
              {
                "id": "color",
                "value": {
                  "mode": "fixed"
                }
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 24,
        "w": 18,
        "x": 0,
        "y": 0
      },
      "id": 13,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "hideZeros": false,
          "maxWidth": -4,
          "mode": "multi",
          "sort": "none"
        }
      },
      "pluginVersion": "11.5.0-pre",
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
          "rawSql": "-- SELECT \n--   time, \n--   AVG(precip) OVER (\n--     PARTITION BY station_id\n--     ORDER BY time\n--     ROWS BETWEEN (${agg_days} - 1) PRECEDING AND CURRENT ROW\n--   ) AS \"TAHMO\", \n--   station_id AS station\n-- FROM \"data_at_stations/1_tahmo_source_stations_precip\"\n-- WHERE time $__timeFilter()\n--   AND ABS(lat - (${lat:raw})::real) <= ${grid_size}\n--   AND ABS(lon - (${lon:raw})::real) <= ${grid_size}\n-- ORDER BY time ASC\nSELECT \n  time, \n  AVG(AVG(precip)) OVER (\n    ORDER BY time\n    ROWS BETWEEN (${agg_days} - 1) PRECEDING AND CURRENT ROW\n  ) AS \"TAHMO\"\nFROM \"data_at_stations/1_tahmo_source_stations_precip\"\nWHERE time $__timeFilter()\n  AND ABS(lat - (${lat:raw})::real) <= ${grid_size}\n  AND ABS(lon - (${lon:raw})::real) <= ${grid_size}\nGROUP BY time\nORDER BY time ASC",
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
          "rawSql": "SELECT time, AVG(AVG(precip)) OVER (\n    ORDER BY time\n    ROWS BETWEEN (${agg_days} - 1) PRECEDING AND CURRENT ROW\n  ) AS imerg_precip\nFROM \"data_at_stations/1_imerg_final_${grid}_tahmo_precip\"\nWHERE time $__timeFilter()\n  AND ABS(lat - (${lat:raw})::real) <= ${grid_size}\n  AND ABS(lon - (${lon:raw})::real) <= ${grid_size}\nGROUP BY time\nORDER BY time ASC",
          "refId": "IMERG",
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
          "rawSql": "SELECT time, AVG(AVG(precip)) OVER (\n    ORDER BY time\n    ROWS BETWEEN (${agg_days} - 1) PRECEDING AND CURRENT ROW\n  ) AS chirps_precip\nFROM \"data_at_stations/1_chirps_v3_${grid}_tahmo_precip\"\nWHERE time $__timeFilter()\n  AND ABS(lat - (${lat:raw})::real) <= ${grid_size}\n  AND ABS(lon - (${lon:raw})::real) <= ${grid_size}\nGROUP BY time\nORDER BY time ASC",
          "refId": "CHIRPS",
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
          "rawSql": "SELECT time, AVG(AVG(precip)) OVER (\n    ORDER BY time\n    ROWS BETWEEN (${agg_days} - 1) PRECEDING AND CURRENT ROW\n  ) AS roa_precip\nFROM \"data_at_stations/1_rain_over_africa_${grid}_tahmo_precip\"\nWHERE time $__timeFilter()\n  AND ABS(lat - (${lat:raw})::real) <= ${grid_size}\n  AND ABS(lon - (${lon:raw})::real) <= ${grid_size}\nGROUP BY time\nORDER BY time ASC",
          "refId": "ROA",
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
          "rawSql": "SELECT time, AVG(AVG(soil_moisture)) OVER (\n    ORDER BY time\n    ROWS BETWEEN (${agg_days} - 1) PRECEDING AND CURRENT ROW\n  ) AS smap_soil_moisture\nFROM \"data_at_stations/1_smap_l3_source_tahmo_soil_moisture\"\nWHERE time $__timeFilter()\n  AND ABS(lat - (${lat:raw})::real) <= ${grid_size}\n  AND ABS(lon - (${lon:raw})::real) <= ${grid_size}\nGROUP BY time\nORDER BY time ASC",
          "refId": "SMAP",
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
          "rawSql": "SELECT \n  generate_series(\n    $__timeFrom()::timestamptz,\n    $__timeTo()::timestamptz,\n    '1 day'::interval\n  ) AS time,\n  ${event} / ${agg_days} AS \"Event Threshold\"",
          "refId": "Threshhold",
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
          "rawSql": "",
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
      "type": "timeseries"
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
        "y": 0
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
        "h": 20,
        "w": 6,
        "x": 18,
        "y": 4
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
          "text": "5.75",
          "value": "5.75"
        },
        "label": "Latitude",
        "name": "lat",
        "options": [
          {
            "selected": true,
            "text": "5.75",
            "value": "5.75"
          }
        ],
        "query": "5.75",
        "type": "textbox"
      },
      {
        "current": {
          "text": "-0.25",
          "value": "-0.25"
        },
        "label": "Longitude",
        "name": "lon",
        "options": [
          {
            "selected": true,
            "text": "-0.25",
            "value": "-0.25"
          }
        ],
        "query": "-0.25",
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
          "text": "global1_5",
          "value": "global1_5"
        },
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
          "text": "0.750001",
          "value": "0.750001"
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
          "text": "10",
          "value": "10"
        },
        "label": "Agg Days",
        "name": "agg_days",
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
          "text": "2.27",
          "value": "2.27"
        },
        "hide": 2,
        "name": "map_zoom",
        "options": [
          {
            "selected": true,
            "text": "2.27",
            "value": "2.27"
          }
        ],
        "query": "2.27",
        "type": "textbox"
      },
      {
        "current": {
          "text": "-10.3586",
          "value": "-10.3586"
        },
        "hide": 2,
        "name": "map_center_lat",
        "options": [
          {
            "selected": true,
            "text": "-10.3586",
            "value": "-10.3586"
          }
        ],
        "query": "-10.3586",
        "type": "textbox"
      },
      {
        "current": {
          "text": "16.0592",
          "value": "16.0592"
        },
        "description": "",
        "hide": 2,
        "name": "map_center_lon",
        "options": [
          {
            "selected": true,
            "text": "16.0592",
            "value": "16.0592"
          }
        ],
        "query": "16.0592",
        "type": "textbox"
      }
    ]
  },
  "time": {
    "from": "2013-09-11T23:39:20.768Z",
    "to": "2033-09-10T23:39:20.768Z"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "Complete Sensor Timeseries",
  "uid": "deokdv0waovlsc",
  "version": 1,
  "weekStart": ""
}
