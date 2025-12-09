"""Test lead-based target date fetching."""
import numpy as np

from sheerwater.climatology import climatology_2015, climatology_agg_raw
from sheerwater.forecasts import salient
from sheerwater.forecasts.ecmwf_er import ifs_extended_range
from sheerwater.forecasts.salient import salient_blend
from sheerwater.reanalysis import era5, era5_rolled
from sheerwater.utils import convert_init_time_to_pred_time, shift_by_days, start_remote


def test_target_date_conversion():
    """Test the conversion of target dates to forecast dates."""
    start_remote(remote_config='large_cluster', remote_name='test_metrics')
    start_date = "2020-01-14"
    end_date = "2020-01-31"

    # Week2: shift back by 7 days
    fd_week2_start = shift_by_days(start_date, -7)
    fd_week2_end = shift_by_days(end_date, -7)
    assert fd_week2_start == "2020-01-07"
    assert fd_week2_end == "2020-01-24"

    # Weeks34: shift back by 14 days
    fd_week34_start = shift_by_days(start_date, -14)
    fd_week34_end = shift_by_days(end_date, -14)
    assert fd_week34_start == "2019-12-31"
    assert fd_week34_end == "2020-01-17"

    # Ground truth data is already in "target date" format
    ds = era5(start_date, end_date, "tmp2m", agg_days=7, grid="global1_5", mask=None, region='global')
    dsr = era5_rolled(start_date, end_date, "tmp2m", agg_days=7, grid="global1_5")
    assert ds.equals(dsr)

    # Climatology data is already in "target date" format
    ds = climatology_2015(start_date, end_date, "tmp2m", agg_days=7, grid="global1_5", mask=None, region='global')
    # Select week 2
    ds = ds.sel(prediction_timedelta=np.timedelta64(0, "D"), time="2020-01-14")
    dsr = climatology_agg_raw("tmp2m", 1985, 2014, agg_days=7, grid="global1_5")
    dsr = dsr.sel(dayofyear="1904-01-14")
    # Align coordinates for comparison
    dsr = dsr.rename({"dayofyear": "time"})
    dsr['time'] = ds['time']
    assert ds.equals(dsr)

    # Test forecast conversion
    ds = salient(start_date, end_date, "tmp2m", agg_days=7, grid="global1_5", mask=None, region='global')
    ds = ds.sel(prediction_timedelta=np.timedelta64(7, "D").astype("timedelta64[ns]"), time="2020-01-15")
    # Raw forecast
    dsr = salient_blend(fd_week2_start, fd_week2_end, "tmp2m", "sub-seasonal", grid="global1_5")
    dsr = dsr.sel(lead=2, quantiles=0.5, forecast_date="2020-01-08")
    dsr = dsr.rename({"forecast_date": "time"})
    dsr['time'] = ds['time']
    assert ((ds-dsr).tmp2m.max() < 1e-10)

    # Test forecast conversion using convert_init_time_to_pred_time
    ds = ifs_extended_range(fd_week2_start, fd_week2_end, "tmp2m", "forecast", grid="global1_5")
    # Get specific lead for week 2 (7 days)
    prediction_timedelta_shift = np.timedelta64(7, 'D').astype("timedelta64[ns]")
    ds = ds.sel(lead_time=prediction_timedelta_shift)

    # Calculate expected target times (init_time + prediction_timedelta)
    target_times = ds.start_date.values + ds.lead_time.values

    # Convert from init_time/prediction_timedelta to time using convert_init_time_to_pred_time
    # First rename to match expected dimensions
    ds = ds.rename({'start_date': 'init_time', 'lead_time': 'prediction_timedelta'})
    ds = ds.expand_dims({'prediction_timedelta': [prediction_timedelta_shift]})
    ds = convert_init_time_to_pred_time(ds)

    # Verify that the time coordinate matches the expected target times
    assert (ds.time.values == target_times).all()


if __name__ == "__main__":
    test_target_date_conversion()
