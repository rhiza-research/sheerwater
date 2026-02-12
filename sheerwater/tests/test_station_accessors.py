"""Tests that station accessors respect aggregation days."""
import numpy as np
import pytest

from sheerwater.data import ghcn, ghcn_avg, tahmo, tahmo_avg, knust, knust_avg, stations


STATION_ACCESSORS = [
    ("ghcn", ghcn),
    ("ghcn_avg", ghcn_avg),
    ("tahmo", tahmo),
    ("tahmo_avg", tahmo_avg),
    ("knust", knust),
    ("knust_avg", knust_avg),
    ("stations", stations),
]


@pytest.mark.parametrize("name,fn", STATION_ACCESSORS)
def test_station_accessors_roll_with_agg_days(name, fn):
    """Larger agg_days should not increase the number of time steps, and 7‑day value matches 1‑day sum."""
    start = "2010-01-01"
    end = "2010-12-31"

    # 1‑day and 7‑day aggregations
    ds_1 = fn(start, end, agg_days=1)
    ds_7 = fn(start, end, agg_days=7)

    assert "time" in ds_1.dims
    assert "time" in ds_7.dims
    assert ds_7.sizes["time"] <= ds_1.sizes["time"]

    # Pick a time point in the 7‑day dataset and find a non‑null lat/lon there.
    var = "precip"
    t = ds_7.time.isel(time=0).values
    slice_2d = ds_7[var].isel(time=0).load().values  # load so not dask for argwhere
    idx = np.argwhere(~np.isnan(slice_2d))
    if idx.size == 0:
        pytest.skip(f"{name}: no non‑NaN values at first 7‑day time step")
    i_lat, i_lon = idx[0]
    lat = ds_7.lat.isel(lat=i_lat).values
    lon = ds_7.lon.isel(lon=i_lon).values
    val_7 = float(ds_7[var].isel(time=0, lat=i_lat, lon=i_lon).load().item())

    window_end = t + np.timedelta64(6, "D")
    window = ds_1[var].sel(time=slice(t, window_end), lat=lat, lon=lon)
    manual_sum = float(window.sum().load().item())

    # 7‑day value is a mean, so 7 * mean == sum of 7 daily values.
    assert pytest.approx(manual_sum, rel=1e-5) == val_7 * 7


def test_metric_stations_vs_tahmo():
    """Compute a metric (MAE) with stations as forecast and tahmo as truth."""
    from sheerwater.metrics import metric

    result = metric(
        start_time="2016-01-01",
        end_time="2016-01-31",
        variable="precip",
        agg_days=7,
        forecast="imerg",
        truth="stations",
        metric_name="mae",
        grid="global1_5",
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
