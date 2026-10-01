"""Every advanced-metric experiment must resolve to a registered metric."""
import pytest

from sheerwater.advanced_metrics import get_experiment_kwargs
from sheerwater.metrics_library import SHEERWATER_METRIC_REGISTRY

pytestmark = pytest.mark.default

EXPERIMENTS = [
    "early_season_accumulation-30d",
    "mid_season_accumulation_by_percent-14d",
    "late_season_accumulation-30d-thresh-30",
    "in_season_dry_spell",
    "big_rain_days",
    "extreme_rain_days",
    "rain_days_soft",
    "dry_spells",
    "dry_spells_soft",
]


@pytest.mark.parametrize("experiment", EXPERIMENTS)
def test_experiment_metric_is_registered(experiment):
    """The experiment's metric name is in the registry, so metric_factory can build it."""
    metric_name = get_experiment_kwargs(experiment, "eastern_africa")[0]
    assert metric_name.lower() in SHEERWATER_METRIC_REGISTRY
