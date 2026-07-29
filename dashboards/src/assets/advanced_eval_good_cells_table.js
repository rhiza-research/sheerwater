function getThresholdColor(ratio) {
    if (ratio == null || isNaN(ratio)) return 'rgba(255,255,255,0)';
    const t = Math.min(1, Math.max(0, ratio));
    const mid = 0.5;
    let r, g, b;
    if (t <= mid) {
        const s = t / mid;
        r = Math.round(220 + s * (255 - 220));
        g = Math.round(50  + s * (253 - 50));
        b = Math.round(50  + s * (220 - 50));
    } else {
        const s = (t - mid) / (1 - mid);
        r = Math.round(255 + s * (56  - 255));
        g = Math.round(253 + s * (168 - 253));
        b = Math.round(220 + s * (83  - 220));
    }
    return `rgba(${r}, ${g}, ${b}, 0.5)`;
}

const renameDict = {
    "Ecmwf Ifs Er": "ECMWF IFS ER",
    "Ecmwf Ifs Ens": "ECMWF IFS ENS",
    "Ecmwf Ifs Er Debiased": "ECMWF IFS ER Debiased",
    "Ecmwf Aifs": "ECMWF AIFS",
    "Ecmwf Hres": "ECMWF HRES",
    "Gfs": "GFS",
    "Salient": "AI-Enhanced NWP",
    "Fuxi": "FuXi S2S",
    "Climatology 2015": "Climatology 1985-2014",
    "Climatology Trend 2015": "Climatology 1985-2014 w/Trend",
    "Climatology Era5 1985 2015": "Climatology ERA5 1985-2014",
    "Climatology Imerg 1998 2016": "Climatology IMERG 1998-2015",
    "Cumulus Ai": "Cumulus AI v0.0.0",
};

function titleCase(str) {
    let name = str.replaceAll('_', ' ')
        .split(' ')
        .map(w => w[0].toUpperCase() + w.substring(1))
        .join(' ');
    return renameDict[name] || name;
}

function getVar(name) {
    const v = variables?.[name];
    if (!v) return null;
    return v.current?.value ?? v.value ?? v.query ?? null;
}

function getField(fields, name) {
    const idx = fields.map(f => f.name).indexOf(name);
    return idx >= 0 ? fields[idx].values : [];
}

const VIEW_CONFIG = {
    auc: {
        title: 'Expected Cells',
        mode: 'value',
        field: 'auc',
        higherIsBetter: true,
        filterNullForecasts: true,
        asPercent: false,
        decimals: 1,
        // Color heatmap as fraction of max cells (points_total).
        colorByFractionOfTotal: true,
    },
    auc_informative: {
        title: 'Expected Informative',
        mode: 'value',
        field: 'auc_informative',
        higherIsBetter: true,
        filterNullForecasts: true,
        asPercent: false,
        decimals: 1,
        colorByFractionOfTotal: true,
    },
    auc_actionable: {
        title: 'Expected Actionable',
        mode: 'value',
        field: 'auc_actionable',
        higherIsBetter: true,
        filterNullForecasts: true,
        asPercent: false,
        decimals: 1,
        colorByFractionOfTotal: true,
    },
};

function resolveTableView(series) {
    const aliases = {
        auc: 'auc',
        'Area Under Curve': 'auc',
        'Total AUC': 'auc',
        'AUC': 'auc',
        'Expected Cells': 'auc',
        'Expected cells': 'auc',
        auc_informative: 'auc_informative',
        'AUC Informative': 'auc_informative',
        'Area Under Curve Informative': 'auc_informative',
        'Expected Informative': 'auc_informative',
        auc_actionable: 'auc_actionable',
        'AUC Actionable': 'auc_actionable',
        'Area Under Curve Actionable': 'auc_actionable',
        'Expected Actionable': 'auc_actionable',
        // Legacy aliases from older View values
        good_enough_cells: 'auc',
        'Good Enough Cells': 'auc',
    };
    const fromSql = getField(series?.fields || [], 'table_view');
    const sqlVal = fromSql.length ? fromSql[0] : null;
    const raw = sqlVal || getVar('gc_view') || 'auc';
    return aliases[raw] || 'auc';
}

function metricActionableThreshold() {
    const m = String(getVar('metric') ?? '');
    const parts = m.split('-thresh-');
    if (parts.length < 2) return 1;
    const t = parseFloat(parts[parts.length - 1]);
    return (t != null && !isNaN(t) && t > 0) ? t : 1;
}

function skillScore(rawVal, tableView, actionableThresh) {
    if (rawVal == null || isNaN(rawVal)) return null;
    if (tableView === 'metric') {
        if (rawVal <= actionableThresh) return 1;
        return Math.max(0, 1 - (rawVal - actionableThresh) / (0.5 * actionableThresh));
    }
    return Math.min(1, Math.max(0, rawVal));
}

function isClimatology(forecast) {
    return String(forecast).toLowerCase().startsWith('climatology');
}

function pickClimatologyForecast(forecasts, truth) {
    const clims = forecasts.filter(isClimatology);
    if (!clims.length) return null;
    const t = String(truth || '').toLowerCase();
    if (t.includes('imerg')) {
        const hit = clims.find(f => f.toLowerCase().includes('imerg'));
        if (hit) return hit;
    }
    if (t.includes('era5') || t.includes('chirps')) {
        const hit = clims.find(f => f.toLowerCase().includes('era5'));
        if (hit) return hit;
    }
    const nonTrend = clims.find(f => !f.toLowerCase().includes('trend'));
    return nonTrend || clims[0];
}

function formatDelta(raw, climRaw, { asPercent = false } = {}) {
    if (raw == null || isNaN(raw) || climRaw == null || isNaN(climRaw)) return null;
    const d = raw - climRaw;
    const sign = d > 0 ? '+' : '';
    if (asPercent) {
        return `${sign}${(d * 100).toFixed(0)}%`;
    }
    return `${sign}${d.toFixed(2)}`;
}

function buildRegionTable(series, regionLabel, tableView, view, domain, mapLinks) {
    const fieldNames = series.fields.map(f => f.name);
    if (fieldNames.indexOf('forecast') < 0 || fieldNames.indexOf('lead_day') < 0) {
        return null;
    }

    const forecastField = series.fields[fieldNames.indexOf('forecast')].values;
    const leadDayField = series.fields[fieldNames.indexOf('lead_day')].values;
    const pointsField = getField(series.fields, 'points_above_threshold');
    const pointsTotalField = getField(series.fields, 'points_total');
    const eventCountField = getField(series.fields, 'event_count_mean');
    const aucRawField = getField(series.fields, 'auc_raw');
    const valueField = view.mode === 'value' ? getField(series.fields, view.field) : [];

    const dataMap = {};
    for (let i = 0; i < forecastField.length; i++) {
        const f = forecastField[i];
        const ld = leadDayField[i];
        if (!dataMap[f]) dataMap[f] = {};
        let raw = null;
        let display = '-';
        if (view.mode === 'points') {
            const num = pointsField[i];
            const denom = pointsTotalField[i];
            if (denom != null && denom !== 0) {
                raw = num / denom;
                display = `${num} / ${denom}`;
            }
        } else if (view.mode === 'auc_points') {
            // auc_raw = ∫ good_cells d(threshold) over [0,1] → mean # good cells;
            // max possible is points_total (all cells good at every threshold).
            const num = aucRawField[i];
            const denom = pointsTotalField[i];
            if (
                num != null && Number.isFinite(Number(num))
                && denom != null && denom !== 0 && Number.isFinite(Number(denom))
            ) {
                raw = Number(num) / Number(denom);
                display = `${Math.round(Number(num))} / ${denom}`;
            }
        } else {
            const v = valueField[i];
            if (v != null && !isNaN(v) && Number.isFinite(Number(v))) {
                raw = parseFloat(v);
                const decimals = view.decimals != null ? view.decimals : 2;
                display = view.asPercent
                    ? `${(raw * 100).toFixed(0)}%`
                    : raw.toFixed(decimals);
            }
        }
        const ec = eventCountField[i];
        const eventCount = (ec != null && !isNaN(ec)) ? Math.round(parseFloat(ec)) : null;
        const pt = pointsTotalField[i];
        const pointsTotal = (pt != null && !isNaN(pt) && Number(pt) > 0)
            ? Number(pt)
            : null;
        dataMap[f][ld] = { raw, display, eventCount, pointsTotal };
    }

    let uniqueForecasts = [...new Set(forecastField)];
    const uniqueLeadDays = [...new Set(leadDayField)].sort((a, b) => a - b);
    if (view.filterNullForecasts) {
        // Hide a forecast if any lead is missing or null (same rule as the curve).
        uniqueForecasts = uniqueForecasts.filter(f =>
            uniqueLeadDays.every(ld => {
                const d = dataMap[f]?.[ld];
                return d && d.raw != null && !isNaN(d.raw);
            })
        );
    }
    const actionableThresh = metricActionableThreshold();
    const truth = getVar('truth');
    const climForecast = pickClimatologyForecast(uniqueForecasts, truth);

    if (uniqueForecasts.length === 0) return { empty: true, uniqueLeadDays };

    const metric = getVar('metric');
    const grid = getVar('grid');
    const region = getVar('region');
    const time_grouping = getVar('time_grouping') || 'year';
    const time_filter = getVar('time_option');

    // Best forecast index per lead by raw value (skillScore saturates at the
    // actionable threshold, so it cannot break ties among "good enough" metrics).
    const bestIdxByLead = {};
    for (const ld of uniqueLeadDays) {
        let bestIdx = -1;
        let bestRaw = null;
        uniqueForecasts.forEach((f, idx) => {
            const raw = dataMap[f]?.[ld]?.raw;
            if (raw == null || isNaN(raw)) return;
            const better = bestRaw == null
                || (view.higherIsBetter ? raw > bestRaw : raw < bestRaw);
            if (better) {
                bestRaw = raw;
                bestIdx = idx;
            }
        });
        bestIdxByLead[ld] = bestIdx;
    }

    const header = [
        `Forecast · ${regionLabel}`,
        ...uniqueLeadDays.map(ld => `D${ld}`),
    ];
    const forecastNames = uniqueForecasts.map(f => {
        const name = titleCase(f);
        return (climForecast && f === climForecast) ? `${name} (baseline)` : name;
    });
    const values = [forecastNames];
    const ratios = [];
    const fontWeights = [uniqueForecasts.map(() => 'normal')];
    const fontColors = [uniqueForecasts.map(() => 'black')];

    for (const ld of uniqueLeadDays) {
        const col = [];
        const ratioCol = [];
        const weightCol = [];
        const colorCol = [];
        const climRaw = climForecast ? dataMap[climForecast]?.[ld]?.raw : null;

        uniqueForecasts.forEach((f, idx) => {
            const d = dataMap[f]?.[ld];
            const isBest = bestIdxByLead[ld] === idx;
            weightCol.push(isBest ? 'bold' : 'normal');
            colorCol.push(isBest ? '#0b3d1f' : 'black');

            if (!d || d.raw == null) {
                col.push('-');
                ratioCol.push(null);
                return;
            }

            let label = d.display;
            const secondary = [];
            // Delta on a second line so bare clim values stay neat when left-aligned
            if (climForecast && f !== climForecast) {
                const delta = formatDelta(d.raw, climRaw, {
                    asPercent: view.asPercent === true,
                });
                if (delta != null) secondary.push(delta);
            }
            if (d.eventCount != null) {
                secondary.push(`n=${d.eventCount}`);
            }
            if (secondary.length) {
                label = `${d.display}<br><span style="font-size:10px;opacity:0.72">${secondary.join(' · ')}</span>`;
            }

            if (isBest) {
                label = `★ ${label}`;
            }

            let cell = label;
            if (mapLinks) {
                const url = `d/ae39q2k3jv668d/plotly-maps?orgId=1` +
                    `&var-forecast=${f}` +
                    `&var-metric=${metric}` +
                    `&var-lead=lead_${ld}` +
                    `&var-truth=era5` +
                    `&var-grid=${grid}` +
                    `&var-region=${region}` +
                    `&var-time_grouping=${time_grouping}` +
                    `&var-time_filter=${time_filter}`;
                cell = `<a href="${url}">${label}</a>`;
            }
            col.push(cell);
            // Heatmap uses [0,1] skill; expected-cell views normalize by max cells.
            if (view.colorByFractionOfTotal && d.pointsTotal) {
                ratioCol.push(d.raw / d.pointsTotal);
            } else {
                ratioCol.push(d.raw);
            }
        });

        values.push(col);
        ratios.push(ratioCol);
        fontWeights.push(weightCol);
        fontColors.push(colorCol);
    }

    const forecast_colors = uniqueForecasts.map(() => 'rgba(0,0,0,0)');
    const skill_colors = ratios.map(ratioCol =>
        ratioCol.map(v => {
            const s = skillScore(v, tableView, actionableThresh);
            return s == null ? 'rgba(255,255,255,0)' : getThresholdColor(s);
        })
    );

    const dividerAt = Math.min(2, uniqueLeadDays.length);
    const headerWithDiv = [
        ...header.slice(0, dividerAt + 1),
        '',
        ...header.slice(dividerAt + 1)
    ];
    const valuesWithDiv = [
        ...values.slice(0, dividerAt + 1),
        Array(uniqueForecasts.length).fill(''),
        ...values.slice(dividerAt + 1)
    ];
    const colorsWithDiv = [
        forecast_colors,
        ...skill_colors.slice(0, dividerAt),
        Array(uniqueForecasts.length).fill('rgba(200,200,200,0.3)'),
        ...skill_colors.slice(dividerAt)
    ];
    const fontWeightWithDiv = [
        ...fontWeights.slice(0, dividerAt + 1),
        Array(uniqueForecasts.length).fill('normal'),
        ...fontWeights.slice(dividerAt + 1)
    ];
    const fontColorWithDiv = [
        ...fontColors.slice(0, dividerAt + 1),
        Array(uniqueForecasts.length).fill('black'),
        ...fontColors.slice(dividerAt + 1)
    ];
    const colWidth = [1.35, ...uniqueLeadDays.map(() => 0.48)];
    colWidth.splice(dividerAt + 1, 0, 0.03);

    // Left-align values so bare clim numbers line up with rows that include Δ
    const align = [
        'left',
        ...uniqueLeadDays.map(() => 'left'),
        'left',
    ];
    // After divider insert, keep left align with columns
    const alignWithDiv = [
        ...align.slice(0, dividerAt + 1),
        'center',
        ...align.slice(dividerAt + 1),
    ];
    const climNote = climForecast
        ? ` · Δ vs ${titleCase(climForecast)}`
        : '';

    const tableFont = '"IBM Plex Sans", "Source Sans 3", "Segoe UI", system-ui, sans-serif';

    return {
        empty: false,
        regionLabel,
        climNote,
        trace: {
            type: 'table',
            domain: domain,
            header: {
                values: headerWithDiv,
                align: alignWithDiv,
                line: { width: 0, color: 'rgba(0,0,0,0)' },
                font: {
                    family: tableFont,
                    size: 12,
                    weight: 600,
                    color: '#3f3f46',
                },
                fill: { color: ['rgba(244,245,245,1)'] },
                height: 30,
            },
            cells: {
                values: valuesWithDiv,
                align: alignWithDiv,
                line: { width: 0.5, color: 'rgba(219,221,222,0.85)' },
                font: {
                    family: tableFont,
                    size: 12,
                    color: fontColorWithDiv,
                    weight: fontWeightWithDiv,
                },
                fill: { color: colorsWithDiv },
                height: 30,
            },
            columnwidth: colWidth,
            name: regionLabel,
        }
    };
}

// ── Main ─────────────────────────────────────────────────────────────────────
function formatRegions(raw) {
    const vals = Array.isArray(raw) ? raw : (raw == null || raw === '' ? [] : [raw]);
    if (!vals.length) return 'selected regions';
    const names = vals.map(v => {
        const s = String(v).replaceAll('_', ' ');
        return s.charAt(0).toUpperCase() + s.slice(1);
    });
    if (names.length <= 3) return names.join(', ');
    return `${names.slice(0, 3).join(', ')} +${names.length - 3} more`;
}

if (!data.series || data.series.length === 0) return { data: [] };

const seriesA = data.series[0];
const tableView = resolveTableView(seriesA);
const view = VIEW_CONFIG[tableView] || VIEW_CONFIG.good_enough_cells;
const regionTitle = formatRegions(getVar('region_option'));

const builtA = buildRegionTable(
    seriesA, regionTitle, tableView, view,
    { x: [0, 1], y: [0, 1] },
    true
);

if (!builtA || builtA.empty) {
    return {
        data: [],
        layout: {
            title: { text: `${view.title} — no data`, xanchor: 'left', x: 0 },
            annotations: [{
                text: 'No data for this selection',
                xref: 'paper', yref: 'paper', x: 0.5, y: 0.5,
                showarrow: false,
                font: { size: 14, color: '#666' }
            }]
        }
    };
}

const climTitleNote = builtA.climNote || '';

return {
    data: [builtA.trace],
    layout: {
        title: {
            text: `${view.title} — ${regionTitle}${climTitleNote} · ★ = best in column`,
            xanchor: 'left',
            x: 0,
            font: {
                size: 14,
                color: '#18181b',
                family: '"IBM Plex Sans", "Source Sans 3", "Segoe UI", system-ui, sans-serif',
                weight: 500,
            }
        },
        margin: { t: 32, b: 6, l: 6, r: 6 },
        paper_bgcolor: '#F4F5F5',
        plot_bgcolor: '#F4F5F5',
        font: {
            family: '"IBM Plex Sans", "Source Sans 3", "Segoe UI", system-ui, sans-serif',
            color: '#27272a',
        },
    },
};
