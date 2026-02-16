// EXTERNAL:auc_map.js

let series = data.series[0];

// --------------------
// Get selected months from multi-select variable
// --------------------
let selectedMonths = variables['months'].current.value;

// Check if "All" is selected
let includeAll = false;
if (!selectedMonths || selectedMonths.length === 0) {
    includeAll = true; // nothing selected → include all
} else if (Array.isArray(selectedMonths) && selectedMonths.includes('$__all')) {
    includeAll = true; // Grafana "All" option
}

// Convert to array of integers if not including all
if (!includeAll) {
    selectedMonths = selectedMonths.map(m => parseInt(m));
} else {
    selectedMonths = []; // empty array = include all months
}

// --------------------
// extract data safely
// --------------------
function getFieldValues(name) {
    const field = series.fields.find(f => f.name.toLowerCase() === name.toLowerCase());
    return field ? field.values.toArray() : [];
}

// --------------------
// Extract columns
// --------------------
const lats = getFieldValues('lat');
const lons = getFieldValues('lon');
const aucs = getFieldValues('auc');
const groups = getFieldValues('group'); // contains "M01", "M02", ...

// --------------------
// Filter by selected months
// --------------------
// Convert selected months to M01-M12 codes
const monthCodes = selectedMonths.map(m => "M" + String(m).padStart(2, "0"));

const filtered = [];
for (let i = 0; i < lats.length; i++) {
    if (includeAll || monthCodes.includes(groups[i])) {
        filtered.push({
            lat: lats[i],
            lon: lons[i],
            auc: aucs[i]
        });
    }
}

// --------------------
// Aggregate average AUC over months per lat/lon
// --------------------
const aggregation = {};
filtered.forEach(d => {
    const key = `${d.lat}_${d.lon}`;
    if (!aggregation[key]) aggregation[key] = { sum: 0, count: 0, lat: d.lat, lon: d.lon };
    aggregation[key].sum += d.auc;
    aggregation[key].count += 1;
});

const aggData = Object.values(aggregation).map(d => ({
    lat: d.lat,
    lon: d.lon,
    auc: d.sum / d.count
}));

// --------------------
// Hover text: show only final averaged AUC
// --------------------
const hoverText = aggData.map(d => `AUC: ${d.auc.toFixed(2)}`);

// --------------------
// Scattermapbox trace
// --------------------
return {
    data: [{
        type: 'scattermapbox',
        lat: aggData.map(d => d.lat),
        lon: aggData.map(d => d.lon),
        mode: 'markers',
        marker: {
            size: 10,
            color: aggData.map(d => d.auc),
            colorscale: [[0, 'red'], [1, 'white']], // red → white
            cmin: 0,
            cmax: 1,
            colorbar: {
                title: 'AUC',
                thickness: 15
            }
        },
        text: hoverText,
        hoverinfo: 'text'
    }],
    layout: {
        mapbox: {
            style: 'carto-positron',
            center: { lat: 0, lon: 20 }, // show all Africa
            zoom: 3
        },
    }
};
