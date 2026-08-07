// EXTERNAL({"panel_id":"singlemap-evaluation","key":"call-function"}):dfd44cgdurwn4f-singlemap-evaluation-call-function.js
(() => {
    function runCurrentMapPanel() {
        if (typeof PANEL_RUNTIME_CONFIG !== "undefined") {
            applyBtPanelConfig(PANEL_RUNTIME_CONFIG);
        }
        const panelDeps = {
            readVars,
            resolveRegion,
        };
        const panelState = createBtPanelState(readVars());
        return initCurrentMapPage(panelState, panelDeps);
    }

    runCurrentMapPanel();
})();
