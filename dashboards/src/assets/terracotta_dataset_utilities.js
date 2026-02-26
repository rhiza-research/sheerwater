// EXTERNAL:terracotta_dataset_utilities.js
function isNullSelection(value) {
    return value === undefined || value === null || value === "" || value === "None";
}

function resolveRegionForForecastValue(forecast, fallbackRegion = "global") {
    if (typeof resolveRegion === "function") {
        try {
            return resolveRegion(forecast);
        } catch (error) {
            console.warn("resolveRegion failed for reference forecast", error);
        }
    }
    return forecast === "salient" ? "africa" : fallbackRegion;
}

function buildReferenceParams(params) {
    const referenceVarMap = params?.referenceVarMap;
    if (!referenceVarMap || typeof referenceVarMap !== "object") {
        return null;
    }

    let hasReferenceOverride = false;
    let forecastOverridden = false;
    const nextParams = { ...params };

    Object.entries(referenceVarMap).forEach(([primaryKey, referenceKey]) => {
        const referenceValue = params?.[referenceKey];
        if (isNullSelection(referenceValue)) {
            return;
        }
        nextParams[primaryKey] = referenceValue;
        hasReferenceOverride = true;
        if (primaryKey === "forecast") {
            forecastOverridden = true;
        }
    });

    if (!hasReferenceOverride) {
        return null;
    }

    if (
        forecastOverridden &&
        !Object.prototype.hasOwnProperty.call(referenceVarMap, "region")
    ) {
        nextParams.region = resolveRegionForForecastValue(
            nextParams.forecast,
            params?.region || "global"
        );
    }

    return nextParams;
}

function resolveTerracottaTileRequest(params) {
    const datasetId = buildDatasetId(params);
    const referenceParams = buildReferenceParams(params);

    if (!referenceParams) {
        return {
            datasetId,
            computeMode: null,
            computeDatasetId2: null,
        };
    }
    const skillScoreSpec = getSkillScoreSpecForMetric(params?.metric);
    if (skillScoreSpec.supported === false) {
        return {
            datasetId,
            computeMode: null,
            computeDatasetId2: null,
        };
    }

    return {
        datasetId,
        computeMode: "skill_score",
        computeDatasetId2: buildDatasetId(referenceParams),
    };
}

function encodeTerracottaQuery(stretch) {
    return encodeURIComponent(stretch).replace(/%26/g, "&").replace(/%3D/g, "=");
}

function buildStretchString(colormap, range) {
    if (!range) {
        return "";
    }
    return `colormap=${colormap}&stretch_range=[${range.min},${range.max}]`;
}

function getSkillScoreSpecForMetric(metric) {
    if (typeof resolveSkillScoreSpec === "function") {
        return resolveSkillScoreSpec(metric);
    }
    return {
        computeMode: "skill_score",
        expression: "(1-v1/v2)",
        range: { min: -1, max: 1 },
        displayRange: { min: -1, max: 1 },
        colormap: "rdylgn",
    };
}

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
    const spec =
        typeof resolveMetricScale === "function"
            ? resolveMetricScale(metric, product, colorMin, colorMax)
            : { colorMin, colorMax, colormap: "reds" };
    return `colormap=${spec.colormap}&stretch_range=[${spec.colorMin},${spec.colorMax}]`;
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

function computeSharedStretchFromMetadata(metadataList, metric, product, params = null) {
    const request = params ? resolveTerracottaTileRequest(params) : null;
    if (request?.computeMode === "skill_score") {
        const spec = getSkillScoreSpecForMetric(metric);
        return buildStretchString(spec.colormap, spec.displayRange || spec.range);
    }
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

async function fetchMetadataByDatasetId(datasetId, signal) {
    const url = `${TERRACOTTA_BASE_URL}/metadata/${encodeURIComponent(datasetId)}`;
    const response = await fetch(url, signal ? { signal } : undefined);
    if (!response.ok) {
        const error = new Error(`Metadata request failed (${response.status})`);
        error.status = response.status;
        throw error;
    }
    return response.json();
}

async function fetchMetadata(params, signal) {
    const request = resolveTerracottaTileRequest(params);
    if (request.computeMode !== "skill_score") {
        return fetchMetadataByDatasetId(request.datasetId, signal);
    }
    const [primaryMetadata] = await Promise.all([
        fetchMetadataByDatasetId(request.datasetId, signal),
        fetchMetadataByDatasetId(request.computeDatasetId2, signal),
    ]);
    return primaryMetadata;
}

async function fetchStretch(params, signal) {
    const request = resolveTerracottaTileRequest(params);
    const metadata = await fetchMetadata(params, signal);
    if (request.computeMode === "skill_score") {
        const spec = getSkillScoreSpecForMetric(params.metric);
        return buildStretchString(spec.colormap, spec.displayRange || spec.range);
    }
    return computeStretch(metadata, params.metric, params.product);
}

function buildTileUrl(params, stretch) {
    const request = resolveTerracottaTileRequest(params);
    const datasetId = request.datasetId;
    if (request.computeMode === "skill_score") {
        const skillScoreSpec = getSkillScoreSpecForMetric(params.metric);
        const base = `${TERRACOTTA_BASE_URL}/compute/{z}/{x}/{y}.png`;
        const queryParts = [];
        if (stretch) {
            queryParts.push(encodeTerracottaQuery(stretch));
        }
        queryParts.push(
            `expression=${encodeURIComponent(skillScoreSpec.expression)}`
        );
        queryParts.push(`v1=${encodeURIComponent(datasetId)}`);
        queryParts.push(`v2=${encodeURIComponent(request.computeDatasetId2)}`);
        return { datasetId, tileUrl: `${base}?${queryParts.join("&")}` };
    }

    const base = `${TERRACOTTA_BASE_URL}/singleband/${encodeURIComponent(datasetId)}/{z}/{x}/{y}.png`;
    if (!stretch) {
        return { datasetId, tileUrl: base };
    }
    const query = encodeTerracottaQuery(stretch);
    return { datasetId, tileUrl: `${base}?${query}` };
}
