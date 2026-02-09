// EXTERNAL:ground_truth_coverage.js

// --------------------
// Color utilities
// --------------------
function hexToRgb(hex) {
    const bigint = parseInt(hex.slice(1), 16);
    return {
        r: (bigint >> 16) & 255,
        g: (bigint >> 8) & 255,
        b: bigint & 255
    };
}

function getColor(value, cmin, cmax) {
    const colors = [
        "#f0f0f0", // very low (light grey)
        "#c7e9c0",
        "#74c476",
        "#31a354",
        "#006d2c"  // high (dark green)
    ];

    let x = (value - cmin) / (cmax - cmin);
    x = Math.min(1, Math.max(0, x));

    if (isNaN(x)) {
        return 'rgba(255,255,255,0.5)';
    }

    const scaled = x * (colors.length - 1);
    const i0 = Math.floor(scaled);
    const i1 = Math.ceil(scaled);

    if (i0 === i1) {
        const c = hexToRgb(colors[i0]);
        return `rgba(${c.r},${c.g},${c.b},0.6)`;
    }

    const c0 = hexToRgb(colors[i0]);
    const c1 = hexToRgb(colors[i1]);
    const t = scaled - i0;

    const r = Math.round(c0.r + t * (c1.r - c0.r));
    const g = Math.round(c0.g + t * (c1.g - c0.g));
    const b = Math.round(c0.b + t * (c1.b - c0.b));

    return `rgba(${r},${g},${b},0.6)`;
}

// --------------------
// agg_days renaming
// --------------------
const specialNames = {
    1: "Day",
    5: "Pentad",
    7: "Week",
    10: "Dekad"
};

function renameField(field) {
    const num = parseInt(field, 10);
    if (isNaN(num)) return field;
    if (specialNames[num]) return specialNames[num];
    return `${num} Days`;
}

// --------------------
// Guard
// --------------------
if (series.length === 0) {
    return { data: [] };
}

// --------------------
// Extract columns
// --------------------
const aggDays = series.fields.find(f => f.name === 'agg_days').values.toArray();
const cellsCount = series.fields.find(f => f.name === 'cells_count').values.toArray();
const periodsCount = series.fields.find(f => f.name === 'periods_count').values.toArray();
const cellsCovered = series.fields.find(f => f.name === 'cells_covered').values.toArray();
const avgCellPeriodsRaw =
    series.fields.find(f => f.name === 'average_cell_periods').values.toArray();

// --------------------
// Average cell scaling
// --------------------
const useYears = periodsCount.some(p => p > 365);

const avgLabel = useYears
    ? "Average Cell Years"
    : "Average Cell Months";

const avgValues = avgCellPeriodsRaw.map(v => {
    if (v == null) return null;
    return useYears ? v / 365.0 : v / 30.0;
});

const avgColorMax = useYears ? 10 : (20.0 / 30.0);

// --------------------
// Header
// --------------------
const header = [
    "",
    ...aggDays.map(d => renameField(d))
];

// --------------------
// Rows
// --------------------
const rowLabels = [
    "Cells Covered",
    avgLabel
];

// Cells covered display: "covered / total"
const coveredDisplay = cellsCovered.map((v, i) => {
    if (v == null) return "-";
    return `${Math.round(v)} / ${Math.round(cellsCount[i])}`;
});

// Transpose helper
function transpose(m) {
    return m[0].map((_, i) => m.map(r => r[i]));
}

const rows = [
    coveredDisplay,
    avgValues.map(v => v != null ? v.toFixed(2) : "-")
];

const cellValues = [
    rowLabels,
    ...transpose(rows)
];

// --------------------
// Coloring
// --------------------
const fillColors = [];

// First column (row labels)
fillColors.push(rowLabels.map(_ => 'rgba(0,0,0,0)'));

// Data columns
for (let i = 0; i < aggDays.length; i++) {
    const coverageFrac =
        cellsCount[i] > 0 ? cellsCovered[i] / cellsCount[i] : null;

    fillColors.push([
        getColor(coverageFrac, 0, 1),
        getColor(avgValues[i], 0, avgColorMax)
    ]);
}

// --------------------
// Station / region formatting
// --------------------
function cap(str) {
    return str.split('_')
        .map(s => s.charAt(0).toUpperCase() + s.slice(1))
        .join(' ');
}

function rename_station(station) {
    if (station === 'tahmo_avg') return 'TAHMO Average';
    if (station === 'ghcn_avg') return 'GHCN Average';
    if (station === 'tahmo') return 'TAHMO Random';
    if (station === 'ghcn') return 'GHCN Random';
    return station;
}

let station = variables['truth'].current.value;
station = rename_station(station);
region = cap(region);

// --------------------
// Final Plotly table
// --------------------
return {
    data: [{
        type: 'table',
        header: {
            values: header,
            align: 'center',
            font: { family: "Inter, sans-serif", size: 14, weight: "bold" },
            fill: { color: 'rgba(0,0,0,0)' },
            line: { color: '#DBDDDE', width: 1 }
        },
        cells: {
            values: cellValues,
            align: ['left', 'right'],
            font: { family: "Inter, sans-serif", size: 14 },
            fill: { color: fillColors },
            height: 35,
            line: { color: '#DBDDDE', width: 1 }
        }
    }],
    layout: {
        title: {
            text: station + " coverage in " + region,
            xanchor: 'left',
            x: 0
        }
    }
};
