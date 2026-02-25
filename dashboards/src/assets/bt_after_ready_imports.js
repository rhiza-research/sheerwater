// EXTERNAL:bt_after_ready_imports.js
(() => {
    if (typeof btLogTiming === "function") {
        btLogTiming("after-ready imports start");
    }
    const shared = window.__btShared;
    if (!shared) {
        throw new Error(
            "Business Text shared preload API not found on window.__btShared. " +
            "Load the preload bundle in 'Before content rendering' before running the after-ready bundle."
        );
    }

    if (
        typeof shared.readVar !== "function" ||
        typeof shared.createBtPanelState !== "function"
    ) {
        throw new Error(
            "Business Text preload bundle is present but missing required shared exports. " +
            "Rebuild and reload the preload bundle before running the after-ready bundle."
        );
    }

    // Assign to global object properties (instead of top-level const declarations)
    // so the after-ready bundle can coexist with preload in the same page (local harness).
    globalThis.readVar = shared.readVar;
    globalThis.resolveMetricProduct = shared.resolveMetricProduct;
    globalThis.createBtPanelState = shared.createBtPanelState;
    globalThis.applyBtPanelConfig = shared.applyBtPanelConfig;
    globalThis.initCurrentMapPage = shared.initCurrentMapPage;
    globalThis.initCurrentMultimapPage = shared.initCurrentMultimapPage;
    if (typeof btLogTiming === "function") {
        btLogTiming("after-ready imports ready");
    }
})();
