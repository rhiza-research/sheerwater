"""Lightweight tests for event registration and basic event behavior."""
import pytest
import xarray as xr

from sheerwater.forecasts import ecmwf_ifs_er
from sheerwater.data import chirps, ghcn
from sheerwater.utils import roll_and_agg, convert_pred_time_to_init_time, convert_init_time_to_pred_time

pytestmark = pytest.mark.default


def test_forecast_roll(remote_dask_cluster): # noqa: ARG001
    """Test rolling forecast across prediction timedelta."""
    ds = ecmwf_ifs_er("2021-01-01", "2021-01-30", agg_days=7)
    ds2 = ecmwf_ifs_er("2021-01-01", "2021-01-30", agg_days=1)
    ds2 = convert_pred_time_to_init_time(ds2)
    ds2 = roll_and_agg(ds2, 7, agg_col='prediction_timedelta')
    ds2 = convert_init_time_to_pred_time(ds2)
    # Conversions back and forth leave a bunch of null times
    ds2 = ds2.dropna(dim='time', how='all')

    xr.testing.assert_equal(ds, ds2)

def test_data_roll(remote_dask_cluster): # noqa: ARG001
    """Test rolling data across time."""
    ds = chirps("2021-01-01", "2021-01-30", agg_days=7)

    # We automatically do an end time shift in the decorator
    ds2 = chirps("2021-01-01", "2021-02-10", agg_days=1)
    ds2 = roll_and_agg(ds2, 7, agg_col='time')
    ds2 = ds2.sel(time=slice("2021-01-01", "2021-01-30"))

    xr.testing.assert_equal(ds, ds2)

def test_ghcn_roll(remote_dask_cluster): #noqa: ARG001
    """Test rolling with a missing thresh."""
    # should having missing thresh of 0.9 so 9/10 days
    ds = ghcn("2021-01-01", "2021-01-30", agg_days=10)

    # We automatically do an end time shift in the decorator
    ds2 = ghcn("2021-01-01", "2021-02-08", agg_days=1)
    ds2 = roll_and_agg(ds2, 10, agg_col='time')

    assert not ds.equals(ds2)

    # We automatically do an end time shift in the decorator
    ds2 = ghcn("2021-01-01", "2021-02-08", agg_days=1)
    ds2 = roll_and_agg(ds2, 10, agg_col='time', agg_thresh=9)
    xr.testing.assert_equal(ds.drop_attrs(), ds2.drop_attrs())
