function getVar(name) {
    const v = variables?.[name];
    if (!v) return null;
    return v.current?.value ?? v.value ?? v.query ?? null;
}

function getField(fields, name) {
    const idx = fields.map(f => f.name).indexOf(name);
    return idx >= 0 ? fields[idx].values : [];
}

const FORECAST_COLORS = [
    '#2563eb', '#dc2626', '#16a34a', '#ca8a04', '#7c3aed', '#0891b2',
    '#db2777', '#4f46e5', '#65a30d', '#b45309', '#0f766e', '#ea580c',
];

// Stable, high-contrast colors by model family (clim always gray, ECMWF always blue).
const FORECAST_COLOR_BY_KEY = {
    ecmwf_ifs_er: '#1d4ed8',
    ecmwf_ifs_ens: '#3b82f6',
    ecmwf_ifs_er_debiased: '#60a5fa',
    ecmwf_aifs: '#0ea5e9',
    ecmwf_hres: '#0284c7',
    fuxi: '#ea580c',
    graphcast: '#c026d3',
    gencast: '#a21caf',
    salient: '#16a34a',
    gfs: '#ca8a04',
    cumulus_ai: '#0f766e',
    climatology_2015: '#57534e',
    climatology_trend_2015: '#78716c',
    climatology_era5_1985_2015: '#44403c',
    climatology_imerg_1998_2016: '#a8a29e',
};

function colorForForecast(forecast, fallbackIndex) {
    const key = String(forecast).toLowerCase();
    if (FORECAST_COLOR_BY_KEY[key]) return FORECAST_COLOR_BY_KEY[key];
    if (key.startsWith('climatology')) return '#57534e';
    if (key.startsWith('ecmwf')) return '#1d4ed8';
    return FORECAST_COLORS[fallbackIndex % FORECAST_COLORS.length];
}

const LEADS = [7, 14, 21, 28, 35, 42];

const renameDict = {
    'Ecmwf Ifs Er': 'ECMWF IFS ER',
    'Ecmwf Ifs Ens': 'ECMWF IFS ENS',
    'Ecmwf Ifs Er Debiased': 'ECMWF IFS ER Debiased',
    'Ecmwf Aifs': 'ECMWF AIFS',
    'Ecmwf Hres': 'ECMWF HRES',
    'Gfs': 'GFS',
    'Salient': 'AI-Enhanced NWP',
    'Fuxi': 'FuXi S2S',
    'Graphcast': 'GraphCast',
    'Gencast': 'GenCast',
    'Climatology 2015': 'Climatology 1985-2014',
    'Climatology Trend 2015': 'Climatology 1985-2014 w/Trend',
    'Climatology Era5 1985 2015': 'Climatology ERA5 1985-2014',
    'Climatology Imerg 1998 2016': 'Climatology IMERG 1998-2015',
    'Cumulus Ai': 'Cumulus AI v0.0.0',
};

function titleCase(str) {
    const name = String(str).replaceAll('_', ' ')
        .split(' ')
        .map(w => w[0].toUpperCase() + w.substring(1))
        .join(' ');
    return renameDict[name] || name;
}

function weekLabel(leadDay) {
    return `Week ${Math.round(Number(leadDay) / 7)}`;
}

function toPercent(v) {
    const n = Number(v);
    if (!Number.isFinite(n)) return null;
    return n <= 1.0000001 ? n * 100 : n;
}

function isFiniteNumber(v) {
    // Number(null) === 0 — treat null/empty/NaN strings as missing.
    if (v === null || v === undefined || v === '') return false;
    if (typeof v === 'string' && ['nan', 'null', 'undefined'].includes(v.toLowerCase())) {
        return false;
    }
    const n = Number(v);
    return Number.isFinite(n);
}

function formatList(raw, { empty = 'selected', max = 3 } = {}) {
    const vals = Array.isArray(raw) ? raw : (raw == null || raw === '' ? [] : [raw]);
    if (!vals.length) return empty;
    const names = vals.map(titleCase);
    if (names.length <= max) return names.join(', ');
    return `${names.slice(0, max).join(', ')} +${names.length - max} more`;
}

function axisId(i, axis) {
    return i === 0 ? axis : `${axis}${i + 1}`;
}

/** Trapezoidal ∫ good_cells dθ over [loPct, hiPct] (θ as percent 0–100). */
function integrateBand(xPct, y, loPct, hiPct) {
    if (!(hiPct > loPct)) return null;
    const pairs = xPct.map((x, i) => [Number(x), Number(y[i])])
        .filter(([x, yi]) => Number.isFinite(x) && Number.isFinite(yi))
        .sort((a, b) => a[0] - b[0]);
    if (pairs.length < 2) return null;

    let area = 0; // in good_cells · θ_fraction
    for (let i = 0; i < pairs.length - 1; i++) {
        const [x0, y0] = pairs[i];
        const [x1, y1] = pairs[i + 1];
        const left = Math.max(x0, loPct);
        const right = Math.min(x1, hiPct);
        if (!(right > left)) continue;
        const t0 = x1 === x0 ? 0 : (left - x0) / (x1 - x0);
        const t1 = x1 === x0 ? 1 : (right - x0) / (x1 - x0);
        const yl = y0 + t0 * (y1 - y0);
        const yr = y0 + t1 * (y1 - y0);
        // dθ_fraction = dθ_pct / 100
        area += 0.5 * (yl + yr) * ((right - left) / 100);
    }
    const width = (hiPct - loPct) / 100; // θ fraction
    return { area, width };
}

function formatExpectedCells(v) {
    if (v == null || !Number.isFinite(v)) return '—';
    return v.toFixed(1);
}

if (!data.series || data.series.length === 0) {
    return { data: [], layout: { title: { text: 'Good cells vs cell cutoff — no data' } } };
}

const series = data.series[0];
const thresh = getField(series.fields, 'cell_threshold');
const leads = getField(series.fields, 'lead_day');
const forecasts = getField(series.fields, 'forecast');
const goods = getField(series.fields, 'good_cells');
const pointsTotals = getField(series.fields, 'points_total');
const informativeCutoffField = getField(series.fields, 'informative_cutoff');
const actionableCutoffField = getField(series.fields, 'actionable_cutoff');

if (!thresh.length) {
    return { data: [], layout: { title: { text: 'Good cells vs cell cutoff — no data' } } };
}

// Drop forecasts with any missing/non-finite good_cells, empty cell sets, or
// incomplete lead coverage (those show up as flat/null lines on the subplots).
const nanForecasts = new Set();
const allForecasts = new Set();
for (let i = 0; i < goods.length; i++) {
    const forecast = String(forecasts[i]);
    allForecasts.add(forecast);
    const pts = pointsTotals.length ? pointsTotals[i] : null;
    if (!isFiniteNumber(goods[i])) {
        nanForecasts.add(forecast);
        continue;
    }
    if (pts != null && (!isFiniteNumber(pts) || Number(pts) <= 0)) {
        nanForecasts.add(forecast);
        continue;
    }
    // At 0% cutoff every valid cell counts; 0 good cells ⇒ no usable percent_good.
    const xp = toPercent(thresh[i]);
    if (xp != null && xp <= 0.0001 && Number(goods[i]) <= 0) {
        nanForecasts.add(forecast);
    }
}

const byKey = new Map();
for (let i = 0; i < thresh.length; i++) {
    const forecast = String(forecasts[i]);
    if (nanForecasts.has(forecast)) continue;
    if (!isFiniteNumber(goods[i])) continue;
    const xp = toPercent(thresh[i]);
    if (xp == null) continue;

    const lead = Number(leads[i]);
    const key = `${forecast}||${lead}`;
    if (!byKey.has(key)) {
        byKey.set(key, {
            forecast,
            lead,
            x: [],
            y: [],
            pointsTotal: pointsTotals.length && isFiniteNumber(pointsTotals[i])
                ? Number(pointsTotals[i])
                : null,
        });
    }
    const bucket = byKey.get(key);
    bucket.x.push(xp);
    bucket.y.push(Number(goods[i]));
    if (bucket.pointsTotal == null && pointsTotals.length && isFiniteNumber(pointsTotals[i])) {
        bucket.pointsTotal = Number(pointsTotals[i]);
    }
}

function resolveCutoffPct(fieldVals, varName, fallback) {
    const fromSql = fieldVals.length ? fieldVals[0] : null;
    const fromVar = getVar(varName);
    return toPercent(fromSql ?? fromVar ?? fallback);
}

let bandLo = resolveCutoffPct(informativeCutoffField, 'informative_cutoff', 0.50);
let mid = resolveCutoffPct(actionableCutoffField, 'actionable_cutoff', 0.75);
const bandHi = 100;
// Keep Informative start ≤ Actionable start ≤ 100%.
if (bandLo == null || !Number.isFinite(bandLo)) bandLo = 50;
if (mid == null || !Number.isFinite(mid)) mid = 75;
if (mid < bandLo) {
    const tmp = bandLo;
    bandLo = mid;
    mid = tmp;
}
bandLo = Math.min(Math.max(bandLo, 0), bandHi);
mid = Math.min(Math.max(mid, bandLo), bandHi);

function leadBandExpectedCells(leadBuckets, forecastFilter) {
    const buckets = forecastFilter
        ? leadBuckets.filter(b => b.forecast === String(forecastFilter))
        : leadBuckets;
    const infos = [];
    const acts = [];
    for (const b of buckets) {
        const info = integrateBand(b.x, b.y, bandLo, mid);
        const act = integrateBand(b.x, b.y, mid, bandHi);
        // Expected cells = ∫ good_cells dθ / band width.
        if (info && info.width > 0) infos.push(info.area / info.width);
        if (act && act.width > 0) acts.push(act.area / act.width);
    }
    const mean = arr => (arr.length
        ? arr.reduce((s, v) => s + v, 0) / arr.length
        : null);
    return {
        info: mean(infos),
        act: mean(acts),
        n: buckets.length,
        forecast: forecastFilter || null,
    };
}

const keysPresentForResolve = [...new Set([...byKey.values()].map(b => b.forecast))];

function resolveForecastKey(raw, knownKeys) {
    if (raw == null || raw === '') return null;
    const s = String(raw);
    if (knownKeys.includes(s)) return s;
    const lower = s.toLowerCase();
    for (const f of knownKeys) {
        if (titleCase(f).toLowerCase() === lower) return f;
        if (f.toLowerCase() === lower) return f;
    }
    // Fall back to raw key even if not currently plotted (SQL may still have it).
    return s;
}

function forecastVarCandidate(sqlFieldName, varName) {
    const fromSql = getField(series.fields, sqlFieldName);
    const raw = (fromSql.length ? fromSql[0] : null) ?? getVar(varName);
    return Array.isArray(raw) ? (raw[0] ?? null) : (raw || null);
}

const evalForecast = resolveForecastKey(
    forecastVarCandidate('eval_forecast', 'eval_forecast'),
    keysPresentForResolve
);

function selectedForecastKeys() {
    const raw = getVar('forecast_option');
    const vals = Array.isArray(raw) ? raw : (raw == null || raw === '' ? [] : [raw]);
    // Grafana "All" often arrives as a single "$__all" token — treat as unrestricted.
    if (vals.length === 1 && String(vals[0]) === '$__all') return null;
    if (!vals.length) return null;
    return new Set(vals.map(String));
}

const plotSelection = selectedForecastKeys();

function shouldPlotForecast(forecast) {
    if (evalForecast && forecast === String(evalForecast)) return true;
    // Unrestricted ("All"): plot everything returned by SQL, including baseline.
    if (plotSelection == null) return true;
    return plotSelection.has(forecast);
}

// Hide forecasts missing any of the six lead subplots (plotting only).
for (const forecast of allForecasts) {
    if (nanForecasts.has(forecast)) continue;
    const missingLead = LEADS.some(ld => !byKey.has(`${forecast}||${ld}`));
    if (missingLead) nanForecasts.add(forecast);
}
for (const key of [...byKey.keys()]) {
    if (nanForecasts.has(key.split('||')[0])) byKey.delete(key);
}

const uniqueForecasts = [...new Set(
    [...byKey.values()].map(b => b.forecast).filter(shouldPlotForecast)
)].sort();
const colorByForecast = new Map(
    uniqueForecasts.map((f, i) => [f, colorForForecast(f, i)])
);

const presentLeads = LEADS.filter(ld =>
    [...byKey.values()].some(b => b.lead === ld && shouldPlotForecast(b.forecast))
);
const subplotLeads = presentLeads.length ? presentLeads : LEADS;

const ncols = 2;
const nrows = 3;
const xPad = 0.05;
const yPadBottom = 0.08;
const yPadTop = 0.03;
const xGap = 0.03;
const yGap = 0.07;
const kpiGutter = 0.12; // space to the right of each plot for KPI boxes
const slotW = (1 - xPad * 2 - xGap * (ncols - 1)) / ncols;
const plotW = Math.max(0.28, slotW - kpiGutter);
const cellH = (1 - yPadTop - yPadBottom - yGap * (nrows - 1)) / nrows;

function domainFor(i) {
    const col = i % ncols;
    const rowFromTop = Math.floor(i / ncols);
    const rowFromBottom = nrows - 1 - rowFromTop;
    const slotX0 = xPad + col * (slotW + xGap);
    const y0 = yPadBottom + rowFromBottom * (cellH + yGap);
    return {
        x: [slotX0, slotX0 + plotW],
        y: [y0, y0 + cellH],
        kpiX: slotX0 + plotW + 0.012,
    };
}

const traces = [];
const shapes = [];
const annotations = [];
const layoutAxes = {};
const legendShown = new Set();

subplotLeads.forEach((lead, i) => {
    const xid = axisId(i, 'x');
    const yid = axisId(i, 'y');
    const domain = domainFor(i);

    layoutAxes[xid === 'x' ? 'xaxis' : `xaxis${i + 1}`] = {
        domain: domain.x,
        anchor: yid,
        type: 'linear',
        range: [0, 100],
        dtick: 50,
        ticksuffix: '%',
        gridcolor: 'rgba(0,0,0,0.08)',
        zeroline: false,
        autorange: false,
        title: i >= ncols * (nrows - 1)
            ? { text: 'Threshold (%)', font: { size: 11 } }
            : undefined,
        tickfont: { size: 10 },
    };
    layoutAxes[yid === 'y' ? 'yaxis' : `yaxis${i + 1}`] = {
        domain: domain.y,
        anchor: xid,
        type: 'linear',
        rangemode: 'tozero',
        gridcolor: 'rgba(0,0,0,0.08)',
        zeroline: false,
        title: (i % ncols === 0) ? { text: 'Good cells', font: { size: 11 } } : undefined,
        tickfont: { size: 10 },
    };

    const leadBuckets = [...byKey.values()]
        .filter(b => b.lead === lead && shouldPlotForecast(b.forecast))
        .sort((a, b) => a.forecast.localeCompare(b.forecast));
    const bandScores = leadBandExpectedCells(leadBuckets, evalForecast);
    const midX = (domain.x[0] + domain.x[1]) / 2;
    const midY = (domain.y[0] + domain.y[1]) / 2;
    const evalLabel = evalForecast ? titleCase(evalForecast) : 'selected';

    annotations.push({
        text: `<b>${weekLabel(lead)}</b> · D${lead}`,
        xref: 'paper',
        yref: 'paper',
        x: midX,
        y: domain.y[1] + 0.012,
        showarrow: false,
        xanchor: 'center',
        yanchor: 'bottom',
        font: { size: 12, color: '#27272a' },
    });

    // Final KPIs for Eval forecast, stacked beside the plot.
    annotations.push({
        text:
            `<span style="font-size:9px;letter-spacing:0.04em">INFORMATIVE</span><br>`
            + `<b style="font-size:18px">${formatExpectedCells(bandScores.info)}</b>`,
        xref: 'paper',
        yref: 'paper',
        x: domain.kpiX,
        y: midY + 0.045,
        showarrow: false,
        xanchor: 'left',
        yanchor: 'middle',
        align: 'center',
        bgcolor: 'rgba(240, 253, 250, 0.96)',
        bordercolor: '#0f766e',
        borderwidth: 2,
        borderpad: 7,
        font: {
            size: 12,
            family: '"IBM Plex Sans", "Segoe UI", system-ui, sans-serif',
            color: '#0f766e',
        },
    });
    annotations.push({
        text:
            `<span style="font-size:9px;letter-spacing:0.04em">ACTIONABLE</span><br>`
            + `<b style="font-size:18px">${formatExpectedCells(bandScores.act)}</b>`,
        xref: 'paper',
        yref: 'paper',
        x: domain.kpiX,
        y: midY - 0.01,
        showarrow: false,
        xanchor: 'left',
        yanchor: 'middle',
        align: 'center',
        bgcolor: 'rgba(247, 254, 231, 0.96)',
        bordercolor: '#4d7c0f',
        borderwidth: 2,
        borderpad: 7,
        font: {
            size: 12,
            family: '"IBM Plex Sans", "Segoe UI", system-ui, sans-serif',
            color: '#4d7c0f',
        },
    });
    annotations.push({
        text: evalLabel,
        xref: 'paper',
        yref: 'paper',
        x: domain.kpiX,
        y: midY - 0.065,
        showarrow: false,
        xanchor: 'left',
        yanchor: 'top',
        align: 'left',
        font: {
            size: 9,
            family: '"IBM Plex Sans", "Segoe UI", system-ui, sans-serif',
            color: '#57534e',
        },
    });

    // Band labels inside the shaded regions
    if (mid > bandLo + 2) {
        annotations.push({
            text: 'informative',
            xref: xid,
            yref: `${yid} domain`,
            x: (bandLo + mid) / 2,
            y: 0.96,
            showarrow: false,
            xanchor: 'center',
            yanchor: 'top',
            font: { size: 9, color: '#0f766e', family: '"IBM Plex Sans", "Segoe UI", system-ui, sans-serif' },
        });
    }
    if (bandHi > mid + 2) {
        annotations.push({
            text: 'actionable',
            xref: xid,
            yref: `${yid} domain`,
            x: (mid + bandHi) / 2,
            y: 0.96,
            showarrow: false,
            xanchor: 'center',
            yanchor: 'top',
            font: { size: 9, color: '#4d7c0f', family: '"IBM Plex Sans", "Segoe UI", system-ui, sans-serif' },
        });
    }

    shapes.push(
        {
            type: 'rect', xref: xid, yref: `${yid} domain`,
            x0: bandLo, x1: mid, y0: 0, y1: 1,
            fillcolor: 'rgba(20, 120, 120, 0.14)',
            line: { width: 0 },
            layer: 'below',
        },
        {
            type: 'rect', xref: xid, yref: `${yid} domain`,
            x0: mid, x1: bandHi, y0: 0, y1: 1,
            fillcolor: 'rgba(100, 110, 40, 0.14)',
            line: { width: 0 },
            layer: 'below',
        },
        {
            type: 'line', xref: xid, yref: `${yid} domain`,
            x0: bandLo, x1: bandLo, y0: 0, y1: 1,
            line: { color: '#0f766e', width: 1.1, dash: 'dot' },
            layer: 'above',
        },
        {
            type: 'line', xref: xid, yref: `${yid} domain`,
            x0: mid, x1: mid, y0: 0, y1: 1,
            line: { color: '#18181b', width: 1.2, dash: 'dash' },
            layer: 'above',
        }
    );

    leadBuckets.forEach(({ forecast, x, y }) => {
        const pairs = x.map((xi, j) => [xi, y[j]])
            .filter(([, yi]) => isFiniteNumber(yi))
            .sort((p, q) => p[0] - q[0]);
        if (!pairs.length) return;

        const isEval = evalForecast && forecast === String(evalForecast);
        const lineColor = colorByForecast.get(forecast) || '#52525b';
        const showInLegend = !legendShown.has(forecast);
        if (showInLegend) legendShown.add(forecast);

        traces.push({
            type: 'scatter',
            mode: 'lines',
            name: titleCase(forecast),
            legendgroup: forecast,
            showlegend: showInLegend,
            x: pairs.map(p => p[0]),
            y: pairs.map(p => p[1]),
            xaxis: xid,
            yaxis: yid,
            connectgaps: false,
            line: {
                color: lineColor,
                width: isEval ? 3.4 : 2.0,
                dash: 'solid',
            },
            hovertemplate:
                `${weekLabel(lead)} · %{fullData.name}` +
                '<br>threshold=%{x:.0f}%<br>good cells=%{y:.0f}<extra></extra>',
        });
    });
});

const regionTitle = formatList(getVar('region_option'), { empty: 'selected regions' });
const forecastTitle = formatList(
    uniqueForecasts.length ? uniqueForecasts : getVar('forecast_option'),
    { empty: 'selected forecasts' }
);
const droppedNote = nanForecasts.size
    ? ` · hidden ${nanForecasts.size} with NaN`
    : '';

return {
    data: traces,
    layout: {
        title: {
            text: `Good cells vs cell cutoff — ${regionTitle} · ${forecastTitle}${droppedNote}`,
            xanchor: 'left',
            x: 0,
            font: {
                size: 14,
                color: '#18181b',
                family: '"IBM Plex Sans", "Source Sans 3", "Segoe UI", system-ui, sans-serif',
                weight: 500,
            },
        },
        ...layoutAxes,
        shapes,
        annotations,
        legend: {
            orientation: 'h',
            y: -0.02,
            x: 0,
            font: { size: 11 },
            title: { text: 'Forecast', font: { size: 11 } },
        },
        margin: { t: 44, b: 56, l: 48, r: 8 },
        paper_bgcolor: '#F4F5F5',
        plot_bgcolor: '#F4F5F5',
        font: {
            family: '"IBM Plex Sans", "Source Sans 3", "Segoe UI", system-ui, sans-serif',
            color: '#27272a',
        },
        hovermode: 'closest',
    },
};
