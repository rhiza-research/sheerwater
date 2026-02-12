// EXTERNAL:dataset_utilities.js
function buildDatasetId(params) {
    const timeSuffix =
        params.timeFilter && params.timeFilter !== "None" ? `_${params.timeFilter}` : "";
    return (
        "grouped_metric_2022-12-31_" +
        `${params.forecast}_${params.grid}_${params.lead}_lsm_${params.metric}_` +
        `${params.region}_True_2016-01-01_${params.timeGrouping}_${params.product}` +
        timeSuffix
    );
}

function computeStretch(metadata, metric, product) {
    const percentiles = metadata?.percentiles || [];
    if (percentiles.length < 95) {
        return "";
    }

    let colorMin = percentiles[4];
    let colorMax = percentiles[94];

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

async function fetchStretch(params, signal) {
    const datasetId = buildDatasetId(params);
    const url = `${TERRACOTTA_BASE_URL}/metadata/${encodeURIComponent(datasetId)}`;
    const response = await fetch(url, signal ? { signal } : undefined);
    const metadata = await response.json();
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
