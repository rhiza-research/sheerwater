// EXTERNAL:advanced_metrics_maps.js
forecast = variables.forecast.current.value
metric = variables.metric.current.value
metric_name = variables.metric.current.name
truth = variables.truth.current.value
grid = variables.grid.current.value
regions = variables.region.current.value
time_grouping = variables.time_grouping.current.value
time =  variables.time_filter.current.value

DATASET_KEYS = []
regions.forEach((region) => {
  DATASET_KEYS.push(`forecast_metric_map_1_2024-12-31_${forecast}_${grid}_${LEAD_DAY}_forecast_filter-False_obs_filter-True_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_precip`)
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
  color_max = 80
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

layers_to_map = []
DATASET_KEYS.forEach((key) => {
  layers_to_map.push({
          opacity: 0.7,
          sourcetype: "raster",
          source: [
            `https://terracotta.shared.rhizaresearch.org/singleband/${key}/{z}/{x}/{y}.png?${stretch}`
          ],
          below: "traces",
        })
});


return {
  data: [{
    type: 'scattermap',
    lat: ['45.5017', '46.9027'],
    lon: ['-73.5673', '-73.5673'],
    mode: 'markers',
    marker: {
      size: 0,
      showscale: true,
      colorscale: cscale,
      cmin: color_min,
      cmax: color_max
    }
  }],
  layout:
  {
    dragmode: 'zoom',
    map: {
      style: 'open-street-map',
      layers: layers_to_map,
      center: center,
      zoom: zoom
    },
    margin: {r: 0, t: 30, b: 0, l: 0},
    title: {
        text: `${metric_name} - Week ${lead_week} - ${advanced_metric}${advanced_units}`,
        xanchor: 'left',
        x: 0
    }

  }
}
