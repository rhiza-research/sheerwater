// EXTERNAL:advanced_metrics_maps.js
forecast = variables.forecast.current.value
metric = variables.metric.current.value
truth = variables.truth.current.value
grid = variables.grid.current.value
regions = variables.region.current.value
time_grouping = variables.time_grouping.current.value
time =  variables.time_filter.current.value

LEADS = [7, 14, 21, 28, 35, 42]
FILTERS = ['forecast_filter-False_obs_filter-True','forecast_filter-True_obs_filter-False']

LEAD_KEYS = []
FILTERS.forEach((filter) => {
    LEADS.forEach((lead) => {
        DATASET_KEYS = []
        regions.forEach((region) => {
          DATASET_KEYS.push(`forecast_metric_map_1_2024-12-31_${forecast}_${grid}_${lead}_${filter}_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_precip`)
        })
        LEAD_KEYS.push(DATASET_KEYS)
    })
})
console.log(DATASET_KEYS)

if (time == 'None') {
  time = '';
} else {
  time = '_' + time;
}


DATASET_KEYS.forEach((key) => {
  try {
    var xmlHttp = new XMLHttpRequest();
    url = `https://terracotta.shared.rhizaresearch.org/metadata/${key}`
    xmlHttp.open( "GET", url, false ); // false for synchronous request
    xmlHttp.send( null );

    if(xmlHttp.status != 200) {
      console.log("Error getting dataset metadata");
      return {};
    }

    console.log("Dataset exists");
  } catch (error) {
    // If we can't get this metric just return early
    console.log("Error getting dataset metadata");
    console.log(error)
    return {}
  }
})

lead_week = LEAD_DAY/7

advanced_metric = ""
advanced_units = "mm"
if (variables.metric.current.value == 'early_season_accumulation-30d' ) {
  color_min = 0
  color_max = 50
  tera_cscale='ylorbr'
  advanced_metric = "MAE"
  advanced_units = " (mm)"
  metric_name = "Early season accumulation"
} else if (variables.metric.current.value == 'acc' ){
  color_min = -1
  color_max = 1
  tera_cscale = 'rdbu'
} else if(variables.metric.current.value == 'seeps' ){
  tera_cscale = 'reds'
  color_min = 0
  color_max = 2.0
}else {
  // set the terracotta colorscale
  tera_cscale = 'reds'
}
stretch = `colormap=${tera_cscale}&stretch_range=[${color_min},${color_max}]`

//Query the color scale
var xmlHttp = new XMLHttpRequest();
url = `https://terracotta.shared.rhizaresearch.org/colormap?colormap=${tera_cscale}&stretch_range=[${color_min},${color_max}]&num_values=10`
xmlHttp.open( "GET", url, false ); // false for synchronous request
xmlHttp.send( null );

f = JSON.parse(xmlHttp.responseText)
cscale = []
for(var i = 0; i < f.colormap.length; i++) {
  rgb = `rgb(${f.colormap[i].rgba[0]},${f.colormap[i].rgba[1]},${f.colormap[i].rgba[2]})`
  cscale.push([i/f.colormap.length + i*(.1/(f.colormap.length-1)), rgb])
}

console.log(cscale)
console.log(color_min)
console.log(color_max)

var units = ""
if (metric == 'mae' || metric == 'bias' || metric == 'crps' || metric == 'rmse') {
    units = " (mm/day)"
}

center = {'lat': 0, 'lon': 0};
zoom = 0
if(document.last_zoom) {
  zoom = document.last_zoom
}
if(document.last_center) {
  center = document.last_center
}

var subplotLeads = LEADS
var subplotLeadLabels = subplotLeads.map((option) => `<b>Day ${option} lead</b>`)
var columnCount = LEADS.length
var mapIds = Array.from({ length: columnCount * 2 }, (_, index) =>
    index === 0 ? 'map' : `map${index + 1}`
)
var data = []
mapIds.forEach((mapId, index) => {
    data.push({
        type: 'scattermap',
        lat: ['45.5017', '46.9027'],
        lon: ['-73.5673', '-73.5673'],
        mode: 'markers',
        marker: {
            size: 0,
            showscale: (index === 0),
            colorscale: cscale,
            cmin: color_min,
            cmax: color_max,
            colorbar: {
                y: 0.5,
                len: 0.97
            }
        },
        subplot: mapId
    })
})

layers_to_map = []
LEAD_KEYS.forEach((dataset_key) => {
    layers_to_add = []
    dataset_key.forEach((key) => {
      layers_to_add.push({
              opacity: 0.7,
              sourcetype: "raster",
              source: [
                `https://terracotta.shared.rhizaresearch.org/singleband/${key}/{z}/{x}/{y}.png?${stretch}`
              ],
              below: "traces",
            })
    });
    layers_to_map.push(layers_to_add)
})

var layoutMaps = {}
var gap = 0.01
mapIds.forEach((mapId, index) => {
    var colIndex = index % columnCount
    var rowIndex = index < columnCount ? 0 : 1
    var x0 = colIndex / columnCount + gap / 2
    var x1 = (colIndex + 1) / columnCount - gap / 2
    var rowGap = 0.04
    var rowHeight = (1 - rowGap) / 2
    var y0 = rowIndex === 0 ? rowHeight + rowGap : 0
    var y1 = rowIndex === 0 ? 1 : rowHeight
    layoutMaps[mapId] = {
        domain: { x: [x0, x1], y: [y0, y1] },
        style: 'open-street-map',
        layers: layers_to_map[index],
        center: center,
        zoom: zoom
    }
})

return {
    data: data,
    layout:
    {
        dragmode: 'zoom',
        grid: { rows: 2, columns: columnCount, pattern: 'independent' },
        margin: { r: 0, t: 30, b: 40, l: 0 },
        showlegend: false,
        annotations: [
            {
                text: `<b>${metric_name} - ${advanced_metric}${advanced_units} - truth triggered events.</b>`,
                x: 0,
                xanchor: 'left',
                y: 1,
                yanchor: 'bottom',
                showarrow: false
            },
            {
                text: `<b>${metric_name} - ${advanced_metric}${advanced_units} - forecast triggered events.</b>`,
                x: 0,
                xanchor: 'left',
                y: 0.48,
                yanchor: 'bottom',
                showarrow: false
            },
            ...subplotLeadLabels.map((label, index) => ({
                text: label,
                x: (index + 0.5) / columnCount,
                xanchor: 'center',
                y: -0.02,
                yanchor: 'top',
                xref: 'paper',
                yref: 'paper',
                showarrow: false
            }))
        ],
        ...layoutMaps
    }
}

