// EXTERNAL:click_precip_pt.js

const urlFragment = 'https://dev.shared.rhizaresearch.org/sheerwater/112/d/deokdv0waovlsc/complete-sensor-timeseries?'
try {
  const { type: eventType, data: eventData } = event;

  if (eventType === 'click') {
    const clickedPoint = eventData?.points?.[0];
    const pointIndex = clickedPoint?.pointIndex;

    //get the lat, lon, time of the clicked point
    fields = data.series[0].fields;
    let lat = fields.find(f => f.name === "lat");
    let lon = fields.find(f => f.name === "lon");
    let timeField = fields.find(f => f.name === "time");

    //get agg days from variables
    let aggDays = variables.agg_days.current.value;
    // get start and end time stamps from timeField value to + aggDays
    let startTime = new Date(timeField.values.get(pointIndex));
    let endTime = new Date(startTime.getTime() + aggDays * 24 * 60 * 60 * 1000);

    if (pointIndex != null) {
        const url = `${urlFragment}var-lat=${lat.values.get(pointIndex)}&var-lon=${lon.values.get(pointIndex)}&from=${startTime.toISOString()}&to=${endTime.toISOString()}&var-timezone=utc`;
        window.open(url, '_blank');
    }
    
  }
} catch (error) {
    console.error('Error in map click handler:', error);
}
