local threshold_curve_sql = importstr './assets/advanced_eval_threshold_curve_multi.sql';
local threshold_curve_js = importstr './assets/advanced_eval_threshold_curve.js';
local good_cells_sql = importstr './assets/advanced_eval_good_cells_multi.sql';
local good_cells_table_js = importstr './assets/advanced_eval_good_cells_table.js';

local plotlyTarget(refId, rawSql) = {
  datasource: { type: 'grafana-postgresql-datasource', uid: 'bdz3m3xs99p1cf' },
  editorMode: 'code',
  format: 'table',
  rawQuery: true,
  rawSql: rawSql,
  refId: refId,
  sql: {
    columns: [{ parameters: [], type: 'function' }],
    groupBy: [{ property: { type: 'string' }, type: 'groupBy' }],
    limit: 50,
  },
};

local regionQuery = |||
  SELECT DISTINCT initcap(replace("$region", '_', ' ')) AS __text, "$region" AS __value
  FROM "${unimodal_metric_name}" WHERE lead_day IN (7, 14, 21, 28, 35, 42)
  UNION
  SELECT DISTINCT initcap(replace("$region", '_', ' ')) AS __text, "$region" AS __value
  FROM "${unimodal_shifted_metric_name}" WHERE lead_day IN (7, 14, 21, 28, 35, 42)
  UNION
  SELECT DISTINCT initcap(replace("$region", '_', ' ')) AS __text, "$region" AS __value
  FROM "${bimodal_metric_name}" WHERE lead_day IN (7, 14, 21, 28, 35, 42)
|||;

local forecastLabelExpr = |||
  CASE forecast
    WHEN 'ecmwf_ifs_er' THEN 'ECMWF IFS ER'
    WHEN 'ecmwf_ifs_ens' THEN 'ECMWF IFS ENS'
    WHEN 'ecmwf_ifs_er_debiased' THEN 'ECMWF IFS ER Debiased'
    WHEN 'ecmwf_aifs' THEN 'ECMWF AIFS'
    WHEN 'ecmwf_hres' THEN 'ECMWF HRES'
    WHEN 'gfs' THEN 'GFS'
    WHEN 'salient' THEN 'AI-Enhanced NWP'
    WHEN 'fuxi' THEN 'FuXi S2S'
    WHEN 'graphcast' THEN 'GraphCast'
    WHEN 'gencast' THEN 'GenCast'
    WHEN 'climatology_2015' THEN 'Climatology 1985-2014'
    WHEN 'climatology_trend_2015' THEN 'Climatology 1985-2014 w/Trend'
    WHEN 'climatology_era5_1985_2015' THEN 'Climatology ERA5 1985-2014'
    WHEN 'climatology_imerg_1998_2016' THEN 'Climatology IMERG 1998-2015'
    WHEN 'cumulus_ai' THEN 'Cumulus AI v0.0.0'
    ELSE initcap(replace(forecast, '_', ' '))
  END
|||;

local forecastSelect = 'SELECT DISTINCT ' + forecastLabelExpr + ' AS __text, forecast AS __value';

local forecastQuery =
  forecastSelect + '\nFROM "${unimodal_metric_name}" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\n'
  + forecastSelect + '\nFROM "${unimodal_shifted_metric_name}" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nUNION\n'
  + forecastSelect + '\nFROM "${bimodal_metric_name}" WHERE lead_day IN (7, 14, 21, 28, 35, 42)\nORDER BY 1';


local yearsQuery = |||
  SELECT DISTINCT
      initcap(replace(COALESCE(time_grouping, 'None'), '_', ' ')) AS __text,
      COALESCE(time_grouping, 'None') AS __value
  FROM "${unimodal_metric_name}"
  WHERE lead_day IN (7, 14, 21, 28, 35, 42)
|||;

local table_panel = {
  datasource: {
    default: true,
    type: 'grafana-postgresql-datasource',
    uid: 'bdz3m3xs99p1cf',
  },
  fieldConfig: { defaults: {}, overrides: [] },
  gridPos: { h: 9, w: 24, x: 0, y: 0 },
  id: 1,
  options: {
    allData: {},
    config: {},
    data: [],
    imgFormat: 'png',
    layout: {
      font: { family: 'Inter, sans-serif' },
      margin: { b: 4, l: 0, r: 0, t: 0 },
      paper_bgcolor: '#F4F5F5',
      plot_bgcolor: '#F4F5F5',
      title: {
        align: 'left',
        automargin: true,
        font: { color: 'black', family: 'Inter, sans-serif', size: 14, weight: 500 },
        text: 'Good Enough Cells',
        x: 0,
        xanchor: 'left',
      },
      xaxis: { automargin: true, autorange: true },
      yaxis: { automargin: true, autorange: true },
    },
    onclick: '',
    resScale: 2,
    script: good_cells_table_js,
    syncTimeRange: false,
    timeCol: '',
  },
  pluginVersion: '1.8.2',
  targets: [plotlyTarget('A', good_cells_sql)],
  title: '',
  transparent: true,
  type: 'nline-plotlyjs-panel',
};

local threshold_curve_panel = {
  datasource: {
    default: true,
    type: 'grafana-postgresql-datasource',
    uid: 'bdz3m3xs99p1cf',
  },
  fieldConfig: { defaults: {}, overrides: [] },
  gridPos: { h: 28, w: 24, x: 0, y: 9 },
  id: 2,
  options: {
    allData: {},
    config: {},
    data: [],
    imgFormat: 'png',
    layout: {
      font: { family: 'Inter, sans-serif' },
      margin: { b: 40, l: 50, r: 20, t: 40 },
      paper_bgcolor: '#F4F5F5',
      plot_bgcolor: '#F4F5F5',
      title: {
        align: 'left',
        automargin: true,
        font: { color: 'black', family: 'Inter, sans-serif', size: 14, weight: 500 },
        text: 'Good cells vs cell cutoff',
        x: 0,
        xanchor: 'left',
      },
      xaxis: { type: 'linear', automargin: true, autorange: false, range: [0, 100] },
      yaxis: { type: 'linear', automargin: true, autorange: true },
    },
    onclick: '',
    resScale: 2,
    script: threshold_curve_js,
    syncTimeRange: false,
    timeCol: '',
  },
  pluginVersion: '1.8.2',
  targets: [plotlyTarget('A', threshold_curve_sql)],
  title: '',
  transparent: true,
  type: 'nline-plotlyjs-panel',
};

{
  annotations: {
    list: [
      {
        builtIn: 1,
        datasource: { type: 'grafana', uid: '-- Grafana --' },
        enable: true,
        hide: true,
        iconColor: 'rgba(0, 211, 255, 1)',
        name: 'Annotations & Alerts',
        type: 'dashboard',
      },
    ],
  },
  description: 'Good Enough Cells table and threshold curve, summed over a multiselect of regions.',
  editable: true,
  fiscalYearStartMonth: 0,
  graphTooltip: 0,
  links: [
    {
      asDropdown: false,
      icon: 'dashboard',
      includeVars: true,
      keepTime: true,
      tags: [],
      targetBlank: false,
      title: 'Advanced Forecast Evaluation Tables',
      tooltip: '',
      type: 'link',
      // Force Average Metric on arrival; includeVars won't override this name from gc_view.
      url: '/d/cfoumv7uu5xq8f/advanced-forecast-evaluation-tables?var-table_view=metric',
    },
  ],
  panels: [table_panel, threshold_curve_panel],
  preload: false,
  refresh: '',
  schemaVersion: 40,
  tags: ['advanced', 'evaluation'],
  templating: {
    list: [
      {
        description: 'Advanced event metric. percent_good is computed against the -thresh- actionable bar in the metric name.',
        current: {
          text: 'In season dry spells',
          value: 'in_season_dry_spell-thresh-20',
        },
        includeAll: false,
        label: 'Metric',
        name: 'metric',
        options: [
          { selected: false, text: 'Early season accumulation', value: 'early_season_accumulation-30d-thresh-30' },
          { selected: false, text: 'Large rain days', value: 'big_rain_days-thresh-0.30' },
          { selected: false, text: '90th percentile rain', value: 'extreme_rain_days-thresh-0.30' },
          { selected: true, text: 'In season dry spells', value: 'in_season_dry_spell-thresh-20' },
        ],
        query: 'Early season accumulation : early_season_accumulation-30d-thresh-30, Large rain days : big_rain_days-thresh-0.30, 90th percentile rain : extreme_rain_days-thresh-0.30, In season dry spells : in_season_dry_spell-thresh-20',
        type: 'custom',
      },
      {
        description: 'SQL column name for the selected metric (metric name with the -thresh-… suffix removed).',
        current: { text: 'in_season_dry_spell', value: 'in_season_dry_spell' },
        definition: "SELECT split_part('${metric}', '-thresh-', 1)",
        hide: 2,
        name: 'metric_column',
        options: [],
        query: "SELECT split_part('${metric}', '-thresh-', 1)",
        refresh: 1,
        regex: '',
        type: 'query',
      },
      {
        description: 'Expected cells: average good_cells when sweeping cutoff uniformly over the band. Total: [0,1]. Informative: teal band. Actionable: green band.',
        current: {
          text: 'Expected Cells',
          value: 'auc',
        },
        includeAll: false,
        label: 'View',
        // Distinct from advanced tables' table_view so includeVars click-through
        // does not overwrite the destination default.
        name: 'gc_view',
        options: [
          { selected: true, text: 'Expected Cells', value: 'auc' },
          { selected: false, text: 'Expected Informative', value: 'auc_informative' },
          { selected: false, text: 'Expected Actionable', value: 'auc_actionable' },
        ],
        query: 'Expected Cells : auc, Expected Informative : auc_informative, Expected Actionable : auc_actionable',
        type: 'custom',
      },
      {
        description: 'How rows are grouped in time in the underlying tables (currently year).',
        current: { text: 'year', value: 'year' },
        hide: 2,
        includeAll: false,
        label: 'Time Grouping',
        name: 'time_grouping',
        options: [{ selected: true, text: 'Year', value: 'year' }],
        query: 'Year : year',
        type: 'custom',
      },
      {
        description: 'Which years (or other time groups) to include when averaging cell scores.',
        current: {
          text: ['Y2016', 'Y2017', 'Y2018', 'Y2019', 'Y2020', 'Y2021', 'Y2022', 'Y2023', 'Y2024'],
          value: ['Y2016', 'Y2017', 'Y2018', 'Y2019', 'Y2020', 'Y2021', 'Y2022', 'Y2023', 'Y2024'],
        },
        definition: yearsQuery,
        label: 'Years',
        multi: true,
        name: 'time_option',
        options: [],
        query: yearsQuery,
        refresh: 1,
        regex: '',
        type: 'query',
      },
      {
        description: 'Observational rainfall product used as ground truth when the metric tables were built.',
        current: { text: 'IMERG', value: 'imerg_final' },
        includeAll: false,
        label: 'Truth',
        name: 'truth',
        options: [
          { selected: false, text: 'ERA5', value: 'era5' },
          { selected: true, text: 'IMERG', value: 'imerg_final' },
          { selected: false, text: 'CHIRPS V3', value: 'chirps_v3' },
        ],
        query: 'ERA5 : era5, IMERG : imerg_final, CHIRPS V3 : chirps_v3',
        type: 'custom',
      },
      {
        description: 'Deterministic vs probabilistic forecast tables.',
        current: { text: 'Deterministic', value: 'deterministic' },
        includeAll: false,
        label: 'Prob',
        name: 'prob_type',
        options: [
          { selected: true, text: 'Deterministic', value: 'deterministic' },
          { selected: false, text: 'Probabilistic', value: 'probabilistic' },
        ],
        query: 'Deterministic : deterministic, Probabilistic : probabilistic',
        type: 'custom',
      },
      {
        description: 'Internal: cache-key suffix for probabilistic metric tables.',
        current: { text: '', value: '' },
        datasource: { type: 'grafana-postgresql-datasource', uid: 'bdz3m3xs99p1cf' },
        definition: "SELECT CASE WHEN '${prob_type}' = 'probabilistic' THEN '_prob_type-probabilistic' ELSE '' END",
        hide: 2,
        includeAll: false,
        name: 'prob_type_suffix',
        options: [],
        query: "SELECT CASE WHEN '${prob_type}' = 'probabilistic' THEN '_prob_type-probabilistic' ELSE '' END",
        refresh: 2,
        regex: '',
        type: 'query',
      },
      {
        description: 'Spatial grid resolution of the metric tables (1.5° or 0.25°).',
        current: { text: '1.5', value: 'global1_5' },
        includeAll: false,
        label: 'Grid',
        name: 'grid',
        options: [
          { selected: true, text: '1.5', value: 'global1_5' },
          { selected: false, text: '0.25', value: 'global0_25' },
        ],
        query: '1.5 : global1_5, 0.25 : global0_25',
        type: 'custom',
      },
      {
        description: 'Region typology used for the region multiselect (country, rainfall region, etc.).',
        current: { text: 'Countries', value: 'country' },
        includeAll: false,
        label: 'Region type',
        name: 'region',
        options: [
          { selected: true, text: 'Countries', value: 'country' },
          { selected: false, text: 'Rainfall Region', value: 'rainfall_region' },
          { selected: false, text: 'Subregion', value: 'subregion_region' },
          { selected: false, text: 'Rainfall Region+Country', value: 'region' },
        ],
        query: 'Countries : country, Rainfall Region : rainfall_region, Subregion : subregion_region, Rainfall Region+Country : region',
        type: 'custom',
      },
      {
        description: 'One or more regions to include. Table counts and the curve sum cells across the selection.',
        current: {
          text: ['Ghana', 'Kenya'],
          value: ['ghana', 'kenya'],
        },
        definition: regionQuery,
        includeAll: true,
        label: 'Regions',
        multi: true,
        name: 'region_option',
        options: [],
        query: regionQuery,
        refresh: 1,
        regex: '',
        type: 'query',
      },
      {
        description: 'One or more forecasts to include. Curve uses color for week and line style for forecast.',
        current: {
          text: ['ECMWF IFS ER', 'Cumulus AI v0.0.0'],
          value: ['ecmwf_ifs_er', 'cumulus_ai'],
        },
        definition: forecastQuery,
        includeAll: true,
        label: 'Forecasts',
        multi: true,
        name: 'forecast_option',
        options: [],
        query: forecastQuery,
        refresh: 1,
        regex: '',
        type: 'query',
      },
      {
        description: 'Single forecast whose Informative / Actionable expected-cell KPIs are shown beside each lead subplot.',
        current: {
          text: 'Cumulus AI v0.0.0',
          value: 'cumulus_ai',
        },
        definition: forecastQuery,
        includeAll: false,
        label: 'Eval forecast',
        multi: false,
        name: 'eval_forecast',
        options: [],
        query: forecastQuery,
        refresh: 1,
        regex: '',
        type: 'query',
      },
      {
        description: 'Internal: hashed SQL table for unimodal-season, observation-filtered events.',
        current: { text: '', value: '' },
        datasource: { type: 'grafana-postgresql-datasource', uid: 'bdz3m3xs99p1cf' },
        definition: "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        hide: 2,
        includeAll: false,
        name: 'unimodal_metric_name',
        options: [],
        query: "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        refresh: 2,
        regex: '',
        type: 'query',
      },
      {
        description: 'Internal: hashed SQL table for unimodal-season, forecast-filtered events.',
        current: { text: '', value: '' },
        datasource: { type: 'grafana-postgresql-datasource', uid: 'bdz3m3xs99p1cf' },
        definition: "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        hide: 2,
        includeAll: false,
        name: 'unimodal_metric_fcst_name',
        options: [],
        query: "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        refresh: 2,
        regex: '',
        type: 'query',
      },
      {
        description: 'Internal: hashed SQL table for shifted unimodal-season, observation-filtered events.',
        current: { text: '', value: '' },
        datasource: { type: 'grafana-postgresql-datasource', uid: 'bdz3m3xs99p1cf' },
        definition: "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        hide: 2,
        includeAll: false,
        name: 'unimodal_shifted_metric_name',
        options: [],
        query: "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        refresh: 2,
        regex: '',
        type: 'query',
      },
      {
        description: 'Internal: hashed SQL table for shifted unimodal-season, forecast-filtered events.',
        current: { text: '', value: '' },
        datasource: { type: 'grafana-postgresql-datasource', uid: 'bdz3m3xs99p1cf' },
        definition: "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        hide: 2,
        includeAll: false,
        name: 'unimodal_shifted_fcst_metric_name',
        options: [],
        query: "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_unimodal_shifted_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        refresh: 2,
        regex: '',
        type: 'query',
      },
      {
        description: 'Internal: hashed SQL table for bimodal-season, observation-filtered events.',
        current: { text: '', value: '' },
        datasource: { type: 'grafana-postgresql-datasource', uid: 'bdz3m3xs99p1cf' },
        definition: "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        hide: 2,
        includeAll: false,
        name: 'bimodal_metric_name',
        options: [],
        query: "select * from md5('advanced_spatial_metric_table/2024-12-31_${grid}_forecast_filter-False_obs_filter-True${prob_type_suffix}_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip')",
        refresh: 2,
        regex: '',
        type: 'query',
      },
      {
        description: 'Internal: hashed SQL table for bimodal-season, forecast-filtered events.',
        current: { text: '', value: '' },
        datasource: { type: 'grafana-postgresql-datasource', uid: 'bdz3m3xs99p1cf' },
        definition: "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        hide: 2,
        includeAll: false,
        name: 'bimodal_metric_fcst_name',
        options: [],
        query: "SELECT md5(\n    'advanced_spatial_metric_table/2024-12-31_${grid}_'\n    || CASE '${metric}'\n         WHEN 'early_season_accumulation-30d-thresh-30' THEN 'forecast_filter-False_obs_filter-True'\n         ELSE 'forecast_filter-True_obs_filter-False'\n       END\n    || '${prob_type_suffix}'\n    || '_${metric}_africa_bimodal_season_country_rainfall_region_2016-01-01_${time_grouping}_${truth}_precip'\n)",
        refresh: 2,
        regex: '',
        type: 'query',
      },
      {
        description: 'Lower edge of the teal Informative band (0–1). Informative expected cells average over this cutoff up to the Actionable cutoff.',
        current: { text: '0.50', value: '0.50' },
        label: 'Informative cutoff',
        name: 'informative_cutoff',
        options: [{ selected: true, text: '0.50', value: '0.50' }],
        query: '0.50',
        type: 'textbox',
      },
      {
        description: 'Start of the green Actionable band (0–1). Also used as the table cell-count cutoff and dashed line on the curve. Actionable expected cells average from here to 100%.',
        current: { text: '0.75', value: '0.75' },
        label: 'Actionable cutoff',
        name: 'actionable_cutoff',
        options: [{ selected: true, text: '0.75', value: '0.75' }],
        query: '0.75',
        type: 'textbox',
      },
      {
        description: 'Which event filter to include: forecast-defined events, observation-defined events, or both (combined).',
        current: { text: 'Both', value: 'both' },
        label: 'Events',
        name: 'source',
        options: [
          { selected: false, text: 'Forecasted events', value: 'forecast' },
          { selected: false, text: 'Observed events', value: 'obs' },
          { selected: true, text: 'Both', value: 'both' },
        ],
        query: 'Forecasted events : forecast, Observed events : obs, Both : both',
        type: 'custom',
      },
    ],
  },
  time: { from: 'now-6h', to: 'now' },
  timepicker: { hidden: true },
  timezone: 'utc',
  title: 'Good Cells vs Cell Cutoff',
  uid: 'sw-good-cells-cutoff',
  version: 1,
  weekStart: '',
}
