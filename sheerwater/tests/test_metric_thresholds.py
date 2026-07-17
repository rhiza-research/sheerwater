"""Integration tests for separate forecast/observation thresholds in contingency metrics.

Each test calls ``metric()`` with a different way of specifying the
forecast/observation thresholds. When the thresholds are equivalent, all
invocations should produce the same result.
"""
import numpy as np
import pytest

from sheerwater.metrics import metric

pytestmark = pytest.mark.default

START_TIME = "2022-01-01"
END_TIME = "2022-12-31"
GRID = "global1_5"
REGION = "kenya"


def test_threshold_in_metric_name(remote_dask_cluster):  # noqa: ARG001
    """``pod-5`` puts the threshold in the metric name."""
    ds = metric(START_TIME, END_TIME, variable="precip",
                forecast="ecmwf_ifs_er_debiased", truth="imerg",
                metric_name="pod-5",
                event="above_threshold",
                agg_days=1, spatial=False, grid=GRID, region=REGION,
                cache_mode="read_only", recompute=['metric', 'metric_with_event_count'])
    assert "pod" in ds
    assert not np.isnan(ds.pod.values).all()


def test_threshold_in_shared_event_kwargs(remote_dask_cluster):  # noqa: ARG001
    """A single ``event_kwargs`` is broadcast to both forecast and observation."""
    ds = metric(START_TIME, END_TIME, variable="precip",
                forecast="ecmwf_ifs_er_debiased", truth="imerg",
                metric_name="pod",
                event="above_threshold",
                event_kwargs={"threshold": 5.0},
                agg_days=1, spatial=False, grid=GRID, region=REGION,
                cache_mode="read_only", recompute=['metric', 'metric_with_event_count'])
    assert "pod" in ds
    assert not np.isnan(ds.pod.values).all()


def test_threshold_in_separate_fcst_obs_kwargs(remote_dask_cluster):  # noqa: ARG001
    """Separate ``event_kwargs`` work too."""
    ds = metric(START_TIME, END_TIME, variable="precip",
                forecast="ecmwf_ifs_er_debiased", truth="imerg",
                metric_name="pod",
                event="above_threshold",
                event_kwargs={"fcst": {"threshold": 5.0}, "obs": {"threshold": 5.0}},
                agg_days=1, spatial=False, grid=GRID, region=REGION,
                cache_mode="read_only", recompute=['metric', 'metric_with_event_count'])
    assert "pod" in ds
    assert not np.isnan(ds.pod.values).all()


def test_three_invocations_match(remote_dask_cluster):  # noqa: ARG001
    """All three ways of specifying threshold=5 should yield the same metric values."""
    ds_name = metric(START_TIME, END_TIME, variable="precip",
                     forecast="ecmwf_ifs_er_debiased", truth="imerg",
                     metric_name="pod-5",
                     event="above_threshold",
                     agg_days=1, spatial=False, grid=GRID, region=REGION,
                     cache_mode="read_only", recompute=['metric', 'metric_with_event_count'])

    ds_shared = metric(START_TIME, END_TIME, variable="precip",
                       forecast="ecmwf_ifs_er_debiased", truth="imerg",
                       metric_name="pod",
                       event="above_threshold",
                       event_kwargs={"threshold": 5.0},
                       agg_days=1, spatial=False, grid=GRID, region=REGION,
                       cache_mode="read_only", recompute=['metric', 'metric_with_event_count'])

    ds_split = metric(START_TIME, END_TIME, variable="precip",
                      forecast="ecmwf_ifs_er_debiased", truth="imerg",
                      metric_name="pod",
                      event="above_threshold",
                      event_kwargs={"fcst": {"threshold": 5.0}, "obs": {"threshold": 5.0}},
                      agg_days=1, spatial=False, grid=GRID, region=REGION,
                      cache_mode="read_only", recompute=['metric', 'metric_with_event_count'])

    np.testing.assert_allclose(ds_name.pod.values, ds_shared.pod.values, equal_nan=True)
    np.testing.assert_allclose(ds_name.pod.values, ds_split.pod.values, equal_nan=True)


def test_asymmetric_thresholds_via_name_and_kwargs_match(remote_dask_cluster):  # noqa: ARG001
    """``pod-1-5`` (obs=1, fcst=5) should match the equivalent split-kwargs form."""
    ds_name = metric(START_TIME, END_TIME, variable="precip",
                     forecast="ecmwf_ifs_er_debiased", truth="imerg",
                     metric_name="pod-1-5",
                     event="above_threshold",
                     agg_days=1, spatial=False, grid=GRID, region=REGION,
                     cache_mode="read_only", recompute=['metric', 'metric_with_event_count'])

    ds_split = metric(START_TIME, END_TIME, variable="precip",
                      forecast="ecmwf_ifs_er_debiased", truth="imerg",
                      metric_name="pod",
                      event="above_threshold",
                      event_kwargs={"fcst": {"threshold": 5.0}, "obs": {"threshold": 1.0}},
                      agg_days=1, spatial=False, grid=GRID, region=REGION,
                      cache_mode="read_only", recompute=['metric', 'metric_with_event_count'])

    np.testing.assert_allclose(ds_name.pod.values, ds_split.pod.values, equal_nan=True)


def test_mismatched_threshold_in_name_and_kwargs_raises(remote_dask_cluster):  # noqa: ARG001
    """Disagreement between the key thresholds and the explicit kwargs is an error."""
    with pytest.raises(ValueError, match="threshold passed does not match the threshold specified in the key."):
        metric(START_TIME, END_TIME, variable="precip",
               forecast="ecmwf_ifs_er_debiased", truth="imerg",
               metric_name="pod-1-5",
               event="above_threshold",
               event_kwargs={"fcst": {"threshold": 99.0}, "obs": {"threshold": 1.0}},
               agg_days=1, spatial=False, grid=GRID, region=REGION,
               cache_mode="read_only", recompute=['metric', 'metric_with_event_count'])
