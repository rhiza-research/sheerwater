local color_utilities_js = importstr './assets/color_utilities.js';
local dfd44cgdurwn4f_singlemap_evaluation_call_function_js = importstr './assets/dfd44cgdurwn4f-singlemap-evaluation-call-function.js';
local dfd44cgdurwn4f_station_evaluation_params_js = importstr './assets/dfd44cgdurwn4f-station-evaluation-params.js';
local maplibre_map_builder_js = importstr './assets/maplibre-map-builder.js';
local maplibre_multimap_orchestration_js = importstr './assets/maplibre-multimap-orchestration.js';
local maplibre_singlemap_orchestration_js = importstr './assets/maplibre-singlemap-orchestration.js';
local metrics_utilities_js = importstr './assets/metrics_utilities.js';
local terracotta_dataset_utilities_js = importstr './assets/terracotta_dataset_utilities.js';
local time_grouping_utilities_js = importstr './assets/time_grouping_utilities.js';

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
        "h": 27,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 9,
      "options": {
        "afterRender": dfd44cgdurwn4f_station_evaluation_params_js + maplibre_map_builder_js + time_grouping_utilities_js + metrics_utilities_js + color_utilities_js + terracotta_dataset_utilities_js + maplibre_singlemap_orchestration_js + maplibre_multimap_orchestration_js + dfd44cgdurwn4f_singlemap_evaluation_call_function_js,
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
          "text": "chirps_v3",
          "value": "chirps_v3"
        },
        "label": "Analysis",
        "name": "reanalysis",
        "options": [
          {
            "selected": false,
            "text": "CHIRP v3",
            "value": "chirp_v3"
          },
          {
            "selected": true,
            "text": "CHIRPS v3 (Gauge-Adjusted)",
            "value": "chirps_v3"
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
            "selected": false,
            "text": "ERA5",
            "value": "era5"
          },
          {
            "selected": false,
            "text": "Rain over Africa",
            "value": "rain_over_africa"
          },
          {
            "selected": false,
            "text": "TAMSAT",
            "value": "tamsat"
          }
        ],
        "query": "CHIRP v3 : chirp_v3, CHIRPS v3 (Gauge-Adjusted) : chirps_v3, IMERG Late Run : imerg_late, IMERG Final Run (Gauge-Adjusted) : imerg_final, ERA5 : era5, Rain over Africa : rain_over_africa, TAMSAT : tamsat",
        "type": "custom"
      },
      {
        "current": {
          "text": "stations",
          "value": "stations"
        },
        "label": "Truth",
        "name": "truth",
        "options": [
          {
            "selected": true,
            "text": "All Stations Average",
            "value": "stations"
          },
          {
            "selected": false,
            "text": "TAHMO Average",
            "value": "tahmo_avg"
          }
        ],
        "query": " All Stations Average : stations, TAHMO Average : tahmo_avg",
        "type": "custom"
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
          }
        ],
        "query": "1.5 : global1_5, 0.25 : global0_25",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "1",
          "value": "1"
        },
        "definition": "SELECT column_name FROM information_schema.columns WHERE table_name = '$precip_tab_name' AND column_name NOT IN ('forecast', 'time_grouping', 'region');",
        "label": "Agg Days",
        "name": "agg_days",
        "options": [],
        "query": "SELECT column_name FROM information_schema.columns WHERE table_name = '$precip_tab_name' AND column_name NOT IN ('forecast', 'time_grouping', 'region');",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "acc",
          "value": "acc"
        },
        "description": "",
        "label": "Metric",
        "name": "metric",
        "options": [
          {
            "selected": false,
            "text": "MAE",
            "value": "mae"
          },
          {
            "selected": false,
            "text": "Bias",
            "value": "bias"
          },
          {
            "selected": true,
            "text": "ACC",
            "value": "acc"
          },
          {
            "selected": false,
            "text": "Pearson",
            "value": "pearson"
          },
          {
            "selected": false,
            "text": "POD 40mm/11 days",
            "value": "pod-3.6"
          },
          {
            "selected": false,
            "text": "FAR 40mm/11 days",
            "value": "far-3.6"
          },
          {
            "selected": false,
            "text": "ETS 40mm/11 days",
            "value": "ets-3.6"
          },
          {
            "selected": false,
            "text": "CSI 40mm/11 days",
            "value": "csi-3.6"
          },
          {
            "selected": false,
            "text": "Freq Bias 40mm/11 days",
            "value": "frequencybias-3.6"
          },
          {
            "selected": false,
            "text": "POD 20mm/3 days",
            "value": "pod-6.6"
          },
          {
            "selected": false,
            "text": "FAR 20mm/3 days",
            "value": "far-6.6"
          },
          {
            "selected": false,
            "text": "ETS 20mm/3 days",
            "value": "ets-6.6"
          },
          {
            "selected": false,
            "text": "CSI 20mm/3 days",
            "value": "csi-6.6"
          },
          {
            "selected": false,
            "text": "Freq Bias 20mm/3 days",
            "value": "frequencybias-6.6"
          },
          {
            "selected": false,
            "text": "POD 38mm/5 days",
            "value": "pod-7.6"
          },
          {
            "selected": false,
            "text": "FAR 38mm/5 days",
            "value": "far-7.6"
          },
          {
            "selected": false,
            "text": "ETS 38mm/5 days",
            "value": "ets-7.6"
          },
          {
            "selected": false,
            "text": "CSI 38mm/5 days",
            "value": "csi-7.6"
          },
          {
            "selected": false,
            "text": "Freq Bias 38mm/5 days",
            "value": "frequencybias-7.6"
          },
          {
            "selected": false,
            "text": "Heidke (Dry 1.5/Wet 7.6 mm)",
            "value": "heidke-1.5-7.6"
          },
          {
            "selected": false,
            "text": "POD Dry Spell 1.5mm",
            "value": "pod-1.5"
          },
          {
            "selected": false,
            "text": "FAR Dry Spell 1.5mm",
            "value": "far-1.5"
          },
          {
            "selected": false,
            "text": "ETS Dry Spell 1.5mm",
            "value": "ets-1.5"
          }
        ],
        "query": "MAE : mae, Bias : bias, ACC : acc, Pearson : pearson,  POD 40mm/11 days : pod-3.6,  FAR 40mm/11 days : far-3.6, ETS 40mm/11 days : ets-3.6, CSI 40mm/11 days : csi-3.6, Freq Bias 40mm/11 days : frequencybias-3.6, POD 20mm/3 days : pod-6.6,  FAR 20mm/3 days : far-6.6, ETS 20mm/3 days : ets-6.6, CSI 20mm/3 days : csi-6.6, Freq Bias 20mm/3 days : frequencybias-6.6, POD 38mm/5 days : pod-7.6,  FAR 38mm/5 days : far-7.6, ETS 38mm/5 days : ets-7.6, CSI 38mm/5 days : csi-7.6, Freq Bias 38mm/5 days : frequencybias-7.6, Heidke (Dry 1.5/Wet 7.6 mm) : heidke-1.5-7.6, POD Dry Spell 1.5mm : pod-1.5, FAR Dry Spell 1.5mm : far-1.5, ETS Dry Spell 1.5mm : ets-1.5",
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
          "text": "month_of_year",
          "value": "month_of_year"
        },
        "includeAll": false,
        "label": "Time Grouping",
        "name": "time_grouping",
        "options": [
          {
            "selected": false,
            "text": "None",
            "value": "None"
          },
          {
            "selected": true,
            "text": "Month of Year",
            "value": "month_of_year"
          }
        ],
        "query": "None : None, Month of Year : month_of_year",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "January",
          "value": "January"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"43b9f8fd510b587766b75442e9bb46d6\";",
        "includeAll": false,
        "label": "Time Filter",
        "name": "time_filter",
        "options": [],
        "query": "SELECT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"43b9f8fd510b587766b75442e9bb46d6\";",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "5359a2e418b8e1ebfb1094b70d2c96c6",
          "value": "5359a2e418b8e1ebfb1094b70d2c96c6"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('ground_truth_metric_table/2024-12-31_${grid}_${metric}_subregion_1998-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "precip_tab_name",
        "options": [],
        "query": "select * from md5('ground_truth_metric_table/2024-12-31_${grid}_${metric}_subregion_1998-01-01_${time_grouping}_${truth}_precip')",
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
      },
      {
        "current": {
          "text": "",
          "value": ""
        },
        "label": "vmin",
        "name": "vmin",
        "options": [
          {
            "selected": true,
            "text": "",
            "value": ""
          }
        ],
        "query": "",
        "type": "textbox"
      },
      {
        "current": {
          "text": "",
          "value": ""
        },
        "label": "vmax",
        "name": "vmax",
        "options": [
          {
            "selected": true,
            "text": "",
            "value": ""
          }
        ],
        "query": "",
        "type": "textbox"
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
