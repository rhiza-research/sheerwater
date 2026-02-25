// EXTERNAL:bt_after_ready_imports.js
const __btShared = window.__btShared;
if (!__btShared) {
    throw new Error(
        "Business Text shared preload API not found on window.__btShared. " +
        "Load the preload bundle in 'Before content rendering' before running the after-ready bundle."
    );
}
const {
    readVar,
    resolveMetricProduct,
    createBtPanelState,
    applyBtPanelConfig,
    initCurrentMapPage,
    initCurrentMultimapPage,
} = __btShared;
if (typeof readVar !== "function" || typeof createBtPanelState !== "function") {
    throw new Error(
        "Business Text preload bundle is present but missing required shared exports. " +
        "Rebuild and reload the preload bundle before running the after-ready bundle."
    );
}
