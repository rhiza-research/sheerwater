"""Test the metrics library functions."""
import pytest

from sheerwater.metrics_library import metric_factory


@pytest.mark.remote
def test_metric_factory(dask_cluster):
    """Test the metric factory function."""
    cache_kwargs = {
        'start_time': '2016-01-01',
        'end_time': '2022-12-31',
        'variable': 'precip',
        'agg_days': 7,
        'forecast': 'ecmwf_ifs_er_debiased',
        'truth': 'era5',
        'time_grouping': 'month',
        'spatial': False,
        'grid': 'global1_5',
        'mask': 'lsm',
        'region': 'country',
    }

    met = metric_factory('heidke-1-5-10-20', **cache_kwargs)
    test = met.compute()
    assert test is not None


if __name__ == "__main__":
    from sheerwater.utils import start_remote
    start_remote(remote_config='large_cluster', remote_name='test_metrics')
    test_metric_factory(None)
