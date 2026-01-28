//EXTERNAL:ground_truth_coverage.js
// Utility function to convert hex color to an RGB object
function hexToRgb(hex) {
    const bigint = parseInt(hex.slice(1), 16);
    return {
        r: (bigint >> 16) & 255,
        g: (bigint >> 8) & 255,
        b: bigint & 255
    };
}

// Function to get interpolated color by passing a value from 0 to 1
function getColor(value, cmin, cmax, colorMap) {
    let colors;

    // Define color scales based on the selected colormap
    if (colorMap === 'BrBG') {
        colors = [
            "#543005",
            "#8C510A", "#BF812D", "#DFC27D", "#F6E8C3",
            "#F5F5F5", "#C7EAE5", "#80CDC1", "#35978F", "#01665E",
            "#003C30"
        ];
    } else if (colorMap === 'balance') {
        colors = [
            "#2a0a0a",
            "#751b1b", "#b73c3c", "#e88484", "#f3c3c3", // Negative side
            "#ffffff",                                            // Neutral middle
            "#c3e4f3", "#84c2e8", "#3c9fb7", "#1b5e75",  // Positive side
            "#0a2a2a"
        ];
        colors = colors.reverse()
    } else if (colorMap === 'RdBu') {
        colors = ['#ff0000', '#ffffff', '#0000ff'];
    } else {
        throw new Error("Invalid colorMap. Choose 'BrBG', 'balance', or 'RdBu'.");
    }

    let x = (value - cmin) / (cmax 

    // Clamp value between 0 and 1
    x = Math.min(1, Math.max(0, x));
    if (isNaN(x)) {
        return `rgba(255, 255, 255, 0.5)`;
    }

    // Compute exact position in color array
    const scaledValue = x * (colors.length - 1);
    const lowerIndex = Math.floor(scaledValue);
    const upperIndex = Math.ceil(scaledValue);

    // Edge case: if at the end of the array, return the last color
    if (lowerIndex === upperIndex) {
        const color = hexToRgb(colors[lowerIndex]);
        return `rgba(${color.r}, ${color.g}, ${color.b}, 0.5)`;
    }

    // Interpolate between the two colors
    const lowerColor = hexToRgb(colors[lowerIndex]);
    const upperColor = hexToRgb(colors[upperIndex]);
    const t = scaledValue - lowerIndex;

    // Interpolate RGB channels
    const r = Math.round(lowerColor.r + t * (upperColor.r - lowerColor.r));
    const g = Math.round(lowerColor.g + t * (upperColor.g - lowerColor.g));
    const b = Math.round(lowerColor.b + t * (upperColor.b - lowerColor.b));

    // Return the interpolated color as an rgb(r, g, b) string
    return `rgba(${r}, ${g}, ${b}, 0.5)`;
}

const specialNames = {
  1: "Day",
  5: "Pentad",
  7: "Week",
  10: "Dekad"
};

function renameField(fieldName) {
  // Try to interpret as integer
  const num = parseInt(fieldName, 10);

  // If not numeric → keep the original name
  if (isNaN(num)) return fieldName;

  // If numeric and special → use special name
  if (specialNames[num]) return specialNames[num];

  // Otherwise → "<num> Days"
  return `${num} Days`;
}

if (series.length == 0) {
    return {
        data: []
    }
}


// Returned data has format station, time_grouping, region, [agg_days]
// Build header, data source first, then rename days
let header = [
  "Data Source",
  ...series.fields.slice(3).map(f => renameField(f.name))
];

// get coverage values 
values = series.fields.slice(3).map(f => f.values)
// get data source
data_source = series.fields[0].values

// round values to two decimal places
values = values.map((period) => period.map((x) => { if (x) { return x.toFixed(2) } else { return '-' } }))


// Rename dictionary
const renameDict = {
    "ghcn_avg": "GHCN Average",
    "tahmo_avg": "TAHMO Average",
    "ghcn": "GHCN Random",
    "tahmo": "TAHMO Random"
};

// Apply custom renaming to the first column of cellValues
data_source = data_source.toArray().map(value => renameDict[value] || value);

// get region & station selection & format
var station = variables['truth'].current.value

function cap(str) {
  var i, frags = str.split('_');
  for (i=0; i<frags.length; i++) {
    frags[i] = frags[i].charAt(0).toUpperCase() + frags[i].slice(1);
  }
  return frags.join(' ');
}

// convert tahmo_avg to TAHMO Average, ghcn_avg to GHCN Average, etc.
function rename_station(station) {
    if (station == 'tahmo_avg') {
        return 'TAHMO Average';
    } else if (station == 'ghcn_avg') {
        return 'GHCN Average';
    } else if (station == 'tahmo') {
        return 'TAHMO Random';
    } else if (station == 'ghcn') {
        return 'GHCN Random';
    } else {
        return station;
    }
}

region = cap(region)
station = rename_station(station)

// First column black
const firstColColor = data_source.map(_ => 'rgba(0,0,0,0)');

// Other columns colored
const otherColsColors = values.map(col =>
    col.map(v => v != null ? getColor(v, 0, 0.5, "RdBu") : 'rgba(255,255,255,0.5)')
);

// Combine colors into a single array
const allColors = [firstColColor, ...otherColsColors];

return {
    data: [{
        type: 'table',
        header: {
            values: header,
            align: ['left', 'right', 'right', 'right', 'right'],
            line: { width: 0, color: '#DBDDDE' },
            font: { family: "Inter, sans-serif", size: 14, weight: "bold" },
            fill: {
                color: ['rgba(0,0,0,0)']
            }
        },
        cells: {
            values: [data_source, ...values],
            align: ['left', 'right',  'right', 'right', 'right'],
            line: { width: 1, color: "#DBDDDE" },
            font: { family: "Inter, sans-serif", size: 14, color: ["black"] },
            fill: {
                color: allColors
            },
            height: 35
        },
        columnwidth: [0.4, 0.5, 0.5, 0.5, 0.5, 0.5] // Make divider column very thin
    }],
    layout: {
        title: {
            text: station + " coverage in " + region,
            xanchor: 'left',
            x: 0
        }
    }
}
