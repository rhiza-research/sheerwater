local f_2016_2022_precip_sql = importstr './assets/2016-2022-precip.sql';
local colors_js = importstr './assets/colors.js';
local ee2jzeymn1o8wf_5_afterRender_js = importstr './assets/ee2jzeymn1o8wf-5-afterRender.js';
local ee2jzeymn1o8wf_5_content_md = importstr './assets/ee2jzeymn1o8wf-5-content.md';
local ee2jzeymn1o8wf_7_afterRender_js = importstr './assets/ee2jzeymn1o8wf-7-afterRender.js';
local ee2jzeymn1o8wf_7_content_txt = importstr './assets/ee2jzeymn1o8wf-7-content.txt';
local ee2jzeymn1o8wf_monthly_precipitation_results_params_js = importstr './assets/ee2jzeymn1o8wf-monthly-precipitation-results-params.js';
local ee2jzeymn1o8wf_monthly_precipitation_results_script_js = importstr './assets/ee2jzeymn1o8wf-monthly-precipitation-results-script.js';
local ee2jzeymn1o8wf_monthly_temperature_results_params_js = importstr './assets/ee2jzeymn1o8wf-monthly-temperature-results-params.js';
local ee2jzeymn1o8wf_monthly_temperature_results_script_js = importstr './assets/ee2jzeymn1o8wf-monthly-temperature-results-script.js';
local ee2jzeymn1o8wf_weekly_precipitation_results_params_txt = importstr './assets/ee2jzeymn1o8wf-weekly-precipitation-results-params.txt';
local ee2jzeymn1o8wf_weekly_precipitation_results_script_js = importstr './assets/ee2jzeymn1o8wf-weekly-precipitation-results-script.js';
local ee2jzeymn1o8wf_weekly_temperature_results_params_txt = importstr './assets/ee2jzeymn1o8wf-weekly-temperature-results-params.txt';
local ee2jzeymn1o8wf_weekly_temperature_results_script_js = importstr './assets/ee2jzeymn1o8wf-weekly-temperature-results-script.js';

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
  "id": 25,
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
      "id": 5,
      "options": {
        "afterRender": ee2jzeymn1o8wf_5_afterRender_js,
        "content": ee2jzeymn1o8wf_5_content_md,
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
      "pluginVersion": "6.0.0",
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
      "collapsed": true,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 4
      },
      "id": 7,
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
                    "color": "green"
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
            "h": 12,
            "w": 24,
            "x": 0,
            "y": 5
          },
          "id": 8,
          "options": {
            "afterRender": ee2jzeymn1o8wf_7_afterRender_js,
            "content": ee2jzeymn1o8wf_7_content_txt,
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
          "pluginVersion": "6.0.0",
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
        }
      ],
      "title": "Notes and Caveats",
      "type": "row"
    },
    {
      "collapsed": false,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 5
      },
      "id": 9,
      "panels": [],
      "title": "Metrics",
      "type": "row"
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
        "h": 12,
        "w": 12,
        "x": 0,
        "y": 6
      },
      "id": 1,
      "options": {
        "allData": {},
        "config": {},
        "data": [],
        "imgFormat": "png",
        "layout": {
          "font": {
            "family": "Inter, sans-serif"
          },
          "margin": {
            "b": 4,
            "l": 0,
            "r": 0,
            "t": 0
          },
          "paper_bgcolor": "#F4F5F5",
          "plog_bgcolor": "#F4F5F5",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            },
            "pad": {
              "b": 30
            },
            "text": "Weekly",
            "x": 0,
            "xanchor": "left"
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
        "onclick": "",
        "resScale": 2,
        "script": ee2jzeymn1o8wf_weekly_temperature_results_params_txt + colors_js + ee2jzeymn1o8wf_weekly_temperature_results_script_js,
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
          "rawSql": "select * from \"$tmp2m_tab_name\"\n ${time_filter_query}",
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
          "rawSql": "select '${baseline}'",
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
        "h": 12,
        "w": 12,
        "x": 12,
        "y": 6
      },
      "id": 2,
      "options": {
        "allData": {},
        "config": {},
        "data": [],
        "imgFormat": "png",
        "layout": {
          "font": {
            "family": "Inter, sans-serif"
          },
          "margin": {
            "b": 0,
            "l": 0,
            "r": 0,
            "t": 0
          },
          "paper_bgcolor": "#F4F5F5",
          "plog_bgcolor": "#F4F5F5",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            },
            "pad": {
              "b": 30
            },
            "test": "blah",
            "text": "Weekly",
            "x": 0,
            "xanchor": "left"
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
        "onclick": "",
        "resScale": 0,
        "script": ee2jzeymn1o8wf_weekly_precipitation_results_params_txt + colors_js + ee2jzeymn1o8wf_weekly_precipitation_results_script_js,
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
          "rawSql": "select * from \"$precip_tab_name\"\n ${time_filter_query}",
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
          "rawSql": "select '${baseline}'",
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
        "h": 5,
        "w": 12,
        "x": 0,
        "y": 18
      },
      "id": 4,
      "options": {
        "allData": {},
        "config": {},
        "data": [],
        "imgFormat": "png",
        "layout": {
          "font": {
            "family": "Inter, sans-serif"
          },
          "margin": {
            "b": 0,
            "l": 0,
            "r": 0,
            "t": 0
          },
          "paper_bgcolor": "#F4F5F5",
          "plog_bgcolor": "#F4F5F5",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            },
            "pad": {
              "b": 30
            },
            "x": 0,
            "xanchor": "left"
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
        "onclick": "",
        "resScale": 0,
        "script": ee2jzeymn1o8wf_monthly_temperature_results_params_js + colors_js + ee2jzeymn1o8wf_monthly_temperature_results_script_js,
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
          "rawSql": "select * from \"$seasonal_tmp2m_tab_name\"\n ${time_filter_query}",
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
          "rawSql": "select '${baseline}'",
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
        "h": 5,
        "w": 12,
        "x": 12,
        "y": 18
      },
      "id": 3,
      "options": {
        "allData": {},
        "config": {},
        "data": [],
        "imgFormat": "png",
        "layout": {
          "font": {
            "family": "Inter, sans-serif"
          },
          "margin": {
            "b": 0,
            "l": 0,
            "r": 0,
            "t": 0
          },
          "paper_bgcolor": "#F4F5F5",
          "plog_bgcolor": "#F4F5F5",
          "title": {
            "align": "left",
            "automargin": true,
            "font": {
              "color": "black",
              "family": "Inter, sans-serif",
              "size": 14,
              "weight": 500
            },
            "pad": {
              "b": 30
            },
            "x": 0,
            "xanchor": "left"
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
        "onclick": "",
        "resScale": 0,
        "script": ee2jzeymn1o8wf_monthly_precipitation_results_params_js + colors_js + ee2jzeymn1o8wf_monthly_precipitation_results_script_js,
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
          "rawSql": "select * from \"$seasonal_precip_tab_name\"\n ${time_filter_query}",
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
          "rawSql": "select '${baseline}'",
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
          "text": "acc",
          "value": "acc"
        },
        "includeAll": false,
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
            "text": "CRPS",
            "value": "crps"
          },
          {
            "selected": false,
            "text": "RMSE",
            "value": "rmse"
          },
          {
            "selected": true,
            "text": "ACC",
            "value": "acc"
          },
          {
            "selected": false,
            "text": "Bias",
            "value": "bias"
          },
          {
            "selected": false,
            "text": "SMAPE",
            "value": "smape"
          },
          {
            "selected": false,
            "text": "SEEPS",
            "value": "seeps"
          },
          {
            "selected": false,
            "text": "Heidke (1/5/10/20mm)",
            "value": "heidke-1-5-10-20"
          },
          {
            "selected": false,
            "text": "POD 1mm",
            "value": "pod-1"
          },
          {
            "selected": false,
            "text": "POD 5mm",
            "value": "pod-5"
          },
          {
            "selected": false,
            "text": "POD 10mm",
            "value": "pod-10"
          },
          {
            "selected": false,
            "text": "FAR 1mm",
            "value": "far-1"
          },
          {
            "selected": false,
            "text": "FAR 5mm",
            "value": "far-5"
          },
          {
            "selected": false,
            "text": "FAR 10mm",
            "value": "far-10"
          },
          {
            "selected": false,
            "text": "ETS 1mm",
            "value": "ets-1"
          },
          {
            "selected": false,
            "text": "ETS 5mm",
            "value": "ets-5"
          },
          {
            "selected": false,
            "text": "ETS 10mm",
            "value": "ets-10"
          }
        ],
        "query": "MAE : mae, CRPS : crps, RMSE : rmse, ACC : acc, Bias : bias, SMAPE : smape, SEEPS : seeps, Heidke (1/5/10/20mm) : heidke-1-5-10-20, POD 1mm : pod-1, POD 5mm : pod-5, POD 10mm : pod-10, FAR 1mm : far-1, FAR 5mm : far-5, FAR 10mm : far-10, ETS 1mm : ets-1, ETS 5mm : ets-5, ETS 10mm : ets-10",
        "type": "custom"
      },
      {
        "current": {
          "text": "Clim 1985-2014",
          "value": "climatology_2015"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select \nforecast as __value,\ncase\n when forecast = 'salient' then 'Salient' \nwhen forecast = 'climatology_2015' then 'Clim 1985-2014' \nwhen forecast = 'climatology_trend_2015' then 'Clim + Trend' \nwhen forecast = 'climatology_rolling' then 'Clim Rolling' \nwhen forecast = 'ecmwf_ifs_er' then 'ECMWF IFS ER' \nwhen forecast = 'ecmwf_ifs_er_debiased' then 'ECMWF IFS ER Debiased' \nwhen forecast = 'fuxi' then 'FuXi S2S' \n else forecast\nend as __text\nfrom \"${precip_tab_name_baseline}\" where week1 is not null",
        "includeAll": false,
        "label": "Baseline",
        "name": "baseline",
        "options": [],
        "query": "select \nforecast as __value,\ncase\n when forecast = 'salient' then 'Salient' \nwhen forecast = 'climatology_2015' then 'Clim 1985-2014' \nwhen forecast = 'climatology_trend_2015' then 'Clim + Trend' \nwhen forecast = 'climatology_rolling' then 'Clim Rolling' \nwhen forecast = 'ecmwf_ifs_er' then 'ECMWF IFS ER' \nwhen forecast = 'ecmwf_ifs_er_debiased' then 'ECMWF IFS ER Debiased' \nwhen forecast = 'fuxi' then 'FuXi S2S' \n else forecast\nend as __text\nfrom \"${precip_tab_name_baseline}\" where week1 is not null",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "era5",
          "value": "era5"
        },
        "includeAll": false,
        "label": "Ground Truth",
        "name": "truth",
        "options": [
          {
            "selected": true,
            "text": "ERA5",
            "value": "era5"
          }
        ],
        "query": "ERA5 : era5",
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
          "text": "africa",
          "value": "africa"
        },
        "includeAll": false,
        "label": "Region",
        "name": "region",
        "options": [
          {
            "selected": false,
            "text": "Global",
            "value": "global"
          },
          {
            "selected": true,
            "text": "Africa",
            "value": "africa"
          },
          {
            "selected": false,
            "text": "East Africa",
            "value": "east_africa"
          },
          {
            "selected": false,
            "text": "Nigeria",
            "value": "nigeria"
          },
          {
            "selected": false,
            "text": "Kenya",
            "value": "kenya"
          },
          {
            "selected": false,
            "text": "Ethiopia",
            "value": "ethiopia"
          },
          {
            "selected": false,
            "text": "Chile",
            "value": "chile"
          },
          {
            "selected": false,
            "text": "Bangladesh",
            "value": "bangladesh"
          },
          {
            "selected": false,
            "text": "CONUS",
            "value": "conus"
          }
        ],
        "query": "Global : global, Africa : africa, East Africa : east_africa, Nigeria : nigeria, Kenya : kenya, Ethiopia : ethiopia, Chile : chile, Bangladesh : bangladesh,  CONUS : conus",
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
          "text": "603561dbe136e8d30da05b8eb27b3708",
          "value": "603561dbe136e8d30da05b8eb27b3708"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('summary_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_tmp2m')",
        "hide": 2,
        "includeAll": false,
        "name": "tmp2m_tab_name",
        "options": [],
        "query": "select * from md5('summary_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_tmp2m')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "2585031bf3d9d2576182203d8d37227d",
          "value": "2585031bf3d9d2576182203d8d37227d"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('seasonal_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_tmp2m')",
        "hide": 2,
        "includeAll": false,
        "name": "seasonal_tmp2m_tab_name",
        "options": [],
        "query": "select * from md5('seasonal_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_tmp2m')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "ded8af931c81e7f097229a75c4e4d0f0",
          "value": "ded8af931c81e7f097229a75c4e4d0f0"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": f_2016_2022_precip_sql,
        "hide": 2,
        "includeAll": false,
        "name": "precip_tab_name",
        "options": [],
        "query": f_2016_2022_precip_sql,
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "371a2b24d7253ce68d31373c3e388bff",
          "value": "371a2b24d7253ce68d31373c3e388bff"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('seasonal_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "seasonal_precip_tab_name",
        "options": [],
        "query": "select * from md5('seasonal_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
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
          "text": "f0cccbbc24afc419c5ef96b316a3cfd7",
          "value": "f0cccbbc24afc419c5ef96b316a3cfd7"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('biweekly_summary_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_tmp2m')",
        "hide": 2,
        "includeAll": false,
        "name": "tmp2m_tab_name_biweekly",
        "options": [],
        "query": "select * from md5('biweekly_summary_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_tmp2m')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "168940b89ad339e3e76045958cb8ea3e",
          "value": "168940b89ad339e3e76045958cb8ea3e"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('biweekly_summary_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "precip_tab_name_biweekly",
        "options": [],
        "query": "select * from md5('biweekly_summary_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "ded8af931c81e7f097229a75c4e4d0f0",
          "value": "ded8af931c81e7f097229a75c4e4d0f0"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": f_2016_2022_precip_sql,
        "hide": 2,
        "includeAll": false,
        "name": "precip_tab_name_baseline",
        "options": [],
        "query": f_2016_2022_precip_sql,
        "refresh": 2,
        "regex": "",
        "type": "query"
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
  "title": "Forecast Evaluation",
  "uid": "ee2jzeymn1o8wf",
  "version": 9,
  "weekStart": ""
}