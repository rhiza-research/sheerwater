"""Test forecasters functionality and interfaces."""
import dask.array as da
import numpy as np
import pandas as pd
import xarray as xr
from dateutil.relativedelta import relativedelta

from sheerwater.forecasts import ecmwf_ifs_er_debiased
from sheerwater.climatology import climatology_era5_1985_2015
from sheerwater.utils import densify_fcst, convert_pred_time_to_init_time


def test_densify_fcst(remote_dask_cluster):  # noqa: ARG001
    """Test that the densify_fcst function works."""
    start_time = '2016-01-01'
    end_time = '2016-03-30'
    ds = ecmwf_ifs_er_debiased(start_time=start_time, end_time=end_time,
                               grid='global1_5', mask='lsm', region='kenya')
    ds = convert_pred_time_to_init_time(ds)
    ds_dense = densify_fcst(ds, start_time=start_time, end_time=end_time)

    # The forecast is filled from the previous forecast for this init time
    ds1 = ds.sel(init_time="2016-01-04", prediction_timedelta=np.timedelta64(2, 'D'))
    ds2 = ds_dense.sel(init_time="2016-01-06", prediction_timedelta=np.timedelta64(0, 'D'))
    assert (ds2 - ds1).precip.max() < 1e-10

    # The forecast is filled forward from it's last value for the same init time
    ds3 = ds_dense.sel(init_time="2016-01-06").isel(prediction_timedelta=-1)
    ds4 = ds_dense.sel(init_time="2016-01-06").isel(prediction_timedelta=-3)
    assert (ds3 - ds4).precip.max() < 1e-10

def _make_reforecast_ds(issuance_dates, start_years):
    """Build a minimal synthetic reforecast dataset backed by dask arrays."""
    shape = (len(issuance_dates), len(start_years), 2)
    data = da.ones(shape, chunks=shape, dtype=float)
    return xr.Dataset(
        {'precip': (['model_issuance_date', 'start_year', 'lead_time'], data)},
        coords={
            'model_issuance_date': pd.DatetimeIndex(issuance_dates),
            'start_year': start_years,
            'lead_time': [np.timedelta64(0, 'D'), np.timedelta64(7, 'D')],
        }
    )


def test_reforecast_to_timeseries_basic():
    """Output has init_time/prediction_timedelta dims; init times match issuance + relativedelta."""
    ds = _make_reforecast_ds(['2020-03-15', '2020-03-18'], [-1, -2])
    result = reforecast_to_timeseries(ds)

    assert 'init_time' in result.dims
    assert 'prediction_timedelta' in result.dims
    assert 'model_issuance_date' not in result.dims
    assert 'start_year' not in result.dims
    assert 'lead_time' not in result.dims

    expected_times = sorted([
        pd.Timestamp('2020-03-15') + relativedelta(years=-1),
        pd.Timestamp('2020-03-15') + relativedelta(years=-2),
        pd.Timestamp('2020-03-18') + relativedelta(years=-1),
        pd.Timestamp('2020-03-18') + relativedelta(years=-2),
    ])
    result_times = sorted(pd.DatetimeIndex(result.init_time.values))
    assert result_times == expected_times


def test_reforecast_to_timeseries_dedup_keeps_most_recent():
    """When two (issuance_date, start_year) pairs share an init time, the more recent issuance wins."""
    # Conflict: (2020-01-06, -1) -> 2019-01-06  and  (2021-01-06, -2) -> 2019-01-06
    issuance_dates = ['2020-01-06', '2021-01-06']
    start_years = [-1, -2]
    shape = (2, 2, 2)
    # (mid=2020, sy=-1) gets value 1.0; (mid=2021, sy=-2) gets value 99.0
    data = np.array([[[1.0, 1.0], [2.0, 2.0]],   # mid=2020: sy=-1 -> 1.0, sy=-2 -> 2.0
                     [[3.0, 3.0], [99.0, 99.0]]])  # mid=2021: sy=-1 -> 3.0, sy=-2 -> 99.0
    ds = xr.Dataset(
        {'precip': (['model_issuance_date', 'start_year', 'lead_time'], da.from_array(data, chunks=shape))},
        coords={
            'model_issuance_date': pd.DatetimeIndex(issuance_dates),
            'start_year': start_years,
            'lead_time': [np.timedelta64(0, 'D'), np.timedelta64(7, 'D')],
        }
    )

    result = reforecast_to_timeseries(ds)

    conflict_time = pd.Timestamp('2019-01-06')
    times = pd.DatetimeIndex(result.init_time.values)
    assert conflict_time in times, "Conflicting init_time should appear exactly once"
    assert (times == conflict_time).sum() == 1, "No duplicate init_times"

    val = float(result.sel(init_time=conflict_time)['precip'].isel(prediction_timedelta=0).compute())
    assert val == 99.0, "Most recent issuance (2021-01-06) should win"


def test_reforecast_to_timeseries_no_duplicate_times():
    """Output never has duplicate time values."""
    issuance_dates = pd.date_range('2020-01-01', periods=10, freq='3D').strftime('%Y-%m-%d')
    ds = _make_reforecast_ds(issuance_dates, list(range(-5, 0)))
    result = reforecast_to_timeseries(ds)
    times = pd.DatetimeIndex(result.init_time.values)
    assert times.nunique() == len(times), "All output times must be unique"


def test_climatology(remote_dask_cluster):  # noqa: ARG001
    """Test that climatolgoy expands properly."""
    start_time = '2016-01-01'
    end_time = '2016-03-30'
    ds = climatology_era5_1985_2015(start_time, end_time, variable='precip', forecast_lead_days=2)
    assert ds.time.max().compute() == pd.to_datetime("2016-03-31")

    ds = climatology_era5_1985_2015(start_time, end_time, variable='precip')
    assert len(ds.prediction_timedelta.values) == 46

