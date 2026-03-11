{
  "annotations": {
    "list": [
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
        "filter": {
          "exclude": false,
          "ids": [
            2,
            4
          ]
        },
        "hide": false,
        "iconColor": "red",
        "name": "TAHMO QC: Precip Severe",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Severe Precip QC' as \"text\"\nFROM \"tahmo_qc_flags_all_stations/\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station:raw}' AND \"qc_sensor\" IN ('precipitation_1_quality_tahmo_severe', 'precipitation_2_quality_tahmo_severe')",
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
            2,
            4
          ]
        },
        "hide": true,
        "iconColor": "orange",
        "name": "TAHMO QC: Precip Suspect",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "-- SELECT \n--   \"start\" AS time,\n--   \"end\" AS timeEnd,\n--   'Suspect Precip QC' as \"text\"\n-- FROM \"tahmo_qc_flags/${station}\" \n-- WHERE $__timeFilter(start) AND \"qc_sensor\" = 'precipitation_1_quality_tahmo_suspect'\nSELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Suspect Precip QC' as \"text\"\nFROM \"tahmo_qc_flags_all_stations/\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station:raw}' AND \"qc_sensor\" IN ('precipitation_1_quality_tahmo_suspect', 'precipitation_2_quality_tahmo_suspect')",
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
            5
          ]
        },
        "hide": true,
        "iconColor": "yellow",
        "name": "Stormy, no rain",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Stormy, no rain' as \"text\"\nFROM \"classifier_annotation/rainfall_bad_stormy\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station:raw}'",
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
            5
          ]
        },
        "hide": true,
        "iconColor": "red",
        "name": "Lightning, no rain",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Lightning, no rain' as \"text\"\nFROM \"classifier_annotation/rainfall_bad_lightning\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station:raw}'",
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
            4,
            7,
            2
          ]
        },
        "hide": false,
        "iconColor": "purple",
        "name": "Dripping clog",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Dripping clog' as \"text\"\nFROM \"classifier_annotation/dripping_clog\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station:raw}'",
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
            4,
            2
          ]
        },
        "hide": true,
        "iconColor": "#eb10de",
        "name": "Way Too Much Rain",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Way too much rain' as \"text\"\nFROM \"classifier_annotation/way_too_much_rain\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station:raw}'",
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
            2
          ]
        },
        "hide": false,
        "iconColor": "blue",
        "name": "Precip lower than satellite",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Precip lower than satellite' as \"text\"\nFROM \"classifier_annotation/rainfall_bad_satellite\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station:raw}'",
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
        "builtIn": 1,
        "datasource": {
          "type": "datasource",
          "uid": "grafana"
        },
        "enable": false,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "mappings": {
          "tags": {
            "source": "field",
            "value": "$station"
          }
        },
        "name": "Annotations & Alerts",
        "target": {
          "queryType": "annotations",
          "refId": "Anno",
          "tags": [
            "$station"
          ],
          "type": "tags"
        },
        "type": "dashboard"
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
            4,
            2,
            7
          ]
        },
        "hide": true,
        "iconColor": "#2fe0bb",
        "name": "Stuck",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Stuck away from zero' as \"text\"\nFROM \"classifier_annotation/stuck_away_from_zero\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station:raw}'",
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
            4,
            2,
            7
          ]
        },
        "hide": false,
        "iconColor": "yellow",
        "name": "Offline",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Offline' as \"text\"\nFROM \"classifier_annotation/offline\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station}'\n",
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
          "rawSql": "select time, text, author from \"issues_and_comments_for_display/\" where station_id = '${station:raw}'",
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
        "iconColor": "#e02fba",
        "mappings": {
          "tags": {
            "source": "field",
            "value": "tags"
          },
          "text": {
            "source": "field",
            "value": "text"
          },
          "time": {
            "source": "field",
            "value": "time"
          },
          "timeEnd": {
            "source": "field",
            "value": "end_time"
          },
          "title": {
            "source": "field",
            "value": "title"
          }
        },
        "name": "Manual Rain Annotation",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "select time, end_time, title, text, tags from \"manual_annotations/\" where station_id = '${station:raw}'",
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
        "name": "Bad Rainfall",
        "target": {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n  \"start\" AS time,\n  \"end\" AS timeEnd,\n  'Bad rainfall' as \"text\"\nFROM \"classifier_annotation/rainfall_final\"\nWHERE ($__timeFrom() < \"end\" AND $__timeTo() > \"start\") AND \"station_id\" = '${station:raw}'",
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
                  "fixedColor": "super-light-orange",
                  "mode": "fixed"
                }
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
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "CHIRPS Precip"
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
                  "fixedColor": "super-light-red",
                  "mode": "fixed"
                }
              },
              {
                "id": "custom.axisWidth",
                "value": 45
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
        "h": 6,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 2,
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
          "query": "SELECT sum(\"value\") FROM \"controlled\" WHERE (\"station\"::tag =~ /^$station$/ AND \"variable\"::tag = 'pr') AND $timeFilter GROUP BY time(1d), \"sensor\"::tag",
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
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "cegueq2crd3wge"
          },
          "editorMode": "code",
          "format": "table",
          "hide": false,
          "rawQuery": true,
          "rawSql": "select time, precip as imerg_precip \nfrom \"imerg_tahmo/\" \nwhere code = '${station:raw}' AND time $__timeFilter() order by time asc",
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
          "rawSql": "select time, precip as \"CHIRPS Precip\"\nfrom \"chirps_tahmo/\" \nwhere code = '${station:raw}' AND time $__timeFilter() order by time asc",
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
          "query": "SELECT sum(\"value\")/2.9411 FROM \"controlled\" WHERE (\"station\"::tag =~ /^$station$/ AND \"variable\"::tag = 'pt') AND $timeFilter GROUP BY time(1d)",
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
          "query": "SELECT sum(\"value\")/58.823 FROM \"controlled\" WHERE (\"station\"::tag =~ /^$station$/ AND \"variable\"::tag = 'pd') AND $timeFilter GROUP BY time(1d)",
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
            "fixedColor": "blue",
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "Instant Precip (mm)",
            "axisPlacement": "left",
            "axisWidth": 42,
            "barAlignment": 0,
            "barWidthFactor": 0.2,
            "drawStyle": "line",
            "fillOpacity": 1,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": 1200000,
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
          "max": 3,
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
          },
          "unit": "none"
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "Instant Precip S001278"
            },
            "properties": [
              {
                "id": "custom.axisWidth"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Instant Precip S001993"
            },
            "properties": [
              {
                "id": "custom.axisWidth"
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 5,
        "w": 24,
        "x": 0,
        "y": 6
      },
      "id": 4,
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
          "alias": "Instant Precip $tag_sensor",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "sensor::tag"
              ],
              "type": "tag"
            }
          ],
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT \"value\" FROM \"controlled\" WHERE (\"station\"::tag =~ /^$station$/ AND \"variable\"::tag = 'pr') AND $timeFilter GROUP BY \"sensor\"::tag",
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
              "value": "pr"
            }
          ]
        },
        {
          "alias": "Dual Station: Drip count",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT \"value\"  / 58.8235 FROM \"controlled\" WHERE (\"station\"::tag =~ /^$station$/ AND \"variable\"::tag = 'pd') AND $timeFilter",
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
                "params": [
                  " / 58.8235"
                ],
                "type": "math"
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
              "value": "pd"
            }
          ]
        },
        {
          "alias": "Dual Station: Tip count",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [],
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
                "params": [
                  " / 2.9411"
                ],
                "type": "math"
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
              "value": "pt"
            }
          ]
        }
      ],
      "title": "5-minute Rainfall",
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
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "Instant Precip (mm)",
            "axisPlacement": "left",
            "axisWidth": 45,
            "barAlignment": 0,
            "barWidthFactor": 0.2,
            "drawStyle": "line",
            "fillOpacity": 1,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": 1200000,
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
          "max": 0.1,
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
          },
          "unit": "none"
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "Instant Precip S001278"
            },
            "properties": [
              {
                "id": "custom.axisWidth"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Instant Precip S001993"
            },
            "properties": [
              {
                "id": "custom.axisWidth"
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 4,
        "w": 24,
        "x": 0,
        "y": 11
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
          "alias": "Instant Precip $tag_sensor",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [
            {
              "params": [
                "sensor::tag"
              ],
              "type": "tag"
            }
          ],
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT \"value\" FROM \"controlled\" WHERE (\"station\"::tag =~ /^$station$/ AND \"variable\"::tag = 'pr') AND $timeFilter GROUP BY \"sensor\"::tag",
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
              "value": "pr"
            }
          ]
        },
        {
          "alias": "Dual Station: Drip count",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [],
          "hide": false,
          "measurement": "controlled",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT \"value\"  / 58.8235 FROM \"controlled\" WHERE (\"station\"::tag =~ /^$station$/ AND \"variable\"::tag = 'pd') AND $timeFilter",
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
                "params": [
                  " / 58.8235"
                ],
                "type": "math"
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
              "value": "pd"
            }
          ]
        },
        {
          "alias": "Dual Station: Tip count",
          "datasource": {
            "type": "influxdb",
            "uid": "eepjuov1zfi0wb"
          },
          "groupBy": [],
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
                "params": [
                  " / 2.9411"
                ],
                "type": "math"
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
              "value": "pt"
            }
          ]
        }
      ],
      "title": "Precipitation Dripping View",
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
            "axisWidth": 45,
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
          "max": 5,
          "min": -5,
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
              },
              {
                "id": "custom.axisWidth",
                "value": 45
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
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 5,
        "w": 24,
        "x": 0,
        "y": 15
      },
      "id": 6,
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
            "fixedColor": "semi-dark-yellow",
            "mode": "fixed"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "Lightning Strikes",
            "axisPlacement": "auto",
            "axisWidth": 45,
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
            "insertNulls": 3600000,
            "lineInterpolation": "linear",
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
              "options": "1d cumulative precip"
            },
            "properties": [
              {
                "id": "custom.drawStyle",
                "value": "points"
              },
              {
                "id": "color",
                "value": {
                  "fixedColor": "blue",
                  "mode": "fixed"
                }
              },
              {
                "id": "custom.axisSoftMax",
                "value": 100
              },
              {
                "id": "custom.axisPlacement",
                "value": "hidden"
              },
              {
                "id": "custom.axisWidth",
                "value": 45
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "lightning distance"
            },
            "properties": [
              {
                "id": "color",
                "value": {
                  "fixedColor": "dark-red",
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
        "y": 20
      },
      "id": 5,
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
          "alias": "lightning strikes",
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
              "value": "le"
            }
          ]
        },
        {
          "alias": "1d cumulative precip",
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
        }
      ],
      "title": "Lightning vs Precip",
      "type": "timeseries"
    }
  ],
  "preload": false,
  "refresh": "",
  "schemaVersion": 40,
  "tags": [
    "Precip Timeseries"
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
        "allowCustomValue": false,
        "current": {
          "text": "TA00002 - Benso SHS",
          "value": "TA00002"
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
        "allowCustomValue": false,
        "current": {
          "text": "2.15",
          "value": "2.15"
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
          "text": "ZL6",
          "value": "ZL6"
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
    "from": "2025-05-24T12:00:03.500Z",
    "to": "2025-07-03T11:59:55.500Z"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "Precipitation Timeseries",
  "uid": "eenvpy0gxghz4c",
  "version": 1,
  "weekStart": ""
}
