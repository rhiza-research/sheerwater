local color_utilities_js = importstr './assets/color_utilities.js';
local dfd44cgdurwn4f_singlemap_evaluation_call_function_js = importstr './assets/dfd44cgdurwn4f-singlemap-evaluation-call-function.js';
local dfd44cgdurwn4f_station_evaluation_params_js = importstr './assets/dfd44cgdurwn4f-station-evaluation-params.js';
local maplibre_map_builder_js = importstr './assets/maplibre-map-builder.js';
local maplibre_multimap_orchestration_js = importstr './assets/maplibre-multimap-orchestration.js';
local maplibre_singlemap_orchestration_js = importstr './assets/maplibre-singlemap-orchestration.js';
local terracotta_dataset_utilities_js = importstr './assets/terracotta_dataset_utilities.js';

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
        "type": "datasource",
        "uid": "grafana"
      },
      "fieldConfig": {
        "defaults": {
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
        "h": 25,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 9,
      "options": {
        "afterRender": dfd44cgdurwn4f_station_evaluation_params_js + maplibre_map_builder_js + color_utilities_js + terracotta_dataset_utilities_js + maplibre_singlemap_orchestration_js + maplibre_multimap_orchestration_js + dfd44cgdurwn4f_singlemap_evaluation_call_function_js,
        "content": "<div id=\"map-container\" style=\"height:900px\" />",
        "contentPartials": [],
        "defaultContent": "",
        "editor": {
          "format": "auto",
          "language": "html"
        },
        "editors": [
          "afterRender"
        ],
        "externalStyles": [],
        "helpers": "",
        "renderMode": "data",
        "styles": "",
        "wrap": true
      },
      "pluginVersion": "6.2.0",
      "targets": [
        {
          "datasource": {
            "type": "datasource",
            "uid": "grafana"
          },
          "path": "img",
          "queryType": "list",
          "refId": "A"
        }
      ],
      "title": "",
      "transparent": true,
      "type": "marcusolsson-dynamictext-panel"
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
          "text": "era5",
          "value": "era5"
        },
        "label": "Analysis",
        "name": "reanalysis",
        "options": [
          {
            "selected": false,
            "text": "CHIRPS v2",
            "value": "chirp_v2"
          },
          {
            "selected": false,
            "text": "CHIRPS v3",
            "value": "chirp_v3"
          },
          {
            "selected": false,
            "text": "IMERG Late Run",
            "value": "imerg_late"
          },
          {
            "selected": false,
            "text": "IMERG Final Run (Gauge-Adjusted)",
            "value": "imerg_final"
          },
          {
            "selected": true,
            "text": "ERA5",
            "value": "era5"
          }
        ],
        "query": "CHIRPS v2 : chirp_v2, CHIRPS v3 : chirp_v3, IMERG Late Run : imerg_late, IMERG Final Run (Gauge-Adjusted) : imerg_final, ERA5 : era5",
        "type": "custom"
      },
      {
        "current": {
          "text": "tahmo",
          "value": "tahmo"
        },
        "label": "Truth",
        "name": "truth",
        "options": [
          {
            "selected": true,
            "text": "TAHMO Stations",
            "value": "tahmo"
          },
          {
            "selected": false,
            "text": "TAHMO Area Average",
            "value": "tahmo_avg"
          },
          {
            "selected": false,
            "text": "GHCN Stations",
            "value": "ghcn"
          },
          {
            "selected": false,
            "text": "GHCN Area Average",
            "value": "ghcn_avg"
          }
        ],
        "query": "TAHMO Stations : tahmo, TAHMO Area Average : tahmo_avg, GHCN Stations : ghcn, GHCN Area Average : ghcn_avg",
        "type": "custom"
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
          }
        ],
        "query": "1.5 : global1_5, 0.25 : global0_25",
        "type": "custom"
      },
      {
        "current": {
          "text": "7",
          "value": "7"
        },
        "label": "Agg Days",
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
            "text": "7",
            "value": "7"
          },
          {
            "selected": false,
            "text": "10",
            "value": "10"
          }
        ],
        "query": "1,5,7,10",
        "type": "custom"
      },
      {
        "current": {
          "text": "mae",
          "value": "mae"
        },
        "label": "Metric",
        "name": "metric",
        "options": [
          {
            "selected": true,
            "text": "MAE",
            "value": "mae"
          }
        ],
        "query": "MAE : mae",
        "type": "custom"
      },
      {
        "current": {
          "text": "precip",
          "value": "precip"
        },
        "label": "Product",
        "name": "product",
        "options": [
          {
            "selected": true,
            "text": "Precipitation",
            "value": "precip"
          }
        ],
        "query": "Precipitation : precip",
        "type": "custom"
      },
      {
        "current": {
          "text": "None",
          "value": "None"
        },
        "includeAll": false,
        "label": "Time Grouping",
        "name": "time_grouping",
        "options": [
          {
            "selected": true,
            "text": "None",
            "value": "None"
          },
          {
            "selected": false,
            "text": "Month of Year",
            "value": "month_of_year"
          },
          {
            "selected": false,
            "text": "Year",
            "value": "year"
          }
        ],
        "query": "None : None, Month of Year : month_of_year, Year : year",
        "type": "custom"
      },
      {
        "current": {
          "text": "select v.* from (values ('None')) v(t)",
          "value": "select v.* from (values ('None')) v(t)"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select \nCASE\n    WHEN v.g = 'None' THEN 'select v.* from (values (''None'')) v(t)'\n    ELSE 'select distinct time from \"${precip_tab_name}\"'\nEND\nfrom (values ('$time_grouping')) v(g)",
        "hide": 2,
        "includeAll": false,
        "name": "time_filter_filter_query",
        "options": [],
        "query": "select \nCASE\n    WHEN v.g = 'None' THEN 'select v.* from (values (''None'')) v(t)'\n    ELSE 'select distinct time from \"${precip_tab_name}\"'\nEND\nfrom (values ('$time_grouping')) v(g)",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "None",
          "value": "None"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "${time_filter_filter_query:raw}",
        "includeAll": false,
        "label": "Time Filter",
        "name": "time_filter",
        "options": [],
        "query": "${time_filter_filter_query:raw}",
        "refresh": 1,
        "regex": "",
        "sort": 3,
        "type": "query"
      },
      {
        "current": {
          "text": "",
          "value": ""
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select \nCASE\n    WHEN v.g = 'None' THEN ''\n    ELSE 'where time = ' || v.t\nEND\nfrom (values ('$time_filter', '$time_grouping')) v(t, g)",
        "hide": 2,
        "includeAll": false,
        "name": "time_filter_query",
        "options": [],
        "query": "select \nCASE\n    WHEN v.g = 'None' THEN ''\n    ELSE 'where time = ' || v.t\nEND\nfrom (values ('$time_filter', '$time_grouping')) v(t, g)",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "1e5a29f205927ed32172704459e4ddde",
          "value": "1e5a29f205927ed32172704459e4ddde"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('summary_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "precip_tab_name",
        "options": [],
        "query": "select * from md5('summary_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "false",
          "value": "false"
        },
        "hide": 2,
        "includeAll": false,
        "label": "Standardize Forecast Colors",
        "name": "standardize_forecast_colors",
        "options": [
          {
            "selected": true,
            "text": "False",
            "value": "false"
          }
        ],
        "query": "False : false",
        "type": "custom"
      },
      {
        "current": {
          "text": "false",
          "value": "false"
        },
        "hide": 2,
        "includeAll": false,
        "label": "Standardize Lead Colors",
        "name": "standardize_lead_colors",
        "options": [
          {
            "selected": true,
            "text": "False",
            "value": "false"
          }
        ],
        "query": "False : false",
        "type": "custom"
      }
    ]
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "hidden": true
  },
  "timezone": "utc",
  "title": "Station Data Evaluation Map",
  "uid": "dfd44cgdurwn4f",
  "version": 1,
  "weekStart": ""
}
