// EXTERNAL:precip_scatter.js
let series = data.series[0];

// --- Read variables ---
let station = String(variables.station.current.value).trim();
let satellite = String(variables.satellite.current.value).trim();
let showDensity = String(variables.density.current.value).trim().toLowerCase() === "true";

// --- Build field names ---
let xFieldName = `${station}_precip`;
let yFieldName = `${satellite}_precip`;

// --- Find fields safely ---
let xField = series.fields.find(f => f.name === xFieldName);
let yField = series.fields.find(f => f.name === yFieldName);
let lat = series.fields.find(f => f.name === "lat");
let lon = series.fields.find(f => f.name === "lon");
let timeField = series.fields.find(f => f.name === "time");

if (!xField || !yField) throw new Error("X or Y field not found.");

// --- Extract values ---
let xValues = Array.from(xField.values || xField.values.buffer || []);
let yValues = Array.from(yField.values || yField.values.buffer || []);
let latValues = Array.from(lat.values || lat.values.buffer || []);
let lonValues = Array.from(lon.values || lon.values.buffer || []);
let timeValues = Array.from(timeField.values || timeField.values.buffer || []);

if (xValues.length !== yValues.length || xValues.length === 0) 
    throw new Error("X and Y values must match in length and not be empty.");

// --- Compute safe min/max for axes ---
let overallMin = Math.min(
    xValues.reduce((a,v)=>Math.min(a,v), Infinity),
    yValues.reduce((a,v)=>Math.min(a,v), Infinity)
);
let overallMax = Math.max(
    xValues.reduce((a,v)=>Math.max(a,v), -Infinity),
    yValues.reduce((a,v)=>Math.max(a,v), -Infinity)
);

// Add 5% padding
let padding = 0.05 * (overallMax - overallMin);
let xRange = [overallMin - padding, overallMax + padding];
let yRange = [overallMin - padding, overallMax + padding];

// --- Build traces ---
let traces = [];

// Scatter points
if (!showDensity) {
    const hoverText = latValues.map((lat, i) =>
        `Lat: ${lat}<br>Lon: ${lonValues[i]}<br>Time: ${new Date(timeValues[i]).toLocaleDateString()}`
    );

    traces.push({
        x: xValues,
        y: yValues,
        type: 'scatter',
        mode: 'markers',
        marker: {
            size: 6,
            color: 'blue', // all points blue
            opacity: 0.2
        },
        showlegend: false,
        hovertext: hoverText,
        hoverinfo: 'text'
    });
}

// Density contour (if enabled)
if (showDensity) {
    traces.push({
        x: xValues,
        y: yValues,
        type: 'histogram2dcontour',
        colorscale: 'Blues',
        reversescale: true,
        showscale: false,
        opacity: 1,
        contours: { coloring:'lines', showlines:true, start:1, end:500, size:50 },
        line: { width: 2, color:'orange' },
        showlegend: false
    });
}

// x=y line
traces.push({
    x: [overallMin, overallMax],
    y: [overallMin, overallMax],
    type: 'scatter',
    mode: 'lines',
    line: { color: 'red', width:2, dash:'dash' },
    opacity:0.5,
    showlegend:false
});

// Event threshold lines
let event_thresh = parseFloat(String(variables.event_thresh.current.value).trim());
if (!isNaN(event_thresh)) {
    traces.push({
        x:[event_thresh,event_thresh],
        y:[overallMin,overallMax],
        type:'scatter',
        mode:'lines',
        line:{color:'orange',width:2,dash:'dot'},
        showlegend:false
    });
    traces.push({
        x:[overallMin,overallMax],
        y:[event_thresh,event_thresh],
        type:'scatter',
        mode:'lines',
        line:{color:'orange',width:2,dash:'dot'},
        showlegend:false
    });
}

// Linear regression
function linearRegression(x,y) {
    let n = x.length;
    if (n<2) return {slope:0,intercept:0};
    let sumX=0,sumY=0,sumXY=0,sumXX=0;
    for (let i=0;i<n;i++){sumX+=x[i]; sumY+=y[i]; sumXY+=x[i]*y[i]; sumXX+=x[i]*x[i];}
    let m = (n*sumXY - sumX*sumY)/(n*sumXX - sumX*sumX);
    let b = (sumY - m*sumX)/n;
    return {slope:m,intercept:b};
}

let fit = linearRegression(xValues,yValues);
let xFit = [overallMin,overallMax];
let yFit = xFit.map(v => fit.slope*v + fit.intercept);

traces.push({
    x:xFit,
    y:yFit,
    type:'scatter',
    mode:'lines',
    line:{color:'purple',width:2},
    opacity:0.5,
    showlegend:false
});

// --- Return Plotly object ---
return {
    data: traces,
    layout: {
        xaxis: { title: xField.name, type:'linear', range: xRange, autorange:false },
        yaxis: { title: yField.name, type:'linear', range: yRange, autorange:false }
    }
};
