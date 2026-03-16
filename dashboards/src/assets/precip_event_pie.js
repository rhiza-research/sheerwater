// EXTERNAL:precip_event_pie.js
let series = data.series[0];

// Read variables
let station = String(variables.station.current.value).trim();
let satellite = String(variables.satellite.current.value).trim();
let event_thresh = Number(String(variables.event_thresh.current.value).trim()); // convert to number

// Build field names
let xFieldName = `${station}_precip`;
let yFieldName = `${satellite}_precip`;

// Find fields safely
let xField = series.fields.find(f => f.name === xFieldName);
let yField = series.fields.find(f => f.name === yFieldName);

// Get x/y values
let xValues = xField.values || xField.values.buffer;
let yValues = yField.values || yField.values.buffer;

// --- Compute quadrant counts ---
let counts = { TP: 0, FP: 0, FN: 0, TN: 0 };

for (let i = 0; i < xValues.length; i++) {
    let x = xValues[i];
    let y = yValues[i];

    if (x >= event_thresh && y >= event_thresh) counts.TP++;
    else if (x >= event_thresh && y < event_thresh) counts.FN++;
    else if (x < event_thresh && y >= event_thresh) counts.FP++;
    else counts.TN++;
}

// --- Build pie chart trace with custom colors ---
let pie_trace = {
    type: 'pie',
    labels: ['False Positive', 'True Positive', 'False Negative', 'True Negative'],
    values: [counts.FP, counts.TP, counts.FN, counts.TN],
    textinfo: 'percent',   // <-- only show percentages
    hole: 0.4,             // optional donut style
    marker: {
        colors: [
            '#FF0000', // FP - red
            '#00CC00', // TP - green
            '#FFA500', // FN - orange
            '#0000FF'  // TN - blue
        ]
    }
};


return {
    data: [pie_trace],
    layout: {
        title: `Quadrant Breakdown (Threshold = ${event_thresh})`
    }
};
