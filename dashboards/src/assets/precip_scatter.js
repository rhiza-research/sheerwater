// EXTERNAL:precip_scatter.js
let series = data.series[0];

console.log(variables.lat1)

// --- Read variables ---
let station = String(variables.station.current.value).trim();
let satellite = String(variables.satellite.current.value).trim();
let colorby = String(variables.colorby.current.value).trim();
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

// --- Get x/y values ---
let xValues = Array.from(xField.values || xField.values.buffer || []);
let yValues = Array.from(yField.values || yField.values.buffer || []);
// --- get lat, lon, time values ---
let latValues = Array.from(lat.values || lat.values.buffer || []);
let lonValues = Array.from(lon.values || lon.values.buffer || []);
let timeValues = Array.from(timeField.values || timeField.values.buffer || []);

if (xValues.length !== yValues.length || xValues.length === 0) throw new Error("X and Y values must match in length and not be empty.");

// --- Helper: generate marker colors ---
function getMarkerColors(colorField, type="auto") {
    if (!colorField) return "blue";
    let values = Array.from(colorField.values || colorField.values.buffer || []);
    if (type === "auto") type = (typeof values.find(v=>v!=null) === "number") ? "numeric" : "categorical";
    if (type === "numeric") return values;
    let categories = Array.from(new Set(values));
    let categoryColors = {};
    let colors = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692','#B6E880','#FF97FF','#FECB52'];
    categories.forEach((cat,i)=>categoryColors[cat]=colors[i%colors.length]);
    return values.map(v => categoryColors[v] || 'grey');
}

// --- Determine color field ---
let colorField, colorType = "auto";
if (colorby === "humidity") { colorField = series.fields.find(f => f.name === "rh2m_pct"); colorType="numeric"; }
else if (colorby === "temperature") { colorField = series.fields.find(f => f.name === "tmp2m"); colorType="numeric"; }
else if (colorby === "admin1") { colorField = series.fields.find(f => f.name === "admin_1_region"); colorType="categorical"; }
else if (colorby === "agroecological") { colorField = series.fields.find(f => f.name === "agroecological_zone_region"); colorType="categorical"; }
else if (colorby === "latitude") { colorField = series.fields.find(f => f.name === "lat"); colorType="numeric"; }
else if (colorby === "longitude") { colorField = series.fields.find(f => f.name === "lon"); colorType="numeric"; }
// if colorby is location, use sqrt(lat^2 + lon^2) as colorfield
else if (colorby === "location") {
    let latField = series.fields.find(f => f.name === "lat");
    let lonField = series.fields.find(f => f.name === "lon");

    if (!latField || !lonField) throw new Error("lat or lon field not found");

    let latVals = Array.from(latField.values || latField.values.buffer || []);
    let lonVals = Array.from(lonField.values || lonField.values.buffer || []);

    colorField = latVals.map((lat, i) =>
        (typeof lat === "number" && typeof lonVals[i] === "number")
            ? Math.sqrt(lat * lat + lonVals[i] * lonVals[i])
            : null
    );

    colorType = "numeric";
}

let markerColors = getMarkerColors(colorField, colorType);

// --- Compute safe min/max ---
let overallMin = Math.min(xValues.reduce((a,v)=>Math.min(a,v), Infinity), yValues.reduce((a,v)=>Math.min(a,v), Infinity));
let overallMax = Math.max(xValues.reduce((a,v)=>Math.max(a,v), -Infinity), yValues.reduce((a,v)=>Math.max(a,v), -Infinity));

// --- Build traces ---
let traces = [];

// Only scatter when density is off
if (!showDensity) {
    // time should show as a timestamp in the format of YYYY-MM-DD HH
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
            color: markerColors,
            opacity: 0.2,
            ...(colorType === "numeric"
                ? { colorscale: "Viridis", colorbar: { title: colorby } }
                : {})
        },
        showlegend: false,
        hovertext: hoverText,
        hoverinfo: 'text'
    });
}

// Always include density contour (if desired)
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

// event threshold lines
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
// Convert axis limit variable from string to number
let axisLim = Number(String(variables.axis_lim.current.value).trim());

// Fallback if variable is empty or invalid
if (isNaN(axisLim)) {
    axisLim = 70; // default
}

return {
    data: traces,
    layout: {
        xaxis: {
            title: xField.name,
            type: 'linear',
            range: [0, axisLim],
            autorange: false
        },
        yaxis: {
            title: yField.name,
            type: 'linear',
            range: [0, axisLim],
            autorange: false
        }
    }
};
