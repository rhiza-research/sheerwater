// EXTERNAL:conditional_slice.js


let series = data.series[0];
// get fields by name
let estimateField = series.fields.find(f => f.name === "estimate");
let truthField    = series.fields.find(f => f.name === "truth");
let precipField   = series.fields.find(f => f.name === "precip");
// get values
let estimate = estimateField.values || estimateField.values.buffer;
let truth    = truthField.values || truthField.values.buffer;
let precip   = precipField.values || precipField.values.buffer;

// get grafana dashboard variables
let sliceValue    = parseFloat(variables.slice.current.value);
let conditionOn   = variables.condition_on.current.value; // "satellite" or "stations"
let satellite     = variables.satellite.current.text || variables.satellite.current.value;
let stations      = variables.stations.current.text || variables.stations.current.value;


let xValues = []; // plotted variable; not the condition variable
let counts  = []; // count of precipitation in the bin

for (let i = 0; i < estimate.length; i++) {
    let e = Number(estimate[i]);
    let t = Number(truth[i]);
    let p = Number(precip[i]);

    if (conditionOn === "satellite") {
        // condition on satellite (estimate), plot stations (truth)
        if (sliceValue >= e && sliceValue < e + 1) {
            xValues.push(t);
            counts.push(p);
        }
    } else if (conditionOn === "stations") {
        // condition on stations (truth), plot satellite (estimate)
        if (sliceValue >= t && sliceValue < t + 1) {
            xValues.push(e);
            counts.push(p);
        }
    }
}

// fill missing bins with 0
let minBin = Math.min(...xValues);
let maxBin = Math.max(...xValues);

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
    ? `${stations} (mm/day) given ${sliceValue} mm/day ${satellite}`
    : `${satellite} (mm/day) given ${sliceValue} mm/day ${stations}`;

return {
    data: [
        {
            x: fullBins,
            y: fullCounts,
            type: "scatter",
            mode: "lines",
            fill: "tozeroy",
            line: { color: "grey" },
            hovertemplate: "%{x} mm/day<br>Count: %{y}<extra></extra>"
        }
    ],
    layout: {
        xaxis: { title: xlabel, type: "linear", autorange: true },
        yaxis: { title: "number of observations", type: "linear", autorange: true },
        margin: { t: 30, b: 50 }
    }
};
