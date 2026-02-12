"""Tests that station accessors respect aggregation days."""
import numpy as np
import pytest

from sheerwater.data import ghcn, ghcn_avg, tahmo, tahmo_avg, knust, knust_avg, stations


STATION_ACCESSORS = [
    ("knust", knust),
    ("knust_avg", knust_avg),
    ("tahmo", tahmo),
    ("tahmo_avg", tahmo_avg),
    ("ghcn", ghcn),
    ("ghcn_avg", ghcn_avg),
    ("stations", stations),
]


@pytest.mark.parametrize("name,fn", STATION_ACCESSORS)
def test_station_accessors_roll_with_agg_days(name, fn):
    """Larger agg_days should not increase the number of time steps, and 7‑day value matches 1‑day sum."""
    start = "2020-08-01"
    end = "2020-09-30"

    # 1‑day and 7‑day aggregations
    ds_1 = fn(start, end, agg_days=1)
    ds_7 = fn(start, end, agg_days=7)
    import pdb; pdb.set_trace()

    assert "time" in ds_1.dims
    assert "time" in ds_7.dims
    assert ds_7.sizes["time"] <= ds_1.sizes["time"]

    # Use a known point with data: lat 6.75, lon -1.5 at 2020-06-21
    var = "precip"
    lat, lon = 6.75, -1.5
    t = np.datetime64("2020-08-28")
    val_7 = float(ds_7[var].sel(time=t, lat=lat, lon=lon).values)
    if np.isnan(val_7):
        pytest.skip(f"{name}: no value at {t}, {lat}, {lon}")

    window_end = t + np.timedelta64(6, "D")
    manual_mean = float(ds_1[var].sel(time=slice(t, window_end), lat=lat, lon=lon).mean().values)

    # 7‑day value is a mean, so 7 * mean == sum of 7 daily values.
    assert pytest.approx(manual_mean, rel=1e-4) == val_7


def test_metric_stations_vs_tahmo():
    """Compute a metric (MAE) with stations and tahmo as truth."""
    from sheerwater.metrics import metric

    result = metric(
        start_time="2016-01-01",
        end_time="2016-01-31",
        variable="precip",
        agg_days=7,
        forecast="imerg",
        truth="stations",
        metric_name="mae",
        grid="global0_25",
    )
    assert "mae" in result
    assert result["mae"].size >= 1

    result = metric(
        start_time="2016-01-01",
        end_time="2016-01-31",
        variable="precip",
        agg_days=7,
        forecast="tahmo_avg",
        truth="stations",
        metric_name="mae",
        grid="global1_5",
    )
    assert "mae" in result
    assert result["mae"].size >= 1
