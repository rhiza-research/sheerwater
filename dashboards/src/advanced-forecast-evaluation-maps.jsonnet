local advanced_metrics_maps_js = importstr './assets/advanced_metrics_maps.js';
local ffojsn16cxs00e_10_lead_35_consts_js = importstr './assets/ffojsn16cxs00e-10-lead_35_consts.js';
local ffojsn16cxs00e_11_lead_42_consts_js = importstr './assets/ffojsn16cxs00e-11-lead_42_consts.js';
local ffojsn16cxs00e_5_lead_7_consts_js = importstr './assets/ffojsn16cxs00e-5-lead_7_consts.js';
local ffojsn16cxs00e_7_lead_14_consts_js = importstr './assets/ffojsn16cxs00e-7-lead_14_consts.js';
local ffojsn16cxs00e_8_lead_21_consts_js = importstr './assets/ffojsn16cxs00e-8-lead_21_consts.js';
local ffojsn16cxs00e_9_lead_28_consts_js = importstr './assets/ffojsn16cxs00e-9-lead_28_consts.js';

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
        "h": 4,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 6,
      "options": {
        "afterRender": "// window.onload = function () {\n//     renderMathInElement(document.body, {\n//         delimiters: [\n//             { left: \"$$\", right: \"$$\", display: true },\n//             { left: \"\\\\(\", right: \"\\\\)\", display: false }\n//         ]\n//     });\n// };\n",
        "content": "### Selected Metric: {{#if (eq metric \"mae\")}}MAE {{/if}} {{#if (eq metric \"rmse\")}}RMSE{{/if}} {{#if (eq metric \"crps\")}}CRPS{{/if}} {{#if (eq metric \"bias\")}}Bias{{/if}} {{#if (eq metric \"smape\")}}SMAPE{{/if}} {{#if (eq metric \"seeps\")}}SEEPS{{/if}} {{#if (eq metric \"acc\")}}ACC{{/if}}  {{#if (eq metric \"heidke-1-5-10-20\")}}Heidke 1/5/10/20mm{{/if}} {{#if (eq metric \"far-1\")}}FAR 1mm{{/if}} {{#if (eq metric \"far-5\")}}FAR 5mm{{/if}} {{#if (eq metric \"far-10\")}}FAR 10mm{{/if}} {{#if (eq metric \"pod-1\")}}POD 1mm{{/if}} {{#if (eq metric \"pod-5\")}}POD 5mm{{/if}} {{#if (eq metric \"pod-10\")}}POD 10mm{{/if}} {{#if (eq metric \"ets-1\")}}ETS 1mm{{/if}} {{#if (eq metric \"ets-5\")}}ETS 5mm{{/if}} {{#if (eq metric \"ets-10\")}}ETS 10mm{{/if}}\n\n{{#if (eq metric \"mae\")}}\nMean absolute error (MAE) measures the average magnitude of the errors in a set of predictions, without considering\ntheir direction.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower MAE means better predictions.</span> \n\n{{else if (eq metric \"crps\")}}\nContinuous ranked probability score (CRPS) assesses the accuracy of probabilistic forecasts by comparing the cumulative\ndistribution function of forecasts to the observed values.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower CRPS indicates better probabilistic forecasting skill.</span>\n\n{{else if (eq metric \"rmse\")}}\nRoot mean squared error (RMSE) gives higher weight to large errors, making it more sensitive to outliers.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower RMSE means better predictions.</span>\n\n{{else if (eq metric \"acc\")}}\nAnomaly correlation coefficient (ACC) ACC is a measure of how well the forecast anomalies have represented the observed anomalies\nrelative to climatology. We used 1991-2020 climatology (years inclusive) for our ACC calculation.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — higher ACC means better predictions. Range [-1, 1].</span>\n\n{{else if (eq metric \"bias\")}}\nBias measures the signed magnitude of errors in a set of predictions. \\\n<span style=\"color: gray; font-weight: bold;\">⚪ Ideal value = 0.0 — Bias should be close to 0.0 for an unbiased forecast.</span>\n\n{{else if (eq metric \"smape\")}}\nSymmetric mean absolute percentage error (SMAPE) is a normalized version of Mean Absolute Percentage Error (MAPE) and calculate sthe error as a percentage of the total value. We only calculate SMAPE for precipitation.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower SMAPE indicates better forecasting accuracy. Range [0, 1].</span>\n\n{{else if (eq metric \"seeps\")}}\nStable equitable error in probability space (SEEPS) is a score designed for evaluating rainfall forecasts while taking into account climactic difference in rainfall. Areas that are too dry or wet are exclued. \nWe include all cells with a 3-93% non-dry day frequency to ensure inclusion of relevant parts of Africa. We only calculate SEEPS for precipitation.\\\n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower SEEPS indicates better forecasting accuracy. Good SEEPS for short term forecasts on cells that have 10-85% non-dry days are considered between 0-1.</span>\n\n{{else if (eq metric \"heidke-1-5-10-20\")}}\nHeidke skill score (HSS) compares the accuracy of a forecast to random chance for a set of predetermined rainfall thresholds—in this case, 1, 5, 10, and 20mm. We only calculate Heidke for precipitation.\\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — a higher HSS indicates better skill. Range [-&infin;, 1]</span>\n\n{{else if (or (eq metric \"pod-1\") (or (eq metric \"pod-5\") (eq metric \"pod-10\")))}}\nProbability of detection (POD) measures the fraction of observed rainfall events that were correctly predicted—in this case, a weekly average daily rainfall of over 1, 5, or 10mm. We only calculate POD for precipitation. \\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — higher probability of detection is better. Range [0, 1]. </span>\n\n{{else if (or (eq metric \"far-1\") (or (eq metric \"far-5\") (eq metric \"far-10\")))}}\nFalse alarm rate (FAR) quantifies the fraction of predicted rainfall events that were not observed—in this case, a weekly average daily rainfall of over 1, 5, or 10mm. We only calculate FAR for precipitation.\\ \n<span style=\"color: red; font-weight: bold;\">🔴 Smaller is better — lower false alarm rate is better. Range [0, 1].</span>\n\n{{else if (or (eq metric \"ets-1\") (or (eq metric \"ets-5\") (eq metric \"ets-10\")))}}\nEquitable threat score (ETS) measures a combination of POD and FAR while accounting for random chance on a specific event—in this case, a weekly average daily rainfall of over 1, 5, or 10mm. We only calculate ETS for precipitation. \\\n<span style=\"color: green; font-weight: bold;\">🟢 Larger is better — higher ETS indicates better skill. Range [-1/3, 1].</span>\n\n{{else}}\n_no description available for this metric._\n{{/if}}\n",
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
      "pluginVersion": "6.2.3",
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
        "default": true,
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 11,
        "w": 6,
        "x": 0,
        "y": 4
      },
      "id": 5,
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
            "t": 500
          },
          "paper_bgcolor": "rgba(0, 0, 0, 0)",
          "plog_bgcolor": "rgba(0, 0, 0, 0)",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            }
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
        "onclick": "console.log(event)\ndocument.last_zoom = event.data['map.zoom'];\ndocument.last_center = event.data['map.center'];\n",
        "resScale": 2,
        "script": ffojsn16cxs00e_5_lead_7_consts_js + advanced_metrics_maps_js,
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
          "rawSql": "-- select * from (values ('${forecast}${lead}${metric}${region}${standardize_lead_colors}${standardize_forecast_colors}${time_grouping}${time_filter}') ) v(t)\nselect *\nfrom (\n    values (\n        '${forecast}${lead}${region:doublequote}${metric}${truth}${time_grouping}${time_filter}'\n    )\n) v(t);",
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
          "rawSql": "-- select '${forecast} ${grid} ${metric} ${ground_truth} ${region} ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}'\nselect \n  '${forecast} ${grid} ${metric} ${ground_truth} ' ||\n  case when '${forecast}' = 'salient'\n       then 'africa'\n       else 'global'\n  end || \n  ' ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}';",
          "refId": "B",
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
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
        "default": true,
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 11,
        "w": 6,
        "x": 6,
        "y": 4
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
            "t": 500
          },
          "paper_bgcolor": "rgba(0, 0, 0, 0)",
          "plog_bgcolor": "rgba(0, 0, 0, 0)",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            }
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
        "onclick": "console.log(event)\ndocument.last_zoom = event.data['map.zoom'];\ndocument.last_center = event.data['map.center'];\n",
        "resScale": 2,
        "script": ffojsn16cxs00e_7_lead_14_consts_js + advanced_metrics_maps_js,
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
          "rawSql": "-- select * from (values ('${forecast}${lead}${metric}${region}${standardize_lead_colors}${standardize_forecast_colors}${time_grouping}${time_filter}') ) v(t)\nselect *\nfrom (\n    values (\n        '${forecast}${lead}${region:doublequote}${metric}${truth}${time_grouping}${time_filter}'\n    )\n) v(t);",
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
          "rawSql": "-- select '${forecast} ${grid} ${metric} ${ground_truth} ${region} ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}'\nselect \n  '${forecast} ${grid} ${metric} ${ground_truth} ' ||\n  case when '${forecast}' = 'salient'\n       then 'africa'\n       else 'global'\n  end || \n  ' ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}';",
          "refId": "B",
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
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
        "default": true,
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 11,
        "w": 6,
        "x": 12,
        "y": 4
      },
      "id": 8,
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
            "t": 500
          },
          "paper_bgcolor": "rgba(0, 0, 0, 0)",
          "plog_bgcolor": "rgba(0, 0, 0, 0)",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            }
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
        "onclick": "console.log(event)\ndocument.last_zoom = event.data['map.zoom'];\ndocument.last_center = event.data['map.center'];\n",
        "resScale": 2,
        "script": ffojsn16cxs00e_8_lead_21_consts_js + advanced_metrics_maps_js,
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
          "rawSql": "-- select * from (values ('${forecast}${lead}${metric}${region}${standardize_lead_colors}${standardize_forecast_colors}${time_grouping}${time_filter}') ) v(t)\nselect *\nfrom (\n    values (\n        '${forecast}${lead}${region:doublequote}${metric}${truth}${time_grouping}${time_filter}'\n    )\n) v(t);",
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
          "rawSql": "-- select '${forecast} ${grid} ${metric} ${ground_truth} ${region} ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}'\nselect \n  '${forecast} ${grid} ${metric} ${ground_truth} ' ||\n  case when '${forecast}' = 'salient'\n       then 'africa'\n       else 'global'\n  end || \n  ' ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}';",
          "refId": "B",
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
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
        "default": true,
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 11,
        "w": 6,
        "x": 18,
        "y": 4
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
            "t": 500
          },
          "paper_bgcolor": "rgba(0, 0, 0, 0)",
          "plog_bgcolor": "rgba(0, 0, 0, 0)",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            }
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
        "onclick": "console.log(event)\ndocument.last_zoom = event.data['map.zoom'];\ndocument.last_center = event.data['map.center'];\n",
        "resScale": 2,
        "script": ffojsn16cxs00e_9_lead_28_consts_js + advanced_metrics_maps_js,
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
          "rawSql": "-- select * from (values ('${forecast}${lead}${metric}${region}${standardize_lead_colors}${standardize_forecast_colors}${time_grouping}${time_filter}') ) v(t)\nselect *\nfrom (\n    values (\n        '${forecast}${lead}${region:doublequote}${metric}${truth}${time_grouping}${time_filter}'\n    )\n) v(t);",
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
          "rawSql": "-- select '${forecast} ${grid} ${metric} ${ground_truth} ${region} ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}'\nselect \n  '${forecast} ${grid} ${metric} ${ground_truth} ' ||\n  case when '${forecast}' = 'salient'\n       then 'africa'\n       else 'global'\n  end || \n  ' ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}';",
          "refId": "B",
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
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
        "default": true,
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 11,
        "w": 6,
        "x": 0,
        "y": 15
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
            "t": 500
          },
          "paper_bgcolor": "rgba(0, 0, 0, 0)",
          "plog_bgcolor": "rgba(0, 0, 0, 0)",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            }
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
        "onclick": "console.log(event)\ndocument.last_zoom = event.data['map.zoom'];\ndocument.last_center = event.data['map.center'];\n",
        "resScale": 2,
        "script": ffojsn16cxs00e_10_lead_35_consts_js + advanced_metrics_maps_js,
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
          "rawSql": "-- select * from (values ('${forecast}${lead}${metric}${region}${standardize_lead_colors}${standardize_forecast_colors}${time_grouping}${time_filter}') ) v(t)\nselect *\nfrom (\n    values (\n        '${forecast}${lead}${region:doublequote}${metric}${truth}${time_grouping}${time_filter}'\n    )\n) v(t);",
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
          "rawSql": "-- select '${forecast} ${grid} ${metric} ${ground_truth} ${region} ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}'\nselect \n  '${forecast} ${grid} ${metric} ${ground_truth} ' ||\n  case when '${forecast}' = 'salient'\n       then 'africa'\n       else 'global'\n  end || \n  ' ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}';",
          "refId": "B",
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
      "type": "nline-plotlyjs-panel"
    },
    {
      "datasource": {
        "default": true,
        "type": "grafana-postgresql-datasource",
        "uid": "bdz3m3xs99p1cf"
      },
      "fieldConfig": {
        "defaults": {},
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "forecast"
            },
            "properties": []
          }
        ]
      },
      "gridPos": {
        "h": 11,
        "w": 6,
        "x": 6,
        "y": 15
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
            "t": 500
          },
          "paper_bgcolor": "rgba(0, 0, 0, 0)",
          "plog_bgcolor": "rgba(0, 0, 0, 0)",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            }
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
        "onclick": "console.log(event)\ndocument.last_zoom = event.data['map.zoom'];\ndocument.last_center = event.data['map.center'];\n",
        "resScale": 2,
        "script": ffojsn16cxs00e_11_lead_42_consts_js + advanced_metrics_maps_js,
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
          "rawSql": "-- select * from (values ('${forecast}${lead}${metric}${region}${standardize_lead_colors}${standardize_forecast_colors}${time_grouping}${time_filter}') ) v(t)\nselect *\nfrom (\n    values (\n        '${forecast}${lead}${region:doublequote}${metric}${truth}${time_grouping}${time_filter}'\n    )\n) v(t);",
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
          "rawSql": "-- select '${forecast} ${grid} ${metric} ${ground_truth} ${region} ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}'\nselect \n  '${forecast} ${grid} ${metric} ${ground_truth} ' ||\n  case when '${forecast}' = 'salient'\n       then 'africa'\n       else 'global'\n  end || \n  ' ${time_grouping} ${time_filter} ${standardize_forecast_colors} ${standardize_lead_colors}';",
          "refId": "B",
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
          "text": "ecmwf_ifs_er_debiased",
          "value": "ecmwf_ifs_er_debiased"
        },
        "includeAll": false,
        "label": "Forecast",
        "name": "forecast",
        "options": [
          {
            "selected": false,
            "text": "ECMWF IFS ER",
            "value": "ecmwf_ifs_er"
          },
          {
            "selected": true,
            "text": "ECMWF IFS ER Debiased",
            "value": "ecmwf_ifs_er_debiased"
          },
          {
            "selected": false,
            "text": "Clim ERA5 1985-2014",
            "value": "climatology_era5_1985_2015"
          },
          {
            "selected": false,
            "text": "Clim IMERG 1998-2015",
            "value": "climatology_imerg_1998_2016"
          },
          {
            "selected": false,
            "text": "Fuxi",
            "value": "fuxi"
          },
          {
            "selected": false,
            "text": "GraphCast",
            "value": "graphcast"
          },
          {
            "selected": false,
            "text": "GenCast",
            "value": "gencast"
          },
          {
            "selected": false,
            "text": "ECMWF IFS ENS",
            "value": "ecmwf_ifs_ens"
          },
          {
            "selected": false,
            "text": "ECMWF HRES",
            "value": "ecmwf_hres"
          },
          {
            "selected": false,
            "text": "ECMWF AIFS",
            "value": "ecmwf_aifs"
          },
          {
            "selected": false,
            "text": "GFS",
            "value": "gfs"
          }
        ],
        "query": "ECMWF IFS ER : ecmwf_ifs_er, ECMWF IFS ER Debiased : ecmwf_ifs_er_debiased, Clim ERA5 1985-2014 : climatology_era5_1985_2015,  Clim IMERG 1998-2015 : climatology_imerg_1998_2016, Fuxi : fuxi, GraphCast : graphcast, GenCast : gencast, ECMWF IFS ENS : ecmwf_ifs_ens, ECMWF HRES : ecmwf_hres, ECMWF AIFS : ecmwf_aifs, GFS : gfs",
        "type": "custom"
      },
      {
        "current": {
          "text": "early_season_accumulation-30d",
          "value": "early_season_accumulation-30d"
        },
        "includeAll": false,
        "label": "Metric",
        "name": "metric",
        "options": [
          {
            "selected": true,
            "text": "Early Season Accumulation",
            "value": "early_season_accumulation-30d"
          }
        ],
        "query": "Early Season Accumulation : early_season_accumulation-30d",
        "type": "custom"
      },
      {
        "current": {
          "text": "imerg_final",
          "value": "imerg_final"
        },
        "includeAll": false,
        "label": "Ground Truth",
        "name": "truth",
        "options": [
          {
            "selected": true,
            "text": "IMERG",
            "value": "imerg_final"
          },
          {
            "selected": false,
            "text": "CHIRPS V3",
            "value": "chirps_v3"
          },
          {
            "selected": false,
            "text": "ERA5",
            "value": "era5"
          }
        ],
        "query": "IMERG : imerg_final, CHIRPS V3 : chirps_v3, ERA5 : era5",
        "type": "custom"
      },
      {
        "current": {
          "text": "global1_5",
          "value": "global1_5"
        },
        "includeAll": false,
        "label": "Grid",
        "name": "grid",
        "options": [
          {
            "selected": true,
            "text": "1.5",
            "value": "global1_5"
          }
        ],
        "query": "1.5 : global1_5",
        "type": "custom"
      },
      {
        "current": {
          "text": [
            "africa_unimodal_season",
            "africa_unimodal_shifted_season",
            "africa_bimodal_season"
          ],
          "value": [
            "africa_unimodal_season",
            "africa_unimodal_shifted_season",
            "africa_bimodal_season"
          ]
        },
        "includeAll": false,
        "label": "Region",
        "multi": true,
        "name": "region",
        "options": [
          {
            "selected": true,
            "text": "Africa Bimodal",
            "value": "africa_bimodal_season"
          },
          {
            "selected": true,
            "text": "Africa Unimodal",
            "value": "africa_unimodal_season"
          },
          {
            "selected": true,
            "text": "Africa Unimodal Shifted",
            "value": "africa_unimodal_shifted_season"
          }
        ],
        "query": "Africa Bimodal : africa_bimodal_season, Africa Unimodal : africa_unimodal_season, Africa Unimodal Shifted : africa_unimodal_shifted_season",
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
          "text": "bdb60156ef2ae3cb28a5901e45ea7bb0",
          "value": "bdb60156ef2ae3cb28a5901e45ea7bb0"
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
  "title": "Advanced Forecast Evaluation Maps",
  "uid": "ffojsn16cxs00e",
  "version": 1,
  "weekStart": ""
}
