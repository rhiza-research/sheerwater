// EXTERNAL:advanced_forecast_maps_onclick.js

var foundCenter = null
var foundZoom = null
for (const key of Object.keys(event.data || {})) {
  if (key.includes('.center')) foundCenter = event.data[key]
  if (key.includes('.zoom')) foundZoom = event.data[key]
}

if (foundCenter === null && foundZoom === null) {
  return event.layout   // nothing changed — don't clobber the view
}

document.last_center = foundCenter !== null ? foundCenter : document.last_center
document.last_zoom = foundZoom !== null ? foundZoom : document.last_zoom

updated_layout = event.layout
for (const key of Object.keys(event.layout)) {
  if (key.includes('map')) {
    if (foundCenter !== null) updated_layout[key].center = foundCenter
    if (foundZoom !== null) updated_layout[key].zoom = foundZoom
  }
}
return updated_layout
