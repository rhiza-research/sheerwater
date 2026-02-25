// EXTERNAL({"panel_id":"multimap-forecast-evaluation","key":"call-function"}):bfd145p7u3jlse-multimap-forecast-evaluation-call-function.js
(() => {
    function runCurrentMultimapPanel() {
        if (typeof PANEL_RUNTIME_CONFIG !== "undefined") {
            applyBtPanelConfig(PANEL_RUNTIME_CONFIG);
        }
        const panelDeps = {
            readVars,
            resolveRegion,
            getLeadWeeks,
            products: MULTIMAP_PRODUCTS,
        };
        const panelState = createBtPanelState(readVars());
        return initCurrentMultimapPage(panelState, panelDeps);
    }

    runCurrentMultimapPanel();
})();
