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

async function initCurrentMapPage(panelState = null, panelDeps = {}) {
    const readVarsFn =
        panelDeps.readVars ||
        (typeof readVars === "function" ? readVars : null);
    const resolveRegionFn =
        panelDeps.resolveRegion ||
        (typeof resolveRegion === "function" ? resolveRegion : (_) => "global");
    if (typeof readVarsFn !== "function") {
        throw new Error("initCurrentMapPage requires panelDeps.readVars");
    }
    if (!panelState) {
        panelState = createBtPanelState(readVarsFn());
    }
    const container = injectContainerAndStyles();
    const currentVars = panelState.vars;

    const params = {
        ...currentVars,
        region: resolveRegionFn(currentVars.forecast),
    };

    // Kick off all three network requests in parallel
    const [maplibreResult, stretchResult, styleResult] = await Promise.allSettled([
        loadMaplibre(),
        fetchStretch(params),
        fetchPreparedStyle(DEFAULT_FLAVOR),
    ]);

    // ── Validate MapLibre loaded ──
    if (maplibreResult.status === "rejected") {
        console.error("MapLibre failed to load.", maplibreResult.reason);
        return;
    }
    if (!getMaplibreGlobal()) {
        console.error("MapLibre is unavailable after load.");
        return;
    }
    if (!window.maplibregl && getMaplibreGlobal()) {
        window.maplibregl = getMaplibreGlobal();
    }

    // ── Resolve stretch (may have failed → no-data) ──
    let stretch = "";
    let fetchFailed = false;
    if (stretchResult.status === "fulfilled") {
        stretch = stretchResult.value;
    } else {
        console.error("Failed to fetch stretch", stretchResult.reason);
        fetchFailed = true;
    }

    // ── Apply vmin/vmax overrides ──
    stretch = applyVminVmaxOverrides(
        stretch,
        currentVars.vmin,
        currentVars.vmax,
        params.metric,
        params.product
    );

    refreshColorScale(stretch, params.product, params.metric);
    refreshMetricDescription(params.metric);

    // ── Resolve base style ──
    if (styleResult.status === "rejected") {
        console.error("Failed to fetch prepared style", styleResult.reason);
        return;
    }
    const baseStyle = styleResult.value;

    const { datasetId, tileUrl } = buildTileUrl(params, stretch);

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
        if (fetchFailed || !stretch) {
            showNoDataOverlay(container);
        } else {
            hideNoDataOverlay(container);
            setRasterLayer(map, tileUrl, 0, TERRACOTTA_OPACITY);
        }
        removeRasterSlot(map, 1);
    });

    let pendingVars = null;
    let pendingSince = 0;
    let refreshToken = 0;

    window.__grafanaMaplibre.pollHandle = window.setInterval(async () => {
        if (!window.__grafanaMaplibre?.ready) {
            return;
        }

        const observedVars = readVarsFn();
        const observedSig = JSON.stringify(observedVars);
        const currentSig = JSON.stringify(panelState.vars);
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

        if (
            Date.now() - pendingSince <
            getBtConfig("VAR_STABILIZE_MS", VAR_STABILIZE_MS)
        ) {
            return;
        }

        panelState.vars = pendingVars;
        pendingVars = null;
        pendingSince = 0;
        const nextVars = panelState.vars;
        const nextParams = {
            ...nextVars,
            region: resolveRegionFn(nextVars.forecast),
        };

        if (panelState.stretchRequestController) {
            panelState.stretchRequestController.abort();
        }
        panelState.stretchRequestController = new AbortController();
        const token = ++refreshToken;

        let nextStretch = "";
        let nextFetchFailed = false;
        try {
            nextStretch = await fetchStretch(
                nextParams,
                panelState.stretchRequestController.signal
            );
        } catch (error) {
            if (error?.name === "AbortError") {
                return;
            }
            console.error("Failed to fetch stretch", error);
            nextFetchFailed = true;
        }
        if (token !== refreshToken) {
            return;
        }

        // ── Apply vmin/vmax overrides ──
        nextStretch = applyVminVmaxOverrides(
            nextStretch,
            nextVars.vmin,
            nextVars.vmax,
            nextParams.metric,
            nextParams.product
        );

        // Handle no-data state
        if (nextFetchFailed || !nextStretch) {
            showNoDataOverlay(container);
            removeRasterSlot(map, 0);
            removeRasterSlot(map, 1);
            refreshColorScale("", nextParams.product, nextParams.metric);
        } else {
            hideNoDataOverlay(container);

            const next = buildTileUrl(nextParams, nextStretch);
            if (nextStretch !== window.__grafanaMaplibre.stretch) {
                refreshColorScale(nextStretch, nextParams.product, nextParams.metric);
            }

            if (next.tileUrl !== window.__grafanaMaplibre.tileUrl) {
                await swapRasterLayer(window.__grafanaMaplibre, next.tileUrl);
            }

            window.__grafanaMaplibre.datasetId = next.datasetId;
            window.__grafanaMaplibre.tileUrl = next.tileUrl;
            window.__grafanaMaplibre.stretch = nextStretch;
        }

        // Always refresh metric description on variable change
        refreshMetricDescription(nextParams.metric);
        window.__grafanaMaplibre.params = nextParams;
    }, getBtConfig("POLL_INTERVAL_MS", POLL_INTERVAL_MS));
}
