// EXTERNAL:afl21x2g76a68a-17-script.js: prob_viz.js
let allSeries = data.series;

// get fields by name
function getField(name) {
  for (let s of allSeries) {
    let f = s.fields.find(f => f.name === name);
    if (f) return f.values || f.values.buffer;
  }
  return null;
}


let time  = getField("time");

let imerg = getField("imerg_val");
let tahmo = getField("tahmo_val");

let prob_dry = getField("imerg_prob_given_dry");
let prob_wet = getField("imerg_prob_given_wet");

// -------------------------------------------------
// clean NaNs (IMPORTANT: keep nulls for Plotly)
// -------------------------------------------------
function clean(arr) {
  if (!arr) return [];
  return Array.from(arr).map(v => {
    if (v === null || v === undefined) return null;
    if (Number.isNaN(v)) return null;
    return v;
  });
}

imerg    = clean(imerg);
tahmo    = clean(tahmo);
prob_dry = clean(prob_dry);
prob_wet = clean(prob_wet);

// -------------------------------------------------
// wet / dry ratio
// -------------------------------------------------
let ratio = prob_wet.map((w, i) => {
  let d = prob_dry[i];

  if (w === null || d === null) return null;
  if (d === 0 || d === null) return null;

  return w / d;
});

// PLOT
return {
  data: [

    // -------------------------
    // IMERG
    // -------------------------
    {
      x: time,
      y: imerg,
      type: "scatter",
      mode: "lines",
      name: "IMERG",
      line: { color: "rgba(99, 110, 250, 1)" },
      connectgaps: false,
      yaxis: "y1"
    },

    // -------------------------
    // TAHMO
    // -------------------------
    {
      x: time,
      y: tahmo,
      type: "scatter",
      mode: "lines",
      name: "TAHMO",
      line: { color: "rgba(239, 85, 59, 1)" },
      connectgaps: false,
      yaxis: "y1"
    },

    // -------------------------
    // WET / DRY RATIO (UPDATED STYLE)
    // -------------------------
    {
      x: time,
      y: ratio,
      type: "scatter",
      mode: "lines",
      name: "Wet / Dry ratio",
      line: {
        color: "rgba(0, 180, 0, 1)",
        dash: "dot"
      },
      connectgaps: false,
      yaxis: "y2"
    }
  ],

  layout: {

    xaxis: {
      title: "Time",
      type: "date"
    },

    yaxis: {
      title: "Precipitation",
      side: "left"
    },

    yaxis2: {
      title: "Wet / Dry likelihood ratio",
      overlaying: "y",
      side: "right"
    },

    legend: {
      orientation: "h"
    },

    margin: { t: 20, b: 40, l: 50, r: 60 },

    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)"
  }
};
