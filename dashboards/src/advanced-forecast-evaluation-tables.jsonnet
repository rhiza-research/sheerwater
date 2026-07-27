local metrics_explainer_md = importstr './assets/metrics_explainer.md';
local summary_sql_tmpl = importstr './assets/advanced_eval_summary.sql';
local value_table_js = importstr './assets/advanced_eval_value_table.js';

local summarySql(regionOption) =
  std.strReplace(summary_sql_tmpl, '__REGION_OPTION__', regionOption);

local plotlyTarget(refId, rawSql) = {
  datasource: { type: 'grafana-postgresql-datasource', uid: 'bdz3m3xs99p1cf' },
  editorMode: 'code',
  format: 'table',
  rawQuery: true,
  rawSql: rawSql,
  refId: refId,
  sql: {
    columns: [{ parameters: [], type: 'function' }],
    groupBy: [{ property: { type: 'string' }, type: 'groupBy' }],
    limit: 50,
  },
};

local table_panel = {
  datasource: {
    default: true,
    type: 'grafana-postgresql-datasource',
    uid: 'bdz3m3xs99p1cf',
  },
  fieldConfig: { defaults: {}, overrides: [] },
  gridPos: { h: 18, w: 24, x: 0, y: 1 },
  id: 1,
  options: {
    allData: {},
    config: {},
    data: [],
    imgFormat: 'png',
    layout: {
      font: { family: 'Inter, sans-serif' },
      margin: { b: 4, l: 0, r: 0, t: 0 },
      paper_bgcolor: '#F4F5F5',
      plog_bgcolor: '#F4F5F5',
      title: {
        align: 'left',
        automargin: true,
        font: { color: 'black', family: 'Inter, sans-serif', size: 14, weight: 500 },
        pad: { b: 30 },
        text: 'Weekly',
        x: 0,
        xanchor: 'left',
      },
      xaxis: { automargin: true, autorange: true, type: 'date' },
      yaxis: { automargin: true, autorange: true },
    },
    onclick: '',
    resScale: 2,
    script: value_table_js,
    syncTimeRange: false,
    timeCol: '',
  },
  pluginVersion: '1.8.2',
  targets: [
    plotlyTarget('A', summarySql('$region_option')),
    plotlyTarget('B', summarySql('$region_option2')),
  ],
  title: '',
  transparent: true,
  type: 'nline-plotlyjs-panel',
};

local view_panels = [table_panel];

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
  "links": [
    {
      "asDropdown": false,
      "icon": "dashboard",
      "includeVars": true,
      "keepTime": true,
      "tags": [],
      "targetBlank": false,
      "title": "Good Cells vs Cell Cutoff",
      "tooltip": "",
      "type": "link",
      "url": "/d/sw-good-cells-cutoff/good-cells-vs-cell-cutoff"
    }
  ],
  "panels": [
    {
      "collapsed": true,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 16,
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
          "h": 5,
          "w": 24,
          "x": 0,
          "y": 0
        },
        "id": 17,
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
      }
      ],
      "title": "Metric description",
      "type": "row"
    }
  ] + view_panels + [
    {
      "collapsed": true,
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 19
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
            "afterRender": "// window.onload = function () {\n//     renderMathInElement(document.body, {\n//         delimiters: [\n//             { left: \"$$\", right: \"$$\", display: true },\n//             { left: \"\\\\(\", right: \"\\\\)\", display: false }\n//         ]\n//     });\n// };\n",
            "content": " - Models are evaluated from 2016-01-01 through 2022-12-31\n - All metrics are computed with the ECMWF land-sea mask that includes any cell with non-zero land coverage. \n - Spatial averages use latitude-based weighting.\n\n - Conservative regridding is used for both upscaling and downscaling forecasts. \n \n - ECMWF and FuXi S2S forecasts are native 1.5x1.5. \n \n - Salient, Graphcast, and Gencast are native 0.25x0.25.\n\n - Salient is conservatively regridded from their native 0.125 shifted grid to our round 0.25/1.5 grid. \n\n - All metrics are computed deterministically except for CRPS\n\n - Deterministic forecasts are derived from ensemble forecasts (ECMWF, FuXi, Gencast) through taking the average of the ensemble members\n\n - Deterministic forecasts are derived from quantile forecasts (Salient) by taking the median quantile.\n\n - The source for Gencast temperature forecasts was corrupted so they have been excluded.\n\n - Metrics that cannot be globally computed and then reduced (such as ACC, POD, FAR, ETC) are not available with time groupings.",
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
        }
      ],
      "title": "Notes and Caveats",
      "type": "row"
    }
  ],
  "preload": false,
  "refresh": "",
  "schemaVersion": 40,
  "tags": [],
  "templating": {
    "list": [
      {
        "description": "Advanced event metric to evaluate. The -thresh- value in the name is the actionable bar used for percent_good and for Average Metric cell coloring.",
        "current": {
          "text": "in_season_dry_spell-thresh-20",
          "value": "in_season_dry_spell-thresh-20"
        },
        "includeAll": false,
        "label": "Metric",
        "name": "metric",
        "options": [
          {
            "selected": false,
            "text": "Early season accumulation",
            "value": "early_season_accumulation-30d-thresh-30"
          },
          {
            "selected": false,
            "text": "Large rain days",
            "value": "big_rain_days-thresh-0.30"
          },
          {
            "selected": false,
            "text": "90th percentile rain",
            "value": "extreme_rain_days-thresh-0.30"
          },
          {
            "selected": true,
            "text": "In season dry spells",
            "value": "in_season_dry_spell-thresh-20"
          }
        ],
        "query": "Early season accumulation : early_season_accumulation-30d-thresh-30, Large rain days : big_rain_days-thresh-0.30, 90th percentile rain : extreme_rain_days-thresh-0.30, In season dry spells : in_season_dry_spell-thresh-20",
        "type": "custom"
      },
      {
        "description": "SQL column name for the selected metric (metric name with the -thresh-\u2026 suffix removed).",
        "current": {
          "text": "in_season_dry_spell",
          "value": "in_season_dry_spell"
        },
        "definition": "SELECT split_part('${metric}', '-thresh-', 1)",
        "hide": 2,
        "name": "metric_column",
        "options": [],
        "query": "SELECT split_part('${metric}', '-thresh-', 1)",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Which table summary to show. Percent Good Enough Members requires Prob Type = Probabilistic.",
        "current": {
          "text": "Percent Good Enough",
          "value": "percent_good"
        },
        "includeAll": false,
        "label": "View",
        "name": "table_view",
        "options": [
          {
            "selected": true,
            "text": "Percent Good Enough",
            "value": "percent_good"
          },
          {
            "selected": false,
            "text": "Percent Good Enough Members",
            "value": "percent_good_members"
          },
          {
            "selected": false,
            "text": "Good Enough Cells",
            "value": "good_enough_cells"
          },
          {
            "selected": false,
            "text": "Average Metric",
            "value": "metric"
          }
        ],
        "query": "Percent Good Enough : percent_good, Percent Good Enough Members : percent_good_members, Good Enough Cells : good_enough_cells, Average Metric : metric",
        "type": "custom"
      },
      {
        "description": "When Yes, stack Region 1 and Region 2 vertically (full width each). When No, show only Region 1.",
        "current": {
          "text": "No",
          "value": "no"
        },
        "includeAll": false,
        "label": "Compare",
        "name": "compare_regions",
        "options": [
          {
            "selected": false,
            "text": "Yes",
            "value": "yes"
          },
          {
            "selected": true,
            "text": "No",
            "value": "no"
          }
        ],
        "query": "Yes : yes, No : no",
        "type": "custom"
      },

      {
        "description": "How rows are grouped in time in the underlying tables (currently year).",
        "current": {
          "text": "year",
          "value": "year"
        },
        "hide": 2,
        "includeAll": false,
        "label": "Time Grouping",
        "name": "time_grouping",
        "options": [
          {
            "selected": true,
            "text": "Year",
            "value": "year"
          }
        ],
        "query": "Year : year",
        "type": "custom"
      },
      {
        "description": "Which years (or other time groups) to include when averaging cell scores.",
        "current": {
          "text": [
            "Y2016",
            "Y2017",
            "Y2018",
            "Y2019",
            "Y2020",
            "Y2021",
            "Y2022",
            "Y2023",
            "Y2024"
          ],
          "value": [
            "Y2016",
            "Y2017",
            "Y2018",
            "Y2019",
            "Y2020",
            "Y2021",
            "Y2022",
            "Y2023",
            "Y2024"
          ]
        },
        "definition": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"\nWHERE lead_day = 0",
        "label": "Years",
        "multi": true,
        "name": "time_option",
        "options": [],
        "query": "SELECT DISTINCT\n    initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,\n    COALESCE(time_grouping, 'None') AS __value\nFROM \"${unimodal_metric_name}\"\nWHERE lead_day = 0",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Observational rainfall product used as ground truth when the metric tables were built.",
        "current": {
          "text": "imerg_final",
          "value": "imerg_final"
        },
        "includeAll": false,
        "label": "Truth",
        "name": "truth",
        "options": [
          {
            "selected": false,
            "text": "ERA5",
            "value": "era5"
          },
          {
            "selected": true,
            "text": "IMERG",
            "value": "imerg_final"
          },
          {
            "selected": false,
            "text": "CHIRPS V3",
            "value": "chirps_v3"
          }
        ],
        "query": "ERA5 : era5, IMERG : imerg_final, CHIRPS V3 : chirps_v3",
        "type": "custom"
      },
      {
        "description": "Deterministic vs probabilistic forecast tables. Probabilistic is required for Percent Good Enough Members.",
        "current": {
          "text": "Deterministic",
          "value": "deterministic"
        },
        "includeAll": false,
        "label": "Prob",
        "name": "prob_type",
        "options": [
          {
            "selected": true,
            "text": "Deterministic",
            "value": "deterministic"
          },
          {
            "selected": false,
            "text": "Probabilistic",
            "value": "probabilistic"
          }
        ],
        "query": "Deterministic : deterministic, Probabilistic : probabilistic",
        "type": "custom"
      },
      {
        "description": "Internal: cache-key suffix for probabilistic metric tables.",
        "current": {
          "text": "",
          "value": ""
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT CASE WHEN '${prob_type}' = 'probabilistic' THEN '_prob_type-probabilistic' ELSE '' END",
        "hide": 2,
        "includeAll": false,
        "name": "prob_type_suffix",
        "options": [],
        "query": "SELECT CASE WHEN '${prob_type}' = 'probabilistic' THEN '_prob_type-probabilistic' ELSE '' END",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },

      {
        "description": "Spatial grid resolution of the metric tables (1.5\u00b0 or 0.25\u00b0).",
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
        "description": "Region typology used for the left/right region pickers (country, rainfall region, etc.).",
        "current": {
          "text": "country",
          "value": "country"
        },
        "includeAll": false,
        "label": "Region type",
        "name": "region",
        "options": [
          {
            "selected": true,
            "text": "Countries",
            "value": "country"
          },
          {
            "selected": false,
            "text": "Rainfall Region",
            "value": "rainfall_region"
          },
          {
            "selected": false,
            "text": "Subregion",
            "value": "subregion_region"
          },
          {
            "selected": false,
            "text": "Rainfall Region+Country",
            "value": "region"
          }
        ],
        "query": "Countries : country, Rainfall Region : rainfall_region, Subregion : subregion_region, Rainfall Region+Country : region",
        "type": "custom"
      },
      {
        "description": "Region shown in the left-hand table.",
        "current": {
          "text": "Ghana",
          "value": "ghana"
        },
        "definition": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day = 0",
        "label": "Region 1",
        "name": "region_option",
        "options": [],
        "query": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day = 0",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Second region for side-by-side comparison (used when Compare Regions is Yes).",
        "allowCustomValue": false,
        "current": {
          "text": "Kenya",
          "value": "kenya"
        },
        "definition": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day = 0",
        "label": "Region 2",
        "name": "region_option2",
        "options": [],
        "query": "SELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${unimodal_shifted_metric_name}\" WHERE lead_day = 0\n\nUNION\n\nSELECT DISTINCT initcap(replace(\"$region\", '_', ' ')) AS __text, \"$region\" AS __value\nFROM \"${bimodal_metric_name}\" WHERE lead_day = 0",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Internal: hashed SQL table for unimodal-season, observation-filtered events.",
        "current": {
          "text": "6ff92e4dd5349c6a59868964ce479a78",
          "value": "6ff92e4dd5349c6a59868964ce479a78"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_metric_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Internal: hashed SQL table for unimodal-season, forecast-filtered events.",
        "current": {
          "text": "84b7eb24707bfdf37a9ca90cd3364d8f",
          "value": "84b7eb24707bfdf37a9ca90cd3364d8f"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_metric_fcst_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Internal: hashed SQL table for shifted unimodal-season, observation-filtered events.",
        "current": {
          "text": "cb67961274c40387afc3ccd3875a70d1",
          "value": "cb67961274c40387afc3ccd3875a70d1"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_shifted_metric_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Internal: hashed SQL table for shifted unimodal-season, forecast-filtered events.",
        "current": {
          "text": "e190ca5c9e854e6edbccf8bb61ae9caa",
          "value": "e190ca5c9e854e6edbccf8bb61ae9caa"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "hide": 2,
        "includeAll": false,
        "name": "unimodal_shifted_fcst_metric_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Internal: hashed SQL table for bimodal-season, observation-filtered events.",
        "current": {
          "text": "525c534e50f08f616bcdba6d01630263",
          "value": "525c534e50f08f616bcdba6d01630263"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "hide": 2,
        "includeAll": false,
        "name": "bimodal_metric_name",
        "options": [],
        "query": "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Internal: hashed SQL table for bimodal-season, forecast-filtered events.",
        "current": {
          "text": "13d2b8ebd4b50a0371a63c2de25610b6",
          "value": "13d2b8ebd4b50a0371a63c2de25610b6"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "hide": 2,
        "includeAll": false,
        "name": "bimodal_metric_fcst_name",
        "options": [],
        "query": "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "description": "Only used by the Good Enough Cells view: a grid cell counts when its average percent_good is at or above this cutoff (0–1). Does not change Percent Good Enough or Average Metric.",
        "current": {
          "text": "0.75",
          "value": "0.75"
        },
        "label": "Cell cutoff",
        "name": "threshold",
        "options": [
          {
            "selected": true,
            "text": "0.75",
            "value": "0.75"
          }
        ],
        "query": "0.75",
        "type": "textbox"
      },
      {
        "description": "Which event filter to include: forecast-defined events, observation-defined events, or both (combined).",
        "current": {
          "text": "both",
          "value": "both"
        },

        "label": "Events",
        "name": "source",
        "options": [
          {
            "selected": false,
            "text": "Forecasted events",
            "value": "forecast"
          },
          {
            "selected": false,
            "text": "Observed events",
            "value": "obs"
          },
          {
            "selected": true,
            "text": "Both",
            "value": "both"
          }
        ],
        "query": "Forecasted events : forecast, Observed events : obs, Both : both",
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
  "title": "Advanced Forecast Evaluation Tables",
  "uid": "cfoumv7uu5xq8f",
  "version": 1,
  "weekStart": ""
}
