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
let sliceValue = parseFloat(variables.slice.current.value);
let conditionOn = variables.condition_on.current.value;
let satellite = String(variables.satellite.current.value).trim();
let stations = String(variables.stations.current.value).trim();

let xValues = []; // plotted variable; not the condition variable
let counts  = []; // count of precipitation in the bin

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

// fill missing bins with 0
let fullBins = [];
let fullCounts = [];

for (let bin = minBin; bin <= maxBin; bin++) {
    fullBins.push(bin);
    // get the count of precipitation in the bin if it exists, otherwise 0
    let idx = xValues.indexOf(bin);
    fullCounts.push(idx >= 0 ? counts[idx] : 0);
}

// x axis labels
let xlabel = conditionOn === "satellite"
    ? `${stations} when ${satellite} = ${sliceValue} mm/day`
    : `${satellite} when ${stations} = ${sliceValue} mm/day`;

// plot aesthetics
const FILL_COLOR   = "rgba(99, 179, 237, 0.25)";  // soft sky blue fill
const LINE_COLOR   = "rgba(49, 130, 206, 0.90)";  // stronger blue line
const SLICE_COLOR  = "rgba(237, 137, 54, 0.90)";  // warm amber vertical line
const FONT_FAMILY  = "'Inter', 'Helvetica Neue', Arial, sans-serif";
const FONT_COLOR  = "#777777";

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
        // warm vertical line at the slice value
        shapes: [
            {
                type: "line",
                x0: sliceValue,
                x1: sliceValue,
                y0: 0,
                y1: 1,
                yref: "paper",          // spans full plot height regardless of y scale
                line: {
                    color: SLICE_COLOR,
                    width: 2,
                    dash: "dot"
                }
            }
        ],
        // label the slice line
        annotations: [
            {
                x: sliceValue,
                y: 1,
                yref: "paper",
                text: `${conditionOn} = ${sliceValue} mm/day`,
                showarrow: false,
                xanchor: "left",
                yanchor: "bottom",
                xshift: 6,
                font: { color: SLICE_COLOR, size: 12, family: FONT_FAMILY }
            }
        ],
        margin: { t: 40, b: 70, l: 70, r: 30 },
        paper_bgcolor: "rgba(0,0,0,0)",  // transparent — inherits Grafana panel bg
        plot_bgcolor:  "rgba(0,0,0,0)"
    }
};
