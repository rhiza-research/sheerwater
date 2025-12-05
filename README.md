# Sheerwater

A weather forecast and data benchmarking library. The Sheerwater project is working to benchmark
ML- and physics-based weather and climate forecasts regionally and globally with a focus
on model performance on the African continent.

Sheerwater contains a set of data accessors to fetch common forecasts and ground-truth data sources, 
a library of common evaluation metrics, and a metrics interface to validate forecasts against data
products and station data.

## Getting started

To run this code, you need read access to Sheerwater forecasts and ground truth data stored in our cloud bucket.  Please request access from Rhiza if you would like to execute this code. Once you have access, you can read data and run metrics by importing `sheerwater` and running your code.

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

# Get the FuXi S2S forecast as an xarray
ds_fuxi = fuxi("2020-01-01", "2022-01-01", lead="week2", variable="precip", grid="global1_5",)

# Get gridded GHCN weather station data
ds_ghcn = ghcn("2020-01-01", "2022-01-01", agg_days=7, variable="precip", grid="global0_25")

# Fetch an evaluation metric - note, already computed metrics are defined from 2016-01-01 to 2022-12-31
# Computing new metrics can be computationally intensive
val = metric("2016-01-01", "2022-12-31", forecast="fuxi", truth="era5", variable="precip", metric_name="mae", region="country", grid="global1_5")
print(val)
```

## Evaluating your own forecasts against your own data

If you have a forecast you would like to evaluate, you can tag it in the sheerwater forecast decorator so that sheerwater can find it for evaluation.

```py

from sheerwater.forecasts import forecast
from sheerwater.data import data
from sheerwater.metrics import metric

# Forecasts must be xarrays with coordinates for lat, lon, init_time, and prediction_timedelta with a matching variable on the correct grid
@forecast
def my_forecast(start_time, end_time, agg_days, variable, grid, **kwargs):
    ds = fetch_forecast(start_time, end_time, agg_days, variable, grid)
    ds = ds.rename({'start_time': 'init_time', 
                    'timestep': 'prediction_timedelta',
                    'latitude': 'lat',
                    'longitude': 'lon'})
    ds = ds.rename_vars({'precipitation_mm': 'precip'})
    return ds

# Data must be xarrays with coordinates for lat, lon, and time with a matching variable on the correct grid
@data
def my_station_data(start_time, end_time, agg_days, variable, grid, **kwargs):
    ds = fetch_data(start_time, end_time, agg_days, variable, grid)
    return ds

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

This repository is integrated with the Rhiza infrastructure for deployment of metrics to databases and integration of those databases into Grafana dashboards for visualization. If you are deploying this code on backend infrastructure with Grafana and Terraform, please read the backend README [Infrastructure README](infrastructure/README.md). 
