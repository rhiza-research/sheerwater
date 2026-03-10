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

function formatRangeValue(value) {
    if (value === Infinity) return "∞";
    if (value === -Infinity) return "−∞";
    if (typeof value !== "number" || Number.isNaN(value)) return String(value || "");
    if (Number.isInteger(value)) return String(value);
    return String(value);
}

function formatMetricRange(range) {
    if (!range) return "";
    const minLabel = formatRangeValue(range.min);
    const maxLabel = formatRangeValue(range.max);
    if (!minLabel && !maxLabel) return "";
    if (minLabel && maxLabel) return `[${minLabel}, ${maxLabel}]`;
    if (minLabel) return `[${minLabel}, …]`;
    return `[…, ${maxLabel}]`;
}

// ─── Metric descriptions ────────────────────────────────────────────────────
// direction: "lower" (smaller is better), "higher" (larger is better), "zero" (ideal = 0)
const METRIC_DESCRIPTIONS = {
    mae: {
        name: "Mean Absolute Error (MAE)",
        description:
            "Mean absolute error measures the average magnitude of the errors in a set of predictions, without considering their direction.",
        direction: "lower",
        visual: { mode: "data", colormap: "reds" },
    },
    rmse: {
        name: "Root Mean Square Error (RMSE)",
        description:
            "Root mean squared error gives higher weight to large errors.",
        direction: "lower",
        visual: { mode: "data", colormap: "reds" },
    },
    crps: {
        name: "Continuous Ranked Probability Score (CRPS)",
        description:
            "Continuous ranked probability score assesses probabilistic forecast accuracy.",
        direction: "lower",
        visual: { mode: "data", colormap: "reds" },
    },
    bias: {
        name: "Bias",
        description:
            "Bias measures signed error magnitude.",
        direction: "zero",
        visual: {
            mode: "symmetric_zero",
            colormapByProduct: {
                temperature: "rdbu_r",
                default: "brbg",
            },
        },
    },
    smape: {
        name: "SMAPE",
        description:
            "SMAPE expresses error as a percent of total value (precip only).",
        direction: "lower",
        range: { min: 0, max: 1 },
        visual: { mode: "fixed", min: 0, max: 1, colormap: "reds" },
    },
    seeps: {
        name: "Stable Equitable Error in Probability Space (SEEPS)",
        description:
            "SEEPS evaluates rainfall forecasts accounting for climatology.",
        direction: "lower",
        range: { min: 0, max: 2 },
        visual: { mode: "fixed", min: 0, max: 2, colormap: "reds" },
    },
    acc: {
        name: "Anomaly Correlation Coefficient (ACC)",
        description:
            "Anomaly correlation coefficient compares forecast and observed anomalies relative to climatology.",
        direction: "higher",
        range: { min: -1, max: 1 },
        visual: { mode: "fixed", min: -1, max: 1, colormap: "rdbu" },
    },
    pearson: {
        name: "Pearson Correlation",
        description:
            "Pearson correlation measures linear association between predictions and observations.",
        direction: "higher",
        range: { min: -1, max: 1 },
        visual: { mode: "fixed", min: -1, max: 1, colormap: "rdbu" },
    },
    spread: {
        name: "Spread",
        description:
            "The ensemble spread (standard deviation) of forecasts. Useful for assessing whether forecast uncertainty is well calibrated.",
        direction: null,
        visual: { mode: "data", colormap: "reds" },
    },
    bss: {
        name: "Brier Skill Score (BSS)",
        description:
            "Measures the improvement of a probabilistic forecast over a reference (climatology). Positive values indicate skill above the reference.",
        direction: "higher",
        range: { min: -1, max: 1 },
        visual: { mode: "fixed", min: -1, max: 1, colormap: "rdylgn" },
    },
};

// Prefix-based metrics (heidke-*, pod-*, far-*, ets-*, csi-*)
const PREFIX_METRIC_DESCRIPTIONS = [
    {
        prefix: "heidke-",
        name: "Heidke Skill Score (HSS)",
        description:
            "Heidke skill score compares forecast accuracy against random chance for one or more event thresholds.",
        direction: "higher",
        range: { min: -Infinity, max: 1 },
        visual: { mode: "cap_max", max: 1, colormap: "rdbu" },
    },
    {
        prefix: "pod-",
        name: "Probability of Detection (POD)",
        description:
            "Probability of detection = fraction of observed events correctly forecast.",
        direction: "higher",
        range: { min: 0, max: 1 },
        visual: { mode: "fixed", min: 0, max: 1, colormap: "rdbu" },
    },
    {
        prefix: "csi-",
        name: "Critical Success Index (CSI)",
        description:
            "Critical success index measures the fraction of observed and/or forecast events that were correctly predicted (hits ÷ hits + misses + false alarms).",
        direction: "higher",
        range: { min: 0, max: 1 },
        visual: { mode: "fixed", min: 0, max: 1, colormap: "rdylgn" },
    },
    {
        prefix: "far-",
        name: "False Alarm Rate (FAR)",
        description:
            "False alarm rate = fraction of predicted events not observed.",
        direction: "lower",
        range: { min: 0, max: 1 },
        visual: { mode: "fixed", min: 0, max: 1, colormap: "reds" },
    },
    {
        prefix: "ets-",
        name: "Equitable Threat Score (ETS)",
        description:
            "Equitable threat score measures threshold-event skill adjusted for chance.",
        direction: "higher",
        range: { min: -1 / 3, max: 1 },
        visual: { mode: "fixed", min: -1 / 3, max: 1, colormap: "rdylgn" },
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

function resolveSkillScoreSpec(metric) {
    const info = lookupMetricInfo(metric);
    const metricName = info?.name || String(metric || "").toUpperCase() || "Metric";
    const direction = info?.direction || null;
    const normalizedMetric = String(metric || "").toLowerCase();
    const isAlreadySkillMetric =
        normalizedMetric === "bss" ||
        normalizedMetric === "spread_skill" ||
        normalizedMetric.startsWith("heidke-");

    const base = {
        computeMode: "skill_score",
        expression: "(1-v1/v2)",
        range: { min: -1, max: 1 },
        displayRange: { min: -1, max: 1 },
        theoreticalRange: { min: -Infinity, max: 1 },
        colormap: "rdylgn",
        formulaLabel: "Skill Score Formula",
    };

    if (isAlreadySkillMetric) {
        return {
            ...base,
            supported: false,
            formulaType: "already_skill_metric",
            reason: "already_skill_metric",
            description: {
                body:
                    `🛑 No skill-score transform was applied because ${metricName} is already a skill-style metric.`,
            },
        };
    }

    if (direction === "lower") {
        return {
            ...base,
            supported: true,
            formulaType: "lower_better_zero_ideal",
            description: {
                body:
                    `Skill score measures relative improvement over the selected reference using ${metricName}.`,
            },
        };
    }

    if (direction === "higher") {
        return {
            ...base,
            supported: true,
            formulaType: "higher_better_upper1_ideal",
            expression: "((v1-v2)/(1-v2))",
            description: {
                body:
                    `Skill score measures improvement toward the perfect score (1) relative to the selected reference using ${metricName}.`,
            },
        };
    }

    if (normalizedMetric === "bias") {
        return {
            ...base,
            supported: false,
            formulaType: "signed_zero_ideal_metric",
            reason: "signed_metric",
            description: {
                body:
                    `🛑 No skill-score transform was applied to ${metricName} because ${metricName} is signed and zero-centered.`,
            },
        };
    }

    return {
        ...base,
        supported: false,
        formulaType: "unsupported_metric_shape",
        reason: "unsupported_metric_shape",
        description: {
            body:
                `🛑 This skill-score transform uses a simple ratio-based formula that may not be well-defined for ${metricName}. Interpret values with caution.`,
        },
    };
}

function isTemperatureProduct(product) {
    const p = String(product || "").toLowerCase();
    return (
        p.includes("tmp2m") ||
        p.includes("t2m") ||
        p.includes("temp") ||
        p.includes("sst")
    );
}

function resolveMetricScale(metric, product, colorMin, colorMax) {
    const info = lookupMetricInfo(metric) || {};
    const visual = info.visual || { mode: "data", colormap: "reds" };
    const mode = visual.mode || "data";
    let nextMin = colorMin;
    let nextMax = colorMax;
    let colormap = visual.colormap || "reds";

    if (mode === "symmetric_zero") {
        const absMax = Math.max(Math.abs(nextMin), Math.abs(nextMax));
        nextMin = -absMax;
        nextMax = absMax;
        if (visual.colormapByProduct) {
            colormap = isTemperatureProduct(product)
                ? (visual.colormapByProduct.temperature || visual.colormapByProduct.default || colormap)
                : (visual.colormapByProduct.default || colormap);
        }
    } else if (mode === "fixed") {
        nextMin = visual.min;
        nextMax = visual.max;
    } else if (mode === "cap_max") {
        nextMax = visual.max;
    } else if (mode === "cap_min") {
        nextMin = visual.min;
    }

    return { colorMin: nextMin, colorMax: nextMax, colormap };
}

function renderMetricDescriptionHtml(metric) {
    const options =
        arguments.length > 1 && arguments[1] && typeof arguments[1] === "object"
            ? arguments[1]
            : {};
    const info = lookupMetricInfo(metric);
    if (!info) return "";

    const isSkillScoreMode = options.computeMode === "skill_score";
    const skillScoreSpec = isSkillScoreMode && typeof resolveSkillScoreSpec === "function"
        ? resolveSkillScoreSpec(metric)
        : null;
    const title = isSkillScoreMode
        ? `Skill Score on ${info.name}`
        : info.name;
    let directionHtml = "";
    const rangeText = formatMetricRange(info.range);
    if (!isSkillScoreMode && info.direction === "lower") {
        directionHtml = `<span style="color:#d32f2f; font-weight:600;">🔴 Smaller is better.</span>`;
    } else if (!isSkillScoreMode && info.direction === "higher") {
        directionHtml = `<span style="color:#2e7d32; font-weight:600;">🟢 Larger is better.</span>`;
    } else if (!isSkillScoreMode && info.direction === "zero") {
        directionHtml = `<span style="color:#757575; font-weight:600;">⚪ Ideal = 0.</span>`;
    }
    const skillScoreRangeText = formatMetricRange(
        options.skillScoreRange ||
        skillScoreSpec?.displayRange ||
        skillScoreSpec?.range ||
        { min: -1, max: 1 }
    );
    const skillScoreTheoreticalRangeText = formatMetricRange(
        skillScoreSpec?.theoreticalRange || null
    );
    const skillScoreFormula =
        options.skillScoreFormula || skillScoreSpec?.expression || "";
    const skillScoreBody =
        skillScoreSpec?.description?.body ||
        "Skill score measures relative improvement over the selected reference using the displayed metric.";
    const skillScoreFormulaLabel = skillScoreSpec?.formulaLabel || "Formula";
    const showAppliedSkillScoreDetails = skillScoreSpec?.supported !== false;
    const skillScoreDirectionHtml = showAppliedSkillScoreDetails
        ? `<span style="color:#2e7d32; font-weight:600;">🟢 Larger is better. Ideal = 1, Parity with reference = 0.</span>`
        : "";
    const skillScoreHtml = isSkillScoreMode
        ? `
        <br/>
        ${showAppliedSkillScoreDetails && skillScoreFormula ? `<br/><span style="opacity:0.82;">${skillScoreFormulaLabel}: ${skillScoreFormula}</span>` : ""}
        <br/><span style="opacity:0.82;">${skillScoreBody}</span>
        ${showAppliedSkillScoreDetails && (skillScoreTheoreticalRangeText || skillScoreRangeText)
            ? `<br/><span style="opacity:0.82;">${skillScoreTheoreticalRangeText ? `Theoretical range: ${skillScoreTheoreticalRangeText}` : ""}${skillScoreTheoreticalRangeText && skillScoreRangeText ? `. ` : ""}${skillScoreRangeText ? `Display Range: ${skillScoreRangeText}` : ""}</span>`
            : ""}
        ${skillScoreDirectionHtml ? `<br/>${skillScoreDirectionHtml}` : ""}
      `
        : "";

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
        <strong style="font-size:14px;">${title}</strong><br/>
        <span style="opacity:0.82;">${info.description}</span>
        ${isSkillScoreMode ? skillScoreHtml : ""}
        ${!isSkillScoreMode && rangeText ? `<br/><span style="opacity:0.82;">Reference range: ${rangeText}</span>` : ""}
        ${directionHtml ? `<br/>${directionHtml}` : ""}
      </div>
    `;
}

// ─── Refresh metric description panel ────────────────────────────────────────
function refreshMetricDescription(metric, options = {}) {
    const panel = document.getElementById("metric-description-panel");
    if (!panel) return;
    panel.innerHTML = renderMetricDescriptionHtml(metric, options);
}
