# Sheerwater

A weather forecast and data benchmarking library. The Sheerwater project is working to benchmark
ML- and physics-based weather and climate forecasts regionally and globally with a focus
on model performance on the African continent.

Sheerwater contains a set of data accessors to fetch common forecasts and ground-truth data sources, 
a library of common evaluation metrics, and a metrics interface to validate forecasts against data
products and station data.

## Getting started

To run this code, you need read access to Sheerwater forecasts and ground truth data stored in our cloud bucket. Some
of this data, included CHIRPS, IMERG, ERA5, and ECMWF ER are in a public bucket that requires no additional
credentials, so all you have to do is:

1) Install sheerwater in your environment:

```console
pip install sheerwater
```

2) Use sheerwater to access forecasts or data:
```py
from sheerwater.reanalysis import era5
from sheerwater.data import ghcn, chirps_v3
from sheerwater.metrics import grouped_metric

# Get ERA5 as an xarray
ds_era5 = era5("2020-01-01", "2022-01-01", agg_days=1, variable="precip", grid="global1_5",)

# Get gridded GHCN weather station data
ds_ghcn = ghcn("2020-01-01", "2022-01-01", agg_days=7, variable="precip", grid="global0_25")

# Get chirps data with default parameters
ds_chirps = chirps_v2()
```

3) Run evaluation metrics on public forecasts or data

```py
# Run an evaluation metric - this might take some time!
val = metric("2016-01-01", "2022-12-31", forecast="era5", truth="ghcn", variable="precip", 
             metric_name="mae", region="country", grid="global1_5")
print(val)
```

## Accessing sheerwater private data

Some data requires access to the sheerwater private bucket. Please send us an email for access so we 
can discuss use cases and collaboration. After we have added you to our bucket you can:

```console
curl https://sdk.cloud.google.com | bash
gcloud auth application-default login
```

No you should be able to access data that 


## Evaluating your own forecasts against your own data

If you have a forecast you would like to evaluate, you can tag it in the sheerwater forecast decorator so that sheerwater can find it for evaluation.

```py

from sheerwater.forecasts import forecast
from sheerwater.data import data
from sheerwater.metrics import metric

# Forecasts must be xarrays with coordinates for lat, lon, init_time, and 
# prediction_timedelta with a matching variable on the correct grid
@forecast
def my_forecast(start_time, end_time, agg_days, variable, grid, **kwargs):
    ds = fetch_forecast(start_time, end_time, agg_days, variable, grid)
    ds = ds.rename({'start_time': 'init_time', 
                    'timestep': 'prediction_timedelta',
                    'latitude': 'lat',
                    'longitude': 'lon'})
    ds = ds.rename_vars({'precipitation_mm': 'precip'})
    return ds

# Data must be xarrays with coordinates for lat, lon, and time with a 
# matching variable on the correct grid
@data
def my_station_data(start_time, end_time, agg_days, variable, grid, **kwargs):
    ds = fetch_data(start_time, end_time, agg_days, variable, grid)
    return ds

# Evaluate the forecast
metric("2015-01-01", "2022-01-01", forecast="my_forecast", truth="my_station_data", 
        agg_days=1, variable='precip', grid='global1_5', metric_name="bias", 
        region="country", time_grouping="month_of_year")
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

This repository is integrated with the Rhiza infrastructure for deployment of metrics to databases and integration of those databases into Grafana dashboards for visualization. If you are deploying this code on backend infrastructure with Grafana and Terraform, please read the [Infrastructure README](infrastructure/README.md). 
