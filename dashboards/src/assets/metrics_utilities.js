// EXTERNAL:metrics_utilities.js

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
        background:transparent;
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

// ─── Refresh metric description panel ────────────────────────────────────────
function refreshMetricDescription(metric) {
    const panel = document.getElementById("metric-description-panel");
    if (!panel) return;
    panel.innerHTML = renderMetricDescriptionHtml(metric);
}
