local advanced_forecast_maps_onclick_js = importstr './assets/advanced_forecast_maps_onclick.js';
local advanced_groundtruth_map_js = importstr './assets/advanced_groundtruth_map.js';
local advanced_metrics_maps_js = importstr './assets/advanced_metrics_maps.js';
local ffojsn16cxs00e_5_lead_7_consts_js = importstr './assets/ffojsn16cxs00e-5-lead_7_consts.js';
local metrics_explainer_md = importstr './assets/metrics_explainer.md';

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
        "h": 8,
        "w": 19,
        "x": 0,
        "y": 0
      },
      "id": 6,
      "options": {
        "afterRender": "// window.onload = function () {\n//     renderMathInElement(document.body, {\n//         delimiters: [\n//             { left: \"$$\", right: \"$$\", display: true },\n//             { left: \"\\\\(\", right: \"\\\\)\", display: false }\n//         ]\n//     });\n// };\n",
        "content": metrics_explainer_md,
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
        "h": 8,
        "w": 5,
        "x": 19,
        "y": 0
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
          "grid": {
            "columns": "6,",
            "pattern": "independent",
            "rows": "2,"
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
        "onclick": advanced_forecast_maps_onclick_js,
        "resScale": 2,
        "script": advanced_groundtruth_map_js,
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
        "h": 14,
        "w": 24,
        "x": 0,
        "y": 8
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
          "grid": {
            "columns": "6,",
            "pattern": "independent",
            "rows": "2,"
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
        "onclick": advanced_forecast_maps_onclick_js,
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
          "text": "ecmwf_ifs_er",
          "value": "ecmwf_ifs_er"
        },
        "includeAll": false,
        "label": "Forecast",
        "name": "forecast",
        "options": [
          {
            "selected": true,
            "text": "ECMWF IFS ER",
            "value": "ecmwf_ifs_er"
          },
          {
            "selected": false,
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
            "text": "Early season accumulation",
            "value": "early_season_accumulation-30d"
          },
          {
            "selected": false,
            "text": "Large rain days",
            "value": "big_rain_days"
          },
          {
            "selected": false,
            "text": "In season dry spells",
            "value": "in_season_dry_spell"
          }
        ],
        "query": "Early season accumulation : early_season_accumulation-30d, Large rain days : big_rain_days, In season dry spells : in_season_dry_spell",
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
