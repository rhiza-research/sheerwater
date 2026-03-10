// EXTERNAL:bt_shared_preload_exports.js
(() => {
    function runBtPreloadWarmup() {
        const warmupTasks = [];

        if (typeof ensureMultimapStyles === "function") {
            try {
                ensureMultimapStyles();
            } catch (error) {
                console.warn("[bt preload] Failed to inject multimap styles", error);
            }
        }

        if (typeof loadMaplibre === "function") {
            warmupTasks.push(
                Promise.resolve()
                    .then(() => loadMaplibre())
                    .catch((error) => {
                        console.warn("[bt preload] MapLibre warmup failed", error);
                        return null;
                    })
            );
        }

        if (typeof fetchPreparedStyle === "function") {
            warmupTasks.push(
                Promise.resolve()
                    .then(() => fetchPreparedStyle(DEFAULT_FLAVOR))
                    .catch((error) => {
                        console.warn("[bt preload] Base style warmup failed", error);
                        return null;
                    })
            );
        }

        const warmupPromise = Promise.allSettled(warmupTasks);
        const runtime = getBtSharedRuntime();
        runtime.preloadWarmupReady = warmupPromise;
        return warmupPromise;
    }

    const shared = {
        readVar,
        resolveMetricProduct,
        createBtPanelState,
        getBtSharedRuntime,
        applyBtPanelConfig,
        getBtConfig,
        loadMaplibre,
        fetchPreparedStyle,
        ensureMultimapStyles,
        initCurrentMapPage,
        initCurrentMultimapPage,
        runBtPreloadWarmup,
    };
    window.__btShared = {
        ...(window.__btShared || {}),
        ...shared,
    };
    if (!window.__btShared.__preloadWarmupStarted) {
        window.__btShared.__preloadWarmupStarted = true;
        runBtPreloadWarmup();
    }
})();
