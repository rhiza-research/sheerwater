// EXTERNAL:maplibre-map-builder.js
function buildStyleUrl(flavor) {
    return BASE_STYLE_URL_TEMPLATE.replace("{flavor}", flavor)
        .replace("{lang}", BASE_STYLE_LANG)
        .replace("{key}", PROTOMAPS_KEY);
}

async function fetchPreparedStyle(flavor) {
    const response = await fetch(buildStyleUrl(flavor));
    if (!response.ok) {
        throw new Error(`Style request failed (${response.status}).`);
    }
    const rawStyle = await response.json();
    return prepareStyle(rawStyle);
}

function prepareStyle(styleJson) {
    const allowedSourceLayers = new Set(ALLOWED_SOURCE_LAYERS);
    const filteredLayers = (styleJson.layers || [])
        .filter((layer) => {
            const sourceLayer = layer["source-layer"];
            if (!sourceLayer) {
                return true;
            }
            return (
                allowedSourceLayers.size === 0 ||
                allowedSourceLayers.has(sourceLayer)
            );
        })
        .map((layer) => {
            if (layer.type !== "fill" || layer["source-layer"] !== "water") {
                return layer;
            }
            return {
                ...layer,
                paint: {
                    ...(layer.paint || {}),
                    "fill-opacity": 0.8,
                },
            };
        });

    return {
        ...styleJson,
        layers: filteredLayers,
        sprite: `https://protomaps.github.io/basemaps-assets/sprites/v4/${DEFAULT_FLAVOR}`,
    };
}

function getGroupedManagedLayers(map) {
    if (!map || !map.getStyle) {
        return {};
    }
    const style = map.getStyle();
    const groups = {};
    const claimed = new Set();
    MANAGED_OVERLAY_GROUPS.forEach((group) => {
        groups[group.key] = [];
        (style.layers || []).forEach((layer) => {
            if (claimed.has(layer.id)) {
                return;
            }
            if (
                layer.type === group.type &&
                layer["source-layer"] === group.sourceLayer
            ) {
                groups[group.key].push(layer.id);
                claimed.add(layer.id);
            }
        });
    });
    return groups;
}

function getManagedLayerIds(map) {
    const grouped = getGroupedManagedLayers(map);
    return MANAGED_OVERLAY_GROUPS.flatMap((group) => grouped[group.key] || []);
}

function getAdminBoundaryLayerIds(map) {
    const grouped = getGroupedManagedLayers(map);
    return grouped.adminLines || [];
}

function getBoundaryLabelLayerIds(map) {
    const grouped = getGroupedManagedLayers(map);
    return [...(grouped.adminBoundaryLabels || []), ...(grouped.adminAreaLabels || [])];
}

function applyBoundaryLineContrast(map, layerId) {
    if (!map || !map.getLayer(layerId)) {
        return;
    }
    const style = map.getStyle();
    const layerDef = (style.layers || []).find((layer) => layer.id === layerId);
    if (!layerDef) {
        return;
    }
    const basePaint = layerDef.paint || {};
    const baseWidth = basePaint["line-width"] ?? 1;
    const casingLayerId = `${layerId}__contrast_casing`;
    if (map.getLayer(casingLayerId)) {
        map.removeLayer(casingLayerId);
    }

    const casingPaint = {
        ...basePaint,
        "line-color": BOUNDARY_CONTRAST.lineCasingColor,
        "line-opacity": BOUNDARY_CONTRAST.lineCasingOpacity,
        "line-width": ["+", baseWidth, BOUNDARY_CONTRAST.lineCasingExtraWidth],
    };

    try {
        map.addLayer(
            {
                ...layerDef,
                id: casingLayerId,
                paint: casingPaint,
            },
            layerId
        );
    } catch (error) {
        console.warn(`Failed to add contrast casing for ${layerId}:`, error);
    }

    map.setPaintProperty(layerId, "line-color", BOUNDARY_CONTRAST.lineStrokeColor);
    map.setPaintProperty(
        layerId,
        "line-opacity",
        BOUNDARY_CONTRAST.lineStrokeOpacity
    );
}

function applyBoundaryLabelContrast(map, layerId) {
    if (!map || !map.getLayer(layerId)) {
        return;
    }
    map.setPaintProperty(layerId, "text-color", BOUNDARY_CONTRAST.labelTextColor);
    map.setPaintProperty(
        layerId,
        "text-halo-color",
        BOUNDARY_CONTRAST.labelHaloColor
    );
    map.setPaintProperty(
        layerId,
        "text-halo-width",
        BOUNDARY_CONTRAST.labelHaloWidth
    );
    map.setPaintProperty(
        layerId,
        "text-halo-blur",
        BOUNDARY_CONTRAST.labelHaloBlur
    );
}

function applyBoundaryContrastOverrides(map) {
    getAdminBoundaryLayerIds(map).forEach((layerId) => {
        applyBoundaryLineContrast(map, layerId);
    });
    getBoundaryLabelLayerIds(map).forEach((layerId) => {
        applyBoundaryLabelContrast(map, layerId);
    });
}

function applyManagedOverlayLayerOrder(map) {
    getManagedLayerIds(map).forEach((layerId) => {
        if (!map.getLayer(layerId)) {
            return;
        }
        try {
            map.moveLayer(layerId);
        } catch (error) {
            console.warn(`Failed to move managed layer ${layerId}:`, error);
        }
    });
}

function getRasterInsertBeforeId(map) {
    return getManagedLayerIds(map).find((layerId) => map.getLayer(layerId)) || null;
}

function getRasterSlotId(slot) {
    return `${TERRACOTTA_LAYER_ID}-${slot}`;
}

function removeRasterSlot(map, slot) {
    const slotId = getRasterSlotId(slot);
    if (map.getLayer(slotId)) {
        map.removeLayer(slotId);
    }
    if (map.getSource(slotId)) {
        map.removeSource(slotId);
    }
}

function setRasterLayer(map, tileUrl, slot = 0, opacity = TERRACOTTA_OPACITY) {
    if (!map || !tileUrl) {
        return;
    }
    const slotId = getRasterSlotId(slot);
    removeRasterSlot(map, slot);

    map.addSource(slotId, {
        type: "raster",
        tiles: [tileUrl],
        tileSize: 256,
    });

    const layerDefinition = {
        id: slotId,
        type: "raster",
        source: slotId,
        paint: {
            "raster-opacity": opacity,
            "raster-fade-duration": 0,
        },
    };
    const beforeLayerId = getRasterInsertBeforeId(map);
    if (beforeLayerId) {
        map.addLayer(layerDefinition, beforeLayerId);
    } else {
        map.addLayer(layerDefinition);
    }
    applyManagedOverlayLayerOrder(map);
    return slotId;
}

function fadeRasterOpacity(map, layerId, fromOpacity, toOpacity, durationMs) {
    if (!map.getLayer(layerId)) {
        return Promise.resolve();
    }
    const clampOpacity = (value) => Math.max(0, Math.min(1, Number(value) || 0));
    const safeFromOpacity = clampOpacity(fromOpacity);
    const safeToOpacity = clampOpacity(toOpacity);
    if (durationMs <= 0 || fromOpacity === toOpacity) {
        map.setPaintProperty(layerId, "raster-opacity", safeToOpacity);
        return Promise.resolve();
    }
    const start = performance.now();
    return new Promise((resolve) => {
        const step = (now) => {
            if (!map.getLayer(layerId)) {
                resolve();
                return;
            }
            const t = Math.max(0, Math.min(1, (now - start) / durationMs));
            const current = safeFromOpacity + (safeToOpacity - safeFromOpacity) * t;
            map.setPaintProperty(layerId, "raster-opacity", clampOpacity(current));
            if (t >= 1) {
                resolve();
                return;
            }
            requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    });
}

async function swapRasterLayer(runtime, tileUrl) {
    const map = runtime?.map;
    if (!map || !tileUrl) {
        return;
    }
    const oldSlot = runtime.rasterSlot ?? 0;
    const nextSlot = oldSlot === 0 ? 1 : 0;
    const nextSlotId = setRasterLayer(map, tileUrl, nextSlot, 0);
    const oldSlotId = getRasterSlotId(oldSlot);
    const swapToken = (runtime.rasterSwapToken || 0) + 1;
    runtime.rasterSwapToken = swapToken;

    await new Promise((resolve) => {
        let settled = false;
        const finish = () => {
            if (settled) {
                return;
            }
            settled = true;
            map.off("sourcedata", onSourceData);
            resolve();
        };
        const onSourceData = (event) => {
            if (event.sourceId !== nextSlotId) {
                return;
            }
            if (map.isSourceLoaded(nextSlotId)) {
                finish();
            }
        };
        map.on("sourcedata", onSourceData);
        window.setTimeout(finish, RASTER_LOAD_TIMEOUT_MS);
    });

    if (runtime.rasterSwapToken !== swapToken) {
        return;
    }

    await Promise.all([
        fadeRasterOpacity(
            map,
            nextSlotId,
            0,
            TERRACOTTA_OPACITY,
            RASTER_CROSSFADE_MS
        ),
        fadeRasterOpacity(
            map,
            oldSlotId,
            TERRACOTTA_OPACITY,
            0,
            RASTER_CROSSFADE_MS
        ),
    ]);

    removeRasterSlot(map, oldSlot);
    runtime.rasterSlot = nextSlot;
}

function getMaplibreGlobal() {
    if (globalThis && globalThis.maplibregl) {
        return globalThis.maplibregl;
    }
    if (window.maplibregl) {
        return window.maplibregl;
    }
    if (window.parent && window.parent.maplibregl) {
        return window.parent.maplibregl;
    }
    if (window.top && window.top.maplibregl) {
        return window.top.maplibregl;
    }
    return null;
}

function waitForMaplibreGlobal(timeoutMs = 4000) {
    return new Promise((resolve, reject) => {
        if (getMaplibreGlobal()) {
            resolve();
            return;
        }
        const start = Date.now();
        const tick = () => {
            if (getMaplibreGlobal()) {
                resolve();
                return;
            }
            if (Date.now() - start > timeoutMs) {
                reject(new Error("maplibregl global not available"));
                return;
            }
            window.setTimeout(tick, 50);
        };
        tick();
    });
}

function loadMaplibre() {
    if (getMaplibreGlobal()) {
        return Promise.resolve();
    }
    if (maplibreReady) {
        return maplibreReady;
    }
    maplibreReady = new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = "https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js";
        script.crossOrigin = "anonymous";
        script.onload = () => {
            waitForMaplibreGlobal()
                .then(() => {
                    const global = getMaplibreGlobal();
                    if (global && !window.maplibregl) {
                        window.maplibregl = global;
                    }
                    resolve();
                })
                .catch(() => {
                    import("https://esm.sh/maplibre-gl@3.6.2")
                        .then((module) => {
                            window.maplibregl = module.default || module;
                            return waitForMaplibreGlobal();
                        })
                        .then(resolve)
                        .catch((error) => {
                            reject(
                                new Error(
                                    `Failed to load maplibre-gl (global + esm). ${error}`
                                )
                            );
                        });
                });
        };
        script.onerror = () => {
            import("https://esm.sh/maplibre-gl@3.6.2")
                .then((module) => {
                    window.maplibregl = module.default || module;
                    return waitForMaplibreGlobal();
                })
                .then(resolve)
                .catch((error) => {
                    reject(
                        new Error(
                            `Failed to load maplibre-gl.js and esm import. ${error}`
                        )
                    );
                });
        };
        document.head.appendChild(script);
    });
    return maplibreReady;
}

// ─── "No Data" overlay helpers ───────────────────────────────────────────────
function resolveNoDataOverlayHost(containerEl) {
    if (!containerEl) {
        return null;
    }

    if (typeof containerEl.closest === "function") {
        const multimapFrame = containerEl.closest(".bt-multimap-map");
        if (multimapFrame) {
            return multimapFrame;
        }

        const mapShell = containerEl.closest(".map-shell");
        if (mapShell) {
            return mapShell;
        }
    }

    return containerEl.parentElement || containerEl;
}

function createNoDataOverlayElement(extraClassName) {
    const overlay = document.createElement("div");
    overlay.className = ["no-data-overlay", extraClassName]
        .filter(Boolean)
        .join(" ");
    overlay.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span style="font-size:15px;font-weight:600;color:rgba(255,255,255,0.88);">No data available</span>
        <span style="font-size:12px;color:rgba(255,255,255,0.5);">This forecast/metric combination has no results</span>
      </div>
    `;
    return overlay;
}

function showNoDataOverlay(containerEl) {
    const host = resolveNoDataOverlayHost(containerEl);
    if (!host) return;

    let overlay = host.querySelector(".no-data-overlay");
    if (!overlay) {
        overlay = createNoDataOverlayElement();
        host.appendChild(overlay);
    }
    overlay.style.display = "flex";
}

function hideNoDataOverlay(containerEl) {
    const host = resolveNoDataOverlayHost(containerEl);
    if (!host) return;

    const overlay = host.querySelector(".no-data-overlay");
    if (overlay) overlay.style.display = "none";
}

// ─── Humanize lead labels (week1 → Week 1) ──────────────────────────────────
function humanizeLeadLabel(lead) {
    const m = String(lead || "").match(/^week(\d+)$/i);
    if (m) return `Week ${m[1]}`;
    return lead;
}

function injectContainerAndStyles() {
    const mapMountId = `${MAP_CONTAINER_ID}__mount`;
    const existing = getOrCreateHostContainer();
    if (existing.querySelector(`#${mapMountId}`)) {
        const existingMount = document.getElementById(mapMountId);
        return existingMount;
    }

    const style = document.createElement("style");
    style.textContent = `
    :root {
      --ink:#0c1f2e;
      --panel:#f5f3ef;
    }
    .map-shell {
      position:relative;
      width:100%;
      height:70vh;
      min-height:60vh;
      font-family:"IBM Plex Sans", "Segoe UI", sans-serif;
      border-radius:18px;
      overflow:hidden;
      box-shadow:0 16px 40px rgba(8, 16, 28, 0.25);
      border:1px solid rgba(12, 31, 46, 0.2);
      background:#0b1220;
    }
    .map-mount {
      position:absolute;
      inset:0;
      width:100%;
      height:100%;
    }
    .maplibregl-canvas {
      width:100% !important;
      height:100% !important;
    }
    /* ── Enlarged color scale ── */
    #map-colorscale {
      position:absolute;
      left:14px;
      bottom:14px;
      z-index:4;
      display:flex;
      align-items:center;
      justify-content:center;
      pointer-events:none;
      background:rgba(245, 243, 239, 0.96);
      color:var(--ink);
      padding:7px 14px;
      border-radius:10px;
      border:1px solid rgba(12, 31, 46, 0.18);
      font-size:14px;
      line-height:1.3;
      min-height:30px;
      white-space:nowrap;
      box-shadow:0 12px 24px rgba(8, 16, 28, 0.15);
    }
    /* ── No-data overlay ── */
    .no-data-overlay {
      position:absolute;
      inset:0;
      z-index:5;
      display:flex;
      align-items:center;
      justify-content:center;
      background:rgba(11,18,32,0.82);
      backdrop-filter:blur(2px);
      pointer-events:none;
      font-family:"IBM Plex Sans","Segoe UI",sans-serif;
    }
    /* ── Multimap: larger lead week labels ── */
    .bt-multimap-lead-label {
      font-size:16px !important;
      font-weight:600 !important;
      letter-spacing:0.01em;
    }
    /* ── Multimap: enlarged per-row color scales ── */
    .bt-multimap-row-scale,
    .bt-multimap-map-scale {
      font-size:14px !important;
      padding:6px 12px !important;
    }
    /* ── Metric description panel ── */
    #metric-description-panel {
      margin-bottom:10px;
    }
`;
    document.head.appendChild(style);

    const hostContainer = getOrCreateHostContainer();

    hostContainer.innerHTML = `
      <div id="metric-description-panel"></div>
      <div class="map-shell" id="map-shell-main">
        <div id="${mapMountId}" class="map-mount"></div>
        <div id="map-colorscale"></div>
      </div>
    `;

    const cssHref = "https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css";

    // Preload CSS so the browser starts fetching immediately
    if (!document.querySelector(`link[rel="preload"][href="${cssHref}"]`)) {
        const preload = document.createElement("link");
        preload.rel = "preload";
        preload.as = "style";
        preload.href = cssHref;
        document.head.appendChild(preload);
    }

    const css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = cssHref;
    document.head.appendChild(css);

    // Kick off MapLibre script load eagerly (non-blocking)
    loadMaplibre();
    return document.getElementById(mapMountId);
}

function createSingleMapInstance(container, baseStyle) {
    const mapContainer =
        container || document.getElementById(`${MAP_CONTAINER_ID}__mount`) || MAP_CONTAINER_ID;
    const fullscreenContainer =
        typeof mapContainer?.closest === "function"
            ? mapContainer.closest(".map-shell")
            : document.getElementById("map-shell-main");
    function forceCompactAttribution(mapInstance) {
        if (!mapInstance || !mapInstance.getContainer) return;
        const root = mapInstance.getContainer();
        const attributions = root.querySelectorAll(".maplibregl-ctrl-attrib");
        attributions.forEach((control) => {
            control.classList.add("maplibregl-compact");
            control.classList.remove("maplibregl-compact-show");
        });
    }
    const map = new window.maplibregl.Map({
        container: mapContainer,
        style: baseStyle,
        center: [0, 20],
        zoom: 1.2,
        attributionControl: false,
        cooperativeGestures: false,
    });

    map.addControl(
        new window.maplibregl.NavigationControl({ showCompass: false })
    );
    map.addControl(
        new window.maplibregl.FullscreenControl(
            fullscreenContainer ? { container: fullscreenContainer } : {}
        ),
        "top-right"
    );
    map.addControl(
        new window.maplibregl.AttributionControl({ compact: true })
    );
    map.on("load", () => forceCompactAttribution(map));
    window.setTimeout(() => forceCompactAttribution(map), 0);

    return map;
}
