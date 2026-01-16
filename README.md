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

## Data access and storage philosophy

Sheerwater access and transforms terra- and sometimes peta-byte scale datasets. It uses [Nuthatch](github.com/rhiza-research/nuthatch) 
to store, recall and slice these datasets to enable more efficient access.  In Nuthatch the results of functions
are stored in caches based on the function name and the arguments that are passed. When the same function is called with
the same key arguments, the data is returned rather than running the function.
Datasets are primarily stored in cloud storage buckets - ``caches`` - some of which are public and some of which are access-restricted. 
When a function is called, Nuthatch therefore checks to see if a global view of the data exists, it slices the data down in time and space
as requested by the function arguments, and then it returns that data, or a view of that data, back to the user.
Nuthatch also enables a user to copy a slice of data to their local machine and then reuse that data for more efficient repeated analysis.

When you install Sheerwater you are automatically configured to access all of Sheerwater's public data through Nuthatch.
Therefore when you call Sheerwater functions, you will mostly just be hitting pre-computed results, but the code serves as a self-documenting
API of how the data was transformed from its source to the result and enables users with enough compute to rerun the code either for
purposes of verification or to compute the functions with arguments that have not already been computed and stored.

## Available data

| Dataset | Variations | Grids | Aggregations (days) | Available date range <img width=75/> | Notes |
|---|:---:|:---:|:---:|---|---|
| IMERG | imerg_late, imerg_final | imerg (native), global0_25, global1_5 | 1, 5, 7, 10 | 1998-01-01<br>2024-12-31 |  |
| CHIRPS | chirps_v2, chirps_v3,<br>chirp_v2, chirp_v3 | chirps, global0_25, global1_5 | 1, 5, 7, 10 | 2000-06-01<br>2024-12-31 | Some variations extend back to 1998 |
| ERA5 | era5 | global0_25, global1_5 | 1, 5, 7, 10 | 1998-01-01<br>2024-12-31 | From google ARCO <br>only tmp2m and precip regridded |
| GHCN | ghcn, ghcn_avg | global0_25, global1_5 | 1, 5, 7, 10, 14, 30 | 1998-01-01<br>2024-12-31 | ghcn picks a random station in a grid cell,<br>ghcn_avg averageas all stations in a grid cell |
| TAHMO | tahmo, tahmo_avg | global0_25, global1_5 | 1, 5, 7, 10, 14, 30 | 2016-01-01<br>2025-06-01 | Requires TAHMO Data Agreement, not in public bucket.<br><br>tahmo picks a random station in a grid cell,<br>tahmo_avg averageas all stations in a grid cell |
| ECMWF IFS ER | ecmwf_ifs_er | global1_5 | 1, 7, 14 | 2016-01-04<br>2023-02-12 | From the weatherbench archive, known version |
| FuXi S2S | fuxi | global1_5 | 7 | 2016-01-03<br>2022-02-02 | Only precip and tmp2m |

Additional data accessors may be available. Please reach out if you see it in the code base but it's not listed here.

## Accessing sheerwater private data

Some data requires access to the sheerwater private bucket. Please send us an email for access so we 
can discuss use cases and collaboration. After we have added you to our bucket you can run the following commands to access data.

```console
curl https://sdk.cloud.google.com | bash
gcloud auth application-default login
```

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

6) Run tests:
```console
uv run pytest
```

Some tests require a remote Dask cluster and will start one automatically. To skip these tests:
```console
uv run pytest --skip-remote
```

## Deployment and Infrastructure

This repository is integrated with the Rhiza infrastructure for deployment of metrics to databases and integration of those databases into Grafana dashboards for visualization. If you are deploying this code on backend infrastructure with Grafana and Terraform, please read the [Infrastructure README](infrastructure/README.md). 
