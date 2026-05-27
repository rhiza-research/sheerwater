"""Lightweight tests for event registration and basic event behavior."""
import numpy as np
import pytest
import xarray as xr

from sheerwater.forecasts import graphcast
from sheerwater.climatology import climatology_era5_1985_2015
from sheerwater.interfaces.events import above_threshold, get_event_fn
from sheerwater.metrics import metric
from sheerwater.forecasts import ecmwf_ifs_er_debiased

pytestmark = pytest.mark.default


def test_get_event_fn_lookup_and_unknown():
    """Known events are discoverable and unknown names raise a clear error."""
    assert get_event_fn("above_threshold") is above_threshold
    with pytest.raises(ValueError, match="not found"):
        get_event_fn("not_a_real_event")


def _tiny_precip_ds():
    """Build a tiny precipitation dataset with one NaN to test null handling."""
    time = np.array(["2020-01-01", "2020-01-02", "2020-01-03"], dtype="datetime64[ns]")
    lat = np.array([0.0], dtype=np.float32)
    lon = np.array([0.0], dtype=np.float32)
    data = np.array([[[0.2]], [[0.8]], [[np.nan]]], dtype=np.float32)
    return xr.Dataset(
        {"precip": (("time", "lat", "lon"), data)},
        coords={"time": time, "lat": lat, "lon": lon},
        attrs={"agg_days": 1.0},
    )


def test_above_threshold_sets_event_attr_and_preserves_nan():
    """Threshold event writes event attr and keeps null pattern intact."""
    ds = _tiny_precip_ds()
    out = above_threshold(ds, agg_days=1, threshold=0.5)

    assert out.attrs["event"] == "above_threshold"
    assert out.precip.sel(time="2020-01-01").item() == pytest.approx(0.0)
    assert out.precip.sel(time="2020-01-02").item() == pytest.approx(1.0)
    assert np.isnan(out.precip.sel(time="2020-01-03").item())


def test_mae_zero_at_lead_minus_duration(remote_dask_cluster):  # noqa: ARG001
    """Check that ."""
    start_time = '2022-01-01'
    end_time = '2022-12-31'
    grid = 'global1_5'
    region = 'kenya'
    ds = metric(start_time, end_time, variable='precip',
                forecast='ecmwf_ifs_er_debiased', truth='imerg',
                metric_name='mae',
                spatial=False, grid=grid,
                recompute=True,
                cache_mode='read_only',
                event='icpac_onset',
                region=region)

    assert float(ds.mae.isel(prediction_timedelta=0).values) == 0.0


def test_event_on_forecaster(remote_dask_cluster):  # noqa: ARG001
    """Check that events on the forecaster work."""
    ds = ecmwf_ifs_er_debiased(
        "2022-01-01", "2022-12-31",
        event='chc_onset',
        grid="global1_5",
        mask='lsm',
        region='kenya')

    assert len(ds.prediction_timedelta) == 17  # no lookback was added
    # No lanting suitability outside of 0 to 1
    assert (ds.precip > 1.0).sum().compute() == 0
    assert (ds.precip < 0.0).sum().compute() == 0

    ds = ecmwf_ifs_er_debiased(
        "2022-01-01", "2022-12-31",
        event='chc_onset',
        lookback_source='imerg',
        grid="global1_5",
        mask='lsm',
        region='kenya')

    # Assert the the additional prediction timedelta have been added
    assert len(ds.prediction_timedelta) == 47

    # Check that if we call with agg days it fails
    with pytest.raises(ValueError, match="requires agg_days to be 1."):
        ecmwf_ifs_er_debiased(
            "2022-01-01", "2022-12-31",
            event='chc_onset',
            agg_days=10,
            lookback_source='imerg',
            grid="global1_5",
            mask='lsm',
            region='kenya')

    # Check that if we call without agg days it fails
    with pytest.raises(ValueError, match="agg_days"):
        ecmwf_ifs_er_debiased(
            "2022-01-01", "2022-12-31",
            event='above_threshold',
            lookback_source='imerg',
            event_kwargs={'threshold': 0.5},
            agg_days=10,
            grid="global1_5",
            mask='lsm',
            region='kenya')


def test_start_of_season_by_spells(remote_dask_cluster):  # noqa: ARG001
    """Check that events on the forecaster work."""
    ds = ecmwf_ifs_er_debiased(
        "2022-01-01", "2022-12-31",
        event='chc_onset',
        grid="global1_5",
        mask='lsm',
        region='kenya')

    assert len(ds.prediction_timedelta) == 17  # no lookback was added
    # No lanting suitability outside of 0 to 1
    assert (ds.precip > 1.0).sum().compute() == 0
    assert (ds.precip < 0.0).sum().compute() == 0

    ds = ecmwf_ifs_er_debiased(
        "2022-01-01", "2022-12-31",
        event='chc_onset',
        lookback_source='imerg',
        grid="global1_5",
        mask='lsm',
        region='kenya')

    # Assert the the additional prediction timedelta have been added
    assert len(ds.prediction_timedelta) == 47

    # Check that if we call with agg days it fails
    with pytest.raises(ValueError, match="requires agg_days to be 1."):
        ecmwf_ifs_er_debiased(
            "2022-01-01", "2022-12-31",
            event='chc_onset',
            agg_days=10,
            lookback_source='imerg',
            grid="global1_5",
            mask='lsm',
            region='kenya')

    # Check that if we call without agg days it fails
    with pytest.raises(ValueError, match="agg_days"):
        ecmwf_ifs_er_debiased(
            "2022-01-01", "2022-12-31",
            event='above_threshold',
            lookback_source='imerg',
            event_kwargs={'threshold': 0.5},
            agg_days=10,
            grid="global1_5",
            mask='lsm',
            region='kenya')

    # Test a custom start of season event
    ds = ecmwf_ifs_er_debiased(
        "2022-01-01", "2022-12-31",
        event='dry_wet_not_dry_onset',
        grid="global1_5",
        mask='lsm',
        region='kenya')


def test_event_duration_longer_than_available_leads(remote_dask_cluster):  # noqa: ARG001
    """Graphcast cannot evaluate events whose `duration` is longer than the available leads."""
    event_name = "above_threshold"
    event_kwargs = {"agg_days": 20, "threshold": 1.0}

    # The event itself reports a duration larger than the single available lead.
    with pytest.raises(ValueError, match="requires at least 20 lead days."):
        graphcast(
            start_time="2020-01-01", end_time="2020-01-15",
            variable="precip", agg_days=1, grid="global1_5",
            mask='lsm', region='kenya',
            event=event_name, event_kwargs=event_kwargs,
        )


def test_event_climatology(remote_dask_cluster):  # noqa: ARG001
    """Check that climatology events work as expected with observational blending."""
    event_name = "above_threshold"
    event_kwargs = {"agg_days": 5, "threshold": 1.0}

    ds = climatology_era5_1985_2015(
        start_time="2020-01-01", end_time="2020-01-15",
        variable="precip", agg_days=1, grid="global1_5",
        mask='lsm', region='kenya',
        lookback_source='imerg',
        event=event_name, event_kwargs=event_kwargs,
    )
    # Ensure the event has been run on the climatology dataset
    assert ds.attrs.get("event") == event_name
    slice1 = ds.sel(time='2020-01-10').isel(prediction_timedelta=0)
    slice2 = ds.sel(time='2020-01-10').isel(prediction_timedelta=5)
    slice3 = ds.sel(time='2020-01-10').isel(prediction_timedelta=10)

    # Assert that the first and second slices are not equal, but the second and third are
    # Climatology doesn't vary with lead, so once we're beyond obs blending, they will be equal
    assert not np.array_equal(slice1.precip.values, slice2.precip.values, equal_nan=True)
    assert np.array_equal(slice2.precip.values, slice3.precip.values, equal_nan=True)


def test_ecmwf_event_via_interface_matches_manual_application(remote_dask_cluster):  # noqa: ARG001
    """Applying `above_threshold` via the forecast interface == calling it on the raw output."""
    common_kwargs = dict(
        start_time="2022-01-01", end_time="2022-12-31",
        variable="precip", agg_days=1,
        grid="global1_5", mask="lsm", region="kenya",
    )

    # Raw forecast, then apply the event manually. agg_days=1 makes the rolling step a
    # per-cell identity, so axis choice (valid time vs. lead time) does not affect values.
    raw = ecmwf_ifs_er_debiased(**common_kwargs)
    manual = above_threshold(raw, agg_days=1, threshold=1.0)

    via_interface = ecmwf_ifs_er_debiased(
        **common_kwargs,
        event="above_threshold",
        event_kwargs={"agg_days": 1, "threshold": 1.0},
    )

    assert manual.equals(via_interface)

    # The interface must stamp the event / post_processed attrs so downstream
    # `post_process` calls know not to re-run the event or processor steps.
    assert via_interface.attrs.get("event") == "above_threshold"
    assert 'post_processed' not in via_interface.attrs

    # Same call but with a processor configured: post_processed must flip to True.
    with_proc = ecmwf_ifs_er_debiased(
        **common_kwargs,
        event="above_threshold",
        event_kwargs={"agg_days": 1, "threshold": 1.0},
        processors=["regrid"],
        processor_kwargs=[{"target_grid": "global1_5"}],
    )
    assert with_proc.attrs.get("event") == "above_threshold"
    assert with_proc.attrs.get("post_processed") is True
