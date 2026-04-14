"""Test forecasters functionality and interfaces."""
import numpy as np

from sheerwater.forecasts import ecmwf_ifs_er_debiased
from sheerwater.utils import desnify_fcst, convert_pred_time_to_init_time


def test_desnify_fcst(remote_dask_cluster):  # noqa: ARG001
    """Test that the desnify_fcst function works."""
    start_time = '2016-01-01'
    end_time = '2016-03-30'
    ds = ecmwf_ifs_er_debiased(start_time=start_time, end_time=end_time,
                               grid='global1_5', mask='lsm', region='kenya')
    ds = convert_pred_time_to_init_time(ds)
    ds_dense = desnify_fcst(ds, start_time=start_time, end_time=end_time)

    # The forecast is filled from the previous forecast for this init time
    ds1 = ds.sel(init_time="2016-01-04", prediction_timedelta=np.timedelta64(2, 'D'))
    ds2 = ds_dense.sel(init_time="2016-01-06", prediction_timedelta=np.timedelta64(0, 'D'))
    assert (ds2 - ds1).precip.max() < 1e-10

    # The forecast is filled forward from it's last value for the same init time
    ds3 = ds_dense.sel(init_time="2016-01-06").isel(prediction_timedelta=-1)
    ds4 = ds_dense.sel(init_time="2016-01-06").isel(prediction_timedelta=-3)
    assert (ds3 - ds4).precip.max() < 1e-10
    import pdb
    pdb.set_trace()
