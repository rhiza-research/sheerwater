// EXTERNAL:afl21x2g76a68a-16-script.js: paired_histogram.js

let series = data.series[0];

// fields
let estimate = series.fields.find(f => f.name === "estimate").values;
let truth    = series.fields.find(f => f.name === "truth").values;
let precip   = series.fields.find(f => f.name === "precip").values;

// handle buffers
estimate = estimate || estimate.buffer;
truth    = truth    || truth.buffer;
precip   = precip   || precip.buffer;

let estimateVals = [...new Set(estimate)].sort((a, b) => a - b);
let truthVals    = [...new Set(truth)].sort((a, b) => a - b);

// index maps
let eIndex = new Map(estimateVals.map((v, i) => [v, i]));
let tIndex = new Map(truthVals.map((v, i) => [v, i]));

// initialize grid
let binCounts = Array.from({ length: estimateVals.length }, () =>
  Array.from({ length: truthVals.length }, () => 0)
);

// fill histogram
for (let i = 0; i < estimate.length; i++) {
  let ei = eIndex.get(estimate[i]);
  let ti = tIndex.get(truth[i]);

  if (ei === undefined || ti === undefined) continue;

  binCounts[ei][ti] = precip[i];
}

// log transform
let binLog = binCounts.map(row =>
  row.map(v => Math.log10((v || 0) + 1))
);

// styling
const FONT_FAMILY = "'Inter', 'Helvetica Neue', Arial, sans-serif";
const FONT_COLOR  = "#777777";

const COLORSCALE = [
  [0.00, "rgba(255,255,255,1.0)"],
  [0.08, "rgba(255,245,200,1.0)"],
  [0.18, "rgba(255,220,120,1.0)"],
  [0.30, "rgba(255,170, 60,1.0)"],
  [0.42, "rgba(255,110,130,1.0)"],
  [0.55, "rgba(200, 80,200,1.0)"],
  [0.68, "rgba(120,100,255,1.0)"],
  [0.80, "rgba( 60,120,255,1.0)"],
  [0.90, "rgba( 20, 60,180,1.0)"],
  [1.00, "rgba(  0,  0,  0,1.0)"]
];

return {
  data: [
    {
      type: "heatmap",
      x: truthVals,
      y: estimateVals,
      z: binLog,
      colorscale: COLORSCALE,
      colorbar: {
        title: {
          text: "log10(count)",
          font: { family: FONT_FAMILY, size: 12, color: FONT_COLOR }
        },
        tickfont: { family: FONT_FAMILY, size: 11, color: FONT_COLOR },
        thickness: 14,
        len: 0.85,
        outlinewidth: 0
      },
      hovertemplate:
        "<b>truth: %{x}</b><br>" +
        "<b>estimate: %{y}</b><br>" +
        "log₁₀(count): %{z:.2f}<extra></extra>"
    }
  ],
  layout: {
    font: { family: FONT_FAMILY, size: 13, color: FONT_COLOR },
    xaxis: {
      title: "Truth (mm/day)",
      type: "linear",
      gridcolor: "rgba(255,255,255,0.08)",
      zerolinecolor: "rgba(255,255,255,0.15)"
    },
    yaxis: {
      title: "Estimate (mm/day)",
      type: "linear",
      gridcolor: "rgba(255,255,255,0.08)",
      zerolinecolor: "rgba(255,255,255,0.15)"
    },
    margin: { t: 10, b: 40, l: 40, r: 10 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)"
  }
};
