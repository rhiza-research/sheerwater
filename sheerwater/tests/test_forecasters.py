"""Test forecasters functionality and interfaces."""
import numpy as np

import pandas as pd
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

def test_climatology(remote_dask_cluster):  # noqa: ARG001
    """Test that climatolgoy expands properly."""
    start_time = '2016-01-01'
    end_time = '2016-03-30'
    ds = climatology_era5_1985_2015(start_time, end_time, variable='precip', forecast_lead_days=2)
    assert ds.time.max().compute() == pd.to_datetime("2016-03-31")

    ds = climatology_era5_1985_2015(start_time, end_time, variable='precip')
    assert len(ds.prediction_timedelta.values) == 46

