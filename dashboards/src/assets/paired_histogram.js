// EXTERNAL:paired_histogram.js

let series = data.series[0];

// identify fields by name (robust to ordering)
let estimateField = series.fields.find(f => f.name === "estimate");
let truthField = series.fields.find(f => f.name === "truth");
let precipField = series.fields.find(f => f.name === "precip");

// get values
let estimate = estimateField.values || estimateField.values.buffer;
let truth = truthField.values || truthField.values.buffer;
let precip = precipField.values || precipField.values.buffer;

// get min and max across both estimate and truth
let min = Math.min(Math.min(...estimate), Math.min(...truth));
let max = Math.max(Math.max(...estimate), Math.max(...truth));
// create range from min to max in steps of 1
let range = [];
for (let v = min; v <= max; v += 1) {
    range.push(v);
}

let estimate_Vals = range;
let truth_Vals = range;
// create index for each value
let estimate_Index = new Map(estimate_Vals.map((v, i) => [v, i]));
let truth_Index = new Map(truth_Vals.map((v, i) => [v, i]));
// initialize full 2d histogram array with zeros
let bin_counts = Array.from({ length: estimate_Vals.length }, () =>
    Array.from({ length: truth_Vals.length }, () => 0)
);
// fill histogram with counts
for (let i = 0; i < estimate.length; i++) {
    let estimate_i = estimate_Index.get(estimate[i]);
    let truth_i = truth_Index.get(truth[i]);
    bin_counts[estimate_i][truth_i] = Math.log10(precip[i] + 1);
}

// get grafana dashboard variables
let stations  = String(variables.stations.current.value).trim();
let satellite = String(variables.satellite.current.value).trim();

// plot aesthetics
const FONT_FAMILY = "'Inter', 'Helvetica Neue', Arial, sans-serif";
const FONT_COLOR  = "#777777";

// heatmap color scale
const COLORSCALE = [
    [0.00, "rgba(10,  20,  50,  1.0)"],   // deep navy
    [0.15, "rgba(30,  80,  140, 1.0)"],   // ocean blue
    [0.35, "rgba(49,  130, 206, 1.0)"],   // sky blue
    [0.55, "rgba(56,  178, 172, 1.0)"],   // teal
    [0.75, "rgba(154, 205, 100, 1.0)"],   // yellow-green
    [1.00, "rgba(237, 137, 54,  1.0)"],   // amber
];

return {
    data: [
        {
            type: "heatmap",
            x: truth_Vals,
            y: estimate_Vals,
            z: bin_counts,
            colorscale: COLORSCALE,
            colorbar: {
                title: {
                    text: "log(count)",
                    font: { family: FONT_FAMILY, size: 12, color: FONT_COLOR }
                },
                tickfont: { family: FONT_FAMILY, size: 11, color: FONT_COLOR },
                thickness: 14,
                len: 0.85,
                outlinewidth: 0
            },
            hovertemplate: "<b>stations: %{x} mm/day</b><br><b>satellite: %{y} mm/day</b><br>log₁₀(count): %{z:.2f}<extra></extra>"
        }
    ],
    layout: {
        font: {
            family: FONT_FAMILY,
            size: 13,
            color: FONT_COLOR
        },
        xaxis: {
            title: { text: stations + " (mm/day)", standoff: 14 },
            type: "linear",
            gridcolor: "rgba(255,255,255,0.08)",
            zerolinecolor: "rgba(255,255,255,0.15)",
            tickfont: { size: 12 }
        },
        yaxis: {
            title: { text: satellite + " (mm/day)", standoff: 14 },
            type: "linear",
            gridcolor: "rgba(255,255,255,0.08)",
            zerolinecolor: "rgba(255,255,255,0.15)",
            tickfont: { size: 12 }
        },
        margin: { t: 10, b: 40, l: 40, r: 10 },        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor:  "rgba(0,0,0,0)"
    }
};
