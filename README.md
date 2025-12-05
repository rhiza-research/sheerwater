# Sheerwater

A forecast and weather data benchmarking library. The sheerwater project is working to benchmark
ML- and physics-based weather and climate forecasts regionally and around the globe with a focus
on model performance on the African continent.

It contains a set of data accessors to fetch common forecasts and ground-truth data sources and
a library of metrics and an interface to evaluate those forecasts.

## Getting started

To run this code you need read access to sheerwater forecasts and ground truth data. Please request access from Rhiza
if you would like to execute this code. Once you have access, you can read data and run metrics by importing
sheerwater and running your code.

1) Install sheerwater in your environment:

```console
pip install sheerwater
```

2) Install Google Cloud CLI and log in:
```console
curl https://sdk.cloud.google.com | bash
gcloud auth application-default login
```

3) Use sheerwater to access forecasts or data:
```py
from sheerwater.forecasts import fuxi
from sheerwater.data import ghcn
from sheerwater.metrics import grouped_metric

# Get the fuxi forecast as an xarray
ds_fuxi = fuxi("2020-01-01", "2022-01-01", lead="week2", variable="precip", grid="global1_5",)

# Get gridded GHCN data
ds_ghcn = ghcn("2020-01-01", "2022-01-01", agg_days=7, variable="precip", grid="global0_25")

# Fetch an evaluation metric - note, already computed metrics are defined from 2016-01-01 to 2022-12-31
# Computing new metrics can be computationally intensive
metric = grouped_metric("2016-01-01", "2022-12-31", forecast="fuxi", truth="era5", variable="precip", metric_name="mae", region="country", grid="global1_5")
print(metric)
```

## Evaluating your own forecasts against your own data

If you have a forecast you would like to evaluate, you can tag it in the sheerwater forecast decorator so that sheerwater
can find it for evaluation.

```py

from sheerwater.forecasts import forecast
from sheerwater.data import data
from sheerwater.metrics import metric

# Forecasts must be xarrays with coordinates for lat, lon, init_time, and prediction_timedelta with a matching variable
# on the correct grid
@forecast
def my_forecast(start_time, end_time, agg_days, variable, grid, **kwargs):
    fetch_forecast(start_time, end_time, agg_days, variable, grid)

# Data must be xarrays with coordinates for lat, lon, and time with a matching variable on the correct grid
@data
def my_station_data(start_time, end_time, agg_days, variable, grid, **kwargs):
    fetch_data(start_time, end_time, agg_days, variable, grid)

# Evaluate the forecast
metric("2015-01-01", "2022-01-01", forecast="my_forecast", truth="my_station_data", agg_days=1, variable='precip', grid='global1_5', metric_name="bias", region="country", time_grouping="month_of_year")
```

To support data fetching, sheerwater depends on [Nuthatch](https://github.com/rhiza-research/nuthatch/blob/main/README.md).

## Developing on sheerwater

1) Install UV

```console
curl -Ls https://astral.sh/uv/install.sh | sh
```

2) Install Google Cloud CLI and log in:
```console
curl https://sdk.cloud.google.com | bash
gcloud auth application-default login
```

3) Install non-Python dependencies:
```console
brew install hdf5 netcdf
```

4) Install Python dependencies:
```console
uv sync
```

5) Run commands with UV:
```console
uv run python ...
```
or
```console
uv run jupyter lab
```

## Deployment and Infrastructure

This repository is integrated with the Rhiza infrastructure for deployments:

### Pull Request Ephemeral Environments

Pull requests labeled with `PR-env` will automatically trigger ephemeral Grafana deployments via ArgoCD ApplicationSets. This allows testing of dashboard changes and configurations before merging.

To enable ephemeral deployment for your PR:
```bash
# Add the PR-env label using GitHub CLI
gh pr edit <PR_NUMBER> --add-label "PR-env"

# Or add the label via GitHub web interface
```

The ephemeral Grafana environment will be accessible at:
- `https://dev.shared.rhizaresearch.org/sheerwater-benchmarking/<PR_NUMBER>`

### Infrastructure Components

The `infrastructure/` directory contains:
- **terraform-config/** - Terraform configurations for Grafana instances (organizations, datasources, dashboards, etc.)
- **terraform-database/** - Database configuration module (imported by the main infrastructure repo)

### Database Configuration

Database access and configuration is managed centrally through the infrastructure repository. The `infrastructure/terraform-database/` module defines:
- PostgreSQL users and roles for Grafana
- Database permissions and grants
- Shared database access between production and ephemeral instances

This module is imported and executed by the infrastructure repository's `terraform/modules/rhiza-shared/database_config.tf`.

### ArgoCD Integration

This repository is monitored by ArgoCD ApplicationSets configured in the [rhiza-research/infrastructure](https://github.com/rhiza-research/infrastructure) repository for PR environments. Pull requests with the `PR-env` label trigger ephemeral environment creation/destruction. 
