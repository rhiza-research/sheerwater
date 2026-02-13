// EXTERNAL:terracotta_dataset_utilities.js
function buildDatasetId(params) {
    const datasetFamily = params?.datasetFamily || "grouped_metric";
    const { startDate, endDate } = resolveDatasetDates(datasetFamily);
    const timeSuffix =
        params.timeFilter && params.timeFilter !== "None" ? `_${params.timeFilter}` : "";

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
    let colormap = "reds";
    if (metric === "bias") {
        if (Math.abs(colorMin) > colorMax) {
            colorMax = Math.abs(colorMin);
        } else {
            colorMin = colorMax * -1;
        }
        colormap = product === "era5_tmp2m" ? "rdbu_r" : "brbg";
    } else if (metric === "acc") {
        colorMin = -1;
        colorMax = 1;
        colormap = "rdbu";
    } else if (metric === "seeps") {
        colorMin = 0;
        colorMax = 2.0;
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
