// EXTERNAL({"panel_id":"multimap-forecast-evaluation","key":"params"}):bfd145p7u3jlse-multimap-forecast-evaluation-params.js
const PROTOMAPS_KEY = "320f86609595a624";
const BASE_STYLE_URL_TEMPLATE =
    "https://api.protomaps.com/styles/v5/{flavor}/{lang}.json?key={key}";
const TERRACOTTA_BASE_URL = "https://terracotta.shared.rhizaresearch.org";
const MAP_CONTAINER_ITEM_CLASS = "map-container";
const MAP_CONTAINER_ID = "map-container";
const TERRACOTTA_LAYER_ID = "terracotta-raster";
const TERRACOTTA_OPACITY = 0.9;
const RASTER_CROSSFADE_MS = 0;
const RASTER_LOAD_TIMEOUT_MS = 1800;
const DEFAULT_FLAVOR = "black";
const BASE_STYLE_LANG = "en";
const ALLOWED_SOURCE_LAYERS = [
    "boundaries",
    "earth",
    "landcover",
    "places",
    "water",
];
const MANAGED_OVERLAY_GROUPS = [
    { key: "hydroFills", type: "fill", sourceLayer: "water" },
    { key: "hydroLines", type: "line", sourceLayer: "water" },
    { key: "adminLines", type: "line", sourceLayer: "boundaries" },
    {
        key: "adminBoundaryLabels",
        type: "symbol",
        sourceLayer: "boundaries",
    },
    { key: "adminAreaLabels", type: "symbol", sourceLayer: "places" },
];
const BOUNDARY_CONTRAST = {
    lineStrokeColor: "rgba(255,255,255,0.92)",
    lineStrokeOpacity: 0.95,
    lineCasingColor: "rgba(0,0,0,0.85)",
    lineCasingOpacity: 0.9,
    lineCasingExtraWidth: 1.8,
    labelTextColor: "#ffffff",
    labelHaloColor: "#000000",
    labelHaloWidth: 1.8,
    labelHaloBlur: 0.3,
};
const POLL_INTERVAL_MS = 300;
const VAR_STABILIZE_MS = 700;

const MULTIMAP_PRODUCTS = [
    { key: "rain", label: "Precipitation", product: "era5_precip" },
    { key: "temp", label: "Temperature", product: "era5_tmp2m" },
];

const replaceVariables =
    typeof context !== "undefined" &&
        context?.grafana?.replaceVariables &&
        typeof context.grafana.replaceVariables === "function"
        ? context.grafana.replaceVariables.bind(context.grafana)
        : (value) => value;

const readVar = (name, fallback = "") => {
    const token = `\${${name}}`;
    const value = replaceVariables(token);
    if (value === token || value === undefined || value === null || value === "") {
        return fallback;
    }
    return value;
};

const readVars = () => ({
    forecast: readVar("forecast"),
    grid: readVar("grid"),
    metric: readVar("metric"),
    timeGrouping: readVar("time_grouping"),
    timeFilter: readVar("time_filter", "None"),
    maxLead: Number(readVar("max_lead", "6")) || 6,
});

function resolveRegion(forecast) {
    return forecast === "salient" ? "africa" : "global";
}

function getLeadWeeks(maxLead) {
    const safeMax = Math.max(1, Math.floor(Number(maxLead) || 1));
    return Array.from({ length: safeMax }, (_, idx) => idx + 1);
}

let VARS = readVars();
let stretchRequestController = null;
let maplibreReady = null;
let syncMoveReady = null;
