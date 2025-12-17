"""Walkthrough script for Example 1 of the Sheerwater data library."""
import numpy as np
import matplotlib.pyplot as plt
from sheerwater.data import chirps, imerg

if __name__ == "__main__":
    # Example 1: Get all CHIRPS data for one year in Eastern Africa
    ds1 = chirps('2019-01-01', '2019-12-31', region='eastern_africa', cache_mode='local')
    # Plot one day. Requires fetchin the data from the remote cache and will run in ~30 seconds.
    ds1.sel(time="2019-06-15").precip.plot(x='lon')
    plt.show()

    # Print attributes of the dataset
    print("Aggregation days: ", ds1.agg_days)
    print("Variable: ", ds1.variable, "with units: ", ds1.units)

    # Plot another day. Will hit your cached local data and plot quickly.
    ds1.sel(time="2019-09-21").precip.plot(x='lon')
    plt.show()

    # Call the same function with the same parameters again. Will hit your cached local data 
    ds1p = chirps('2019-01-01', '2019-12-31', region='eastern_africa', cache_mode='local')

    # Example 2: Request data aggregrated to 16 day intervals. This aggregration does not exist 
    # in the remote cache, so this will trigger local recomputation of the data.
    # This will take ~30 seconds to compute on a modern laptop and then cache the result locally.
    ds2 = chirps('2019-01-01', '2019-12-31', region='eastern_africa', agg_days=16, cache_mode='local')
    ds2.sel(time="2019-09-21").precip.plot(x='lon')
    plt.show()

    # Example 3: Do your own simple reprocessing with the downloaded dataset
    # ds is a standard xarray dataset, so you can use all the standard xarray functions to manipulate it.
    # Get monthly averages of the precipitation data.
    ds3 = ds2.groupby('time.month').mean()
    # Plot this as a time series.
    ds3.precip.plot(x='time')
    plt.show()

    # Plot data with a regional overlay
    # TODO: Genevieve add plot region here

    # Example 4: Get the CHIRPS data regridded to a different grid
    # This will hit the remote cache with the already regridded data and download to your local machine
    ds_chirps = chirps('2019-01-01', '2019-12-31', region='eastern_africa', grid='global1_5', cache_mode='local')

    # This will hit the remote cache with the already regridded data and download to your local machine
    ds_imerg = imerg('2019-01-01', '2019-12-31', region='eastern_africa', grid='global1_5', cache_mode='local')

    # Plot a timeseries of differences between the two datasets
    diff = np.abs(ds_chirps.precip - ds_imerg.precip)
    # TODO: make sure this syntax is right
    diff.precip.sel(lat=0.05, lon=0.25).plot('time')

