// EXTERNAL:maplibre-singlemap-orchestration.js

function getPanelRoot() {
    return (
        document.querySelector("#panel-content") ||
        document.querySelector(".panel-content") ||
        document.querySelector(".panel-content--no-padding") ||
        document.querySelector(".panel-container") ||
        document.body
    );
}

function getOrCreateHostContainer() {
    const existing = document.getElementById(MAP_CONTAINER_ID);
    if (existing) {
        return existing;
    }
    const host = document.createElement("div");
    host.id = MAP_CONTAINER_ID;
    host.className = MAP_CONTAINER_ITEM_CLASS;
    getPanelRoot().appendChild(host);
    return host;
}

async function initCurrentMapPage() {
    const container = injectContainerAndStyles();
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

    const params = {
        ...VARS,
        region: resolveRegion(VARS.forecast),
    };

    let stretch = "";
    try {
        stretch = await fetchStretch(params);
    } catch (error) {
        console.error("Failed to fetch stretch", error);
    }
    refreshColorScale(stretch);

    const { datasetId, tileUrl } = buildTileUrl(params, stretch);
    let baseStyle = null;
    try {
        baseStyle = await fetchPreparedStyle(DEFAULT_FLAVOR);
    } catch (error) {
        console.error("Failed to fetch prepared style", error);
        return;
    }

    const existingRuntime = window.__grafanaMaplibre;
    if (existingRuntime?.pollHandle) {
        window.clearInterval(existingRuntime.pollHandle);
    }
    if (existingRuntime && existingRuntime.map) {
        try {
            existingRuntime.map.remove();
        } catch (error) {
            console.warn("Failed to remove existing map", error);
        }
    }

    const map = createSingleMapInstance(container, baseStyle);

    window.__grafanaMaplibre = {
        map,
        datasetId,
        tileUrl,
        stretch,
        params,
        rasterSlot: 0,
        rasterSwapToken: 0,
        ready: false,
    };

    map.on("load", () => {
        window.__grafanaMaplibre.ready = true;
        applyBoundaryContrastOverrides(map);
        setRasterLayer(map, tileUrl, 0, TERRACOTTA_OPACITY);
        removeRasterSlot(map, 1);
    });

    let pendingVars = null;
    let pendingSince = 0;
    let refreshToken = 0;

    window.__grafanaMaplibre.pollHandle = window.setInterval(async () => {
        if (!window.__grafanaMaplibre?.ready) {
            return;
        }

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
        const nextParams = {
            ...VARS,
            region: resolveRegion(VARS.forecast),
        };

        if (stretchRequestController) {
            stretchRequestController.abort();
        }
        stretchRequestController = new AbortController();
        const token = ++refreshToken;

        let nextStretch = "";
        try {
            nextStretch = await fetchStretch(
                nextParams,
                stretchRequestController.signal
            );
        } catch (error) {
            if (error?.name === "AbortError") {
                return;
            }
            console.error("Failed to fetch stretch", error);
        }
        if (token !== refreshToken) {
            return;
        }

        const next = buildTileUrl(nextParams, nextStretch);
        if (nextStretch !== window.__grafanaMaplibre.stretch) {
            refreshColorScale(nextStretch);
        }

        if (next.tileUrl !== window.__grafanaMaplibre.tileUrl) {
            await swapRasterLayer(window.__grafanaMaplibre, next.tileUrl);
        }

        window.__grafanaMaplibre.datasetId = next.datasetId;
        window.__grafanaMaplibre.tileUrl = next.tileUrl;
        window.__grafanaMaplibre.stretch = nextStretch;
        window.__grafanaMaplibre.params = nextParams;
    }, POLL_INTERVAL_MS);
}
