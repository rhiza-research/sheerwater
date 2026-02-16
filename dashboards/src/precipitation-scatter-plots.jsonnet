local auc_map_js = importstr './assets/auc_map.js';
local click_precip_pt_js = importstr './assets/click_precip_pt.js';
local ffc28h1tj93b4e_1_script_js = importstr './assets/ffc28h1tj93b4e-1-script.js';
local ffc28h1tj93b4e_11_script_js = importstr './assets/ffc28h1tj93b4e-11-script.js';
local precip_event_pie_js = importstr './assets/precip_event_pie.js';
local roc_curve_js = importstr './assets/roc_curve.js';

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
  "description": "Compare different sources of precipitation estimates in a scatter. ",
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
        "h": 10,
        "w": 22,
        "x": 0,
        "y": 0
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
        "onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n  const { type: eventType, data: eventData } = event;\n  const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n  switch (eventType) {\n    case 'click':\n      console.log('Click event:', eventData.points);\n      break;\n    case 'select':\n      console.log('Selection event:', eventData.range);\n      break;\n    case 'zoom':\n      console.log('Zoom event:', eventData);\n      break;\n    default:\n      console.log('Unhandled event type:', eventType, eventData);\n  }\n\n  console.log('Current time zone:', timeZone);\n  console.log('From time:', dayjs(variables.__from).format());\n  console.log('To time:', dayjs(variables.__to).format());\n\n  // Example of using locationService\n  // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n  console.error('Error in onclick handler:', error);\n}\n*/\n  ",
        "resScale": 2,
        "script": auc_map_js,
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
          "rawSql": "SELECT * FROM \"${auc_table}\"",
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
      "title": "Area under ROC curve by location",
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
        "h": 8,
        "w": 11,
        "x": 0,
        "y": 10
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
        "onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n  const { type: eventType, data: eventData } = event;\n  const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n  switch (eventType) {\n    case 'click':\n      console.log('Click event:', eventData.points);\n      break;\n    case 'select':\n      console.log('Selection event:', eventData.range);\n      break;\n    case 'zoom':\n      console.log('Zoom event:', eventData);\n      break;\n    default:\n      console.log('Unhandled event type:', eventType, eventData);\n  }\n\n  console.log('Current time zone:', timeZone);\n  console.log('From time:', dayjs(variables.__from).format());\n  console.log('To time:', dayjs(variables.__to).format());\n\n  // Example of using locationService\n  // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n  console.error('Error in onclick handler:', error);\n}\n*/\n  ",
        "resScale": 2,
        "script": roc_curve_js,
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
          "panelId": 1,
          "refId": "A"
        }
      ],
      "title": "ROC curve for ${region1}",
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
        "h": 8,
        "w": 11,
        "x": 11,
        "y": 10
      },
      "id": 12,
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
        "onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n  const { type: eventType, data: eventData } = event;\n  const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n  switch (eventType) {\n    case 'click':\n      console.log('Click event:', eventData.points);\n      break;\n    case 'select':\n      console.log('Selection event:', eventData.range);\n      break;\n    case 'zoom':\n      console.log('Zoom event:', eventData);\n      break;\n    default:\n      console.log('Unhandled event type:', eventType, eventData);\n  }\n\n  console.log('Current time zone:', timeZone);\n  console.log('From time:', dayjs(variables.__from).format());\n  console.log('To time:', dayjs(variables.__to).format());\n\n  // Example of using locationService\n  // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n  console.error('Error in onclick handler:', error);\n}\n*/\n  ",
        "resScale": 2,
        "script": roc_curve_js,
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
          "panelId": 11,
          "refId": "A"
        }
      ],
      "title": "ROC curve for ${region2}",
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
        "w": 11,
        "x": 0,
        "y": 18
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
        "onclick": click_precip_pt_js,
        "resScale": 2,
        "script": ffc28h1tj93b4e_1_script_js,
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
          "rawSql": "SELECT p.*\nFROM \"${pairwise_precip_tabs}\" p\nJOIN \"auc_region_labels/${grid}_africa\" r\n  ON p.lat = r.lat AND p.lon = r.lon\nWHERE r.country_region = '${region1}'\n",
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
      "title": "precip comparison for ${region1}",
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
        "w": 11,
        "x": 11,
        "y": 18
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
        "onclick": click_precip_pt_js,
        "resScale": 2,
        "script": ffc28h1tj93b4e_11_script_js,
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
          "rawSql": "SELECT p.*\nFROM \"${pairwise_precip_tabs}\" p\nJOIN \"auc_region_labels/${grid}_africa\" r\n  ON p.lat = r.lat AND p.lon = r.lon\nWHERE r.country_region = '${region2}'\n",
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
      "title": "precip comparison for ${region2}",
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
        "h": 8,
        "w": 11,
        "x": 0,
        "y": 27
      },
      "id": 3,
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
        "onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n  const { type: eventType, data: eventData } = event;\n  const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n  switch (eventType) {\n    case 'click':\n      console.log('Click event:', eventData.points);\n      break;\n    case 'select':\n      console.log('Selection event:', eventData.range);\n      break;\n    case 'zoom':\n      console.log('Zoom event:', eventData);\n      break;\n    default:\n      console.log('Unhandled event type:', eventType, eventData);\n  }\n\n  console.log('Current time zone:', timeZone);\n  console.log('From time:', dayjs(variables.__from).format());\n  console.log('To time:', dayjs(variables.__to).format());\n\n  // Example of using locationService\n  // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n  console.error('Error in onclick handler:', error);\n}\n*/\n  ",
        "resScale": 2,
        "script": precip_event_pie_js,
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
          "panelId": 1,
          "refId": "A"
        }
      ],
      "title": "Counts for event in ${region1}",
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
        "h": 8,
        "w": 11,
        "x": 11,
        "y": 27
      },
      "id": 6,
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
        "onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n  const { type: eventType, data: eventData } = event;\n  const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n  switch (eventType) {\n    case 'click':\n      console.log('Click event:', eventData.points);\n      break;\n    case 'select':\n      console.log('Selection event:', eventData.range);\n      break;\n    case 'zoom':\n      console.log('Zoom event:', eventData);\n      break;\n    default:\n      console.log('Unhandled event type:', eventType, eventData);\n  }\n\n  console.log('Current time zone:', timeZone);\n  console.log('From time:', dayjs(variables.__from).format());\n  console.log('To time:', dayjs(variables.__to).format());\n\n  // Example of using locationService\n  // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n  console.error('Error in onclick handler:', error);\n}\n*/\n  ",
        "resScale": 2,
        "script": precip_event_pie_js,
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
          "panelId": 11,
          "refId": "A"
        }
      ],
      "title": "Counts for event in ${region2}",
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
        "allowCustomValue": false,
        "current": {
          "text": "ghana",
          "value": "ghana"
        },
        "description": "",
        "label": "region A",
        "name": "region1",
        "options": [
          {
            "selected": true,
            "text": "ghana",
            "value": "ghana"
          },
          {
            "selected": false,
            "text": "kenya",
            "value": "kenya"
          }
        ],
        "query": "ghana, kenya",
        "type": "custom"
      },
      {
        "current": {
          "text": "kenya",
          "value": "kenya"
        },
        "label": "region B",
        "name": "region2",
        "options": [
          {
            "selected": false,
            "text": "ghana",
            "value": "ghana"
          },
          {
            "selected": true,
            "text": "kenya",
            "value": "kenya"
          }
        ],
        "query": "ghana, kenya",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "imerg",
          "value": "imerg"
        },
        "description": "precip satellite data source",
        "label": "satellite",
        "name": "satellite",
        "options": [
          {
            "selected": true,
            "text": "imerg",
            "value": "imerg"
          },
          {
            "selected": false,
            "text": "chirps",
            "value": "chirps"
          }
        ],
        "query": "imerg, chirps",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "tahmo_avg",
          "value": "tahmo_avg"
        },
        "description": "",
        "label": "stations",
        "name": "station",
        "options": [
          {
            "selected": true,
            "text": "tahmo_avg",
            "value": "tahmo_avg"
          }
        ],
        "query": "tahmo_avg",
        "type": "custom"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "global1_5",
          "value": "global1_5"
        },
        "hide": 1,
        "name": "grid",
        "options": [
          {
            "selected": true,
            "text": "global1_5",
            "value": "global1_5"
          },
          {
            "selected": false,
            "text": "global0_25",
            "value": "global0_25"
          }
        ],
        "query": "global1_5, global0_25",
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
          "text": [
            "$__all"
          ],
          "value": [
            "$__all"
          ]
        },
        "description": "",
        "includeAll": true,
        "label": "months of year",
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
        "allowCustomValue": false,
        "current": {
          "text": "False",
          "value": "False"
        },
        "description": "whether to plot points as density",
        "label": "density",
        "name": "density",
        "options": [
          {
            "selected": false,
            "text": "True",
            "value": "True"
          },
          {
            "selected": true,
            "text": "False",
            "value": "False"
          }
        ],
        "query": "True, False",
        "type": "custom"
      },
      {
        "current": {
          "text": "5",
          "value": "5"
        },
        "label": "event threshold (mm / day)",
        "name": "event_thresh",
        "options": [
          {
            "selected": true,
            "text": "5",
            "value": "5"
          }
        ],
        "query": "5",
        "type": "textbox"
      },
      {
        "current": {
          "text": "bba50c6877a4fef450c4f3f367532ab6",
          "value": "bba50c6877a4fef450c4f3f367532ab6"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('pairwise_precip/${agg_days}_climatology_tahmo_avg_2015_2025_2025-12-31_${grid}_africa_2012-01-01_${station}_${satellite}')",
        "hide": 2,
        "name": "pairwise_precip_tabs",
        "options": [],
        "query": "select * from md5('pairwise_precip/${agg_days}_climatology_tahmo_avg_2015_2025_2025-12-31_${grid}_africa_2012-01-01_${station}_${satellite}')",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {
          "text": "8338ca36ac6eb88f94e7482e23fc6063",
          "value": "8338ca36ac6eb88f94e7482e23fc6063"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "bdz3m3xs99p1cf"
        },
        "definition": "select * from md5('auc_table/${agg_days}_${grid}_africa_${satellite}_${station}_climatology_tahmo_avg_2015_2025_month_of_year')",
        "hide": 2,
        "name": "auc_table",
        "options": [],
        "query": "select * from md5('auc_table/${agg_days}_${grid}_africa_${satellite}_${station}_climatology_tahmo_avg_2015_2025_month_of_year')",
        "refresh": 1,
        "regex": "",
        "type": "query"
      }
    ]
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "utc",
  "title": "Precipitation Scatter Plots",
  "uid": "ffc28h1tj93b4e",
  "version": 1,
  "weekStart": ""
}
