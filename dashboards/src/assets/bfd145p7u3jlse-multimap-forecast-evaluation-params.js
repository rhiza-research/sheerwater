// EXTERNAL({"panel_id":"multimap-forecast-evaluation","key":"params"}):bfd145p7u3jlse-multimap-forecast-evaluation-params.js
const PANEL_RUNTIME_CONFIG = {
    RASTER_CROSSFADE_MS: 0,
};
const MULTIMAP_TIME_FILTER_OUTPUT_MODE = "NUMBER";

const MULTIMAP_PRODUCTS = [
    { key: "rain", label: "Precipitation", product: "era5_precip" },
    { key: "temp", label: "Temperature", product: "era5_tmp2m" },
];

const readVars = () => ({
    forecast: readVar("forecast"),
    grid: readVar("grid"),
    metric: readVar("metric"),
    timeGrouping: readVar("time_grouping"),
    timeFilter: readVar("time_filter", "None"),
    timeFilterOutputMode: MULTIMAP_TIME_FILTER_OUTPUT_MODE,
    maxLead: Number(readVar("max_lead", "6")) || 6,
});

function resolveRegion(forecast) {
    return forecast === "salient" ? "africa" : "global";
}

function getLeadWeeks(maxLead) {
    const safeMax = Math.max(1, Math.floor(Number(maxLead) || 1));
    return Array.from({ length: safeMax }, (_, idx) => idx + 1);
}
