local conditional_slice_js = importstr './assets/conditional_slice.js';
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
        "type": "dashboard"
      }
    ]
  },
  "description": "Compare different sources of precipitation estimates in distributions. ",
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
        "w": 7,
        "x": 0,
        "y": 0
      },
      "id": 9,
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
        "onclick": paired_histogram_js,
        "resScale": 2,
        "script": paired_histogram_js,
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT estimate, truth, SUM(precip) as precip\nFROM \"hist_df/${agg_days}_${satellite}_${grid}_global_${stations}\"\nWHERE region_id = (\n    SELECT region_id\n    FROM \"spacegrouping_category_codes/${grid}_global_country\"\n    WHERE region = '$country1'\n)\nAND group_id IN (${months:csv})\nGROUP BY estimate, truth\nORDER BY estimate, truth;",
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
      "title": "${country1}",
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
        "w": 11,
        "x": 7,
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
        "onclick": conditional_slice_js,
        "resScale": 2,
        "script": conditional_slice_js,
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
          "panelId": 9,
          "refId": "A"
        }
      ],
      "title": "precip conditional distribution for ${country1}",
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
        "w": 7,
        "x": 0,
        "y": 9
      },
      "id": 10,
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
        "onclick": paired_histogram_js,
        "resScale": 2,
        "script": paired_histogram_js,
        "syncTimeRange": false,
        "timeCol": ""
      },
      "pluginVersion": "1.8.2",
      "targets": [
        {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT estimate, truth, SUM(precip) as precip\nFROM \"hist_df/${agg_days}_${satellite}_${grid}_global_${stations}\"\nWHERE region_id = (\n    SELECT region_id\n    FROM \"spacegrouping_category_codes/${grid}_global_country\"\n    WHERE region = '$country2'\n)\nAND group_id IN (${months:csv})\nGROUP BY estimate, truth\nORDER BY estimate, truth;",
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
      "title": "${country2}",
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
        "w": 11,
        "x": 7,
        "y": 9
      },
      "id": 11,
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
        "onclick": conditional_slice_js,
        "resScale": 2,
        "script": conditional_slice_js,
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
          "panelId": 10,
          "refId": "A"
        }
      ],
      "title": "precip conditional distribution for ${country2}",
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
          "text": "kenya",
          "value": "kenya"
        },
        "definition": "SELECT \n  region\nFROM \n  \"spacegrouping_category_codes/global1_5_global_country\"",
        "label": "country1",
        "name": "country1",
        "options": [],
        "query": "SELECT \n  region\nFROM \n  \"spacegrouping_category_codes/global1_5_global_country\"",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "brazil",
          "value": "brazil"
        },
        "definition": "SELECT \n  region\nFROM \n  \"spacegrouping_category_codes/global1_5_global_country\"",
        "label": "country2",
        "name": "country2",
        "options": [],
        "query": "SELECT \n  region\nFROM \n  \"spacegrouping_category_codes/global1_5_global_country\"",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "imerg_late",
          "value": "imerg_late"
        },
        "description": "precip satellite data source",
        "label": "Satellite Product",
        "name": "satellite",
        "options": [
          {
            "selected": false,
            "text": "IMERG Final",
            "value": "imerg_final"
          },
          {
            "selected": true,
            "text": "IMERG Late",
            "value": "imerg_late"
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
        "query": "IMERG Final : imerg_final, IMERG Late : imerg_late, CHIRPS : chirps_v3, Rain over Africa : rain_over_africa",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "stations",
          "value": "stations"
        },
        "description": "",
        "label": "stations",
        "name": "stations",
        "options": [
          {
            "selected": false,
            "text": "tahmo_avg",
            "value": "tahmo_avg"
          },
          {
            "selected": false,
            "text": "tahmo",
            "value": "tahmo"
          },
          {
            "selected": true,
            "text": "stations",
            "value": "stations"
          }
        ],
        "query": "tahmo_avg, tahmo, stations",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": [
            "$__all"
          ],
          "value": [
            "$__all"
          ]
        },
        "description": "",
        "includeAll": true,
        "label": "month of year",
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
            "selected": false,
            "text": "5",
            "value": "5"
          },
          {
            "selected": false,
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
          "text": "stations",
          "value": "stations"
        },
        "label": "condition on",
        "name": "condition_on",
        "options": [
          {
            "selected": false,
            "text": "satellite",
            "value": "satellite"
          },
          {
            "selected": true,
            "text": "stations",
            "value": "stations"
          }
        ],
        "query": "satellite, stations",
        "type": "custom"
      },
      {
        "current": {
          "text": "5",
          "value": "5"
        },
        "label": "slice",
        "name": "slice",
        "options": [
          {
            "selected": true,
            "text": "5",
            "value": "5"
          }
        ],
        "query": "5",
        "type": "custom"
      },
      {
        "current": {
          "text": "10",
          "value": "10"
        },
        "label": "confidence",
        "name": "confidence",
        "options": [
          {
            "selected": true,
            "text": "10",
            "value": "10"
          }
        ],
        "query": "10",
        "type": "custom"
      },
      {
        "current": {
          "text": "50",
          "value": "50"
        },
        "description": "",
        "label": "set axis lims",
        "name": "fix_limits",
        "options": [
          {
            "selected": true,
            "text": "50",
            "value": "50"
          },
          {
            "selected": false,
            "text": "None",
            "value": "None"
          }
        ],
        "query": "50, None",
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
  "title": "Satellite vs Stations Distributions",
  "uid": "bfgfsz50v8lxcd",
  "version": 1,
  "weekStart": ""
}
