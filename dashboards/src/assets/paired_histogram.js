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

// get grafana dashboard variables
let conditionOn = variables.condition_on.current.value;
let sliceValue = parseFloat(variables.slice.current.value);

// get fix_limits variable (empty string if not set)
let fixLimits = variables.fix_limits.current.value;
let fixedMax = (fixLimits !== "" && fixLimits !== "None") ? parseInt(fixLimits, 10) : null;

// get min and max across both estimate and truth
let dataMin = Math.min(Math.min(...estimate), Math.min(...truth));
let dataMax = Math.max(Math.max(...estimate), Math.max(...truth));

let min = 0;
let max = fixedMax !== null ? fixedMax : dataMax;
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
    if (estimate_i === undefined || truth_i === undefined) continue;
    bin_counts[estimate_i][truth_i] = precip[i];
}
// take log of counts
let bin_log_counts = Array.from({ length: estimate_Vals.length }, () =>
    Array.from({ length: truth_Vals.length }, () => 0)
);
for (let i = 0; i < bin_counts.length; i++) {
    for (let j = 0; j < bin_counts[i].length; j++) {
       bin_log_counts[i][j] = Math.log10(bin_counts[i][j] + 1);
    }
}
// determine the 50% bin conditioned on either estimate (satellite) or truth (stations)
function weightedMedianFromCounts(bins, counts) {
  // bins: array of bin-centre values  (same length as counts)
  // counts: raw (non-log) counts for each bin
  // returns the interpolated value where cumulative weight crosses 50 %
  let total = counts.reduce((a, b) => a + b, 0);
  if (total === 0) return null;
  let half = total / 2;
  let cumulative = 0;
  for (let k = 0; k < counts.length; k++) {
      cumulative += counts[k];
      if (cumulative >= half) {
          return bins[k];
      }
  }
  return bins[bins.length - 1];
}

let median_x = [];   // x-coords of the median line
let median_y = [];   // y-coords of the median line

if (conditionOn === "stations") {
  // condition on x (truth/stations) → one median y per x column
  for (let j = 0; j < truth_Vals.length; j++) {
      // extract the column: vary estimate (row index i), fix truth col j
      let colCounts = estimate_Vals.map((_, i) => bin_counts[i][j]);
      let med = weightedMedianFromCounts(estimate_Vals, colCounts);
      if (med !== null) {
          median_x.push(truth_Vals[j]);
          median_y.push(med);
      }
  }
} else {
  // condition on y (estimate/satellite) → one median x per y row
  for (let i = 0; i < estimate_Vals.length; i++) {
      // extract the row: vary truth (col index j), fix estimate row i
      let rowCounts = truth_Vals.map((_, j) => bin_counts[i][j]);
      let med = weightedMedianFromCounts(truth_Vals, rowCounts);
      if (med !== null) {
          median_x.push(med);
          median_y.push(estimate_Vals[i]);
      }
  }
}


// get grafana dashboard variables
let stations  = String(variables.stations.current.value).trim();
let satellite = String(variables.satellite.current.value).trim();

// plot aesthetics
const FONT_FAMILY = "'Inter', 'Helvetica Neue', Arial, sans-serif";
const FONT_COLOR  = "#777777";

// heatmap color scale
const COLORSCALE = [
    [0.00, "rgba(255,255,255,1.0)"],  // white — low
    [0.08, "rgba(255,245,200,1.0)"],  // very light yellow
    [0.18, "rgba(255,220,120,1.0)"],  // yellow
    [0.30, "rgba(255,170, 60,1.0)"],  // orange
    [0.42, "rgba(255,110,130,1.0)"],  // pink
    [0.55, "rgba(200, 80,200,1.0)"],  // purple
    [0.68, "rgba(120,100,255,1.0)"],  // blue-violet
    [0.80, "rgba( 60,120,255,1.0)"],  // blue
    [0.90, "rgba( 20, 60,180,1.0)"],  // dark blue
    [1.00, "rgba(  0,  0,  0,1.0)"],  // black — max
];
return {
  data: [
      {
          type: "heatmap",
          x: truth_Vals,
          y: estimate_Vals,
          z: bin_log_counts,
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
      },
      // median line
      {
          type: "scatter",
          mode: "lines",
          showlegend: false,
          x: median_x,
          y: median_y,
          line: {
              color: "rgba(255, 255, 255, 0.85)",
              width: 2,
              dash: "dot"
          },
          hovertemplate: conditionOn === "stations"
              ? "<b>stations: %{x} mm/day</b><br>median satellite: %{y} mm/day<extra></extra>"
              : "<b>satellite: %{y} mm/day</b><br>median stations: %{x} mm/day<extra></extra>"
      },
      // slice line
      {
        type: "scatter",
        mode: "lines",
        showlegend: false,
        x: conditionOn === "stations" ? [sliceValue, sliceValue] : [min, max],
        y: conditionOn === "stations" ? [min, max] : [sliceValue, sliceValue],
        line: {
            color: "rgba(237, 137, 54, 0.25)",
            width: 5,
        },
        hovertemplate: conditionOn === "stations"
            ? "<b>stations slice: %{x} mm/day</b><extra></extra>"
            : "<b>satellite slice: %{y} mm/day</b><extra></extra>"
    },
    // x = y line
    {
      type: "scatter",
      mode: "lines",
      x: [min, max],
      y: [min, max],
      showlegend: false,
      line: {
          color: "rgba(255, 255, 255, 0.25)",
          width: 1.5,
      },
      hoverinfo: "skip"
  },
  ],
  layout: {
      font:   { family: FONT_FAMILY, size: 13, color: FONT_COLOR },
      xaxis: {
          title:       { text: stations + " (mm/day)", standoff: 14 },
          type:        "linear",
          gridcolor:   "rgba(255,255,255,0.08)",
          zerolinecolor: "rgba(255,255,255,0.15)",
          tickfont:    { size: 12 }
      },
      yaxis: {
          title:       { text: satellite + " (mm/day)", standoff: 14 },
          type:        "linear",
          gridcolor:   "rgba(255,255,255,0.08)",
          zerolinecolor: "rgba(255,255,255,0.15)",
          tickfont:    { size: 12 }
      },
      margin:       { t: 10, b: 40, l: 40, r: 10 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor:  "rgba(0,0,0,0)"
  }
};
