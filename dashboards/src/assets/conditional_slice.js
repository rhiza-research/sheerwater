// EXTERNAL:conditional_slice.js

// get fields by name
let series = data.series[0];
let estimateField = series.fields.find(f => f.name === "estimate");
let truthField = series.fields.find(f => f.name === "truth");
let precipField = series.fields.find(f => f.name === "precip");

// get values
let estimate = estimateField.values || estimateField.values.buffer;
let truth  = truthField.values || truthField.values.buffer;
let precip = precipField.values || precipField.values.buffer;

// get grafana dashboard variables
let sliceValue  = parseFloat(variables.slice.current.value);
let conditionOn = variables.condition_on.current.value;
let satellite   = String(variables.satellite.current.value).trim();
let stations    = String(variables.stations.current.value).trim();
let confidence  = parseFloat(variables.confidence.current.value); // e.g. 10 → 10th/90th

let xValues = [];
let counts  = [];

for (let i = 0; i < estimate.length; i++) {
    let e = Number(estimate[i]);
    let t = Number(truth[i]);
    let p = Number(precip[i]);

    if (conditionOn === "satellite") {
        if (sliceValue >= e && sliceValue < e + 1) {
            xValues.push(t);
            counts.push(p);
        }
    } else if (conditionOn === "stations") {
        if (sliceValue >= t && sliceValue < t + 1) {
            xValues.push(e);
            counts.push(p);
        }
    }
}

let minBin = Math.min(...xValues);
let maxBin = Math.max(...xValues);

let fullBins   = [];
let fullCounts = [];

for (let bin = minBin; bin <= maxBin; bin++) {
    fullBins.push(bin);
    let idx = xValues.indexOf(bin);
    fullCounts.push(idx >= 0 ? counts[idx] : 0);
}

// compute percentile thresholds from the distribution
let loPct  = confidence / 100;           // e.g. 0.10
let hiPct  = 1 - confidence / 100;       // e.g. 0.90

let allObs = [];
for (let i = 0; i < fullBins.length; i++) {
    for (let j = 0; j < fullCounts[i]; j++) {
        allObs.push(fullBins[i]);
    }
}
allObs.sort((a, b) => a - b);

let loVal = allObs[Math.floor(loPct * allObs.length)];
let hiVal = allObs[Math.floor(hiPct * allObs.length)];

// x axis label
let xlabel = conditionOn === "satellite"
    ? `${stations} when ${satellite} = ${sliceValue} mm/day`
    : `${satellite} when ${stations} = ${sliceValue} mm/day`;

// plot aesthetics
const FILL_COLOR   = "rgba(99, 179, 237, 0.25)";
const LINE_COLOR   = "rgba(49, 130, 206, 0.90)";
const SLICE_COLOR  = "rgba(237, 137, 54, 0.90)";
const THRESH_COLOR = "rgba(100, 160, 50, 0.95)";   // yellow-green from histogram
const THRESH_FILL  = "rgba(154, 205, 100, 0.08)";
const FONT_FAMILY  = "'Inter', 'Helvetica Neue', Arial, sans-serif";
const FONT_COLOR   = "#777777";

return {
    data: [
        {
            x: fullBins,
            y: fullCounts,
            type: "scatter",
            mode: "lines",
            fill: "tozeroy",
            fillcolor: FILL_COLOR,
            line: { color: LINE_COLOR, width: 2.5 },
            hovertemplate: "<b>%{x} mm/day</b><br>number of observations: %{y}<extra></extra>"
        }
    ],
    layout: {
        font: {
            family: FONT_FAMILY,
            size: 13,
            color: FONT_COLOR
        },
        xaxis: {
            title: { text: xlabel, standoff: 14 },
            type: "linear",
            autorange: true,
            gridcolor: "rgba(255,255,255,0.08)",
            zerolinecolor: "rgba(255,255,255,0.15)",
            tickfont: { size: 12 }
        },
        yaxis: {
            title: { text: "number of observations", standoff: 14 },
            type: "linear",
            autorange: true,
            gridcolor: "rgba(255,255,255,0.08)",
            zerolinecolor: "rgba(255,255,255,0.15)",
            tickfont: { size: 12 }
        },
        shapes: [
            // green fill between percentile lines — behind everything
            {
                type: "rect",
                x0: loVal, x1: hiVal,
                y0: 0, y1: 1, yref: "paper",
                fillcolor: THRESH_FILL,
                line: { width: 0 },
                layer: "below"
            },
            // slice line
            {
                type: "line",
                x0: sliceValue, x1: sliceValue,
                y0: 0, y1: 1, yref: "paper",
                line: { color: SLICE_COLOR, width: 2, dash: "dot" }
            },
            // lower percentile line
            {
                type: "line",
                x0: loVal, x1: loVal,
                y0: 0, y1: 1, yref: "paper",
                line: { color: THRESH_COLOR, width: 1.5, dash: "dash" }
            },
            // upper percentile line
            {
                type: "line",
                x0: hiVal, x1: hiVal,
                y0: 0, y1: 1, yref: "paper",
                line: { color: THRESH_COLOR, width: 1.5, dash: "dash" }
            }
        ],
        annotations: [
            // slice label — vertical, along the line
            {
                x: sliceValue, y: 0.5, yref: "paper",
                text: `${conditionOn} = ${sliceValue} mm/day`,
                showarrow: false,
                xanchor: "left", yanchor: "middle",
                xshift: 6,
                textangle: -90,
                font: { color: SLICE_COLOR, size: 11, family: FONT_FAMILY }
            },
            // lower percentile label — vertical, along the line
            {
                x: loVal, y: 0.5, yref: "paper",
                text: `${Math.round(loPct * 100)}th pct: ${loVal} mm/day`,
                showarrow: false,
                xanchor: "left", yanchor: "middle",
                xshift: 6,
                textangle: -90,
                font: { color: THRESH_COLOR, size: 11, family: FONT_FAMILY }
            },
            // upper percentile label — vertical, along the line
            {
                x: hiVal, y: 0.5, yref: "paper",
                text: `${Math.round(hiPct * 100)}th pct: ${hiVal} mm/day`,
                showarrow: false,
                xanchor: "left", yanchor: "middle",
                xshift: 6,
                textangle: -90,
                font: { color: THRESH_COLOR, size: 11, family: FONT_FAMILY }
            }
        ],
        margin: { t: 40, b: 70, l: 70, r: 30 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor:  "rgba(0,0,0,0)"
    }
};
