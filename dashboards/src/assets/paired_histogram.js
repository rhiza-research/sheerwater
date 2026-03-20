// EXTERNAL:paired_histogram.js
let series = data.series[0];

// Find fields by name (robust to ordering)
let estimateField = series.fields.find(f => f.name === "estimate");
let truthField = series.fields.find(f => f.name === "truth");
let precipField = series.fields.find(f => f.name === "precip");

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

// Create lookup maps
let estimate_Index = new Map(estimate_Vals.map((v, i) => [v, i]));
let truth_Index = new Map(truth_Vals.map((v, i) => [v, i]));

// Initialize 2D grid
let bin_counts = Array.from({ length: estimate_Vals.length }, () =>
  Array.from({ length: truth_Vals.length }, () => 0)
);

// Fill grid
for (let i = 0; i < estimate.length; i++) {
  // get the index of the bins in the query within the full range
  let estimate_i = estimate_Index.get(estimate[i]);
  let truth_i = truth_Index.get(truth[i]);
  bin_counts[estimate_i][truth_i] = Math.log10(precip[i] + 1);
}

// axis labels
let stations = String(variables.stations.current.value).trim();
let satellite = String(variables.satellite.current.value).trim();
let xlabel = `${stations}`;
let ylabel = `${satellite}`;

return {
  data: [
    {
      type: "heatmap",
      x: truth_Vals,
      y: estimate_Vals,
      z: bin_counts,
      colorscale: "Viridis",
      colorbar: {
        title: "Count"
      },
      hovertemplate:
        "station: %{x}<br>satellite: %{y}<br>Count: %{z}<extra></extra>"
    }
  ],
layout: {
  xaxis: {
    title: xlabel,
    type: "linear",
  },
  yaxis: {
    title: ylabel,
    type: "linear",
  }
}
};
