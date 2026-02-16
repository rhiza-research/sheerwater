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
        colormap = "rdylgn";

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
        colormap = "rdylgn";

        // ── POD: [0, 1], higher is better ──
    } else if (m.startsWith("pod-")) {
        colorMin = 0;
        colorMax = 1;
        colormap = "rdylgn";

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
