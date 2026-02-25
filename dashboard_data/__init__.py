"""Dashboard data for the Sheerwater Benchmarking project."""
from .metrics_tables import (weekly_metric_table, monthly_metric_table,
                             ground_truth_metric_table, biweekly_metric_table)

from .coverage_tables import coverage_table

from nuthatch import config_parameter
from google.cloud import secretmanager

# Add the postgres write password to the config parameter, so that this code
# module can read and write to our postgres database.


@config_parameter('password', location='root', backend='sql', secret=True)
def postgres_write_password():
    """Get a postgres write password."""
    client = secretmanager.SecretManagerServiceClient()

    response = client.access_secret_version(
        request={"name": "projects/750045969992/secrets/postgres-write-password/versions/latest"})
    key = response.payload.data.decode("UTF-8")

    return key


__all__ = ['weekly_metric_table', 'monthly_metric_table',
           'ground_truth_metric_table', 'biweekly_metric_table', 'coverage_table']
