// EXTERNAL:advanced_forecast_maps_onclick.js

console.log(event)
center = {}
zoom = 0
for (const key of Object.keys(event.data)) {
  if (key.includes('.center')) {
    center = event.data[key]
  }
  if (key.includes('.zoom')) {
    zoom = event.data[key]
  }
}

console.log(center)
console.log(zoom)

document.last_zoom = zoom
document.last_center = center

/*
updated_layout = event.layout
for (const key of Object.keys(event.layout)) {
  if (key.includes('map')) {
    updated_layout[key].center = center
    updated_layout[key].zoom = zoom
  }
}

return updated_layout*/
