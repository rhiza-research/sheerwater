"""Advanced metrics for agricultural applications."""


def get_experiment_kwargs(experiment, region):
    """Returns metrics configruations needed to run an advanced agricultural metric."""
    if 'early_season_accumulation' in experiment:
        # Compute the MAE
        metric = 'mae'
        # Filter on a specific threshhold of seasonal accumulation.
        filter_event = 'has_seasonal_accumulation'
        # Choose seasonal accumluation time group based on the region.
        if region == 'eastern_africa':
            time_grouping = 'two_seasons'
        else:
            time_grouping = 'year'
        # Early season accumulation threshold.
        accumulation_threshold = 150.0
        filter_event_kwargs = {
            'time_grouping': time_grouping,
            'accumulation_threshold': accumulation_threshold,
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
            'agg_days': agg_days,
            'densify': True
        }
        # event_kwargs = {
        #     'fcst_event_kwargs': {
        #         'agg_days': agg_days,
        #         'densify': True

        #     },
        #     'obs_event_kwargs': {
        #         'agg_days': agg_days
        #     },
        # }
    else:
        raise ValueError(f"Experiment {experiment} not supported.")
    return metric, metric_kwargs, event, event_kwargs, filter_event, filter_event_kwargs
