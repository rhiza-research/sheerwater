// EXTERNAL:params_maplibre_maps.js

const PROTOMAPS_KEY = "320f86609595a624";
const BASE_STYLE_URL_TEMPLATE =
    "https://api.protomaps.com/styles/v5/{flavor}/{lang}.json?key={key}";
const TERRACOTTA_BASE_URL = "https://terracotta.shared.rhizaresearch.org";
const MAP_CONTAINER_ITEM_CLASS = "map-container";
const MAP_CONTAINER_ID = "map-container";
const TERRACOTTA_LAYER_ID = "terracotta-raster";
const TERRACOTTA_OPACITY = 0.9;

if (typeof RASTER_CROSSFADE_MS === "undefined") {
    globalThis.RASTER_CROSSFADE_MS = 220;
}
if (typeof RASTER_LOAD_TIMEOUT_MS === "undefined") {
    globalThis.RASTER_LOAD_TIMEOUT_MS = 1800;
}
if (typeof POLL_INTERVAL_MS === "undefined") {
    globalThis.POLL_INTERVAL_MS = 300;
}
if (typeof VAR_STABILIZE_MS === "undefined") {
    globalThis.VAR_STABILIZE_MS = 700;
}
if (typeof MAPLIBRE_LOAD_MODE === "undefined") {
    globalThis.MAPLIBRE_LOAD_MODE = "esm-first";
}

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
