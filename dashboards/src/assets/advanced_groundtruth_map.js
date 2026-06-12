// EXTERNAL:advanced_groundtruth_map.js
forecast = variables.forecast.current.value
metric = variables.metric.current.value
truth = variables.truth.current.value
grid = variables.grid.current.value
regions = variables.region.current.value
time_grouping = variables.time_grouping.current.value
time =  variables.time_filter.current.value

//FILTERS = ['forecast_filter-False_obs_filter-True','forecast_filter-True_obs_filter-False']
ftype = variables.filter_type.current.value

if (ftype == 'forecast') {
    FILTERS = ['forecast_filter-True_obs_filter-False']
} else {
    FILTERS = ['forecast_filter-False_obs_filter-True']
}

LEAD_KEYS = []
FILTERS.forEach((filter) => {
    DATASET_KEYS = []
    regions.forEach((region) => {
      DATASET_KEYS.push(`ground_truth_metric_map_1_2024-12-31_${truth}_${grid}_${filter}_${metric}_${region}_2016-01-01_${time_grouping}_tahmo_avg_precip`)
    })
    LEAD_KEYS.push(DATASET_KEYS)
})
console.log(DATASET_KEYS)

if (time == 'None') {
  time = '';
} else {
  time = '_' + time;
}


advanced_metric = ""
advanced_units = "mm"
if (variables.metric.current.value == 'early_season_accumulation-30d' ) {
  color_min = 0
  color_max = 42
  color_max_tc = 85
  tera_cscale='paired'
  advanced_metric = "MAE"
  advanced_units = " (mm)"
  metric_name = "Early season accumulation"
} else if (variables.metric.current.value == 'big_rain_days' ) {
  color_min = 0
  color_max = 0.45
  color_max_tc = 0.91
  tera_cscale='paired'
  advanced_metric = "SMAPE"
  advanced_units = " (percent)"
  metric_name = "Big rain days"
} else if (variables.metric.current.value == 'in_season_dry_spell' ) {
  color_min = 0
  color_max = 30
  color_max_tc = 61
  tera_cscale='paired'
  advanced_metric = "Precipitation"
  advanced_units = " (mm)"
  metric_name = "In season dry spells"
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
stretch = `colormap=${tera_cscale}&stretch_range=[${color_min},${color_max_tc}]`

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

cscale = [
      [0, 'rgb(194, 217, 225)'],
      [0.16, 'rgb(194, 217, 225)'],

      [0.16, 'rgb(109, 154, 192)'],
      [0.33, 'rgb(109, 154, 192)'],

      [0.33, 'rgb(203, 227, 165)'],
      [0.49, 'rgb(203, 227, 165)'],

      [0.49, 'rgb(126, 182, 102)'],
      [0.66, 'rgb(126, 182, 102)'],

      [0.66, 'rgb(245, 175, 177)'],
      [0.83, 'rgb(245, 175, 177)'],

      [0.83, 'rgb(235, 92, 90)'],
      [1, 'rgb(235, 92, 90)'],
    ]



var columnCount = 1
var mapIds = Array.from({ length: columnCount }, (_, index) =>
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
            color: [color_min, color_max],
            colorscale: cscale,
            colorbar: {
                tick0: color_min,
                dtick: (color_max - color_min)/6,
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
    var rowGap = 0
    var rowHeight = (1 - rowGap)
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
        grid: { rows: 1, columns: columnCount, pattern: 'independent' },
        margin: { r: 0, t: 30, b: 10, l: 0 },
        showlegend: false,
        annotations: [
            {
                text: `<b>Ground Truth vs Station Error<br>${metric_name} - ${advanced_metric}${advanced_units}</b>`,
                x: 0,
                xanchor: 'left',
                y: 1,
                yanchor: 'bottom',
                showarrow: false
            },
            /*...subplotLeadLabels.map((label, index) => ({
                text: label,
                x: (index + 0.5) / columnCount,
                xanchor: 'center',
                y: -0.02,
                yanchor: 'top',
                xref: 'paper',
                yref: 'paper',
                showarrow: false
            }))*/
        ],
        ...layoutMaps
    }
}
