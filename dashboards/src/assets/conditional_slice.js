// EXTERNAL:conditional_slice.js
// Assume `data.series[0]` comes from your SQL query
let series = data.series[0];

// Get fields by name
let estimateField = series.fields.find(f => f.name === "estimate");
let truthField    = series.fields.find(f => f.name === "truth");
let precipField   = series.fields.find(f => f.name === "precip");

// Extract values
let estimate = estimateField.values || estimateField.values.buffer;
let truth    = truthField.values || truthField.values.buffer;
let precip   = precipField.values || precipField.values.buffer;

// Get user-selected slice value from Grafana variable
let sliceValue = parseFloat(variables.slice.current.value); // allow decimal slices
let satellite = variables.satellite.current.text || variables.satellite.current.value;

// --------------------
// Filter to the truth bin containing the slice
// --------------------
let filteredEstimate = [];
let filteredPrecip   = [];

for (let i = 0; i < estimate.length; i++) {
    let t = Number(truth[i]);
    if (sliceValue >= t && sliceValue < t + 1) {
        filteredEstimate.push(Number(estimate[i]));
        filteredPrecip.push(Number(precip[i]));
    }
}

// --------------------
// Fill missing estimate bins with 0
// --------------------
let minBin = Math.min(...filteredEstimate);
let maxBin = Math.max(...filteredEstimate);

let fullBins = [];
let fullCounts = [];

for (let e = minBin; e <= maxBin; e++) {
    let idx = filteredEstimate.indexOf(e);
    fullBins.push(e);
    fullCounts.push(idx >= 0 ? filteredPrecip[idx] : 0);
}

// --------------------
// Plotly line plot with grey fill
// --------------------
return {
    data: [
        {
            x: fullBins,
            y: fullCounts,
            type: "scatter",
            mode: "lines",
            fill: "tozeroy",
            line: { color: "grey" },
            hovertemplate: "Estimate: %{x}<br>Count: %{y}<extra></extra>"
        }
    ],
    layout: {
        xaxis: { 
            title: `${satellite} mm/day given ${sliceValue} mm/day`, 
            type: "linear",
            autorange: true
        },
        yaxis: { 
            title: "Counts", 
            type: "linear", 
            autorange: true 
        },
        margin: { t: 30, b: 50 }
    }
};
