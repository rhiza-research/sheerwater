// EXTERNAL({"panel_id":"station-evaluation","key":"params"}):dfd44cgdurwn4f-station-evaluation-params.js
const PROTOMAPS_KEY = "320f86609595a624";
const BASE_STYLE_URL_TEMPLATE =
    "https://api.protomaps.com/styles/v5/{flavor}/{lang}.json?key={key}";
const TERRACOTTA_BASE_URL = "https://terracotta.shared.rhizaresearch.org";
const MAP_CONTAINER_ITEM_CLASS = "map-container";
const MAP_CONTAINER_ID = "map-container";
const TERRACOTTA_LAYER_ID = "terracotta-raster";
const TERRACOTTA_OPACITY = 0.9;
const RASTER_CROSSFADE_MS = 220;
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
const STATIONEVAL_TIME_FILTER_OUTPUT_MODE = "MXX";

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

function resolveMetricProduct(product, truth) {
    if (typeof product === "string" && product.includes("_")) {
        return product;
    }
    const normalizedProduct = (product || "precip").trim() || "precip";
    const normalizedTruth = (truth || "era5").trim() || "era5";
    return `${normalizedTruth}_${normalizedProduct}`;
}

const readVars = () => {
    const truth = readVar("truth", "ghcn");
    const product = readVar("product", "precip");
    return {
        forecast: readVar("reanalysis", "era5"),
        grid: readVar("grid"),
        metric: readVar("metric", "mae"),
        product: resolveMetricProduct(product, truth),
        lead: readVar("lead", "week1"),
        timeGrouping: readVar("time_grouping"),
        timeFilter: readVar("time_filter", "None"),
        timeFilterOutputMode: STATIONEVAL_TIME_FILTER_OUTPUT_MODE,
        aggDays: readVar("agg_days", "7"),
        datasetFamily: "metric",
        vmin: readVar("vmin", ""),
        vmax: readVar("vmax", ""),
    };
};

function resolveRegion(_) {
    return "global";
}

let VARS = readVars();
let stretchRequestController = null;
let maplibreReady = null;
