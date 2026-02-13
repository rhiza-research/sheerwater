// EXTERNAL:maplibre-multimap-orchestration.js

function ensureRuntimeContainer() {
    const existingRuntime = window.__grafanaMaplibreMultimap;
    if (existingRuntime?.pollHandle) {
        window.clearInterval(existingRuntime.pollHandle);
    }
    if (existingRuntime?.cells) {
        existingRuntime.cells.forEach((cellRuntime) => {
            if (cellRuntime?.map) {
                try {
                    cellRuntime.map.remove();
                } catch (error) {
                    console.warn("Failed to remove existing multimap map", error);
                }
            }
        });
    }
}

function applyManualSync(maps) {
    let syncing = false;
    const syncFrom = (sourceMap) => {
        if (syncing) {
            return;
        }
        syncing = true;
        const center = sourceMap.getCenter();
        const zoom = sourceMap.getZoom();
        const bearing = sourceMap.getBearing();
        const pitch = sourceMap.getPitch();

        maps.forEach((map) => {
            if (map === sourceMap) {
                return;
            }
            map.jumpTo({ center, zoom, bearing, pitch });
        });
        syncing = false;
    };

    maps.forEach((map) => {
        map.on("moveend", () => syncFrom(map));
        map.on("zoomend", () => syncFrom(map));
        map.on("dragend", () => syncFrom(map));
    });
}

function loadSyncMovePlugin() {
    if (window.syncMaps && typeof window.syncMaps === "function") {
        return Promise.resolve();
    }
    if (syncMoveReady) {
        return syncMoveReady;
    }

    syncMoveReady = new Promise((resolve) => {
        const script = document.createElement("script");
        script.src = "https://unpkg.com/mapbox-gl-sync-move@0.3.1/index.js";
        script.onload = () => resolve();
        script.onerror = () => resolve();
        document.head.appendChild(script);
    });

    return syncMoveReady;
}

async function synchronizeMaps(cellRuntimes) {
    const maps = cellRuntimes.map((runtime) => runtime.map).filter(Boolean);
    if (maps.length < 2) {
        return;
    }

    await loadSyncMovePlugin();
    if (window.syncMaps && typeof window.syncMaps === "function") {
        try {
            window.syncMaps(...maps);
            return;
        } catch (error) {
            console.warn("syncMaps plugin failed, using fallback sync", error);
        }
    }
    applyManualSync(maps);
}

function buildCellParams(vars, cellDef) {
    return {
        forecast: vars.forecast,
        grid: vars.grid,
        metric: vars.metric,
        product: cellDef.productValue,
        lead: `week${cellDef.week}`,
        timeGrouping: vars.timeGrouping,
        timeFilter: vars.timeFilter,
        region: resolveRegion(vars.forecast),
    };
}

function setProductRowVisibility(productKey, visible) {
    const row = document.getElementById(`bt-multimap-row-${productKey}`);
    if (!row) {
        return;
    }
    row.style.display = visible ? "" : "none";
}

async function refreshAllCells(runtime, vars) {
    if (stretchRequestController) {
        stretchRequestController.abort();
    }
    stretchRequestController = new AbortController();
    const signal = stretchRequestController.signal;
    const token = (runtime.refreshToken || 0) + 1;
    runtime.refreshToken = token;

    const metadataResults = await Promise.all(
        runtime.cells.map(async (cellRuntime) => {
            const nextParams = buildCellParams(vars, cellRuntime.def);
            let metadata = null;
            try {
                metadata = await fetchMetadata(nextParams, signal);
            } catch (error) {
                if (error?.name !== "AbortError" && error?.status !== 404) {
                    console.error("Failed to fetch metadata", error);
                }
            }
            return {
                key: cellRuntime.def.key,
                productKey: cellRuntime.def.productKey,
                params: nextParams,
                metadata,
            };
        })
    );

    if (runtime.refreshToken !== token) {
        return;
    }

    const scaleByProduct = {};
    MULTIMAP_PRODUCTS.forEach((product) => {
        const leadMetadata = metadataResults
            .filter(
                (result) =>
                    result.productKey === product.key && result.metadata !== null
            )
            .map((result) => result.metadata);
        scaleByProduct[product.key] = computeSharedStretchFromMetadata(
            leadMetadata,
            vars.metric,
            product.product
        );
    });

    MULTIMAP_PRODUCTS.forEach((product) => {
        const hasStretch = Boolean(scaleByProduct[product.key]);
        setProductRowVisibility(product.key, hasStretch);
        const scaleMarkup = renderColorScaleHtml(scaleByProduct[product.key] || "");
        const rowScaleEl = document.getElementById(
            `bt-multimap-row-scale-${product.key}`
        );
        if (rowScaleEl) {
            rowScaleEl.innerHTML = scaleMarkup;
        }
        const scaleEls = document.querySelectorAll(
            `.bt-multimap-map-scale[data-product-key="${product.key}"]`
        );
        scaleEls.forEach((scaleEl) => {
            scaleEl.innerHTML = scaleMarkup;
        });
    });

    const results = metadataResults.map((result) => {
        const sharedStretch = scaleByProduct[result.productKey] || "";
        if (!sharedStretch) {
            return {
                ...result,
                stretch: "",
                datasetId: buildDatasetId(result.params),
                tileUrl: "",
            };
        }
        if (result.metadata === null) {
            return {
                ...result,
                stretch: sharedStretch,
                datasetId: buildDatasetId(result.params),
                tileUrl: "",
            };
        }
        const next = buildTileUrl(result.params, sharedStretch);
        return {
            ...result,
            stretch: sharedStretch,
            datasetId: next.datasetId,
            tileUrl: next.tileUrl,
        };
    });

    for (const result of results) {
        const cellRuntime = runtime.cellsByKey.get(result.key);
        if (!cellRuntime) {
            continue;
        }

        const previousTileUrl = cellRuntime.tileUrl;
        cellRuntime.params = result.params;
        cellRuntime.stretch = result.stretch;
        cellRuntime.datasetId = result.datasetId;
        cellRuntime.tileUrl = result.tileUrl;

        if (!cellRuntime.ready) {
            continue;
        }

        if (!result.tileUrl) {
            removeRasterSlot(cellRuntime.map, 0);
            removeRasterSlot(cellRuntime.map, 1);
            continue;
        }

        if (!previousTileUrl) {
            setRasterLayer(cellRuntime.map, result.tileUrl, 0, TERRACOTTA_OPACITY);
            removeRasterSlot(cellRuntime.map, 1);
            continue;
        }

        if (previousTileUrl !== result.tileUrl) {
            await swapRasterLayer(cellRuntime, result.tileUrl);
        }
    }
}

async function initCurrentMultimapPage() {
    const leadWeeks = getLeadWeeks(VARS.maxLead);
    buildMultimapLayout(leadWeeks);

    try {
        await loadMaplibre();
    } catch (error) {
        console.error("MapLibre failed to load.", error);
        return;
    }

    if (!getMaplibreGlobal()) {
        console.error("MapLibre is unavailable after load.");
        return;
    }
    if (!window.maplibregl && getMaplibreGlobal()) {
        window.maplibregl = getMaplibreGlobal();
    }

    let baseStyle = null;
    try {
        baseStyle = await fetchPreparedStyle(DEFAULT_FLAVOR);
    } catch (error) {
        console.error("Failed to fetch prepared style", error);
        return;
    }

    ensureRuntimeContainer();

    const defs = getCellDefinitions(leadWeeks);
    const cells = defs
        .map((def) => {
            const container = document.getElementById(def.containerId);
            if (!container) {
                return null;
            }
            const map = createSingleMapInstance(container, baseStyle);
            const cellRuntime = {
                def,
                map,
                ready: false,
                datasetId: "",
                tileUrl: "",
                stretch: "",
                params: null,
                rasterSlot: 0,
                rasterSwapToken: 0,
            };
            map.on("load", () => {
                cellRuntime.ready = true;
                applyBoundaryContrastOverrides(map);
                if (cellRuntime.tileUrl) {
                    setRasterLayer(map, cellRuntime.tileUrl, 0, TERRACOTTA_OPACITY);
                    removeRasterSlot(map, 1);
                }
            });
            return cellRuntime;
        })
        .filter(Boolean);

    const cellsByKey = new Map(cells.map((cell) => [cell.def.key, cell]));

    window.__grafanaMaplibreMultimap = {
        cells,
        cellsByKey,
        refreshToken: 0,
        pollHandle: null,
    };

    synchronizeMaps(cells);
    await refreshAllCells(window.__grafanaMaplibreMultimap, VARS);

    let pendingVars = null;
    let pendingSince = 0;

    window.__grafanaMaplibreMultimap.pollHandle = window.setInterval(async () => {
        const observedVars = readVars();
        const observedSig = JSON.stringify(observedVars);
        const currentSig = JSON.stringify(VARS);
        if (observedSig === currentSig) {
            pendingVars = null;
            pendingSince = 0;
            return;
        }

        if (!pendingVars || JSON.stringify(pendingVars) !== observedSig) {
            pendingVars = observedVars;
            pendingSince = Date.now();
            return;
        }

        if (Date.now() - pendingSince < VAR_STABILIZE_MS) {
            return;
        }

        VARS = pendingVars;
        pendingVars = null;
        pendingSince = 0;

        await refreshAllCells(window.__grafanaMaplibreMultimap, VARS);
    }, POLL_INTERVAL_MS);
}
