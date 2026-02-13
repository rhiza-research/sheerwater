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

// ─── Month name mapping (M01 → January, etc.) ───────────────────────────────
const MONTH_CODE_TO_NAME = {
    M01: "January",
    M02: "February",
    M03: "March",
    M04: "April",
    M05: "May",
    M06: "June",
    M07: "July",
    M08: "August",
    M09: "September",
    M10: "October",
    M11: "November",
    M12: "December",
};

function humanizeTimeFilter(raw) {
    if (!raw || raw === "None") return raw;
    // Handle comma-separated lists like "M01,M02"
    return raw
        .split(",")
        .map((part) => {
            const trimmed = part.trim();
            return MONTH_CODE_TO_NAME[trimmed] || trimmed;
        })
        .join(", ");
}

// ─── Units lookup ────────────────────────────────────────────────────────────
// Some metrics are inherently unitless (correlations, skill scores, ratios).
// Only error metrics that are in the same units as the variable get product units.
const UNITLESS_METRICS = new Set([
    "acc", "pearson", "smape", "seeps",
    "bss", "spread_skill",
]);
const UNITLESS_METRIC_PREFIXES = [
    "heidke-", "pod-", "far-", "ets-", "csi-",
];

function isUnitlessMetric(metric) {
    const m = String(metric || "").toLowerCase();
    if (UNITLESS_METRICS.has(m)) return true;
    return UNITLESS_METRIC_PREFIXES.some((prefix) => m.startsWith(prefix));
}

function getUnitsForProduct(product) {
    const p = String(product || "").toLowerCase();
    if (p.includes("precip") || p.includes("rain") || p.includes("tp")) {
        return "mm/day";
    }
    if (
        p.includes("tmp2m") ||
        p.includes("t2m") ||
        p.includes("temp") ||
        p.includes("sst")
    ) {
        return "°C";
    }
    if (p.includes("wind") || p.includes("u10") || p.includes("v10")) {
        return "m/s";
    }
    if (p.includes("slp") || p.includes("mslp") || p.includes("pressure")) {
        return "hPa";
    }
    if (p.includes("z500") || p.includes("geopotential")) {
        return "m²/s²";
    }
    return "";
}

/** Resolve display units given both the metric and the product.
 *  Unitless metrics (correlations, skill scores) return "". */
function getUnits(metric, product) {
    if (isUnitlessMetric(metric)) return "";
    return getUnitsForProduct(product);
}

// ─── Metric descriptions ────────────────────────────────────────────────────
// direction: "lower" (smaller is better), "higher" (larger is better), "zero" (ideal = 0)
const METRIC_DESCRIPTIONS = {
    mae: {
        name: "Mean Absolute Error (MAE)",
        description:
            "Mean absolute error measures the average magnitude of the errors in a set of predictions, without considering their direction.",
        direction: "lower",
    },
    rmse: {
        name: "Root Mean Square Error (RMSE)",
        description:
            "Root mean squared error gives higher weight to large errors.",
        direction: "lower",
    },
    crps: {
        name: "Continuous Ranked Probability Score (CRPS)",
        description:
            "Continuous ranked probability score assesses probabilistic forecast accuracy.",
        direction: "lower",
    },
    bias: {
        name: "Bias",
        description:
            "Bias measures signed error magnitude.",
        direction: "zero",
    },
    smape: {
        name: "SMAPE",
        description:
            "SMAPE expresses error as a percent of total value (precip only). Range [0, 1].",
        direction: "lower",
    },
    seeps: {
        name: "Stable Equitable Error in Probability Space (SEEPS)",
        description:
            "SEEPS evaluates rainfall forecasts accounting for climatology.",
        direction: "lower",
    },
    acc: {
        name: "Anomaly Correlation Coefficient (ACC)",
        description:
            "Anomaly correlation coefficient compares forecast and observed anomalies relative to climatology. Range [−1, 1].",
        direction: "higher",
    },
    pearson: {
        name: "Pearson Correlation",
        description:
            "Pearson correlation measures linear association between predictions and observations. Range [−1, 1].",
        direction: "higher",
    },
    spread: {
        name: "Spread",
        description:
            "The ensemble spread (standard deviation) of forecasts. Useful for assessing whether forecast uncertainty is well calibrated.",
        direction: null,
    },
    bss: {
        name: "Brier Skill Score (BSS)",
        description:
            "Measures the improvement of a probabilistic forecast over a reference (climatology). Positive values indicate skill above the reference.",
        direction: "higher",
    },
};

// Prefix-based metrics (heidke-*, pod-*, far-*, ets-*, csi-*)
const PREFIX_METRIC_DESCRIPTIONS = [
    {
        prefix: "heidke-",
        name: "Heidke Skill Score (HSS)",
        description:
            "Heidke skill score compares forecast accuracy against random chance for one or more event thresholds. Range [−∞, 1].",
        direction: "higher",
    },
    {
        prefix: "pod-",
        name: "Probability of Detection (POD)",
        description:
            "Probability of detection = fraction of observed events correctly forecast. Range [0, 1].",
        direction: "higher",
    },
    {
        prefix: "csi-",
        name: "Critical Success Index (CSI)",
        description:
            "Critical success index measures the fraction of observed and/or forecast events that were correctly predicted (hits ÷ hits + misses + false alarms). Range [0, 1].",
        direction: "higher",
    },
    {
        prefix: "far-",
        name: "False Alarm Rate (FAR)",
        description:
            "False alarm rate = fraction of predicted events not observed. Range [0, 1].",
        direction: "lower",
    },
    {
        prefix: "ets-",
        name: "Equitable Threat Score (ETS)",
        description:
            "Equitable threat score measures threshold-event skill adjusted for chance. Range [−⅓, 1].",
        direction: "higher",
    },
];

function lookupMetricInfo(metric) {
    const m = String(metric || "").toLowerCase();
    // Exact match first
    if (METRIC_DESCRIPTIONS[m]) return METRIC_DESCRIPTIONS[m];
    // Prefix match
    for (const entry of PREFIX_METRIC_DESCRIPTIONS) {
        if (m.startsWith(entry.prefix)) return entry;
    }
    return null;
}

/** Return the metric "direction" used by colormap logic. */
function getMetricDirection(metric) {
    const info = lookupMetricInfo(metric);
    return info?.direction || null;
}

function renderMetricDescriptionHtml(metric) {
    const info = lookupMetricInfo(metric);
    if (!info) return "";

    let directionHtml = "";
    if (info.direction === "lower") {
        directionHtml = `<span style="color:#d32f2f; font-weight:600;">🔴 Smaller is better.</span>`;
    } else if (info.direction === "higher") {
        directionHtml = `<span style="color:#2e7d32; font-weight:600;">🟢 Larger is better.</span>`;
    } else if (info.direction === "zero") {
        directionHtml = `<span style="color:#757575; font-weight:600;">⚪ Ideal = 0.</span>`;
    }

    return `
      <div style="
        font-family:'IBM Plex Sans','Segoe UI',sans-serif;
        background:rgba(245,243,239,0.96);
        color:#0c1f2e;
        border:1px solid rgba(12,31,46,0.18);
        border-radius:10px;
        padding:10px 16px;
        margin-top:10px;
        font-size:13px;
        line-height:1.5;
        box-shadow:0 4px 12px rgba(8,16,28,0.10);
      ">
        <strong style="font-size:14px;">${info.name}</strong><br/>
        <span style="opacity:0.82;">${info.description}</span>
        ${directionHtml ? `<br/>${directionHtml}` : ""}
      </div>
    `;
}

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
        aggDays: readVar("agg_days", "7"),
        datasetFamily: "metric",
    };
};

function resolveRegion(_) {
    return "global";
}

let VARS = readVars();
let stretchRequestController = null;
let maplibreReady = null;
