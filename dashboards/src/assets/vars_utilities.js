// EXTERNAL:vars_utilities.js

function getReplaceVariables() {
    if (
        typeof context !== "undefined" &&
        context?.grafana?.replaceVariables &&
        typeof context.grafana.replaceVariables === "function"
    ) {
        return context.grafana.replaceVariables.bind(context.grafana);
    }
    return (value) => value;
}

const readVar = (name, fallback = "") => {
    const token = `\${${name}}`;
    const value = getReplaceVariables()(token);
    if (value === token || value === undefined || value === null || value === "") {
        return fallback;
    }
    return value;
};

function createBtPanelState(initialVars) {
    return {
        vars: initialVars || {},
        stretchRequestController: null,
    };
}

function getBtSharedRuntime() {
    if (!globalThis.__btSharedRuntime) {
        globalThis.__btSharedRuntime = {
            maplibreReady: null,
            syncMoveReady: null,
            config: {},
        };
    }
    return globalThis.__btSharedRuntime;
}

function applyBtPanelConfig(overrides) {
    if (!overrides || typeof overrides !== "object") {
        return getBtSharedRuntime().config;
    }
    const sharedRuntime = getBtSharedRuntime();
    sharedRuntime.config = {
        ...(sharedRuntime.config || {}),
        ...overrides,
    };
    return sharedRuntime.config;
}

function getBtConfig(key, fallback) {
    const sharedRuntime = getBtSharedRuntime();
    const config = sharedRuntime.config || {};
    if (Object.prototype.hasOwnProperty.call(config, key)) {
        return config[key];
    }
    return fallback;
}

function resolveMetricProduct(product, truth) {
    if (typeof product === "string" && product.includes("_")) {
        return product;
    }
    const normalizedProduct = (product || "precip").trim() || "precip";
    const normalizedTruth = (truth || "era5").trim() || "era5";
    return `${normalizedTruth}_${normalizedProduct}`;
}
