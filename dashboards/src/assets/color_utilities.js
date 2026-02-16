// EXTERNAL:color_utilities.js
function getColorStops(colormap) {
    const palette = colormap.endsWith("_r") ? colormap.slice(0, -2) : colormap;
    const paletteStops = {
        brbg: [
            "#543005",
            "#8c510a",
            "#bf812d",
            "#dfc27d",
            "#f6e8c3",
            "#f5f5f5",
            "#c7eae5",
            "#80cdc1",
            "#35978f",
            "#01665e",
            "#003c30",
        ],
        rdbu: [
            "#67001f",
            "#b2182b",
            "#d6604d",
            "#f4a582",
            "#fddbc7",
            "#f7f7f7",
            "#d1e5f0",
            "#92c5de",
            "#4393c3",
            "#2166ac",
            "#053061",
        ],
        rdylgn: [
            "#a50026",
            "#d73027",
            "#f46d43",
            "#fdae61",
            "#fee08b",
            "#ffffbf",
            "#d9ef8b",
            "#a6d96a",
            "#66bd63",
            "#1a9850",
            "#006837",
        ],
        blues: [
            "#f7fbff",
            "#deebf7",
            "#c6dbef",
            "#9ecae1",
            "#6baed6",
            "#4292c6",
            "#2171b5",
            "#08519c",
            "#08306b",
        ],
        reds: [
            "#fff5f0",
            "#fee0d2",
            "#fcbba1",
            "#fc9272",
            "#fb6a4a",
            "#ef3b2c",
            "#cb181d",
            "#a50f15",
            "#67000d",
        ],
    };
    const stops = paletteStops[palette] || paletteStops.reds;
    return colormap.endsWith("_r") ? [...stops].reverse() : stops;
}

function renderColorScaleHtml(stretch, product, metric) {
    if (!stretch) {
        return "<span style='font-size:14px;'>No stretch</span>";
    }
    const decoded = decodeURIComponent(stretch);
    const colormapMatch = decoded.match(/colormap=([^&]+)/);
    const rangeMatch = decoded.match(/stretch_range=\[([^\]]+)\]/);
    const colormap = colormapMatch ? colormapMatch[1] : "";
    const units = getUnits(metric, product);
    const unitsSuffix = units ? ` ${units}` : "";
    let min = "min";
    let max = "max";
    if (rangeMatch) {
        const parts = rangeMatch[1].split(",").map((value) => Number(value.trim()));
        if (parts.length >= 2) {
            min = parts[0].toFixed(1);
            max = parts[1].toFixed(1);
        }
    }
    const stops = getColorStops(colormap);
    const gradient = `linear-gradient(90deg, ${stops.join(", ")})`;
    return `
      <div style="display:flex; align-items:center; height:100%; gap:8px; font-variant-numeric:tabular-nums; font-size:14px;">
        <span>${min}${unitsSuffix}</span>
        <div style="width:120px; height:12px; border-radius:999px; background:${gradient};"></div>
        <span>${max}${unitsSuffix}</span>
      </div>
    `;
}

function refreshColorScale(stretch, product, metric) {
    const scale = document.getElementById("map-colorscale");
    if (!scale) {
        return;
    }
    scale.innerHTML = renderColorScaleHtml(stretch, product, metric);
}

// ─── Refresh metric description panel ────────────────────────────────────────
function refreshMetricDescription(metric) {
    const panel = document.getElementById("metric-description-panel");
    if (!panel) return;
    panel.innerHTML = renderMetricDescriptionHtml(metric);
}
