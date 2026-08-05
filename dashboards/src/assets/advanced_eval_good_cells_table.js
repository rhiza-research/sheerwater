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
        title: 'Cells @ Informative',
        mode: 'value',
        field: 'auc_informative',
        higherIsBetter: true,
        filterNullForecasts: true,
        asPercent: false,
        decimals: 1,
        colorByFractionOfTotal: true,
    },
    auc_actionable: {
        title: 'Cells @ Actionable',
        mode: 'value',
        field: 'auc_actionable',
        higherIsBetter: true,
        filterNullForecasts: true,
        asPercent: false,
        decimals: 1,
        colorByFractionOfTotal: true,
    },
    days_beyond_baseline: {
        title: 'Days Beyond Baseline',
        mode: 'days_beyond',
        higherIsBetter: true,
        filterNullForecasts: false,
        asPercent: false,
        decimals: 1,
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
        days_beyond_baseline: 'days_beyond_baseline',
        'Days Beyond Baseline': 'days_beyond_baseline',
        'Actionable days': 'days_beyond_baseline',
        'Informative days': 'days_beyond_baseline',
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

function formatDaysBeyond(v) {
    if (v == null || !Number.isFinite(v)) return '—';
    const sign = v > 0 ? '+' : '';
    return `${sign}${v.toFixed(1)}`;
}

function resolveBaselineForecast(knownForecasts, series) {
    const fromSql = getField(series?.fields || [], 'baseline_forecast');
    const raw = (fromSql.length ? fromSql[0] : null) ?? getVar('baseline_forecast');
    const candidate = Array.isArray(raw) ? (raw[0] ?? null) : (raw || null);
    if (candidate == null || candidate === '') {
        return pickClimatologyForecast(knownForecasts, getVar('truth'));
    }
    const s = String(candidate);
    if (knownForecasts.includes(s)) return s;
    const lower = s.toLowerCase();
    for (const f of knownForecasts) {
        if (titleCase(f).toLowerCase() === lower) return f;
        if (f.toLowerCase() === lower) return f;
    }
    return s;
}

/** Days beyond baseline at cutoff points, summarized over grid cells.
 *
 * For each cell, horizon = longest lead L ∈ {7,14,21,28} where percent_good
 * meets the Informative / Actionable cutoff (0 if never). Days beyond baseline
 * = horizon_F − horizon_B; the table reports the mean of that over cells.
 *
 * Layout: forecasts as columns; two rows = Informative / Actionable.
 */
function buildDaysBeyondTable(series, regionLabel, domain) {
    const fieldNames = series.fields.map(f => f.name);
    if (fieldNames.indexOf('forecast') < 0) {
        return null;
    }

    const forecastField = series.fields[fieldNames.indexOf('forecast')].values;
    const keys = ['act_min', 'act_avg', 'act_max', 'info_min', 'info_avg', 'info_max'];
    const fields = Object.fromEntries(keys.map(k => [k, getField(series.fields, k)]));
    const nCellsField = getField(series.fields, 'n_cells');

    function parseNullableNumber(raw) {
        // Important: Number(null) === 0 in JS, so treat null/undefined/'' as missing.
        if (raw == null || raw === '') return null;
        const v = Number(raw);
        return Number.isFinite(v) ? v : null;
    }

    const rowValues = {};
    const nCellsByForecast = {};
    for (let i = 0; i < forecastField.length; i++) {
        const f = forecastField[i];
        if (rowValues[f]) continue; // same summary on every lead row
        const row = {};
        for (const k of keys) {
            row[k] = fields[k].length ? parseNullableNumber(fields[k][i]) : null;
        }
        rowValues[f] = row;
        if (nCellsField.length) {
            const n = parseNullableNumber(nCellsField[i]);
            if (n != null) nCellsByForecast[f] = n;
        }
    }

    const allForecasts = [...new Set(forecastField)];
    const baselineForecast = resolveBaselineForecast(allForecasts, series);
    if (!baselineForecast) {
        return { empty: true, climNote: '', uniqueLeadDays: [] };
    }
    // Baseline is the reference: always 0 when present.
    rowValues[baselineForecast] = Object.fromEntries(keys.map(k => [k, 0]));

    let uniqueForecasts = [
        ...allForecasts.filter(f => f !== baselineForecast).sort(),
        ...allForecasts.filter(f => f === baselineForecast),
    ];
    if (!uniqueForecasts.length) {
        return { empty: true, climNote: '', uniqueLeadDays: [] };
    }

    // Prefer a non-baseline n_cells for the title note (comparable cells).
    let nCells = null;
    for (const f of uniqueForecasts) {
        if (f === baselineForecast) continue;
        if (nCellsByForecast[f] != null) {
            nCells = nCellsByForecast[f];
            break;
        }
    }
    if (nCells == null) nCells = nCellsByForecast[baselineForecast] ?? null;

    const metrics = [
        { key: 'info', label: 'Informative', prefix: 'info' },
        { key: 'act', label: 'Actionable', prefix: 'act' },
    ];

    function formatAvg(row, prefix, isBaseline) {
        if (isBaseline) return '0';
        // No overlapping cells / no usable percent_good ⇒ dash, not 0.
        const av = row?.[`${prefix}_avg`];
        if (av == null) return null;
        return formatDaysBeyond(av);
    }

    // Best forecast index per metric row (exclude baseline).
    const bestIdxByMetric = {};
    const maxAbsByMetric = {};
    for (const metric of metrics) {
        let bestIdx = -1;
        let bestRaw = null;
        let maxAbs = 0;
        uniqueForecasts.forEach((f, idx) => {
            if (f === baselineForecast) return;
            const raw = rowValues[f]?.[`${metric.prefix}_avg`];
            if (raw == null || !Number.isFinite(raw)) return;
            maxAbs = Math.max(maxAbs, Math.abs(raw));
            if (bestRaw == null || raw > bestRaw) {
                bestRaw = raw;
                bestIdx = idx;
            }
        });
        bestIdxByMetric[metric.key] = bestIdx;
        maxAbsByMetric[metric.key] = maxAbs;
    }

    /** Soft-wrap a label with <br> so Plotly table headers aren't clipped. */
    function wrapLabel(text, maxChars = 10) {
        const words = String(text).split(/\s+/).filter(Boolean);
        if (!words.length) return text;
        const lines = [];
        let line = '';
        for (const w of words) {
            const next = line ? `${line} ${w}` : w;
            if (line && next.length > maxChars) {
                lines.push(line);
                line = w;
            } else {
                line = next;
            }
        }
        if (line) lines.push(line);
        // Also break very long tokens (e.g. ECMWF…) mid-word as a last resort.
        return lines.map(ln => {
            if (ln.length <= maxChars + 4) return ln;
            const chunks = [];
            for (let i = 0; i < ln.length; i += maxChars) {
                chunks.push(ln.slice(i, i + maxChars));
            }
            return chunks.join('<br>');
        }).join('<br>');
    }

    const wrapWidth = uniqueForecasts.length >= 8 ? 8 : (uniqueForecasts.length >= 5 ? 10 : 12);
    const forecastNames = uniqueForecasts.map(f => {
        const name = wrapLabel(titleCase(f), wrapWidth);
        return f === baselineForecast
            ? `${name}<br><span style="font-size:10px;opacity:0.7">baseline</span>`
            : name;
    });

    // Plotly tables are column-oriented: values[c][r].
    const values = [metrics.map(m => m.label)];
    const fillColors = [metrics.map(() => 'rgba(0,0,0,0)')];
    const fontWeights = [metrics.map(() => '600')];
    const fontColors = [metrics.map(() => '#27272a')];

    uniqueForecasts.forEach((f, fIdx) => {
        const colVals = [];
        const ratioCol = [];
        const weightCol = [];
        const colorCol = [];
        const isBaseline = f === baselineForecast;
        for (const metric of metrics) {
            const row = rowValues[f];
            const avg = row?.[`${metric.prefix}_avg`];
            const isBest = !isBaseline && bestIdxByMetric[metric.key] === fIdx;
            const label = formatAvg(row, metric.prefix, isBaseline);

            if (label == null) {
                colVals.push('—');
                ratioCol.push(null);
                weightCol.push('normal');
                colorCol.push('black');
                continue;
            }

            colVals.push(isBest ? `★ ${label}` : label);
            weightCol.push(isBest ? 'bold' : 'normal');
            colorCol.push(isBest ? '#0b3d1f' : 'black');

            const maxAbs = maxAbsByMetric[metric.key];
            ratioCol.push(
                avg != null && Number.isFinite(avg) && maxAbs > 0
                    ? 0.5 + 0.5 * (avg / maxAbs)
                    : (isBaseline ? 0.5 : null)
            );
        }
        values.push(colVals);
        fillColors.push(ratioCol.map(v => (v == null ? 'rgba(255,255,255,0)' : getThresholdColor(v))));
        fontWeights.push(weightCol);
        fontColors.push(colorCol);
    });

    const header = [`${regionLabel}`, ...forecastNames];
    const align = ['left', ...uniqueForecasts.map(() => 'center')];
    const labelWidth = 1.3;
    const forecastWidth = Math.max(0.85, 3.2 / Math.max(uniqueForecasts.length, 1));
    const colWidth = [labelWidth, ...uniqueForecasts.map(() => forecastWidth)];
    const tableFont = '"IBM Plex Sans", "Source Sans 3", "Segoe UI", system-ui, sans-serif';
    const nNote = nCells != null ? ` · mean over ${Math.round(nCells)} cells` : ' · mean over cells';
    const climNote = ` · vs ${titleCase(baselineForecast)}${nNote}`;

    return {
        empty: false,
        regionLabel,
        climNote,
        daysBeyond: true,
        trace: {
            type: 'table',
            domain,
            header: {
                values: header,
                align,
                line: { width: 0, color: 'rgba(0,0,0,0)' },
                font: {
                    family: tableFont,
                    size: 11,
                    weight: 600,
                    color: '#3f3f46',
                },
                fill: { color: ['rgba(244,245,245,1)'] },
                height: 56,
            },
            cells: {
                values,
                align,
                line: { width: 0.5, color: 'rgba(219,221,222,0.85)' },
                font: {
                    family: tableFont,
                    size: 13,
                    color: fontColors,
                    weight: fontWeights,
                },
                fill: { color: fillColors },
                height: 36,
            },
            columnwidth: colWidth,
            name: regionLabel,
        },
    };
}


function buildRegionTable(series, regionLabel, tableView, view, domain, mapLinks) {
    if (view.mode === 'days_beyond') {
        return buildDaysBeyondTable(series, regionLabel, domain);
    }
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
    // Grafana "All": $__all, or custom allValue (quoted for SQL: '__all__').
    const allTokens = new Set(['$__all', '__all__', "'__all__'"]);
    if (vals.length === 1 && allTokens.has(String(vals[0]))) {
        return 'All regions';
    }
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
const bestNote = builtA.daysBeyond ? '★ = best in row' : '★ = best in column';

return {
    data: [builtA.trace],
    layout: {
        title: {
            text: `${view.title} — ${regionTitle}${climTitleNote} · ${bestNote}`,
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
