"""Lightweight tests for event registration and basic event behavior."""
import pytest
import xarray as xr

from sheerwater.interfaces.processors import get_processor_fn, regrid, processor
from sheerwater.forecasts import ecmwf_ifs_er, ecmwf_ifs_er_debiased
from sheerwater.reanalysis import era5

pytestmark = pytest.mark.default


def test_get_processor_fn_lookup_and_unknown():
    """Known events are discoverable and unknown names raise a clear error."""
    assert get_processor_fn("regrid") is regrid
    with pytest.raises(ValueError, match="not found"):
        get_processor_fn("not_a_real_processor")


@processor()
def return_diff_forecast(ds, **kwargs):  # noqa: ARG001
    """A simple processor for testing."""
    return ecmwf_ifs_er("2021-01-01", "2021-01-05")


def test_basic_processor(remote_dask_cluster):  # noqa: ARG001
    """Make sure the processor runs."""
    ds = ecmwf_ifs_er_debiased("2021-01-01", "2021-01-05", agg_days=1, processors=['return_diff_forecast'])
    ds2 = ecmwf_ifs_er("2021-01-01", "2021-01-05")

    xr.testing.assert_equal(ds.drop_attrs(), ds2.drop_attrs())


def test_qqmap_processor(remote_dask_cluster):  # noqa: ARG001
    """Make sure the processor runs."""
    ds = era5("2021-01-01", "2021-01-05", agg_days=1, grid='global1_5',
              processors=['qqmap'],
              processor_kwargs={
                  'target': "imerg",
                  'target_grid': 'global0_1',
                  'target_region': 'africa',
                                   'time_grouping': 'month_of_year'
              })
    assert ds.attrs['grid'] == 'global0_1'
