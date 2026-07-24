"""Advanced metrics for agricultural applications."""
import copy
import warnings


def _with_input_metric_kwargs(metric_kwargs, input_metric_kwargs=None):
    """Merge caller overrides onto experiment defaults.

    Always returns a new dict (deep-copying input) so later in-place updates —
    densify/pre_filter, Metric storing metric_kwargs by reference, etc. — cannot
    mutate the caller's kwargs across job iterations.
    """
    merged = copy.deepcopy(metric_kwargs)
    if input_metric_kwargs:
        merged.update(copy.deepcopy(input_metric_kwargs))
    return merged


def get_seasonal_accumulation_kwargs(experiment, region, input_metric_kwargs=None):  # noqa: ARG001
    """MAE of accumulated rain at a seasonal accumulation threshold.

    Experiment names follow:
        {early,mid,late}_season_accumulation[-_by_percent]-{N}d
    e.g. early_season_accumulation-30d, mid_season_accumulation_by_percent-14d.
    """
    if region == 'africa_unimodal_season' or region == 'western_africa':
        time_grouping = 'year'
    elif region == 'africa_bimodal_season' or region == 'eastern_africa':
        time_grouping = 'two_seasons'
    elif region == 'africa_unimodal_shifted_season':
        time_grouping = 'shifted_season'
    else:
        warnings.warn(f"Region {region} not supported. Using year as time grouping.")
        time_grouping = 'year'

    early_season_accumulation_mm = 100.0
    early_season_accumulation_by_percent = 0.15
    mid_season_accumulation_mm = 300.0
    mid_season_accumulation_by_percent = 0.30
    late_season_accumulation_mm = 600.0
    late_season_accumulation_by_percent = 0.60

    metric = 'mae'
    if 'early_season_accumulation_by_percent' in experiment:
        accumulation_threshold = early_season_accumulation_by_percent
        by_percent = True
    elif 'early_season_accumulation' in experiment:
        accumulation_threshold = early_season_accumulation_mm
        by_percent = False
    elif 'mid_season_accumulation_by_percent' in experiment:
        accumulation_threshold = mid_season_accumulation_by_percent
        by_percent = True
    elif 'mid_season_accumulation' in experiment:
        accumulation_threshold = mid_season_accumulation_mm
        by_percent = False
    elif 'late_season_accumulation_by_percent' in experiment:
        accumulation_threshold = late_season_accumulation_by_percent
        by_percent = True
    elif 'late_season_accumulation' in experiment:
        accumulation_threshold = late_season_accumulation_mm
        by_percent = False
    else:
        raise ValueError(f"Experiment {experiment} not supported.")
    filter_event = 'has_seasonal_accumulation'
    filter_event_kwargs = {
        'time_grouping': time_grouping,
        'accumulation_threshold': accumulation_threshold,
        'by_percent': by_percent,
        'detect_in_time': {'detect': 'first', 'time_grouping': time_grouping}
    }
    metric_kwargs = _with_input_metric_kwargs({
        'obs_filter': True,
        'forecast_filter': False,
        'densify': True
    }, input_metric_kwargs)
    event = 'accumulated_rain'
    agg_days = int(experiment.split('-')[-1][:-1])
    event_kwargs = {
        'agg_days': agg_days,
        'align': 'right',
    }

    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_in_season_dry_spell_kwargs(experiment, region, input_metric_kwargs=None):  # noqa: ARG001
    """Forecast rain amount during in-season dry spells.

    Experiment name: in_season_dry_spell.
    """
    if region == 'africa_unimodal_season' or region == 'western_africa':
        time_grouping = 'year'
    elif region == 'africa_bimodal_season' or region == 'eastern_africa':
        time_grouping = 'two_seasons'
    elif region == 'africa_unimodal_shifted_season':
        time_grouping = 'shifted_season'
    else:
        warnings.warn(f"Region {region} not supported. Using year as time grouping.")
        time_grouping = 'year'

    early_season_accumulation_by_percent = 0.10
    mid_season_accumulation_by_percent = 0.40
    season_accumulation_minimum_mm = 150.0
    pre_period_in_days = 45
    first_rain_threshold_mm = 4.0
    drying_day_threshold_mm = 15.0  # sum over drying_day_agg_in_days
    drying_day_agg_in_days = 10

    metric_kwargs = _with_input_metric_kwargs({
        'obs_filter': True,
        'forecast_filter': False,
        'pre_filter': True,
        'densify': True,
    }, input_metric_kwargs)
    # Experiment requires densify + pre_filter regardless of caller overrides.
    metric_kwargs.update({'densify': True, 'pre_filter': True})

    if metric_kwargs['forecast_filter'] and not metric_kwargs['obs_filter']:
        metric = 'obsvalue'
    elif metric_kwargs['obs_filter'] and not metric_kwargs['forecast_filter']:
        metric = 'forecastvalue'
    else:
        raise ValueError("Exactly one of forecast_filter or obs_filter must be True.")

    # Baseline filter down to the pre-sesason
    pre_filter_event = 'initial_growing_period'
    pre_filter_event_kwargs = {
        'time_grouping': time_grouping,
        'early_season_accumulation_by_percent': early_season_accumulation_by_percent,
        'mid_season_accumulation_by_percent': mid_season_accumulation_by_percent,
        'season_accumulation_minimum_mm': season_accumulation_minimum_mm,
        'pre_period_in_days': pre_period_in_days,
        'first_rain_threshold_mm': first_rain_threshold_mm,
    }
    metric_kwargs['pre_filter_event'] = pre_filter_event
    metric_kwargs['pre_filter_event_kwargs'] = pre_filter_event_kwargs

    # Filter on a specific threshhold of seasonal accumulation.
    filter_event = 'drying_spells'
    filter_event_kwargs = {
        'drying_day_threshold_mm': drying_day_threshold_mm,
        'drying_day_agg_in_days': drying_day_agg_in_days,
    }

    # Compare accumulated rain on the right-aligned window over the past 30 days
    event = 'accumulated_rain'
    event_kwargs = {
        'agg_days': drying_day_agg_in_days,
        'align': 'right',
    }

    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_big_rain_days_kwargs(experiment, region, input_metric_kwargs=None):  # noqa: ARG001
    """SMAPE of forecast rain on days with heavy observed rainfall.

    Experiment name: big_rain_days.
    """
    big_rain_threshold_mm = 15.0
    big_rain_agg_days = 1
    big_rain_margin_in_days = 5

    metric = 'smape'
    filter_event = 'above_threshold'
    filter_event_kwargs = {
        'agg_days': big_rain_agg_days,
        'threshold': big_rain_threshold_mm,
        'align': 'center',
    }
    metric_kwargs = _with_input_metric_kwargs({
        'obs_filter': True,
        'forecast_filter': False,
        'densify': True
    }, input_metric_kwargs)
    event = 'accumulated_rain'
    event_kwargs = {
        'agg_days': big_rain_margin_in_days,
        'align': 'center',
    }

    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_extreme_rain_days_kwargs(experiment, region, input_metric_kwargs=None):  # noqa: ARG001
    """Extreme rain days according to the quantile ranks of the data source."""
    # Configure the big rain thresholds.
    extreme_rain_threshold_quantile = 0.90
    extreme_rain_agg_days = 1
    extreme_rain_margin_in_days = 5

    # Compute the SMAPE of the forecasted rain during the big rain days
    metric = 'smape'
    # Filter on a specific threshhold of seasonal accumulation.
    filter_event = 'quantile_extremes'
    filter_event_kwargs = {
        'threshold': extreme_rain_threshold_quantile,
        'first_year': 1985,
        'last_year': 2014,
        'agg_days': extreme_rain_agg_days,
        'n_quantiles': 20,
    }
    # Detect the first time the accumulation threshold is reached in the observation.
    metric_kwargs = {
        'obs_filter': True,
        'forecast_filter': False,
        'densify': True
    }
    # Compare accumulated rain on the right-aligned window over the past 30 days
    event = 'accumulated_rain'
    event_kwargs = {
        'agg_days': extreme_rain_margin_in_days,
        'align': 'center',
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_rain_days_soft_kwargs(experiment, region, input_metric_kwargs=None):  # noqa: ARG001
    """POD for rain days using a soft (time-margin) matching window."""
    rain_threshold_mm = 3.0
    rain_agg_days = 1
    rain_margin_in_days = 5

    metric = 'pod'
    filter_event = None
    filter_event_kwargs = {}
    metric_kwargs = _with_input_metric_kwargs({
        'obs_filter': False,
        'forecast_filter': False,
        'soft_margin_in_days': rain_margin_in_days,
        'densify': True
    }, input_metric_kwargs)
    event = 'above_threshold'
    event_kwargs = {
        'agg_days': rain_agg_days,
        'threshold': rain_threshold_mm,
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_dry_spells_kwargs(experiment, region, input_metric_kwargs=None):  # noqa: ARG001
    """Forecast rain amount during dry spells at any point in the year."""
    dry_spell_threshold_mm = 1.5  # average daily rain
    dry_spell_agg_days = 5

    metric = 'forecastabsolutevalue'
    filter_event = 'below_threshold'
    filter_event_kwargs = {
        'agg_days': dry_spell_agg_days,
        'threshold': dry_spell_threshold_mm,
        'align': 'right'
    }
    metric_kwargs = _with_input_metric_kwargs({
        'obs_filter': True,
        'forecast_filter': False,
        'densify': True
    }, input_metric_kwargs)
    event = 'accumulated_rain'
    event_kwargs = {
        'agg_days': dry_spell_agg_days,
        'align': 'right',
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_dry_spells_soft_kwargs(experiment, region, input_metric_kwargs=None):  # noqa: ARG001
    """POD for dry spells using a soft (time-margin) matching window."""
    dry_day_threshold_mm = 1.0
    dry_day_agg_days = 5
    margin_in_days = 5

    metric = 'pod'
    filter_event = None
    filter_event_kwargs = {}
    metric_kwargs = _with_input_metric_kwargs({
        'obs_filter': False,
        'forecast_filter': False,
        'soft_margin_in_days': margin_in_days,
        'densify': True
    }, input_metric_kwargs)
    event = 'below_threshold'
    event_kwargs = {
        'agg_days': dry_day_agg_days,
        'threshold': dry_day_threshold_mm,
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_experiment_kwargs(experiment, region, input_metric_kwargs=None):
    """Returns metrics configruations needed to run an advanced agricultural metric."""
    # Enable actionable thresholds for advanced metrics if the metric name is passed in the form 'metric-thresh-value',
    # e.g. 'early_season_accumulation-30d-thresh-30mm'. If the actionable threshhold is passed, the metric will be
    # configured to evaluate the passing fraction of the metric.
    if '-thresh-' in experiment:
        experiment_name = experiment.split('-thresh-')[0]
        pass_threshold = float(experiment.split('-thresh-')[1])
    else:
        experiment_name = experiment
        pass_threshold = None

    if 'season_accumulation' in experiment:
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_seasonal_accumulation_kwargs(experiment, region, input_metric_kwargs)
    elif experiment == 'in_season_dry_spell':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_in_season_dry_spell_kwargs(experiment, region, input_metric_kwargs)
    elif experiment == 'big_rain_days':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_big_rain_days_kwargs(experiment, region, input_metric_kwargs)
    elif experiment == 'extreme_rain_days':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_extreme_rain_days_kwargs(experiment, region, input_metric_kwargs)
    elif experiment == 'rain_days_soft':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_rain_days_soft_kwargs(experiment, region, input_metric_kwargs)
    elif experiment == 'dry_spells':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_dry_spells_kwargs(experiment, region, input_metric_kwargs)
    elif experiment == 'dry_spells_soft':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_dry_spells_soft_kwargs(experiment, region, input_metric_kwargs)
    else:
        raise ValueError(f"Experiment {experiment_name} not supported.")

    if pass_threshold is not None:
        # If we are evaluating a passing fraction, we need to use the passfraction metric, with the
        # underlying passsing statistic being the metric name.
        metric_kwargs['pass_statistic'] = metric_name
        metric_kwargs['pass_fn'] = lambda x: x <= pass_threshold
        metric_name = 'passfraction'

    return metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs
