"""Advanced metrics for agricultural applications."""


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
    # Configure the seasonal accumulation thresholds.
    early_season_accumulation_mm = 150.0
    early_season_accumulation_by_percent = 0.10
    mid_season_accumulation_mm = 300.0
    mid_season_accumulation_by_percent = 0.30
    late_season_accumulation_mm = 600.0
    late_season_accumulation_by_percent = 0.60

    # Compute the MAE
    metric = 'mae'
    # Filter on a specific threshhold of seasonal accumulation.
    filter_event = 'has_seasonal_accumulation'
    # Choose seasonal accumluation time group based on the region.
    if region in ['eastern_africa', 'kenya', 'ethiopia']:
        time_grouping = 'two_seasons'
    else:
        time_grouping = 'year'
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
    }
    # Compare accumulated rain on the right-aligned window over the past 30 days
    event = 'accumulated_rain'
    agg_days = int(experiment.split('-')[-1][:-1])  # Remove the 'd' from the end of the string.
    event_kwargs = {
        'fcst': {
            'agg_days': agg_days,
            'densify': True

        },
        'obs': {
            'agg_days': agg_days
        },
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_in_season_dry_spell_kwargs(experiment, region):  # noqa: ARG001
    """Agg day accumulation at a specific point in the seasonal accumulation.

    Experiment should be in the form:
        in_season_dry_spell-14d
        in_season_dry_spell-30d
        ... and so forth. 
    """
    # Configure the seasonal accumulation thresholds.
    early_season_accumulation_by_percent = 0.10
    first_rain_threshold_mm = 7.0
    pre_period_in_days = 45
    period_in_days = 60 # look 2 months after the first rain
    drying_day_threshold_mm = 20.0 # this is a sum
    drying_day_agg_in_days = 10
    # drying_day_margin_in_days = 5

    # Compute the MAE
    metric = 'mae'
    # metric = 'bias'
    # metric = 'smape'
    # Filter on a specific threshhold of seasonal accumulation.
    filter_event = 'drying_spells_in_initial_growing_period'
    # Choose seasonal accumluation time group based on the region.
    if region == 'eastern_africa':
        time_grouping = 'two_seasons'
    else:
        time_grouping = 'year'
    # Early season accumulation threshold.

    filter_event_kwargs = {
        'time_grouping': time_grouping,
        'accumulation_threshold': early_season_accumulation_by_percent,
        'by_percent': True,
        'first_rain_threshold_mm': first_rain_threshold_mm,
        'pre_period_in_days': pre_period_in_days,
        'period_in_days': period_in_days,
        'drying_day_threshold_mm': drying_day_threshold_mm,
        'drying_day_agg_in_days': drying_day_agg_in_days,
    }
    # Detect the first time the accumulation threshold is reached in the observation.
    metric_kwargs = {
        'obs_filter': True,
        'fcst_filter': False,
    }
    # Compare accumulated rain on the right-aligned window over the past 30 days
    event = 'accumulated_rain'
    event_kwargs = {
        'fcst': {
            'agg_days': drying_day_agg_in_days,
            'densify': True

        },
        'obs': {
            'agg_days': drying_day_agg_in_days,
        },
    }
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs


def get_experiment_kwargs(experiment, region):
    """Returns metrics configruations needed to run an advanced agricultural metric."""
    if 'season_accumulation' in experiment:
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_seasonal_accumulation_kwargs(experiment, region)
    elif 'in_season_dry_spell' in experiment:
        metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs = \
            get_in_season_dry_spell_kwargs(experiment, region)
    else:
        raise ValueError(f"Experiment {experiment} not supported.")

    return metric_name, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs
