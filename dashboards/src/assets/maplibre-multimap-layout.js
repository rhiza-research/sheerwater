// EXTERNAL:maplibre-multimap-layout.js
function ensureMultimapStyles() {
    if (document.getElementById("bt-multimap-styles")) {
        return;
    }
    const style = document.createElement("style");
    style.id = "bt-multimap-styles";
    style.textContent = `
      .bt-multimap-root {
        display:grid;
        gap:18px;
        width:100%;
        font-family:"IBM Plex Sans", "Segoe UI", sans-serif;
      }
      #metric-description-panel {
        margin-bottom:10px;
      }
      .bt-multimap-row {
        display:grid;
        gap:10px;
      }
      .bt-multimap-row-header {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:12px;
      }
      .bt-multimap-row-title {
        color:#0c1f2e;
        font-size:16px;
        font-family:"IBM Plex Sans", "Segoe UI", sans-serif;
        font-weight:400;
        line-height:1.2;
      }
      .bt-multimap-row-scale {
        background:rgba(245, 243, 239, 0.75);
        color:#0c1f2e;
        padding:4px 8px;
        border-radius:999px;
        border:1px solid rgba(12, 31, 46, 0.18);
        font-size:11px;
        line-height:1;
        min-height:24px;
        display:flex;
        align-items:center;
        justify-content:center;
        white-space:nowrap;
      }
      .bt-multimap-map-scale {
        position:absolute;
        left:10px;
        bottom:10px;
        z-index:4;
        display:none;
        pointer-events:none;
        background:rgba(245, 243, 239, 0.96);
        color:#0c1f2e;
        padding:4px 8px;
        border-radius:10px;
        border:1px solid rgba(12, 31, 46, 0.18);
        font-size:11px;
        line-height:1.2;
        min-height:22px;
        align-items:center;
        justify-content:center;
        white-space:nowrap;
      }
      .bt-multimap-map:fullscreen .bt-multimap-map-scale,
      .bt-multimap-map:-webkit-full-screen .bt-multimap-map-scale {
        display:flex;
      }
      @media (max-width: 720px) {
        .bt-multimap-row-header {
          flex-wrap:wrap;
          row-gap:8px;
        }
      }
      .bt-multimap-grid {
        display:grid;
        gap:12px;
        grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));
      }
      .bt-multimap-cell {
        display:grid;
        gap:6px;
      }
      .bt-multimap-cell-title {
        font-size:12px;
        color:#0c1f2e;
        font-weight:600;
      }
      .bt-multimap-map {
        position:relative;
        width:100%;
        height:280px;
        border-radius:12px;
        overflow:hidden;
        box-shadow:0 10px 28px rgba(8, 16, 28, 0.2);
        border:1px solid rgba(12, 31, 46, 0.2);
        background:#0b1220;
      }
      .no-data-overlay {
        position:absolute;
        inset:0;
        z-index:5;
        display:flex;
        align-items:center;
        justify-content:center;
        background:rgba(11, 18, 32, 0.82);
        backdrop-filter:blur(2px);
        pointer-events:none;
        font-family:"IBM Plex Sans", "Segoe UI", sans-serif;
      }
      .bt-multimap-row-no-data {
        position:relative;
        inset:auto;
        min-height:180px;
        border-radius:12px;
        border:1px solid rgba(12, 31, 46, 0.2);
      }
      .maplibregl-canvas {
        width:100% !important;
        height:100% !important;
      }
      @media (max-width: 900px) {
        .bt-multimap-map {
          height:240px;
        }
      }
    `;
    document.head.appendChild(style);

    const css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = "https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css";
    document.head.appendChild(css);
}

function buildMultimapLayout(leadWeeks) {
    ensureMultimapStyles();
    const host = getOrCreateHostContainer();
    let metricPanel = document.getElementById("metric-description-panel");
    if (!metricPanel) {
        metricPanel = document.createElement("div");
        metricPanel.id = "metric-description-panel";
        host.appendChild(metricPanel);
    }

    const rootId = "bt-multimap-root";
    const existing = document.getElementById(rootId);
    if (existing) {
        if (metricPanel.nextElementSibling !== existing) {
            host.insertBefore(metricPanel, existing);
        }
        return existing;
    }

    const root = document.createElement("div");
    root.id = rootId;
    root.className = "bt-multimap-root";

    MULTIMAP_PRODUCTS.forEach((product) => {
        const row = document.createElement("div");
        row.className = "bt-multimap-row";
        row.id = `bt-multimap-row-${product.key}`;

        const header = document.createElement("div");
        header.className = "bt-multimap-row-header";

        const rowTitle = document.createElement("div");
        rowTitle.className = "bt-multimap-row-title";
        rowTitle.textContent = product.label;
        header.appendChild(rowTitle);

        const rowScale = document.createElement("div");
        rowScale.className = "bt-multimap-row-scale";
        rowScale.id = `bt-multimap-row-scale-${product.key}`;
        rowScale.innerHTML = "Loading...";
        header.appendChild(rowScale);

        row.appendChild(header);

        const grid = document.createElement("div");
        grid.className = "bt-multimap-grid";

        leadWeeks.forEach((week) => {
            const cell = document.createElement("div");
            cell.className = "bt-multimap-cell";

            const title = document.createElement("div");
            title.className = "bt-multimap-cell-title";
            title.textContent = `Week ${week}`;
            cell.appendChild(title);

            const mapContainer = document.createElement("div");
            mapContainer.className = "bt-multimap-map";
            mapContainer.id = `bt-multimap-${product.key}-week${week}`;

            const scale = document.createElement("div");
            scale.className = "bt-multimap-map-scale";
            scale.id = `bt-multimap-scale-${product.key}-week${week}`;
            scale.dataset.productKey = product.key;
            scale.innerHTML = "Loading...";
            mapContainer.appendChild(scale);

            cell.appendChild(mapContainer);

            grid.appendChild(cell);
        });

        row.appendChild(grid);
        root.appendChild(row);
    });

    host.appendChild(root);
    if (metricPanel.nextElementSibling !== root) {
        host.insertBefore(metricPanel, root);
    }
    return root;
}

function getCellDefinitions(leadWeeks) {
    const cells = [];
    MULTIMAP_PRODUCTS.forEach((product) => {
        leadWeeks.forEach((week) => {
            cells.push({
                key: `${product.key}-week${week}`,
                productKey: product.key,
                productValue: product.product,
                week,
                containerId: `bt-multimap-${product.key}-week${week}`,
            });
        });
    });
    return cells;
}
