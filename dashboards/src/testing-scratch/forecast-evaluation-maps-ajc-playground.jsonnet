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
      "pluginVersion": "5.6.0",
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
        "h": 16,
        "w": 24,
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
        "onrelayout": "console.log(event)\n\nvar payload = event && event.data ? event.data : event\n\nif (!payload) {\n    console.log('plotly sync: missing payload', event)\n    return\n}\n\nvar zoomKey = Object.keys(payload).find((key) => key.endsWith('.zoom'))\nvar centerKey = Object.keys(payload).find((key) => key.endsWith('.center'))\n\nif (!zoomKey || !centerKey) {\n    console.log('plotly sync: missing zoom/center keys', Object.keys(payload))\n    return\n}\n\ndocument.last_zoom = payload[zoomKey];\ndocument.last_center = payload[centerKey];\n\nif (document._syncing_maps) {\n    console.log('plotly sync: already syncing')\n    return\n}\n\nvar graphDivs = []\nvar graphDiv = event && (event.graphDiv || event.plot || event.target)\nif (graphDiv && graphDiv.closest) {\n    graphDiv = graphDiv.closest('.js-plotly-plot')\n}\n\nif (graphDiv) {\n    graphDivs = [graphDiv]\n} else {\n    graphDivs = Array.from(document.querySelectorAll('.js-plotly-plot'))\n}\n\nvar mapIds = ['map', 'map2', 'map3', 'map4', 'map5', 'map6']\nvar updates = {}\n\nmapIds.forEach((mapId) => {\n    updates[`${mapId}.zoom`] = document.last_zoom\n    updates[`${mapId}.center`] = document.last_center\n})\n\nif (graphDivs.length) {\n    var tasks = graphDivs.map((div) => {\n        var plotly = null\n        if (typeof Plotly !== 'undefined' && typeof Plotly.relayout === 'function') {\n            plotly = Plotly\n        } else if (div && div._context) {\n            if (div._context.plotly && typeof div._context.plotly.relayout === 'function') {\n                plotly = div._context.plotly\n            } else if (div._context.Plotly && typeof div._context.Plotly.relayout === 'function') {\n                plotly = div._context.Plotly\n            }\n        }\n\n        if (!plotly) {\n            console.log('plotly sync: relayout unavailable', div)\n            return null\n        }\n\n        console.log('plotly sync: relayout', div)\n        return () => Promise.resolve(plotly.relayout(div, updates))\n    }).filter(Boolean)\n\n    if (!tasks.length) {\n        console.log('plotly sync: no relayout targets')\n        return\n    }\n\n    document._syncing_maps = true\n    Promise.all(tasks.map((run) => run())).finally(() => {\n        document._syncing_maps = false\n    })\n} else {\n    console.log('plotly sync: no plotly divs found')\n}\n",
        "resScale": 2,
        "script": "forecast = variables.forecast.current.value\nmetric = variables.metric.current.value\ngrid = variables.grid.current.value\n// region = variables.region.current.value\n// region = variables.forecast.current.value === \"salient\"\n//     ? \"africa\"\n//     : \"global\";\nregion = \"africa\"\nlead = variables.lead.current.value\ntime_grouping = variables.time_grouping.current.value\ntime = variables.time_filter.current.value\nzoom_region = variables.zoom_region ? variables.zoom_region.current.value : 'Global'\n\n\nif (time == 'None') {\n    time = '';\n} else {\n    time = '_' + time;\n}\n\ntry {\n    var xmlHttp = new XMLHttpRequest();\n    url = `https://terracotta.sheerwater.rhizaresearch.org/metadata/grouped_metric_2022-12-31_${forecast}_${grid}_${lead}_lsm_${metric}_${region}_True_2016-01-01_${time_grouping}_era5_precip${time}`\n    xmlHttp.open(\"GET\", url, false); // false for synchronous request\n    xmlHttp.send(null);\n\n    if (xmlHttp.status != 200) {\n        console.log(\"Error getting dataset metadata\");\n        return {};\n    }\n\n    console.log(\"Dataset exists\");\n} catch (error) {\n    // If we can't get this metric just return early\n    console.log(\"Error getting dataset metadata\");\n    console.log(error)\n    return {}\n}\n\ntry {\n    var xmlHttp = new XMLHttpRequest();\n    url = `https://terracotta.sheerwater.rhizaresearch.org/metadata/grouped_metric_2022-12-31_${forecast}_${grid}_${lead}_lsm_${metric}_${region}_True_2016-01-01_${time_grouping}_era5_tmp2m${time}`\n    xmlHttp.open(\"GET\", url, false); // false for synchronous request\n    xmlHttp.send(null);\n\n    if (xmlHttp.status != 200) {\n        console.log(\"Error getting temperature dataset metadata\");\n        return {};\n    }\n\n    console.log(\"Temperature dataset exists\");\n} catch (error) {\n    // If we can't get this metric just return early\n    console.log(\"Error getting temperature dataset metadata\");\n    console.log(error)\n    return {}\n}\n\n// For each forecast get the metadata so that we can construct a color bar\nif (variables.standardize_forecast_colors.current.value == \"true\") {\n    forecasts = variables.forecast.options.map((x) => x.value)\n} else {\n    forecasts = [forecast]\n}\n\n// For each forecast get the metadata so that we can construct a color bar\nif (variables.standardize_lead_colors.current.value == \"true\") {\n    leads = variables.lead.options.map((x) => x.value)\n} else {\n    leads = [lead]\n}\n\n\ncolor_min = 1e8\ncolor_max = 0\nforecasts.forEach(function (i) {\n    leads.forEach(function (j) {\n        try {\n            var xmlHttp = new XMLHttpRequest();\n            url = `https://terracotta.sheerwater.rhizaresearch.org/metadata/grouped_metric_2022-12-31_${i}_${grid}_${j}_lsm_${metric}_${region}_True_2016-01-01_${time_grouping}_era5_precip${time}`\n            xmlHttp.open(\"GET\", url, false); // false for synchronous request\n            xmlHttp.send(null);\n\n            f = JSON.parse(xmlHttp.responseText)\n            console.log(f);\n\n            f = JSON.parse(xmlHttp.responseText).percentiles[4]\n            if (f < color_min) {\n                color_min = f\n            }\n\n            nf = JSON.parse(xmlHttp.responseText).percentiles[94]\n            if (nf > color_max) {\n                color_max = nf\n            }\n        } catch (error) {\n\n        }\n\n    });\n});\n\nconsole.log(color_min)\nconsole.log(color_max)\n\nif (variables.metric.current.value == 'bias') {\n    if (Math.abs(color_min) > color_max) {\n        color_max = Math.abs(color_min)\n    } else {\n        color_min = color_max * -1\n    }\n    console.log(color_min)\n    console.log(color_max)\n    tera_cscale = 'brbg'\n} else if (variables.metric.current.value == 'acc') {\n    color_min = -1\n    color_max = 1\n    tera_cscale = 'rdbu'\n} else if (variables.metric.current.value == 'seeps') {\n    tera_cscale = 'reds'\n    color_min = 0\n    color_max = 2.0\n} else {\n    // set the terracotta colorscale\n    tera_cscale = 'reds'\n}\nstretch = `colormap=${tera_cscale}&stretch_range=[${color_min},${color_max}]`\n\n//Query the color scale\nvar xmlHttp = new XMLHttpRequest();\nurl = `https://terracotta.sheerwater.rhizaresearch.org/colormap?colormap=${tera_cscale}&stretch_range=[${color_min},${color_max}]&num_values=10`\nxmlHttp.open(\"GET\", url, false); // false for synchronous request\nxmlHttp.send(null);\n\nf = JSON.parse(xmlHttp.responseText)\ncscale = []\nfor (var i = 0; i < f.colormap.length; i++) {\n    rgb = `rgb(${f.colormap[i].rgba[0]},${f.colormap[i].rgba[1]},${f.colormap[i].rgba[2]})`\n    cscale.push([i / f.colormap.length + i * (.1 / (f.colormap.length - 1)), rgb])\n}\n\nconsole.log(cscale)\nconsole.log(color_min)\nconsole.log(color_max)\n\ntemp_color_min = 1e8\ntemp_color_max = 0\nforecasts.forEach(function (i) {\n    leads.forEach(function (j) {\n        try {\n            var xmlHttp = new XMLHttpRequest();\n            url = `https://terracotta.sheerwater.rhizaresearch.org/metadata/grouped_metric_2022-12-31_${i}_${grid}_${j}_lsm_${metric}_${region}_True_2016-01-01_${time_grouping}_era5_tmp2m${time}`\n            xmlHttp.open(\"GET\", url, false); // false for synchronous request\n            xmlHttp.send(null);\n\n            f = JSON.parse(xmlHttp.responseText).percentiles[4]\n            if (f < temp_color_min) {\n                temp_color_min = f\n            }\n\n            nf = JSON.parse(xmlHttp.responseText).percentiles[94]\n            if (nf > temp_color_max) {\n                temp_color_max = nf\n            }\n        } catch (error) {\n\n        }\n\n    });\n});\n\nif (variables.metric.current.value == 'bias') {\n    if (Math.abs(temp_color_min) > temp_color_max) {\n        temp_color_max = Math.abs(temp_color_min)\n    } else {\n        temp_color_min = temp_color_max * -1\n    }\n    temp_tera_cscale = 'rdbu_r'\n} else if (variables.metric.current.value == 'acc') {\n    temp_color_min = -1\n    temp_color_max = 1\n    temp_tera_cscale = 'rdbu'\n} else if (variables.metric.current.value == 'seeps') {\n    temp_tera_cscale = 'reds'\n    temp_color_min = 0\n    temp_color_max = 2.0\n} else {\n    temp_tera_cscale = 'reds'\n}\ntemp_stretch = `colormap=${temp_tera_cscale}&stretch_range=[${temp_color_min},${temp_color_max}]`\n\n//Query the color scale\nvar xmlHttp = new XMLHttpRequest();\nurl = `https://terracotta.sheerwater.rhizaresearch.org/colormap?colormap=${temp_tera_cscale}&stretch_range=[${temp_color_min},${temp_color_max}]&num_values=10`\nxmlHttp.open(\"GET\", url, false); // false for synchronous request\nxmlHttp.send(null);\n\nf = JSON.parse(xmlHttp.responseText)\ntemp_cscale = []\nfor (var i = 0; i < f.colormap.length; i++) {\n    rgb = `rgb(${f.colormap[i].rgba[0]},${f.colormap[i].rgba[1]},${f.colormap[i].rgba[2]})`\n    temp_cscale.push([i / f.colormap.length + i * (.1 / (f.colormap.length - 1)), rgb])\n}\n\nvar units = \"\"\nif (metric == 'mae' || metric == 'bias' || metric == 'crps' || metric == 'rmse') {\n    units = \" (mm/day)\"\n}\nvar temp_units = \"\"\nif (metric == 'mae' || metric == 'bias' || metric == 'crps' || metric == 'rmse') {\n    temp_units = \" (C)\"\n}\n\ncenter = { 'lat': 0, 'lon': 0 };\nzoom = 0\nif (zoom_region == 'Kenya') {\n    center = { 'lat': 0.0236, 'lon': 37.9062 }\n    zoom = 4.5\n} else if (zoom_region == 'Africa') {\n    center = { 'lat': 0, 'lon': 20 }\n    zoom = 1.8\n}\nif (document.last_zoom) {\n    zoom = document.last_zoom\n}\nif (document.last_center) {\n    center = document.last_center\n}\n\nvar sharedCenter = center\nvar sharedZoom = zoom\n\nvar leadOptions = variables.lead.options || []\nvar subplotLeads = leadOptions.map((option) => option.value)\nvar subplotLeadLabels = leadOptions\n    .map((option) => option.text || option.label || option.value)\nvar columnCount = subplotLeads.length || 1\nvar mapIds = Array.from({ length: columnCount * 2 }, (_, index) =>\n    index === 0 ? 'map' : `map${index + 1}`\n)\nvar data = []\nmapIds.forEach((mapId, index) => {\n    var isTemp = index >= columnCount\n    var isPrecipScale = index === 0\n    var isTempScale = index === columnCount\n    data.push({\n        type: 'scattermap',\n        lat: ['45.5017', '46.9027'],\n        lon: ['-73.5673', '-73.5673'],\n        mode: 'markers',\n        marker: {\n            size: 0,\n            showscale: isPrecipScale || isTempScale,\n            colorscale: isTemp ? temp_cscale : cscale,\n            cmin: isTemp ? temp_color_min : color_min,\n            cmax: isTemp ? temp_color_max : color_max,\n            colorbar: isTemp\n                ? (isTempScale\n                    ? { tickmode: 'auto', y: 0.25, len: 0.45 }\n                    : undefined)\n                : (isPrecipScale\n                    ? { y: 0.75, len: 0.45 }\n                    : undefined)\n        },\n        subplot: mapId\n    })\n})\n\nvar layoutMaps = {}\nvar gap = 0.01\nmapIds.forEach((mapId, index) => {\n    var colIndex = index % columnCount\n    var rowIndex = index < columnCount ? 0 : 1\n    var x0 = colIndex / columnCount + gap / 2\n    var x1 = (colIndex + 1) / columnCount - gap / 2\n    var rowGap = 0.04\n    var rowHeight = (1 - rowGap) / 2\n    var y0 = rowIndex === 0 ? rowHeight + rowGap : 0\n    var y1 = rowIndex === 0 ? 1 : rowHeight\n    layoutMaps[mapId] = {\n        domain: { x: [x0, x1], y: [y0, y1] },\n        style: 'open-street-map',\n        layers: [\n            {\n                opacity: 0.7,\n                sourcetype: \"raster\",\n                source: [\n                    index < 6\n                        ? `https://terracotta.sheerwater.rhizaresearch.org/singleband/grouped_metric_2022-12-31_${forecast}_${grid}_${subplotLeads[colIndex]}_lsm_${metric}_${region}_True_2016-01-01_${time_grouping}_era5_precip${time}/{z}/{x}/{y}.png?${stretch}`\n                        : `https://terracotta.sheerwater.rhizaresearch.org/singleband/grouped_metric_2022-12-31_${forecast}_${grid}_${subplotLeads[colIndex]}_lsm_${metric}_${region}_True_2016-01-01_${time_grouping}_era5_tmp2m${time}/{z}/{x}/{y}.png?${temp_stretch}`\n                ],\n                below: \"traces\",\n            },\n        ],\n        center: sharedCenter,\n        zoom: sharedZoom\n    }\n})\n\nreturn {\n    data: data,\n    layout:\n    {\n        dragmode: 'zoom',\n        grid: { rows: 2, columns: columnCount, pattern: 'independent' },\n        margin: { r: 0, t: 30, b: 40, l: 0 },\n        showlegend: false,\n        annotations: [\n            {\n                text: \"Precipitation results\" + units,\n                x: 0,\n                xanchor: 'left',\n                y: 1,\n                yanchor: 'bottom',\n                showarrow: false\n            },\n            {\n                text: \"Temperature results\" + temp_units,\n                x: 0,\n                xanchor: 'left',\n                y: 0.48,\n                yanchor: 'bottom',\n                showarrow: false\n            },\n            ...subplotLeadLabels.map((label, index) => ({\n                text: label,\n                x: (index + 0.5) / columnCount,\n                xanchor: 'center',\n                y: -0.02,\n                yanchor: 'top',\n                xref: 'paper',\n                yref: 'paper',\n                showarrow: false\n            }))\n        ],\n        ...layoutMaps\n    }\n}\n",
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
          "rawSql": "-- select * from (values ('${forecast}${lead}${metric}${region}${standardize_lead_colors}${standardize_forecast_colors}${time_grouping}${time_filter}') ) v(t)\nselect *\nfrom (\n    values (\n        '${forecast}${lead}${metric}'\n        ||\n        case when '${forecast}' = 'salient'\n             then 'africa'\n             else 'global'\n        end\n        || '${standardize_lead_colors}${standardize_forecast_colors}${time_grouping}${time_filter}'\n    )\n) v(t);",
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
          "text": "Africa",
          "value": "Africa"
        },
        "includeAll": false,
        "label": "Zoom Region",
        "name": "zoom_region",
        "options": [
          {
            "selected": false,
            "text": "Kenya",
            "value": "Kenya"
          },
          {
            "selected": true,
            "text": "Africa",
            "value": "Africa"
          },
          {
            "selected": false,
            "text": "Global",
            "value": "Global"
          }
        ],
        "query": "Kenya, Africa, Global",
        "type": "custom"
      },
      {
        "current": {
          "text": "salient",
          "value": "salient"
        },
        "includeAll": false,
        "label": "Forecast",
        "name": "forecast",
        "options": [
          {
            "selected": true,
            "text": "AI-Enhanced NWP",
            "value": "salient"
          },
          {
            "selected": false,
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
          "text": "bias",
          "value": "bias"
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
            "selected": false,
            "text": "ACC",
            "value": "acc"
          },
          {
            "selected": true,
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
          "text": "week3",
          "value": "week3"
        },
        "hide": 2,
        "includeAll": false,
        "label": "Lead",
        "name": "lead",
        "options": [
          {
            "selected": false,
            "text": "Week 1",
            "value": "week1"
          },
          {
            "selected": false,
            "text": "Week 2",
            "value": "week2"
          },
          {
            "selected": true,
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
          "text": "4b63bc5e443436de9c429493856bff93",
          "value": "4b63bc5e443436de9c429493856bff93"
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
  "title": "Forecast Evaluation Maps AJC playground",
  "uid": "df9xyzf2qsp34b",
  "version": 1,
  "weekStart": ""
}
