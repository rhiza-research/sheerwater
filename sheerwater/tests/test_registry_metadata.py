"""Test the metadata system for forecasts, data sources, and metrics."""
import pytest

from sheerwater.interfaces import list_forecasts, list_data
from sheerwater.metrics_library import list_metrics, SHEERWATER_METRIC_REGISTRY


class TestListForecasts:
    """Tests for the list_forecasts function."""

    def test_list_forecasts_returns_list(self):
        """Test that list_forecasts returns a list."""
        forecasts = list_forecasts()
        assert isinstance(forecasts, list)

    def test_list_forecasts_returns_dicts(self):
        """Test that list_forecasts returns a list of dictionaries."""
        forecasts = list_forecasts()
        assert len(forecasts) > 0
        for forecast in forecasts:
            assert isinstance(forecast, dict)

    def test_list_forecasts_contains_name(self):
        """Test that each forecast dict contains a 'name' key."""
        forecasts = list_forecasts()
        for forecast in forecasts:
            assert 'name' in forecast
            assert isinstance(forecast['name'], str)

    def test_list_forecasts_known_forecasts_present(self):
        """Test that known forecasts are present in the registry."""
        forecasts = list_forecasts()
        names = [f['name'] for f in forecasts]

        # These should be registered based on our metadata additions
        expected_forecasts = ['ecmwf_ifs_er', 'ecmwf_ifs_er_debiased', 'fuxi',
                              'graphcast', 'gencast', 'salient', 'salient_gem']
        for expected in expected_forecasts:
            assert expected in names, f"Expected forecast '{expected}' not found in registry"

    def test_list_forecasts_has_metadata(self):
        """Test that ALL forecasts have complete metadata fields."""
        forecasts = list_forecasts()

        for forecast in forecasts:
            name = forecast['name']
            # Every forecast must have description
            assert 'description' in forecast, f"Forecast '{name}' missing 'description'"
            assert not forecast['description'].startswith('Forecast model:'), \
                f"Forecast '{name}' has generic description - needs real metadata"

            # Every forecast must have variables
            assert 'variables' in forecast, f"Forecast '{name}' missing 'variables'"
            assert len(forecast['variables']) > 0, f"Forecast '{name}' has empty variables list"

            # Every forecast must have type
            assert 'type' in forecast, f"Forecast '{name}' missing 'type'"
            valid_types = ['deterministic', 'ensemble', 'probabilistic']
            assert forecast['type'] in valid_types, \
                f"Forecast '{name}' has invalid type '{forecast['type']}' - must be one of {valid_types}"


class TestListData:
    """Tests for the list_data function."""

    def test_list_data_returns_list(self):
        """Test that list_data returns a list."""
        data_sources = list_data()
        assert isinstance(data_sources, list)

    def test_list_data_returns_dicts(self):
        """Test that list_data returns a list of dictionaries."""
        data_sources = list_data()
        assert len(data_sources) > 0
        for ds in data_sources:
            assert isinstance(ds, dict)

    def test_list_data_contains_name(self):
        """Test that each data source dict contains a 'name' key."""
        data_sources = list_data()
        for ds in data_sources:
            assert 'name' in ds
            assert isinstance(ds['name'], str)

    def test_list_data_known_sources_present(self):
        """Test that known data sources are present in the registry."""
        data_sources = list_data()
        names = [d['name'] for d in data_sources]

        # These should be registered based on our metadata additions
        expected_sources = ['chirps', 'imerg_final', 'ghcn', 'tahmo']
        for expected in expected_sources:
            assert expected in names, f"Expected data source '{expected}' not found in registry"

    def test_list_data_has_metadata(self):
        """Test that ALL data sources have complete metadata fields."""
        data_sources = list_data()

        for ds in data_sources:
            name = ds['name']
            # Every data source must have description
            assert 'description' in ds, f"Data source '{name}' missing 'description'"
            assert not ds['description'].startswith('Data source:'), \
                f"Data source '{name}' has generic description - needs real metadata"

            # Every data source must have variables
            assert 'variables' in ds, f"Data source '{name}' missing 'variables'"
            assert len(ds['variables']) > 0, f"Data source '{name}' has empty variables list"

            # Every data source must have coverage
            assert 'coverage' in ds, f"Data source '{name}' missing 'coverage'"
            assert ds['coverage'] != 'See documentation', \
                f"Data source '{name}' has placeholder coverage - needs real metadata"

            # Every data source must have type
            assert 'type' in ds, f"Data source '{name}' missing 'type'"
            valid_types = ['gridded', 'station', 'reanalysis']
            assert ds['type'] in valid_types, \
                f"Data source '{name}' has invalid type '{ds['type']}' - must be one of {valid_types}"


class TestListMetrics:
    """Tests for the list_metrics function."""

    def test_list_metrics_returns_list(self):
        """Test that list_metrics returns a list."""
        metrics = list_metrics()
        assert isinstance(metrics, list)

    def test_list_metrics_returns_dicts(self):
        """Test that list_metrics returns a list of dictionaries."""
        metrics = list_metrics()
        assert len(metrics) > 0
        for metric in metrics:
            assert isinstance(metric, dict)

    def test_list_metrics_contains_name(self):
        """Test that each metric dict contains a 'name' key."""
        metrics = list_metrics()
        for metric in metrics:
            assert 'name' in metric
            assert isinstance(metric['name'], str)

    def test_list_metrics_known_metrics_present(self):
        """Test that known metrics are present in the registry."""
        metrics = list_metrics()
        names = [m['name'] for m in metrics]

        # These should be registered
        expected_metrics = ['mae', 'mse', 'rmse', 'bias', 'crps', 'brier',
                            'seeps', 'acc', 'pearson', 'heidke', 'pod', 'far',
                            'ets', 'csi', 'frequencybias']
        for expected in expected_metrics:
            assert expected in names, f"Expected metric '{expected}' not found in registry"

    def test_list_metrics_has_metadata(self):
        """Test that metrics have expected metadata fields."""
        metrics = list_metrics()
        metrics_by_name = {m['name']: m for m in metrics}

        # MAE should have all metadata fields
        if 'mae' in metrics_by_name:
            mae = metrics_by_name['mae']
            assert 'full_name' in mae
            assert 'description' in mae
            assert 'direction' in mae
            assert mae['direction'] == 'lower_is_better'

        # SEEPS should have correct name
        if 'seeps' in metrics_by_name:
            seeps = metrics_by_name['seeps']
            assert 'full_name' in seeps
            assert 'Stable Equitable Error' in seeps['full_name']

    def test_list_metrics_has_category_fields(self):
        """Test that all metrics have prob_type and categorical fields."""
        metrics = list_metrics()
        valid_prob_types = ['deterministic', 'probabilistic']

        for metric in metrics:
            name = metric['name']
            # Every metric must have prob_type
            assert 'prob_type' in metric, f"Metric '{name}' missing 'prob_type'"
            assert metric['prob_type'] in valid_prob_types, \
                f"Metric '{name}' has invalid prob_type '{metric['prob_type']}'"
            # Every metric must have categorical
            assert 'categorical' in metric, f"Metric '{name}' missing 'categorical'"
            assert isinstance(metric['categorical'], bool), \
                f"Metric '{name}' categorical must be bool, got {type(metric['categorical'])}"

    def test_specific_metric_categories(self):
        """Test that specific metrics have correct category values."""
        metrics = list_metrics()
        metrics_by_name = {m['name']: m for m in metrics}

        # CRPS is probabilistic, not categorical
        if 'crps' in metrics_by_name:
            assert metrics_by_name['crps']['prob_type'] == 'probabilistic'
            assert metrics_by_name['crps']['categorical'] is False

        # Brier is probabilistic and categorical (binary events)
        if 'brier' in metrics_by_name:
            assert metrics_by_name['brier']['prob_type'] == 'probabilistic'
            assert metrics_by_name['brier']['categorical'] is True

        # MAE is deterministic, not categorical
        if 'mae' in metrics_by_name:
            assert metrics_by_name['mae']['prob_type'] == 'deterministic'
            assert metrics_by_name['mae']['categorical'] is False

        # Heidke is deterministic but categorical
        if 'heidke' in metrics_by_name:
            assert metrics_by_name['heidke']['prob_type'] == 'deterministic'
            assert metrics_by_name['heidke']['categorical'] is True


class TestMetricClassAttributes:
    """Tests for metric class metadata attributes."""

    def test_metric_classes_have_metadata_attributes(self):
        """Test that metric classes define metadata class attributes."""
        required_attrs = ['full_name', 'description', 'direction']

        for name, cls in SHEERWATER_METRIC_REGISTRY.items():
            for attr in required_attrs:
                value = getattr(cls, attr, None)
                assert value is not None, f"Metric '{name}' missing required attribute '{attr}'"

    def test_metric_direction_values(self):
        """Test that metric direction values are valid."""
        valid_directions = ['lower_is_better', 'higher_is_better', 'closer_to_zero', 'closer_to_one']

        for name, cls in SHEERWATER_METRIC_REGISTRY.items():
            direction = getattr(cls, 'direction', None)
            if direction is not None:
                assert direction in valid_directions, \
                    f"Metric '{name}' has invalid direction '{direction}'"


class TestForecastMetadataAttribute:
    """Tests for the _metadata attribute on decorated functions."""

    def test_forecast_functions_have_metadata_attr(self):
        """Test that forecast functions have _metadata attribute."""
        from sheerwater.interfaces import FORECAST_REGISTRY

        # Import forecasts to populate registry
        import sheerwater.forecasts  # noqa: F401

        # Check that registered functions have _metadata
        forecasts_with_rich_metadata = ['ecmwf_ifs_er', 'ecmwf_ifs_er_debiased',
                                        'fuxi', 'graphcast', 'gencast',
                                        'salient', 'salient_gem']

        for name in forecasts_with_rich_metadata:
            if name in FORECAST_REGISTRY:
                func = FORECAST_REGISTRY[name]
                assert hasattr(func, '_metadata'), f"Forecast '{name}' missing _metadata attribute"


class TestDataMetadataAttribute:
    """Tests for the _metadata attribute on decorated data functions."""

    def test_data_functions_have_metadata_attr(self):
        """Test that data functions have _metadata attribute."""
        from sheerwater.interfaces import DATA_REGISTRY

        # Import data modules to populate registry
        import sheerwater.data  # noqa: F401

        # Check that registered functions have _metadata
        data_with_rich_metadata = ['chirps', 'imerg_final', 'ghcn', 'tahmo']

        for name in data_with_rich_metadata:
            if name in DATA_REGISTRY:
                func = DATA_REGISTRY[name]
                assert hasattr(func, '_metadata'), f"Data source '{name}' missing _metadata attribute"
