// EXTERNAL:terracotta_dataset_utilities.js
function buildDatasetId(params) {
    const datasetFamily = params?.datasetFamily || "grouped_metric";
    const { startDate, endDate } = resolveDatasetDates(datasetFamily);
    const rawTimeFilter = params?.timeFilter;
    const timeFilter =
        typeof normalizeTimeFilter === "function"
            ? normalizeTimeFilter(
                rawTimeFilter,
                params?.timeFilterOutputMode || "MXX"
            )
            : rawTimeFilter;
    const timeSuffix =
        timeFilter && timeFilter !== "None" ? `_${timeFilter}` : "";

    if (datasetFamily === "metric") {
        const aggDays = String(params?.aggDays || "7");
        const { truth, category } = splitProduct(params?.product);
        return (
            [
                "metric",
                aggDays,
                endDate,
                params.forecast,
                params.grid,
                "lsm",
                params.metric,
                "global",
                "None",
                "True",
                startDate,
                params.timeGrouping,
                truth,
                category,
            ].join("_") + timeSuffix
        );
    }

    return (
        `grouped_metric_${endDate}_` +
        `${params.forecast}_${params.grid}_${params.lead}_lsm_${params.metric}_` +
        `${params.region}_True_${startDate}_${params.timeGrouping}_${params.product}` +
        timeSuffix
    );
}

function resolveDatasetDates(datasetFamily) {
    if (datasetFamily === "metric") {
        return { startDate: "1998-01-01", endDate: "2024-12-31" };
    }
    return { startDate: "2016-01-01", endDate: "2022-12-31" };
}

function splitProduct(product) {
    const raw = String(product || "");
    const firstUnderscore = raw.indexOf("_");
    if (firstUnderscore > 0 && firstUnderscore < raw.length - 1) {
        return {
            truth: raw.slice(0, firstUnderscore),
            category: raw.slice(firstUnderscore + 1),
        };
    }
    return { truth: "era5", category: raw || "precip" };
}

function extractPercentileBounds(metadata) {
    const percentiles = metadata?.percentiles || [];
    if (percentiles.length < 95) {
        return null;
    }
    return [percentiles[4], percentiles[94]];
}

function buildStretchFromBounds(colorMin, colorMax, metric, product) {
    const m = String(metric || "").toLowerCase();
    let colormap = "reds";

    // ── Bias: diverging around 0 ──
    if (m === "bias") {
        // Symmetrise around zero
        const absMax = Math.max(Math.abs(colorMin), Math.abs(colorMax));
        colorMin = -absMax;
        colorMax = absMax;
        colormap = product === "era5_tmp2m" ? "rdbu_r" : "brbg";

        // ── ACC / Pearson: correlation [-1, 1], higher is better ──
    } else if (m === "acc" || m === "pearson") {
        colorMin = -1;
        colorMax = 1;
        colormap = "rdbu";

        // ── SEEPS: fixed [0, 2], lower is better ──
    } else if (m === "seeps") {
        colorMin = 0;
        colorMax = 2.0;
        colormap = "reds";

        // ── SMAPE: fixed [0, 1], lower is better ──
    } else if (m === "smape") {
        colorMin = 0;
        colorMax = 1;
        colormap = "reds";

        // ── Heidke: higher is better, open lower bound up to 1 ──
    } else if (m.startsWith("heidke-")) {
        // Keep data-driven min, cap max at 1
        colorMax = 1;
        colormap = "rdbu";

        // ── POD: [0, 1], higher is better ──
    } else if (m.startsWith("pod-")) {
        colorMin = 0;
        colorMax = 1;
        colormap = "rdbu";

        // ── CSI: [0, 1], higher is better ──
    } else if (m.startsWith("csi-")) {
        colorMin = 0;
        colorMax = 1;
        colormap = "rdylgn";

        // ── FAR: [0, 1], lower is better ──
    } else if (m.startsWith("far-")) {
        colorMin = 0;
        colorMax = 1;
        colormap = "reds";

        // ── ETS: [-1/3, 1], higher is better ──
    } else if (m.startsWith("ets-")) {
        colorMin = -1 / 3;
        colorMax = 1;
        colormap = "rdylgn";

        // ── MAE, RMSE, CRPS, and anything else: lower is better ──
    } else {
        // m === "mae" || m === "rmse" || m === "crps" || fallback
        colormap = "reds";
    }

    return `colormap=${colormap}&stretch_range=[${colorMin},${colorMax}]`;
}

/** Parse a vmin/vmax variable string into a finite number, or return null. */
function parseVBound(raw) {
    if (raw === undefined || raw === null || raw === "") return null;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
}

/**
 * Apply user-supplied vmin/vmax overrides to a stretch string.
 * If a stretch string already exists, the colormap is preserved and only the
 * stretch_range bounds that have a corresponding vmin/vmax are replaced.
 * If no stretch string exists yet (e.g. data-driven bounds couldn't be
 * computed), we fall back to buildStretchFromBounds with the overrides so the
 * correct colormap is still chosen for the metric.
 */
function applyVminVmaxOverrides(stretch, vmin, vmax, metric, product) {
    const parsedVmin = parseVBound(vmin);
    const parsedVmax = parseVBound(vmax);

    // Nothing to override
    if (parsedVmin === null && parsedVmax === null) return stretch;

    if (!stretch) {
        // No data-driven stretch available; build one from overrides alone.
        // Use 0 as a reasonable fallback for whichever bound isn't set.
        const fallbackMin = parsedVmin !== null ? parsedVmin : 0;
        const fallbackMax = parsedVmax !== null ? parsedVmax : 0;
        return buildStretchFromBounds(fallbackMin, fallbackMax, metric, product);
    }

    // Parse the existing stretch to extract colormap and current range
    const decoded = decodeURIComponent(stretch);
    const colormapMatch = decoded.match(/colormap=([^&]+)/);
    const rangeMatch = decoded.match(/stretch_range=\[([^\]]+)\]/);
    const colormap = colormapMatch ? colormapMatch[1] : "reds";

    let currentMin = 0;
    let currentMax = 1;
    if (rangeMatch) {
        const parts = rangeMatch[1].split(",").map((v) => Number(v.trim()));
        if (parts.length >= 2) {
            currentMin = parts[0];
            currentMax = parts[1];
        }
    }

    const finalMin = parsedVmin !== null ? parsedVmin : currentMin;
    const finalMax = parsedVmax !== null ? parsedVmax : currentMax;

    return `colormap=${colormap}&stretch_range=[${finalMin},${finalMax}]`;
}

function computeStretch(metadata, metric, product) {
    const bounds = extractPercentileBounds(metadata);
    if (!bounds) {
        return "";
    }
    return buildStretchFromBounds(bounds[0], bounds[1], metric, product);
}

function computeSharedStretchFromMetadata(metadataList, metric, product) {
    const bounds = (metadataList || [])
        .map((metadata) => extractPercentileBounds(metadata))
        .filter((item) => Array.isArray(item));
    if (!bounds.length) {
        return "";
    }
    const colorMin = Math.min(...bounds.map((item) => item[0]));
    const colorMax = Math.max(...bounds.map((item) => item[1]));
    return buildStretchFromBounds(colorMin, colorMax, metric, product);
}

async function fetchMetadata(params, signal) {
    const datasetId = buildDatasetId(params);
    const url = `${TERRACOTTA_BASE_URL}/metadata/${encodeURIComponent(datasetId)}`;
    const response = await fetch(url, signal ? { signal } : undefined);
    if (!response.ok) {
        const error = new Error(`Metadata request failed (${response.status})`);
        error.status = response.status;
        throw error;
    }
    return response.json();
}

async function fetchStretch(params, signal) {
    const metadata = await fetchMetadata(params, signal);
    return computeStretch(metadata, params.metric, params.product);
}

function buildTileUrl(params, stretch) {
    const datasetId = buildDatasetId(params);
    const base = `${TERRACOTTA_BASE_URL}/singleband/${encodeURIComponent(datasetId)}/{z}/{x}/{y}.png`;
    if (!stretch) {
        return { datasetId, tileUrl: base };
    }
    const query = encodeURIComponent(stretch)
        .replace(/%26/g, "&")
        .replace(/%3D/g, "=");
    return { datasetId, tileUrl: `${base}?${query}` };
}
