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
          "uid": "cegueq2crd3wge"
        },
        "enable": false,
        "hide": false,
        "iconColor": "#afe02f63",
        "mappings": {
          "text": {
            "source": "field",
            "value": "firmware_version"
          },
          "time": {
            "source": "field",
            "value": "start"
          },
          "timeEnd": {
            "source": "field",
            "value": "end"
          },
          "title": {
            "source": "field",
            "value": "Firmware version"
          }
        },
        "name": "Firmware version",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "select \"start\", \"end\", 'Firmware version: ' || firmware_version as \"firmware_version\" from \"tahmo_station_firmware_versions/${station:raw}\" WHERE firmware_version = '${firmware_version:raw}'",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": false,
        "hide": false,
        "iconColor": "#2fa9e069",
        "mappings": {
          "text": {
            "source": "field",
            "value": "hardware_version"
          },
          "time": {
            "source": "field",
            "value": "start"
          },
          "timeEnd": {
            "source": "field",
            "value": "end"
          },
          "title": {
            "source": "field",
            "value": "logger_version"
          }
        },
        "name": "Hardware version",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "select \"start\", \"end\", 'Hardware version: ' || logger_version || '/' || logger_id as \"hardware_version\" from \"tahmo_station_hardware_versions/${station:raw}\" WHERE logger_version = '${logger_version:raw}'",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": true,
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
          "rawSql": "select time, text, author from \"issues_and_comments_for_display/\" where station_id = '${station}'",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": false,
        "filter": {
          "exclude": false,
          "ids": [
            7
          ]
        },
        "hide": true,
        "iconColor": "orange",
        "name": "TAHMO QC: Humidity Suspect",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Suspect humidity QC' as \"text\"\nFROM \"tahmo_qc_flags_all_stations/\"\nWHERE($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station}' AND \"qc_sensor\" = 'humidity_quality_tahmo_suspect'",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": false,
        "filter": {
          "exclude": false,
          "ids": [
            7
          ]
        },
        "hide": true,
        "iconColor": "red",
        "name": "TAHMO QC: Humidity Severe",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "-- SELECT \n--   \"start\" AS time,\n--   \"end\" AS timeEnd,\n--   'Severe Humidity QC' as \"text\"\n-- FROM \"tahmo_qc_flags/${station}\" \n-- WHERE $__timeFilter(start) AND \"qc_sensor\" = 'humidity_quality_tahmo_severe'\nSELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Severe Humidity QC' as \"text\"\nFROM \"tahmo_qc_flags_all_stations/\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station}' AND \"qc_sensor\" = 'humidity_quality_tahmo_severe'",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": false,
        "filter": {
          "exclude": false,
          "ids": [
            7
          ]
        },
        "hide": true,
        "iconColor": "red",
        "name": "TAHMO QC: Pressure Severe",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "-- SELECT \n--   \"start\" AS time,\n--   \"end\" AS timeEnd,\n--   'Severe Pressure QC' as \"text\"\n-- FROM \"tahmo_qc_flags/${station}\" \n-- WHERE $__timeFilter(start) AND \"qc_sensor\" = 'pressure_quality_tahmo_severe'\nSELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Severe Pressure QC' as \"text\"\nFROM \"tahmo_qc_flags_all_stations/\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station}' AND \"qc_sensor\" = 'pressure_quality_tahmo_severe'",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": false,
        "hide": true,
        "iconColor": "orange",
        "name": "TAHMO QC: Pressure Suspect",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "-- SELECT \n--   \"start\" AS time,\n--   \"end\" AS timeEnd,\n--   'Suspect Pressure QC' as \"text\"\n-- FROM \"tahmo_qc_flags/${station}\" \n-- WHERE $__timeFilter(start) AND \"qc_sensor\" = 'pressure_quality_tahmo_suspect'\nSELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Suspect Pressure QC' as \"text\"\nFROM \"tahmo_qc_flags_all_stations/\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station}' AND \"qc_sensor\" = 'pressure_quality_tahmo_suspect'",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": false,
        "filter": {
          "exclude": false,
          "ids": [
            8
          ]
        },
        "hide": true,
        "iconColor": "red",
        "name": "TAHMO QC: Wind Severe",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "-- SELECT \n--   \"start\" AS time,\n--   \"end\" AS timeEnd,\n--   'Severe Radiation QC' as \"text\"\n-- FROM \"tahmo_qc_flags/${station}\" \n-- WHERE $__timeFilter(start) AND \"qc_sensor\" = 'solar_radiation_quality_tahmo_severe'\nSELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Wind Speed QC' as \"text\"\nFROM \"tahmo_qc_flags_all_stations/\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"qc_sensor\" = 'wind_speed_quality_tahmo_severe' AND \"station_id\" = '${station}' ",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": false,
        "filter": {
          "exclude": false,
          "ids": [
            8
          ]
        },
        "hide": true,
        "iconColor": "red",
        "name": "TAHMO QC: Wind direction Severe",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "-- SELECT \n--   \"start\" AS time,\n--   \"end\" AS timeEnd,\n--   'Severe Radiation QC' as \"text\"\n-- FROM \"tahmo_qc_flags/${station}\" \n-- WHERE $__timeFilter(start) AND \"qc_sensor\" = 'solar_radiation_quality_tahmo_severe'\nSELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Wind Direction QC' as \"text\"\nFROM \"tahmo_qc_flags_all_stations/\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"qc_sensor\" = 'wind_direction_quality_tahmo_severe' AND \"station_id\" = '${station}' ",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": true,
        "filter": {
          "exclude": false,
          "ids": [
            9
          ]
        },
        "hide": false,
        "iconColor": "red",
        "name": "TAHMO QC: Solar radiation Severe",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "-- SELECT \n--   \"start\" AS time,\n--   \"end\" AS timeEnd,\n--   'Severe Radiation QC' as \"text\"\n-- FROM \"tahmo_qc_flags/${station}\" \n-- WHERE $__timeFilter(start) AND \"qc_sensor\" = 'solar_radiation_quality_tahmo_severe'\nSELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Solar QC' as \"text\"\nFROM \"tahmo_qc_flags_all_stations/\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"qc_sensor\" = 'solar_radiation_quality_tahmo_severe' AND \"station_id\" = '${station}' ",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": true,
        "filter": {
          "exclude": false,
          "ids": [
            7
          ]
        },
        "hide": false,
        "iconColor": "yellow",
        "name": "Storm period",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "-- SELECT \n--   \"start\" AS time,\n--   \"end\" AS timeEnd,\n--   'Stormy no rain' as \"text\"\n-- FROM \"rainfall_stormy/TA00108\"\n-- WHERE $__timeFilter(start)\nSELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Stormy no rain' as \"text\"\nFROM \"classifier_annotation/rainfall_bad_stormy\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station}'",
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
          "uid": "cegueq2crd3wge"
        },
        "enable": true,
        "filter": {
          "exclude": false,
          "ids": [
            10
          ]
        },
        "hide": false,
        "iconColor": "purple",
        "name": "Dripping clogged",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Dripping clog' as \"text\"\nFROM \"classifier_annotation/dripping_clog\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station}'",
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
                "value": 26
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
          }
        ]
      },
      "gridPos": {
        "h": 8,
        "w": 24,
        "x": 0,
        "y": 7
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
            "fixedColor": "semi-dark-yellow",
            "mode": "thresholds",
            "seriesBy": "last"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "Tilt degrees",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "drawStyle": "line",
            "fillOpacity": 0,
            "gradientMode": "scheme",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": 86400000,
            "lineInterpolation": "smooth",
            "lineStyle": {
              "fill": "solid"
            },
            "lineWidth": 2,
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
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "red",
                "value": null
              },
              {
                "color": "red",
                "value": -100
              },
              {
                "color": "green",
                "value": -3
              },
              {
                "color": "green",
                "value": 0
              },
              {
                "color": "red",
                "value": 3
              }
            ]
          }
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "Tilt Y"
            },
            "properties": [
              {
                "id": "custom.drawStyle",
                "value": "line"
              },
              {
                "id": "custom.pointSize",
                "value": 13
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
              "options": "Tilt X"
            },
            "properties": [
              {
                "id": "custom.drawStyle",
                "value": "line"
              },
              {
                "id": "custom.pointSize",
                "value": 13
              },
              {
                "id": "custom.lineWidth",
                "value": 1
              },
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
        "y": 15
      },
      "id": 12,
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
          "alias": "Tilt X",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [],
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
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
              "value": "tx"
            }
          ]
        },
        {
          "alias": "Tilt Y",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "refId": "B",
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
              "value": "ty"
            }
          ]
        }
      ],
      "title": "Station Tilt",
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
        "y": 21
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
    },
    {
      "datasource": {
        "type": "influxdb",
        "uid": "eepjuov1zfi0wb"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "blue",
            "mode": "fixed"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "Instant Precip (mm)",
            "axisPlacement": "left",
            "axisWidth": 3,
            "barAlignment": 0,
            "barWidthFactor": 0.2,
            "drawStyle": "line",
            "fillOpacity": 1,
            "gradientMode": "hue",
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
            "lineWidth": 0.5,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
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
          },
          "unit": "none"
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "precipitation"
            },
            "properties": [
              {
                "id": "unit",
                "value": "none"
              },
              {
                "id": "custom.axisLabel",
                "value": "Precipitation (mm)"
              },
              {
                "id": "max",
                "value": 0.1
              },
              {
                "id": "custom.axisWidth",
                "value": 90
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 7,
        "w": 24,
        "x": 0,
        "y": 27
      },
      "id": 10,
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
          "alias": "precipitation",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [],
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
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
              "value": "pr"
            }
          ]
        }
      ],
      "title": "Precipitation Drip Clog",
      "type": "timeseries"
    },
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
                  "fixedColor": "super-light-orange",
                  "mode": "fixed"
                }
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "1d cumulative precipitation"
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
                "value": 90
              },
              {
                "id": "color",
                "value": {
                  "fixedColor": "super-light-red",
                  "mode": "fixed"
                }
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 6,
        "w": 24,
        "x": 0,
        "y": 34
      },
      "id": 11,
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
          "alias": "1d cumulative precipitation",
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
                "null"
              ],
              "type": "fill"
            }
          ],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
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
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "cegueq2crd3wge"
          },
          "editorMode": "code",
          "format": "table",
          "hide": false,
          "rawQuery": true,
          "rawSql": "select time, precip as imerg_precip \nfrom \"imerg_tahmo/\" \nwhere code = '${station}' AND time $__timeFilter() order by time asc",
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
            "uid": "cegueq2crd3wge"
          },
          "editorMode": "code",
          "format": "table",
          "hide": false,
          "rawQuery": true,
          "rawSql": "select time, precip as chirps_precip \nfrom \"chirps_tahmo/\" \nwhere code = '${station}' AND time $__timeFilter() order by time asc",
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
        }
      ],
      "title": "Daily Precipitation vs Satellites",
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
          "text": "TA00101 - Unimaid WS2",
          "value": "TA00101"
        },
        "definition": "SELECT \n  code || ' - ' || location_name AS __text, \n  code AS __value \nFROM \n  ${tahmo_deployment_name}",
        "label": "Station",
        "name": "station",
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
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "2.03",
          "value": "2.03"
        },
        "definition": "select firmware_version from \"tahmo_station_firmware_versions/${station:raw}\" where $__timeTo() > \"start\" AND $__timeFrom() < \"end\"",
        "description": "Firmware version in the selected time period",
        "label": "Firmware Version",
        "name": "firmware_version",
        "options": [],
        "query": "select firmware_version from \"tahmo_station_firmware_versions/${station:raw}\" where $__timeTo() > \"start\" AND $__timeFrom() < \"end\"",
        "refresh": 2,
        "regex": "",
        "sort": 4,
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "EM60G",
          "value": "EM60G"
        },
        "definition": "select logger_version from \"tahmo_station_hardware_versions/${station:raw}\" where $__timeTo() > \"start\" AND $__timeFrom() < \"end\"",
        "description": "Logger version in the selected time period",
        "label": "Hardware Version",
        "name": "logger_version",
        "options": [],
        "query": "select logger_version from \"tahmo_station_hardware_versions/${station:raw}\" where $__timeTo() > \"start\" AND $__timeFrom() < \"end\"",
        "refresh": 2,
        "regex": "",
        "type": "query"
      }
    ]
  },
  "time": {
    "from": "2016-11-29T10:19:35.961Z",
    "to": "2025-09-26T00:23:35.236Z"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "Complete Sensor Timeseries",
  "uid": "deokdv0waovlsc",
  "version": 1,
  "weekStart": ""
}
