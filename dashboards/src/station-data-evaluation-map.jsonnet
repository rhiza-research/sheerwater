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
        "uid": "bdz3m3xs99p1cf"
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
        "h": 3,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 10,
      "options": {
        "afterRender": "// window.onload = function () {\n//     renderMathInElement(document.body, {\n//         delimiters: [\n//             { left: \"$$\", right: \"$$\", display: true },\n//             { left: \"\\\\(\", right: \"\\\\)\", display: false }\n//         ]\n//     });\n// };\n",
        "content": "### Selected Metric: {{#if (eq metric \"mae\")}}MAE{{else if (eq metric \"rmse\")}}RMSE{{else if (eq metric \"crps\")}}CRPS{{else if (eq metric \"bias\")}}Bias{{else if (eq metric \"smape\")}}SMAPE{{else if (eq metric \"seeps\")}}SEEPS{{else if (eq metric \"acc\")}}ACC{{else if (eq metric \"pearson\")}}Pearson{{else if (match metric \"^heidke-\")}}Heidke{{else if (match metric \"^pod-\")}}POD{{else if (match metric \"^far-\")}}FAR{{else if (match metric \"^ets-\")}}ETS{{else if (match metric \"^csi-\")}}CSI{{else}}Unknown{{/if}}\n\n{{#if (eq metric \"mae\")}}\nMean absolute error (MAE) measures the average magnitude of the errors in a set of predictions, without considering their direction.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower MAE means better predictions.</span> \n\n{{else if (eq metric \"crps\")}}\nContinuous ranked probability score (CRPS) assesses probabilistic forecast accuracy.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better.</span>\n\n{{else if (eq metric \"rmse\")}}\nRoot mean squared error (RMSE) gives higher weight to large errors.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better.</span>\n\n{{else if (eq metric \"acc\")}}\nAnomaly correlation coefficient (ACC) compares forecast and observed anomalies relative to climatology.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — range [-1, 1].</span>\n\n{{else if (eq metric \"pearson\")}}\nPearson correlation measures linear association between predictions and observations.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — range [-1, 1].</span>\n\n{{else if (eq metric \"bias\")}}\nBias measures signed error magnitude.\\\n<span style=\"color: gray; font-weight: bold;\">⚪ Ideal = 0.</span>\n\n{{else if (eq metric \"smape\")}}\nSMAPE expresses error as a percent of total value (precip only).\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — range [0, 1].</span>\n\n{{else if (eq metric \"seeps\")}}\nSEEPS evaluates rainfall forecasts accounting for climatology.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better.</span>\n\n{{else if (match metric \"^heidke-\")}}\nHeidke skill score (HSS) compares forecast accuracy against random chance for one or more event thresholds.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — range [-∞, 1].</span>\n\n{{else if (match metric \"^pod-\")}}\nProbability of detection (POD) = fraction of observed events correctly forecast.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — range [0, 1].</span>\n\n{{else if (match metric \"^csi-\")}}\nCritical success index (CSI) measures the fraction of observed and/or forecast events that were correctly predicted (hits divided by hits + misses + false alarms) for a thresholded event definition.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — higher CSI indicates better event detection skill. Range [0, 1].</span>\n\n{{else if (match metric \"^far-\")}}\nFalse alarm rate (FAR) = fraction of predicted events not observed.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — range [0, 1].</span>\n\n{{else if (match metric \"^ets-\")}}\nEquitable threat score (ETS) measures threshold-event skill adjusted for chance.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — range [-1/3, 1].</span>\n\n{{else}}\n_no description available for this metric._\n{{/if}}\n",
        "contentPartials": [],
        "defaultContent": "The query didn't return any results.",
        "editor": {
          "format": "auto",
          "language": "markdown"
        },
        "editors": [],
        "externalStyles": [],
        "helpers": "",
        "renderMode": "everyRow",
        "styles": "",
        "wrap": true
      },
      "pluginVersion": "6.2.0",
      "targets": [
        {
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "select '${metric}' as metric\n",
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
      "title": "",
      "transparent": true,
      "type": "marcusolsson-dynamictext-panel"
    },
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
        "y": 3
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
          "text": "imerg_late",
          "value": "imerg_late"
        },
        "label": "Analysis",
        "name": "reanalysis",
        "options": [
          {
            "selected": false,
            "text": "CHIRPS v2",
            "value": "chirps_v2"
          },
          {
            "selected": false,
            "text": "CHIRPS v3",
            "value": "chirps_v3"
          },
          {
            "selected": true,
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
          }
        ],
        "query": "CHIRPS v2 : chirps_v2, CHIRPS v3 : chirps_v3, IMERG Late Run : imerg_late, IMERG Final Run (Gauge-Adjusted) : imerg_final, ERA5 : era5",
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
            "text": "All Stations Area Average",
            "value": "stations"
          },
          {
            "selected": false,
            "text": "TAHMO Area Average",
            "value": "tahmo_avg"
          },
          {
            "selected": false,
            "text": "GHCN Area Average",
            "value": "ghcn_avg"
          }
        ],
        "query": " All Stations Area Average : stations, TAHMO Area Average : tahmo_avg, GHCN Area Average : ghcn_avg",
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
          "text": "10",
          "value": "10"
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
            "selected": false,
            "text": "7",
            "value": "7"
          },
          {
            "selected": true,
            "text": "10",
            "value": "10"
          }
        ],
        "query": "1,5,7,10",
        "type": "custom"
      },
      {
        "current": {
          "text": "heidke-1.5-7.6",
          "value": "heidke-1.5-7.6"
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
            "selected": true,
            "text": "Heidke (Dry 1.5/Wet 7.6 mm)",
            "value": "heidke-1.5-7.6"
          },
          {
            "selected": false,
            "text": "POD Dry Spell 1.5mm",
            "value": "far-1.5"
          },
          {
            "selected": false,
            "text": "FAR Dry Spell 1.5mm",
            "value": "pod-1.5"
          },
          {
            "selected": false,
            "text": "ETS Dry Spell 1.5mm",
            "value": "ets-1.5"
          }
        ],
        "query": "MAE : mae, Bias : bias, Pearson : pearson,  POD 40mm/11 days : pod-3.6,  FAR 40mm/11 days : far-3.6, ETS 40mm/11 days : ets-3.6, CSI 40mm/11 days : csi-3.6, Freq Bias 40mm/11 days : frequencybias-3.6, POD 20mm/3 days : pod-6.6,  FAR 20mm/3 days : far-6.6, ETS 20mm/3 days : ets-6.6, CSI 20mm/3 days : csi-6.6, Freq Bias 20mm/3 days : frequencybias-6.6, POD 38mm/5 days : pod-7.6,  FAR 38mm/5 days : far-7.6, ETS 38mm/5 days : ets-7.6, CSI 38mm/5 days : csi-7.6, Freq Bias 38mm/5 days : frequencybias-7.6, Heidke (Dry 1.5/Wet 7.6 mm) : heidke-1.5-7.6, POD Dry Spell 1.5mm : far-1.5, FAR Dry Spell 1.5mm : pod-1.5, ETS Dry Spell 1.5mm : ets-1.5",
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
          }
        ],
        "query": "None : None, Month of Year : month_of_year",
        "type": "custom"
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
        "definition": "SELECT t.value\nFROM unnest(\n  CASE\n    WHEN '$time_grouping' = 'month_of_year' THEN\n      ARRAY(\n        SELECT 'M' || lpad(gs::text, 2, '0')\n        FROM generate_series(1, 12) AS gs\n      )::text[]\n\n    WHEN '$time_grouping' = 'year' THEN\n      ARRAY(\n        SELECT gs::text\n        FROM generate_series(1998, 2024) AS gs\n      )::text[]\n\n    ELSE\n      ARRAY[]::text[]\n  END\n) AS t(value)\nORDER BY t.value;\n",
        "includeAll": false,
        "label": "Time Filter",
        "name": "time_filter",
        "options": [],
        "query": "SELECT t.value\nFROM unnest(\n  CASE\n    WHEN '$time_grouping' = 'month_of_year' THEN\n      ARRAY(\n        SELECT 'M' || lpad(gs::text, 2, '0')\n        FROM generate_series(1, 12) AS gs\n      )::text[]\n\n    WHEN '$time_grouping' = 'year' THEN\n      ARRAY(\n        SELECT gs::text\n        FROM generate_series(1998, 2024) AS gs\n      )::text[]\n\n    ELSE\n      ARRAY[]::text[]\n  END\n) AS t(value)\nORDER BY t.value;\n",
        "refresh": 1,
        "regex": "",
        "sort": 3,
        "type": "query"
      },
      {
        "current": {
          "text": "b37caaaf7166a4315b7f3e8ac9e3673c",
          "value": "b37caaaf7166a4315b7f3e8ac9e3673c"
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
