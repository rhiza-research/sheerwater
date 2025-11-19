"""Library of statistics implementations for verification."""
# flake8: noqa: D102, ARG001, D103

import xarray as xr
import numpy as np
from functools import wraps

import xskillscore
from weatherbench2.metrics import SpatialQuantileCRPS, SpatialSEEPS

from nuthatch import cache

# Global metric registry dictionary
SHEERWATER_STATISTIC_REGISTRY = {}


def statistic(cache=False, name=None,
              data_type='array', timeseries='time',
              cache_args=['variable', 'agg_days', 'forecast', 'truth',
                          'data_key', 'grid', 'statistic'],
              chunking={"lat": 121, "lon": 240, "time": 30, 'region': 300, 'prediction_timedelta': -1},
              chunk_by_arg={
                  'grid': {
                      'global0_25': {"lat": 721, "lon": 1440, "time": 30}
                  },
              }):
    """A unifed statistics decorator.

    With this decorator, you can define a statistic function that will be cached and used to compute the statistic
    for a given forecast and observation. The statistic function will be provided with the forecast, observation, and
    data as arguments, and should return a xarray.DataArray.

    The statistic function will be cached using the cache decorator.

    """
    def create_statistic(func):
        # Register the statistic function with the registry
        # We'll register the wrapped function instead of the original
        @timeseries
        @cache(cache=cache, cache_args=cache_args,
               backend_kwargs={
                   'chunking': chunking
                   'chunk_by_arg': chunk_by_arg
               })
        def global_statistic(
            start_time, end_time,
            data,
            variable, agg_days, forecast, truth,
            data_key, grid, statistic,
            **cache_kwargs
        ):
            # Pass the cache kwargs through
            cache_kwargs = {
                'variable': variable, 'agg_days': agg_days, 'forecast': forecast, 'truth': truth,
                'data_key': data_key, 'grid': grid,
                'statistic': statistic, 'start_time': start_time, 'end_time': end_time,
            }
            ds = func(data=data, **cache_kwargs)
            # Assign attributes in one call
            ds = ds.assign_attrs(
                sparse=data['sparse'],
                prob_type=data['prob_type'],
                forecast=forecast,
                truth=truth,
                statistic=statistic
            )
            return ds

        @wraps(func)
        def wrapper(
            data, **cache_kwargs
        ):
            # Remove start and end time from the kwargs so they can be
            # passed positionally as the cacheable operator requires
            start_time = cache_kwargs.pop('start_time')
            end_time = cache_kwargs.pop('end_time')

            # Set the statistic to the function name in lowercase
            cache_kwargs['statistic'] = name

            # Call the global statistic function
            ds = global_statistic(
                start_time, end_time,
                data=data, **cache_kwargs,
            )
            return ds

        # Register the wrapped function with the registry
        SHEERWATER_STATISTIC_REGISTRY[name] = wrapper

        return wrapper
    return create_statistic


@statistic(cache=False, name='obs')
def fn_obs(data, **cache_kwargs):  # noqa: F821
    return data['obs']


@statistic(cache=False, name='fcst')
def fn_fcst(data, **cache_kwargs):  # noqa: F821
    return data['fcst']


@statistic(cache=False, name='squared_obs')
def fn_squared_obs(data, **cache_kwargs):  # noqa: F821
    return data['obs']**2


@statistic(cache=False, name='squared_fcst')
def fn_squared_fcst(data, **cache_kwargs):  # noqa: F821
    return data['fcst']**2


@statistic(cache=False, name='covariance')
def fn_covariance(data, **cache_kwargs):  # noqa: F821
    return data['fcst'] * data['obs']


@statistic(cache=False, name='obs_anom')
def fn_obs_anom(data, **cache_kwargs):  # noqa: F821
    return data['obs'] - data['climatology']


@statistic(cache=False, name='fcst_anom')
def fn_fcst_anom(data, **cache_kwargs):  # noqa: F821
    return data['fcst'] - data['climatology']


@statistic(cache=False, name='squared_obs_anom')
def fn_squared_obs_anom(data, **cache_kwargs):  # noqa: F821
    obs_anom = fn_obs_anom(data, **cache_kwargs)
    return obs_anom**2


@statistic(cache=False, name='squared_fcst_anom')
def fn_squared_fcst_anom(data, **cache_kwargs):  # noqa: F821
    fcst_anom = fn_fcst_anom(data, **cache_kwargs)
    return fcst_anom**2


@statistic(cache=False, name='anom_covariance')
def fn_anom_covariance(data, **cache_kwargs):  # noqa: F821
    fcst_anom = fn_fcst_anom(data, **cache_kwargs)
    obs_anom = fn_obs_anom(data, **cache_kwargs)
    return obs_anom * fcst_anom


@statistic(cache=False, name='n_valid')
def fn_n_valid(data, **cache_kwargs):  # noqa: F821
    return xr.ones_like(data['fcst']).where(data['fcst'].notnull(), 0.0, drop=False).astype(float)


@statistic(cache=False, name='obs_digitized')
def fn_obs_digitized(data, **cache_kwargs):  # noqa: F821
    # `np.digitize(x, bins, right=True)` returns index `i` such that:
    #   `bins[i-1] < x <= bins[i]`
    # Indices range from 0 (for x <= bins[0]) to len(bins) (for x > bins[-1]).
    # `bins` for np.digitize will be `thresholds_np`.
    ds = xr.apply_ufunc(
        np.digitize,
        data['obs'],
        kwargs={'bins': data['bins'], 'right': True},
        dask='parallelized',
        output_dtypes=[int],
    )
    # Restore NaN values
    return ds.where(data['obs'].notnull(), np.nan, drop=False).astype(float)


@statistic(cache=False, name='fcst_digitized')
def fn_fcst_digitized(data, **cache_kwargs):  # noqa: F821
    # `np.digitize(x, bins, right=True)` returns index `i` such that:
    #   `bins[i-1] < x <= bins[i]`
    # Indices range from 0 (for x <= bins[0]) to len(bins) (for x > bins[-1]).
    # `bins` for np.digitize will be `thresholds_np`.
    ds = xr.apply_ufunc(
        np.digitize,
        data['fcst'],
        kwargs={'bins': data['bins'], 'right': True},
        dask='parallelized',
        output_dtypes=[int],
    )
    # Restore NaN values
    return ds.where(data['fcst'].notnull(), np.nan)


@statistic(cache=False, name='false_positives')
def fn_false_positives(data, **cache_kwargs):  # noqa: F821
    # "Positive events" are 2 (above threshold); negative are 1
    obs_dig = fn_obs_digitized(data, **cache_kwargs)
    fcst_dig = fn_fcst_digitized(data, **cache_kwargs)
    return (obs_dig == 1) & (fcst_dig == 2)


@statistic(cache=False, name='false_negatives')
def fn_false_negatives(data, **cache_kwargs):  # noqa: F821
    obs_dig = fn_obs_digitized(data, **cache_kwargs)
    fcst_dig = fn_fcst_digitized(data, **cache_kwargs)
    return (obs_dig == 2) & (fcst_dig == 1)


@statistic(cache=False, name='true_positives')
def fn_true_positives(data, **cache_kwargs):  # noqa: F821
    obs_dig = fn_obs_digitized(data, **cache_kwargs)
    fcst_dig = fn_fcst_digitized(data, **cache_kwargs)
    return (obs_dig == 2) & (fcst_dig == 2)


@statistic(cache=False, name='true_negatives')
def fn_true_negatives(data, **cache_kwargs):  # noqa: F821
    obs_dig = fn_obs_digitized(data, **cache_kwargs)
    fcst_dig = fn_fcst_digitized(data, **cache_kwargs)
    return (obs_dig == 1) & (fcst_dig == 1)


@statistic(cache=False, name='n_correct')
def fn_n_correct(data, **cache_kwargs):  # noqa: F821
    obs_dig = fn_obs_digitized(data, **cache_kwargs)
    fcst_dig = fn_fcst_digitized(data, **cache_kwargs)
    return (obs_dig == fcst_dig)


# Dynamically generate functions for each category and bind it with the correct category
def make_fn_n_obs_bin(category):
    @statistic(cache=False, name=f'n_obs_bin_{category}')
    def fn_n_obs_bin(data, **cache_kwargs):
        obs_dig = fn_obs_digitized(data, **cache_kwargs)
        return (obs_dig == category)
    return fn_n_obs_bin


def make_fn_n_fcst_bin(category):
    @statistic(cache=False, name=f'n_fcst_bin_{category}')
    def fn_n_fcst_bin(data, **cache_kwargs):
        fcst_dig = fn_fcst_digitized(data, **cache_kwargs)
        return (fcst_dig == category)
    return fn_n_fcst_bin


# Generate 10 categorical obserations by default for the categorical metrics
for cat in range(1, 10):
    make_fn_n_obs_bin(cat)
    make_fn_n_fcst_bin(cat)


@statistic(cache=False, name='mae')
def fn_mae(data, **cache_kwargs):  # noqa: F821
    return abs(data['fcst'] - data['obs'])


@statistic(cache=False, name='mse')
def fn_mse(data, **cache_kwargs):  # noqa: F821
    return (data['fcst'] - data['obs'])**2


@statistic(cache=False, name='bias')
def fn_bias(data, **cache_kwargs):  # noqa: F821
    return data['fcst'] - data['obs']


@statistic(cache=False, name='mape')
def fn_mape(data, **cache_kwargs):  # noqa: F821
    return abs(data['fcst'] - data['obs']) / np.maximum(abs(data['obs']), 1e-10)


@statistic(cache=False, name='smape')
def fn_smape(data, **cache_kwargs):  # noqa: F821
    return abs(data['fcst'] - data['obs']) / (abs(data['fcst']) + abs(data['obs']))


@statistic(cache=False, name='brier')
def fn_brier(data, **cache_kwargs):  # noqa: F821
    fcst_dig = fn_fcst_digitized(data, **cache_kwargs)
    obs_dig = fn_obs_digitized(data, **cache_kwargs)
    positive_event_id = 2
    fcst_event_prob = (fcst_dig == positive_event_id).mean(dim='member')
    obs_event_prob = (obs_dig == positive_event_id)
    return (fcst_event_prob - obs_event_prob)**2


@statistic(cache=True, name='seeps')
def fn_seeps(data, **cache_kwargs):  # noqa: F821
    wet_threshold = data['wet_threshold']
    dry_fraction = data['dry_fraction']
    clim_ds = xr.merge([wet_threshold, dry_fraction])
    m_ds = SpatialSEEPS(climatology=clim_ds,
                        dry_threshold_mm=0.25,
                        precip_name='precip',
                        min_p1=0.03,
                        max_p1=0.93) \
        .compute(forecast=data['fcst'], truth=data['obs'],
                 avg_time=False, skipna=True)
    m_ds = m_ds.rename({'latitude': 'lat', 'longitude': 'lon'})
    return m_ds


@statistic(cache=False, name='crps')
def fn_crps(data, **cache_kwargs):  # noqa: F821
    if data['prob_type'] == 'ensemble':
        fcst = data['fcst'].chunk(member=-1, time=1, prediction_timedelta=1,
                                  lat=250, lon=250)  # member must be -1 to succeed
        m_ds = xskillscore.crps_ensemble(observations=data['obs'],
                                         forecasts=fcst, mean=False, dim=['time', 'prediction_timedelta'])
    elif data['prob_type'] == 'quantile':
        m_ds = SpatialQuantileCRPS(quantile_dim='member').compute(
            forecast=data['fcst'], truth=data['obs'], avg_time=False, skipna=True)
        m_ds = m_ds.rename({'latitude': 'lat', 'longitude': 'lon'})
    else:
        raise ValueError(f"Invalid probability type: {data['prob_type']}")
    return m_ds


def statistic_factory(statistic_name: str):
    """Get a statistic function by name from the registry."""
    try:
        return SHEERWATER_STATISTIC_REGISTRY[statistic_name.lower()]
    except KeyError:
        raise ValueError(f"Unknown statistic: {statistic_name}. Available statistics: {list_statistics()}")


def list_statistics():
    """List all available statistics in the registry."""
    return list(SHEERWATER_STATISTIC_REGISTRY.keys())
