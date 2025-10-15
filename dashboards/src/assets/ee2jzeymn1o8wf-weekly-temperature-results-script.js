// EXTERNAL({panel_id:"weekly-temperature-results"}):ee2jzeymn1o8wf-weekly-temperature-results-script.js
let series = data.series[0]
if (series.length == 0) {
    return {
        data: []
    }
}
let maximize;
if (params.enable_maximize) {
    let metric = variables['metric'].current.value;
    if (metric.startsWith('heidke') || metric.startsWith('pod') || metric.startsWith('ets')) {
        maximize = true; // these metrics are maximized
    } else {
        maximize = false;
    }
}

if (variables.time_grouping.current.value != 'None') {
    idx = 1
} else {
    idx = 0
}
forecasts = series.fields[1 + idx].values
values = []
skills = []
header = ["Forecast"]
orig_header = ["forecast"]
let max = -Infinity;
let min = Infinity;

skill_baseline_idx = null;
for (var i = 0; i < forecasts.length; i = i + 1) {
    if (variables.baseline.current.value == forecasts[i]) {
        skill_baseline_idx = i
    }
}

baseline_values = []
for (var i = 2 + idx; i < series.fields.length; i = i + 1) {
    baseline_values.push(series.fields[i].values[skill_baseline_idx])
}

let skill_val;
for (var i = 2 + idx; i < series.fields.length; i = i + 1) {
    v = series.fields[i].values
    skill_values = []
    for (var j = 0; j < v.length; j++) {
        let val = parseFloat(v[j]);
        if (val > max) {
            max = val;
        }
        if (val < min) {
            min = val;
        }

        if (params.enable_maximize & maximize){
            // Compute the skill of the distance from 1
            skill_val = (1 - ((1-val) / (1-baseline_values[(i - 2 - idx)])));
            skill_values.push(skill_val)

        } else {
            skill_val = (1 - (val / baseline_values[(i - 2 - idx)]));
            skill_values.push(skill_val)
        }
    }
    values.push(v)
    skills.push(skill_values)
    header.push("Week " + (i - 1 - idx))
    orig_header.push("week" + (i - 1 - idx))
}

console.log(skills)

// round to two decimal places
values = values.map((week) => week.map((x) => { if (x) { return x.toFixed(2) } else { return '-' } }))
forecasts = forecasts.map((forecast) => forecast.replaceAll('_', ' ').split(' ').map((word) => word[0].toUpperCase() + word.substring(1)).join(' '))
values.unshift(forecasts)

// Define a dictionary for custom renaming
const renameDict = {
    "Ecmwf Ifs Er": "ECMWF IFS ER",
    "Ecmwf Ifs Er Debiased": "ECMWF IFS ER Debiased",
    "Salient": "AI-Enhanced NWP",
    "Fuxi": "FuXi S2S",
    "Climatology 2015": "Climatology 1985-2014",
    "Climatology Trend 2015": "Climatology 1985-2014 w/Trend"
};

// Apply custom renaming to the first column of cellValues
values[0] = values[0].map(value => renameDict[value] || value);

// assign the forecast colors
forecast_colors = []
for (var i = 0; i < forecasts.length; i++) {
    forecast_colors.push('rgba(0,0,0,0)')
}

let skill_colors = []
// assign the skill colors
let colorMap, cmax, cmin;
// if (variables['metric'].current.value == 'bias') {
//     colormap = 'balance';
//     cmax = max;
//     cmin = min;
// }
// else {
//     colormap = 'rdbu';
//     cmax = 1;
//     cmin = -1;
// }
// Determine color map and ranges based on metric
switch (variables['metric'].current.value) {
    case 'bias':
        colorMap = 'BuRd';
        [cmin, cmax] = [min, max];
        break;
    case 'acc':
        colorMap = 'RdBu';
        [cmin, cmax] = [-1, 1];
        break;
    // Error metrics - smaller is better
    case 'mae':
    case 'crps':
    case 'rmse':
    case 'smape':
    case 'seeps':
        colorMap = 'RdBu';
        [cmin, cmax] = [-1, 1];
        break;
    // Skill score metrics - larger is better
    case 'heidke-1-5-10-20':
    case 'pod-1':
    case 'pod-5':
    case 'pod-10':
    case 'ets-1':
    case 'ets-5':
    case 'ets-10':
        colorMap = 'RdBu';
        [cmin, cmax] = [0, 1];
        break;
    // FAR metrics - smaller is better
    case 'far-1':
    case 'far-5':
    case 'far-10':
        colorMap = 'RdBu';
        [cmin, cmax] = [0, 1];
        break;
    default:
        colorMap = 'RdBu';
        [cmax, cmin] = [1, -1];
}

for (var i = 0; i < skills.length; i++) {
    let week_colors = [];
    for (var j = 0; j < skills[i].length; j++) {
        if (variables['metric'].current.value == 'acc' || variables['metric'].current.value == 'bias') {
            val = parseFloat(values[i + 1][j]);
        } else {
            val = parseFloat(skills[i][j]);
        }
        week_colors.push(getColor(val, cmin, cmax, colorMap))
    }
    skill_colors.push(week_colors)
}

// Turn the metrics into links
orig_forecasts = series.fields[1 + idx].values
metric = variables.metric.current.value
grid = variables.grid.current.value
region = variables.region.current.value
time_grouping = variables.time_grouping.current.value
time_filter = variables.time_filter.current.value
for (var i = 1; i < values.length; i++) {
    for (var j = 0; j < values[i].length; j++) {
        url = `d/ae39q2k3jv668d/plotly-maps?orgId=1&var-forecast=${orig_forecasts[j]}&var-metric=${metric}&var-lead=${orig_header[i]}&var-truth=era5&var-grid=${grid}&var-region=${region}&var-time_grouping=${time_grouping}&var-time_filter=${time_filter}`
        values[i][j] = `<a href="${url}">` + values[i][j] + '</a>'
    }
}

var units = ""
if (metric == 'mae' || metric == 'bias' || metric == 'crps' || metric == 'rmse') {
    units = " (" + params.units + ")"
}

return {
    data: [{
        type: 'table',
        header: {
            values: [...header.slice(0, 3), '', ...header.slice(3)], // Add empty column for divider
            align: ['left', 'right', 'right', 'right', 'right', 'right'],
            line: { width: 0, color: '#DBDDDE' },
            font: { family: "Inter, sans-serif", size: 14, weight: "bold" },
            fill: {
                color: ['rgba(0,0,0,0)']
            }
        },
        cells: {
            values: [...values.slice(0, 3), Array(values[0].length).fill(''), ...values.slice(3)], // Add empty column
            align: ['left', 'right', 'right', 'right', 'right', 'right'],
            line: { width: 1, color: "#DBDDDE" },
            font: { family: "Inter, sans-serif", size: 14, color: ["black"] },
            fill: {
                color: [
                    forecast_colors, 
                    ...skill_colors.slice(0, 2), 
                    Array(forecasts.length).fill('grey'), // Divider column
                    ...skill_colors.slice(2)
                ]
            },
            height: 35
        },
        columnwidth: params.columnwidth // Make divider column very thin
    }],
    layout: {
        title: {
            text: params.title + units,
            xanchor: 'left',
            x: 0
        }
    }
}
// return {
    // data: [{
    //     type: 'table',
    //     header: {
    //         values: header,
    //         align: ['left', 'right', 'right', 'right', 'right'],
    //         line: { width: 0, color: '#DBDDDE' },
    //         font: { family: "Inter, sans-serif", size: 14, weight: "bold" },
    //         fill: {
    //             color: ['rgba(0,0,0,0)']
    //         }
    //     },
    //     cells: {
    //         values: values,
    //         align: ['left', 'right', 'right', 'right', 'right'],
    //         line: { color: "#DBDDDE", width: 1 },
    //         font: { family: "Inter, sans-serif", size: 14, color: ["black"] },
    //         fill: {
    //             color: [forecast_colors, ...skill_colors]
    //         },
    //         height: 35

    //     },
    //     columnwidth: [1.2, 0.5, 0.5, 0.5, 0.5, 0.5]
    // }]
// }
