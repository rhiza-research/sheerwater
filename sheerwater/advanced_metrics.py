"""Advanced metrics for agricultural applications."""
import warnings


def get_seasonal_accumulation_kwargs(experiment, region):
    """Agg day accumulation at a specific point in the seasonal accumulation.

    Experiment should be in the form:
        early_season_accumulation-30d
        early_season_accumulation_by_percent-30d
        mid_season_accumulation-30d
        mid_season_accumulation_by_percent-30d
        late_season_accumulation-30d
        late_season_accumulation_by_percent-30d

    or with a differnt number of days evaluated before the event:
        early_season_accumulation-14d
        ... and so forth.
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

    # Configure the seasonal accumulation thresholds.
    early_season_accumulation_mm = 100.0
    early_season_accumulation_by_percent = 0.15
    mid_season_accumulation_mm = 300.0
    mid_season_accumulation_by_percent = 0.30
    late_season_accumulation_mm = 600.0
    late_season_accumulation_by_percent = 0.60

    # Compute the MAE
    metric = 'mae'
    # Filter on a specific threshhold of seasonal accumulation.
    # Early season accumulation threshold.
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
    # Detect the first time the accumulation threshold is reached in the observation.
    metric_kwargs = {
        'obs_filter': True,
        'fcst_filter': False,
        'densify': True
    }
    # Compare accumulated rain on the right-aligned window over the past 30 days
    event = 'accumulated_rain'
    agg_days = int(experiment.split('-')[-1][:-1])  # Remove the 'd' from the end of the string.
    event_kwargs = {
        'agg_days': agg_days,
        'align': 'right',
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_in_season_dry_spell_kwargs(experiment, region):  # noqa: ARG001
    """Agg day accumulation at a specific point in the seasonal accumulation.

    Experiment should be in the form:
        in_season_dry_spell
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

    # Configure the seasonal accumulation thresholds.
    early_season_accumulation_by_percent = 0.10
    mid_season_accumulation_by_percent = 0.40
    season_accumulation_minimum_mm = 50.0
    pre_period_in_days = 45
    first_rain_threshold_mm = 4.0
    drying_day_threshold_mm = 15.0  # this is a sum
    drying_day_agg_in_days = 10

    # Compute the amount of forecasted rain during the dry period
    metric = 'forecastvalue'

    # Filter on a specific threshhold of seasonal accumulation.
    filter_event = 'drying_spells_in_initial_growing_period'

    # Early season accumulation threshold.
    filter_event_kwargs = {
        'time_grouping': time_grouping,
        'early_season_accumulation_by_percent': early_season_accumulation_by_percent,
        'mid_season_accumulation_by_percent': mid_season_accumulation_by_percent,
        'season_accumulation_minimum_mm': season_accumulation_minimum_mm,
        'pre_period_in_days': pre_period_in_days,
        'first_rain_threshold_mm': first_rain_threshold_mm,
        'drying_day_threshold_mm': drying_day_threshold_mm,
        'drying_day_agg_in_days': drying_day_agg_in_days,
    }
    # Detect the first time the accumulation threshold is reached in the observation.
    metric_kwargs = {
        'obs_filter': True,
        'fcst_filter': False,
        'densify': True
    }
    # Compare accumulated rain on the right-aligned window over the past 30 days
    event = 'accumulated_rain'
    event_kwargs = {
        'agg_days': drying_day_agg_in_days,
        'align': 'right',
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_big_rain_days_kwargs(experiment, region):  # noqa: ARG001
    """Agg day accumulation at a specific point in the seasonal accumulation.

    Experiment should be in the form:
    bi
        ... and so forth.
    """
    # Configure the big rain thresholds.
    big_rain_threshold_mm = 15.0
    big_rain_agg_days = 1
    big_rain_margin_in_days = 5

    # Compute the SMAPE of the forecasted rain during the big rain days
    metric = 'smape'
    # Filter on a specific threshhold of seasonal accumulation.
    filter_event = 'above_threshold'
    filter_event_kwargs = {
        'agg_days': big_rain_agg_days,
        'threshold': big_rain_threshold_mm,
        'align': 'center',
    }
    # Detect the first time the accumulation threshold is reached in the observation.
    metric_kwargs = {
        'obs_filter': True,
        'fcst_filter': False,
        'densify': True
    }
    # Compare accumulated rain on the right-aligned window over the past 30 days
    event = 'accumulated_rain'
    event_kwargs = {
        'agg_days': big_rain_margin_in_days,
        'align': 'center',
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_rain_days_soft_kwargs(experiment, region):  # noqa: ARG001
    """Rain days with a soft probability of detection."""
    # Configure the big rain thresholds.
    rain_threshold_mm = 3.0
    rain_agg_days = 1
    rain_margin_in_days = 5

    # Compute the MAE
    # metric = 'mae'
    # metric = 'forecastabsolutevalue'
    metric = 'pod'
    # Filter on a specific threshhold of seasonal accumulation.
    filter_event = None
    filter_event_kwargs = {}
    # Detect the first time the accumulation threshold is reached in the observation.
    metric_kwargs = {
        'obs_filter': False,
        'fcst_filter': False,
        'soft_margin_in_days': rain_margin_in_days,
        'densify': True
    }
    event = 'above_threshold'
    event_kwargs = {
        'agg_days': rain_agg_days,
        'threshold': rain_threshold_mm,
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_dry_spells_kwargs(experiment, region):  # noqa: ARG001
    """Dry spell performance at any point in the year."""
    # Configure the big rain thresholds.
    dry_spell_threshold_mm = 1.5  # Average daily rain
    dry_spell_agg_days = 5

    # Compute the MAE
    # metric = 'mae'
    metric = 'forecastabsolutevalue'
    # Filter on a specific threshhold of seasonal accumulation.
    filter_event = 'below_threshold'
    filter_event_kwargs = {
        'agg_days': dry_spell_agg_days,
        'threshold': dry_spell_threshold_mm,
        'align': 'right'
    }
    # Detect the first time the accumulation threshold is reached in the observation.
    metric_kwargs = {
        'obs_filter': True,
        'fcst_filter': False,
        'densify': True
    }
    # Compare accumulated rain on the right-aligned window over the past 30 days
    event = 'accumulated_rain'
    event_kwargs = {
        'agg_days': dry_spell_agg_days,
        'align': 'right',
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_dry_spells_soft_kwargs(experiment, region):  # noqa: ARG001
    """Rain days with a soft probability of detection."""
    # Configure the big rain thresholds.
    dry_day_threshold_mm = 1.0
    dry_day_agg_days = 5
    margin_in_days = 5

    # Compute the MAE
    metric = 'pod'
    # Filter on a specific threshhold of seasonal accumulation.
    filter_event = None
    filter_event_kwargs = {}
    # Detect the first time the accumulation threshold is reached in the observation.
    metric_kwargs = {
        'obs_filter': False,
        'fcst_filter': False,
        'soft_margin_in_days': margin_in_days,
        'densify': True
    }
    # Compare accumulated rain on the right-aligned window over the past 30 days
    event = 'below_threshold'
    event_kwargs = {
        'agg_days': dry_day_agg_days,
        'threshold': dry_day_threshold_mm,
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_experiment_kwargs(experiment, region):
    """Returns metrics configruations needed to run an advanced agricultural metric."""
    if 'season_accumulation' in experiment:
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_seasonal_accumulation_kwargs(experiment, region)
    elif experiment == 'in_season_dry_spell':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_in_season_dry_spell_kwargs(experiment, region)
    elif experiment == 'big_rain_days':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_big_rain_days_kwargs(experiment, region)
    elif experiment == 'rain_days_soft':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_rain_days_soft_kwargs(experiment, region)
    elif experiment == 'dry_spells':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_dry_spells_kwargs(experiment, region)
    elif experiment == 'dry_spells_soft':
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_dry_spells_soft_kwargs(experiment, region)
    else:
        raise ValueError(f"Experiment {experiment} not supported.")

    return metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs
