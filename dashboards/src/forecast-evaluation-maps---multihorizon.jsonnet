local bfd145p7u3jlse_multimap_forecast_evaluation_call_function_js = importstr './assets/bfd145p7u3jlse-multimap-forecast-evaluation-call-function.js';
local bfd145p7u3jlse_multimap_forecast_evaluation_params_js = importstr './assets/bfd145p7u3jlse-multimap-forecast-evaluation-params.js';
local color_utilities_js = importstr './assets/color_utilities.js';
local maplibre_map_builder_js = importstr './assets/maplibre-map-builder.js';
local maplibre_multimap_layout_js = importstr './assets/maplibre-multimap-layout.js';
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
        "h": 25,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 9,
      "options": {
        "afterRender": bfd145p7u3jlse_multimap_forecast_evaluation_params_js + maplibre_map_builder_js + time_grouping_utilities_js + metrics_utilities_js + color_utilities_js + terracotta_dataset_utilities_js + maplibre_singlemap_orchestration_js + maplibre_multimap_orchestration_js + maplibre_multimap_layout_js + bfd145p7u3jlse_multimap_forecast_evaluation_call_function_js,
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
          "text": [
            "SOM",
            "KEN"
          ],
          "value": [
            "SOM",
            "KEN"
          ]
        },
        "hide": 2,
        "includeAll": false,
        "label": "Countries",
        "multi": true,
        "name": "countries",
        "options": [
          {
            "selected": false,
            "text": "Algeria",
            "value": "DZA"
          },
          {
            "selected": false,
            "text": "Angola",
            "value": "AGO"
          },
          {
            "selected": false,
            "text": "Benin",
            "value": "BEN"
          },
          {
            "selected": false,
            "text": "Botswana",
            "value": "BWA"
          },
          {
            "selected": false,
            "text": "Burkina Faso",
            "value": "BFA"
          },
          {
            "selected": false,
            "text": "Burundi",
            "value": "BDI"
          },
          {
            "selected": false,
            "text": "Cabo Verde",
            "value": "CPV"
          },
          {
            "selected": false,
            "text": "Cameroon",
            "value": "CMR"
          },
          {
            "selected": false,
            "text": "Central African Republic",
            "value": "CAF"
          },
          {
            "selected": false,
            "text": "Chad",
            "value": "TCD"
          },
          {
            "selected": false,
            "text": "Comoros",
            "value": "COM"
          },
          {
            "selected": false,
            "text": "Congo (Republic)",
            "value": "COG"
          },
          {
            "selected": false,
            "text": "Congo (DRC)",
            "value": "COD"
          },
          {
            "selected": false,
            "text": "Djibouti",
            "value": "DJI"
          },
          {
            "selected": false,
            "text": "Egypt",
            "value": "EGY"
          },
          {
            "selected": false,
            "text": "Equatorial Guinea",
            "value": "GNQ"
          },
          {
            "selected": false,
            "text": "Eritrea",
            "value": "ERI"
          },
          {
            "selected": false,
            "text": "Eswatini",
            "value": "SWZ"
          },
          {
            "selected": false,
            "text": "Ethiopia",
            "value": "ETH"
          },
          {
            "selected": false,
            "text": "Gabon",
            "value": "GAB"
          },
          {
            "selected": false,
            "text": "Gambia",
            "value": "GMB"
          },
          {
            "selected": false,
            "text": "Ghana",
            "value": "GHA"
          },
          {
            "selected": false,
            "text": "Guinea",
            "value": "GIN"
          },
          {
            "selected": false,
            "text": "Guinea-Bissau",
            "value": "GNB"
          },
          {
            "selected": false,
            "text": "Cote d'Ivoire",
            "value": "CIV"
          },
          {
            "selected": true,
            "text": "Kenya",
            "value": "KEN"
          },
          {
            "selected": false,
            "text": "Lesotho",
            "value": "LSO"
          },
          {
            "selected": false,
            "text": "Liberia",
            "value": "LBR"
          },
          {
            "selected": false,
            "text": "Libya",
            "value": "LBY"
          },
          {
            "selected": false,
            "text": "Madagascar",
            "value": "MDG"
          },
          {
            "selected": false,
            "text": "Malawi",
            "value": "MWI"
          },
          {
            "selected": false,
            "text": "Mali",
            "value": "MLI"
          },
          {
            "selected": false,
            "text": "Mauritania",
            "value": "MRT"
          },
          {
            "selected": false,
            "text": "Mauritius",
            "value": "MUS"
          },
          {
            "selected": false,
            "text": "Morocco",
            "value": "MAR"
          },
          {
            "selected": false,
            "text": "Mozambique",
            "value": "MOZ"
          },
          {
            "selected": false,
            "text": "Namibia",
            "value": "NAM"
          },
          {
            "selected": false,
            "text": "Niger",
            "value": "NER"
          },
          {
            "selected": false,
            "text": "Nigeria",
            "value": "NGA"
          },
          {
            "selected": false,
            "text": "Rwanda",
            "value": "RWA"
          },
          {
            "selected": false,
            "text": "Sao Tome and Principe",
            "value": "STP"
          },
          {
            "selected": false,
            "text": "Senegal",
            "value": "SEN"
          },
          {
            "selected": false,
            "text": "Seychelles",
            "value": "SYC"
          },
          {
            "selected": false,
            "text": "Sierra Leone",
            "value": "SLE"
          },
          {
            "selected": true,
            "text": "Somalia",
            "value": "SOM"
          },
          {
            "selected": false,
            "text": "South Africa",
            "value": "ZAF"
          },
          {
            "selected": false,
            "text": "South Sudan",
            "value": "SSD"
          },
          {
            "selected": false,
            "text": "Sudan",
            "value": "SDN"
          },
          {
            "selected": false,
            "text": "Tanzania",
            "value": "TZA"
          },
          {
            "selected": false,
            "text": "Togo",
            "value": "TGO"
          },
          {
            "selected": false,
            "text": "Tunisia",
            "value": "TUN"
          },
          {
            "selected": false,
            "text": "Uganda",
            "value": "UGA"
          },
          {
            "selected": false,
            "text": "Zambia",
            "value": "ZMB"
          },
          {
            "selected": false,
            "text": "Zimbabwe",
            "value": "ZWE"
          }
        ],
        "query": "Algeria : DZA, Angola : AGO, Benin : BEN, Botswana : BWA, Burkina Faso : BFA, Burundi : BDI, Cabo Verde : CPV, Cameroon : CMR, Central African Republic : CAF, Chad : TCD, Comoros : COM, Congo (Republic) : COG, Congo (DRC) : COD, Djibouti : DJI, Egypt : EGY, Equatorial Guinea : GNQ, Eritrea : ERI, Eswatini : SWZ, Ethiopia : ETH, Gabon : GAB, Gambia : GMB, Ghana : GHA, Guinea : GIN, Guinea-Bissau : GNB, Cote d'Ivoire : CIV, Kenya : KEN, Lesotho : LSO, Liberia : LBR, Libya : LBY, Madagascar : MDG, Malawi : MWI, Mali : MLI, Mauritania : MRT, Mauritius : MUS, Morocco : MAR, Mozambique : MOZ, Namibia : NAM, Niger : NER, Nigeria : NGA, Rwanda : RWA, Sao Tome and Principe : STP, Senegal : SEN, Seychelles : SYC, Sierra Leone : SLE, Somalia : SOM, South Africa : ZAF, South Sudan : SSD, Sudan : SDN, Tanzania : TZA, Togo : TGO, Tunisia : TUN, Uganda : UGA, Zambia : ZMB, Zimbabwe : ZWE",
        "type": "custom"
      },
      {
        "current": {
          "text": "ADM1",
          "value": "ADM1"
        },
        "hide": 2,
        "includeAll": false,
        "label": "Geo Level",
        "name": "geo_level",
        "options": [
          {
            "selected": true,
            "text": "ADM1",
            "value": "ADM1"
          },
          {
            "selected": false,
            "text": "ADM2",
            "value": "ADM2"
          },
          {
            "selected": false,
            "text": "ADM3",
            "value": "ADM3"
          }
        ],
        "query": "ADM1, ADM2, ADM3",
        "type": "custom"
      },
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
            "text": "AI-Enhanced NWP",
            "value": "salient"
          },
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
            "text": "Clim 1985-2014",
            "value": "climatology_2015"
          },
          {
            "selected": false,
            "text": "Clim + Trend",
            "value": "climatology_trend_2015"
          },
          {
            "selected": false,
            "text": "Clim Rolling",
            "value": "climatology_rolling"
          },
          {
            "selected": false,
            "text": "FuXi",
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
          }
        ],
        "query": "AI-Enhanced NWP : salient, ECMWF IFS ER : ecmwf_ifs_er, ECMWF IFS ER Debiased : ecmwf_ifs_er_debiased, Clim 1985-2014 : climatology_2015, Clim + Trend : climatology_trend_2015, Clim Rolling : climatology_rolling, FuXi : fuxi, GraphCast : graphcast, GenCast : gencast",
        "type": "custom"
      },
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
          "text": "week1",
          "value": "week1"
        },
        "hide": 2,
        "includeAll": false,
        "label": "Lead",
        "name": "lead",
        "options": [
          {
            "selected": true,
            "text": "Week 1",
            "value": "week1"
          },
          {
            "selected": false,
            "text": "Week 2",
            "value": "week2"
          },
          {
            "selected": false,
            "text": "Week 3",
            "value": "week3"
          },
          {
            "selected": false,
            "text": "Week 4",
            "value": "week4"
          },
          {
            "selected": false,
            "text": "Week 5",
            "value": "week5"
          },
          {
            "selected": false,
            "text": "Week 6",
            "value": "week6"
          }
        ],
        "query": "Week 1 : week1, Week 2 : week2, Week 3 : week3, Week 4 : week4, Week 5 : week5, Week 6 : week6",
        "type": "custom"
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
          "text": "global0_25",
          "value": "global0_25"
        },
        "includeAll": false,
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
        "current": {
          "text": "africa",
          "value": "africa"
        },
        "hide": 2,
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
          }
        ],
        "query": " Global : global, Africa : africa",
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
          "text": "6c235561d1756eec47cdfb4f614c11d9",
          "value": "6c235561d1756eec47cdfb4f614c11d9"
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
  "title": "Forecast Evaluation Maps - multihorizon",
  "uid": "bfd145p7u3jlse",
  "version": 1,
  "weekStart": ""
}
