"""Lightweight tests for event registration and basic event behavior."""
import numpy as np
import pytest
import xarray as xr

from sheerwater.interfaces.events import above_threshold, get_event_fn, planting_suitability
from sheerwater.metrics import metric

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
    out = above_threshold(agg_days=1, threshold=0.5)(ds)

    assert out.attrs["event"] == "above_threshold"
    assert out.precip.sel(time="2020-01-01").item() == pytest.approx(0.0)
    assert out.precip.sel(time="2020-01-02").item() == pytest.approx(1.0)
    assert np.isnan(out.precip.sel(time="2020-01-03").item())


def test_planting_suitability_rejects_non_precip_variable():
    """Event constrained to precip raises when dataset has no valid variables."""
    ds = _tiny_precip_ds().drop_vars("precip")
    ds["tmp2m"] = (("time", "lat", "lon"), np.ones((3, 1, 1), dtype=np.float32))

    with pytest.raises(ValueError, match="not valid"):
        planting_suitability()(ds)


def test_mae_zero_at_lead_minus_duration(remote_dask_cluster):  # noqa: ARG001
    """dummy_count_ones has duration 3; metric mae is zero at lead -3."""
    start_time = '2016-01-01'
    end_time = '2022-12-31'
    grid = 'global1_5'
    region = 'kenya'
    ds = metric(start_time, end_time, variable='precip',
                forecast='ecmwf_ifs_er_debiased', truth='imerg',
                metric_name='mae',
                spatial=False, grid=grid,
                recompute=True,
                event='planting_suitability',
                event_kwargs={'wet_spell_threshold': 38.0, 'dry_spell_threshold': 10.0,
                              'wet_spell_agg_days': 10, 'dry_spell_agg_days': 20},
                region=region)

    assert float(ds.mae.isel(prediction_timedelta=0).values) == 0.0
