"""Minimal example to show problem with entirely null dates / leads in the Graphcast data while using dask."""
import xarray as xr
import matplotlib.pyplot as plt
from dask.distributed import Client, LocalCluster
from sheerwater_benchmarking.utils import start_remote

if __name__ == "__main__":
    cluster = LocalCluster()
    client = Client(cluster)
    print("Dask dashboard:", client.dashboard_link)

    ds1 = xr.open_zarr(
        'gs://weathernext/59572747_4_0/zarr/99140631_1_2020_to_2021/forecasts_10d/date_range_2019-12-01_2021-01-22_6_hours.zarr',
        chunks='auto',
        decode_timedelta=True)
    nulls = ds1['2m_temperature'].isnull().sum(dim=['lat', 'lon']) / (1440 * 720)
    nulls_per_timedelta = []
    for i in range(0,40):
        nulls_per_timedelta.append(nulls.isel(prediction_timedelta=i).sum().values)
    print(nulls_per_timedelta)
