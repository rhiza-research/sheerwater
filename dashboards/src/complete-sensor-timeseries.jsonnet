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
        "enable": true,
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
            "insertNulls": 172800000,
            "lineInterpolation": "linear",
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
          "displayName": "Station: ${__field.labels.station}, Sensor: ${__field.labels.sensor}",
          "mappings": [],
          "max": 150,
          "min": 0,
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
                  "fixedColor": "#ff6b35",
                  "mode": "fixed"
                }
              },
              {
                "id": "displayName",
                "value": "IMERG"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "1d Cumulative Rain"
            },
            "properties": [
              {
                "id": "custom.drawStyle",
                "value": "line"
              },
              {
                "id": "custom.pointSize",
                "value": 8
              },
              {
                "id": "custom.lineWidth",
                "value": 2
              },
              {
                "id": "color",
                "value": {
                  "fixedColor": "light-blue",
                  "mode": "fixed"
                }
              },
              {
                "id": "displayName"
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
                  "fixedColor": "#21b460",
                  "mode": "fixed"
                }
              },
              {
                "id": "custom.axisWidth",
                "value": 45
              },
              {
                "id": "displayName",
                "value": "CHIRPS v2"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "1d cumulative drip"
            },
            "properties": [
              {
                "id": "color",
                "value": {
                  "fixedColor": "green",
                  "mode": "fixed"
                }
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 7,
        "w": 24,
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
          "rawSql": "SELECT time, precip as imerg_precip \nFROM \"imerg_tahmo/\" \n  WHERE code = SPLIT_PART('${station:csv}', ',', 1)\n-- WHERE code = '${station:raw}' \n  AND time $__timeFilter() \nORDER BY time ASC",
          "refId": "C",
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
          "rawSql": "SELECT time, precip as chirps_precip \nFROM \"chirps_tahmo/\" \n-- WHERE code = '${station:raw}' \nWHERE code = SPLIT_PART('${station:csv}', ',', 1)\n  AND time $__timeFilter() \nORDER BY time ASC",
          "refId": "D",
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
          "alias": "1d Cumulative Rain $tag_sensor",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "1d"
              ],
              "type": "time"
            },
            {
              "params": [
                "sensor::tag"
              ],
              "type": "tag"
            }
          ],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT sum(\"value\") \nFROM \"controlled\" \nWHERE (\"station\"::tag =~ /^${station:regex}$/ AND \"variable\"::tag = 'pr') \n  AND $timeFilter \nGROUP BY time(1d), \"station\"::tag, \"sensor\"::tag",
          "rawQuery": true,
          "refId": "B",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "sum"
              }
            ]
          ],
          "tags": [
            {
              "key": "station::tag",
              "operator": "=~",
              "value": "/^$station$/"
            },
            {
              "condition": "AND",
              "key": "variable::tag",
              "operator": "=",
              "value": "pr"
            }
          ]
        },
        {
          "alias": "1d Dual Station (Tip count)",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "1d"
              ],
              "type": "time"
            }
          ],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT sum(\"value\")/2.9411 \nFROM \"controlled\" \nWHERE (\"station\"::tag =~ /^${station:regex}$/ AND \"variable\"::tag = 'pt') \n  AND $timeFilter \nGROUP BY time(1d), \"station\"::tag, \"sensor\"::tag",
          "rawQuery": true,
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "sum"
              }
            ]
          ],
          "tags": [
            {
              "key": "station::tag",
              "operator": "=~",
              "value": "/^$station$/"
            },
            {
              "condition": "AND",
              "key": "variable::tag",
              "operator": "=",
              "value": "pr"
            }
          ]
        },
        {
          "alias": "1d Dual Station (Drip count)",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "1d"
              ],
              "type": "time"
            }
          ],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT sum(\"value\")/58.823 \nFROM \"controlled\" \nWHERE (\"station\"::tag =~ /^${station:regex}$/ AND \"variable\"::tag = 'pd') \n  AND $timeFilter \nGROUP BY time(1d), \"station\"::tag, \"sensor\"::tag",
          "rawQuery": true,
          "refId": "E",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "sum"
              }
            ]
          ],
          "tags": [
            {
              "key": "station::tag",
              "operator": "=~",
              "value": "/^$station$/"
            },
            {
              "condition": "AND",
              "key": "variable::tag",
              "operator": "=",
              "value": "pr"
            }
          ]
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
          "rawSql": "-- SELECT \n--   \"start\" AS time,\n--   \"end\" AS timeEnd,\n--   \"station_id\",\n--   'Bad rainfall' as \"text\"\n-- FROM \"classifier_annotation/rainfall_final\"\n-- WHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") \n--   AND \"station_id\" IN (${station:singlequote})",
          "refId": "F",
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
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "influxdb",
        "uid": "eepjuov1zfi0wb"
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
            "axisLabel": "",
            "axisPlacement": "auto",
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
            "insertNulls": 432000000,
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": 3600000,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
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
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "Temperature"
            },
            "properties": [
              {
                "id": "unit",
                "value": "none"
              },
              {
                "id": "custom.axisLabel",
                "value": "Degree C"
              },
              {
                "id": "custom.axisPlacement",
                "value": "left"
              },
              {
                "id": "custom.axisWidth",
                "value": 30
              },
              {
                "id": "displayName",
                "value": "Temperature: ${__field.labels.station}"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Humidity"
            },
            "properties": [
              {
                "id": "unit",
                "value": "none"
              },
              {
                "id": "custom.axisLabel",
                "value": "Relative Humidity"
              },
              {
                "id": "custom.axisPlacement",
                "value": "left"
              },
              {
                "id": "custom.axisWidth",
                "value": 30
              },
              {
                "id": "displayName",
                "value": "Relative Humidity: ${__field.labels.station}"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Pressure"
            },
            "properties": [
              {
                "id": "unit",
                "value": "none"
              },
              {
                "id": "custom.axisLabel",
                "value": "Pressure (kPa)"
              },
              {
                "id": "custom.axisPlacement",
                "value": "left"
              },
              {
                "id": "custom.axisWidth",
                "value": 30
              },
              {
                "id": "displayName",
                "value": "Pressure: ${__field.labels.station}"
              }
            ]
          },
          {
            "matcher": {
              "id": "byRegexp",
              "options": ""
            },
            "properties": [
              {
                "id": "displayName"
              }
            ]
          },
          {
            "__systemRef": "hideSeriesFrom",
            "matcher": {
              "id": "byNames",
              "options": {
                "mode": "exclude",
                "names": [
                  "Relative Humidity: TA00190",
                  "Relative Humidity: TA00719"
                ],
                "prefix": "All except:",
                "readOnly": true
              }
            },
            "properties": [
              {
                "id": "custom.hideFrom",
                "value": {
                  "legend": false,
                  "tooltip": false,
                  "viz": true
                }
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 7,
        "w": 24,
        "x": 0,
        "y": 7
      },
      "id": 7,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "hideZeros": false,
          "mode": "multi",
          "sort": "none"
        }
      },
      "pluginVersion": "11.5.0-pre",
      "targets": [
        {
          "alias": "Pressure",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT mean(\"value\") \nFROM \"controlled\" \nWHERE (\"station\"::tag =~ /^${station:regex}$/ AND \"variable\"::tag = 'ap') \n  AND $timeFilter \nGROUP BY time($__interval), \"station\"::tag fill(null)",
          "rawQuery": true,
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": [
            {
              "key": "station::tag",
              "operator": "=~",
              "value": "/^$station$/"
            },
            {
              "condition": "AND",
              "key": "variable::tag",
              "operator": "=",
              "value": "ap"
            }
          ]
        },
        {
          "alias": "Temperature",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT mean(\"value\") \nFROM \"controlled\" \nWHERE (\"station\"::tag =~ /^${station:regex}$/ AND \"variable\"::tag = 'te') \n  AND $timeFilter \nGROUP BY time($__interval), \"station\"::tag fill(null)",
          "rawQuery": true,
          "refId": "B",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": [
            {
              "key": "station::tag",
              "operator": "=~",
              "value": "/^$station$/"
            },
            {
              "condition": "AND",
              "key": "variable::tag",
              "operator": "=",
              "value": "te"
            }
          ]
        },
        {
          "alias": "Humidity",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT mean(\"value\") \nFROM \"controlled\" \nWHERE (\"station\"::tag =~ /^${station:regex}$/ AND \"variable\"::tag = 'rh') \n  AND $timeFilter \nGROUP BY time($__interval), \"station\"::tag fill(null)",
          "rawQuery": true,
          "refId": "C",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": [
            {
              "key": "station::tag",
              "operator": "=~",
              "value": "/^$station$/"
            },
            {
              "condition": "AND",
              "key": "variable::tag",
              "operator": "=",
              "value": "rh"
            }
          ]
        }
      ],
      "title": "Temperature, humidity, pressure",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "influxdb",
        "uid": "eepjuov1zfi0wb"
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
            "axisLabel": "",
            "axisPlacement": "auto",
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
            "insertNulls": 432000000,
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": 3600000,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
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
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "Wind speed"
            },
            "properties": [
              {
                "id": "unit",
                "value": "none"
              },
              {
                "id": "custom.axisLabel",
                "value": "Wind Speed (m/s)"
              },
              {
                "id": "custom.axisPlacement",
                "value": "left"
              },
              {
                "id": "custom.axisWidth",
                "value": 45
              },
              {
                "id": "max",
                "value": 7
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Wind direction"
            },
            "properties": [
              {
                "id": "unit",
                "value": "none"
              },
              {
                "id": "custom.axisLabel",
                "value": "Wind Direction (Degree)"
              },
              {
                "id": "custom.axisPlacement",
                "value": "left"
              },
              {
                "id": "custom.axisWidth",
                "value": 45
              },
              {
                "id": "custom.drawStyle",
                "value": "line"
              },
              {
                "id": "color",
                "value": {
                  "fixedColor": "#f28f0c",
                  "mode": "fixed"
                }
              },
              {
                "id": "custom.lineStyle",
                "value": {
                  "dash": [
                    0,
                    10
                  ],
                  "fill": "dot"
                }
              },
              {
                "id": "max"
              },
              {
                "id": "custom.lineWidth",
                "value": 2
              }
            ]
          },
          {
            "matcher": {
              "id": "byRegexp",
              "options": "/.*/"
            },
            "properties": [
              {
                "id": "displayName",
                "value": "Station: ${__field.labels.station}"
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 8,
        "w": 24,
        "x": 0,
        "y": 14
      },
      "id": 8,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "hideZeros": false,
          "mode": "multi",
          "sort": "none"
        }
      },
      "pluginVersion": "11.5.0-pre",
      "targets": [
        {
          "alias": "Wind speed",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT mean(\"value\") \nFROM \"controlled\" \nWHERE (\"station\"::tag =~ /^${station:regex}$/ AND \"variable\"::tag = 'ws') \n  AND $timeFilter \nGROUP BY time($__interval), \"station\"::tag fill(null)",
          "rawQuery": true,
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": [
            {
              "key": "variable::tag",
              "operator": "=",
              "value": "ws"
            },
            {
              "condition": "AND",
              "key": "station::tag",
              "operator": "=~",
              "value": "/^$station$/"
            }
          ]
        },
        {
          "alias": "Wind direction",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT mean(\"value\") \nFROM \"controlled\" \nWHERE (\"station\"::tag =~ /^${station:regex}$/ AND \"variable\"::tag = 'wd') \n  AND $timeFilter \nGROUP BY time($__interval), \"station\"::tag fill(null)",
          "rawQuery": true,
          "refId": "B",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": [
            {
              "key": "variable::tag",
              "operator": "=",
              "value": "wd"
            },
            {
              "condition": "AND",
              "key": "station::tag",
              "operator": "=~",
              "value": "/^$station$/"
            }
          ]
        }
      ],
      "title": "Wind speed and direction",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "influxdb",
        "uid": "eepjuov1zfi0wb"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "dark-yellow",
            "mode": "fixed"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "Irradiance (W/m^2)",
            "axisPlacement": "auto",
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
            "insertNulls": 432000000,
            "lineInterpolation": "linear",
            "lineWidth": 0.5,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": 3600000,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "displayName": "Station: ${__field.labels.station}",
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "solar radiation"
            },
            "properties": [
              {
                "id": "custom.axisWidth",
                "value": 90
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 6,
        "w": 24,
        "x": 0,
        "y": 22
      },
      "id": 9,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "hideZeros": false,
          "mode": "multi",
          "sort": "none"
        }
      },
      "pluginVersion": "11.5.0-pre",
      "targets": [
        {
          "alias": "solar radiation",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [],
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT \"value\" \nFROM \"controlled\" \nWHERE (\"station\"::tag =~ /^${station:regex}$/ AND \"variable\"::tag = 'ra') \n  AND $timeFilter \nGROUP BY \"station\"::tag",
          "rawQuery": true,
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "field"
              }
            ]
          ],
          "tags": [
            {
              "key": "station::tag",
              "operator": "=~",
              "value": "/^$station$/"
            },
            {
              "condition": "AND",
              "key": "variable::tag",
              "operator": "=",
              "value": "ra"
            }
          ]
        }
      ],
      "title": "Solar Radiation",
      "type": "timeseries"
    }
  ],
  "preload": false,
  "refresh": "",
  "schemaVersion": 40,
  "tags": [
    "Other timeseries"
  ],
  "templating": {
    "list": [
      {
        "current": {
          "text": "6.75",
          "value": "6.75"
        },
        "label": "Latitude",
        "name": "lat",
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
        "label": "Longitude",
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
        "allowCustomValue": true,
        "current": {
          "text": [
            "TA00847",
            "TA00845",
            "TA00844",
            "TA00843",
            "TA00842",
            "TA00757",
            "TA00617",
            "TA00393",
            "TA00039",
            "TA00044",
            "TA00279"
          ],
          "value": [
            "TA00847",
            "TA00845",
            "TA00844",
            "TA00843",
            "TA00842",
            "TA00757",
            "TA00617",
            "TA00393",
            "TA00039",
            "TA00044",
            "TA00279"
          ]
        },
        "definition": "SELECT station_ids\nFROM \"tahmo_grid_counts/global0_25\"\nWHERE lat = ${lat} AND lon = ${lon}",
        "includeAll": true,
        "label": "Station",
        "multi": true,
        "name": "station",
        "options": [],
        "query": "SELECT station_ids\nFROM \"tahmo_grid_counts/global0_25\"\nWHERE lat = ${lat} AND lon = ${lon}",
        "refresh": 1,
        "regex": "",
        "type": "query"
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
          "text": "TA00002 - Benso SHS",
          "value": "TA00002"
        },
        "definition": "SELECT \n  code || ' - ' || location_name AS __text, \n  code AS __value \nFROM \n  ${tahmo_deployment_name}",
        "hide": 2,
        "label": "Station",
        "name": "all_station",
        "options": [],
        "query": "SELECT \n  code || ' - ' || location_name AS __text, \n  code AS __value \nFROM \n  ${tahmo_deployment_name}",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "ec6142179608733b2a6d10218590cf61",
          "value": "ec6142179608733b2a6d10218590cf61"
        },
        "definition": "select * from 'tahmo_station/${station}_controlled'",
        "hide": 2,
        "name": "station_table_name",
        "options": [],
        "query": "select * from 'tahmo_station/${station}_controlled'",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "2bd5bb18c0f0a80adf62831278519769",
          "value": "2bd5bb18c0f0a80adf62831278519769"
        },
        "definition": "select * from md5('battery_cycle_periods_all_stations/')",
        "hide": 2,
        "name": "batt_zero_name",
        "options": [],
        "query": "select * from md5('battery_cycle_periods_all_stations/')",
        "refresh": 1,
        "regex": "",
        "type": "query"
      }
    ]
  },
  "time": {
    "from": "2024-11-26T07:58:20.206Z",
    "to": "2025-12-06T07:32:37.349Z"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "Complete Sensor Timeseries",
  "uid": "deokdv0waovlsc",
  "version": 1,
  "weekStart": ""
}
