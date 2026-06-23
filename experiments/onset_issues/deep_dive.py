"""Look at onset dates and rainfall time series at a given lat/lon"""

from matplotlib import pyplot as plt
import numpy as np

from sheerwater.utils import start_remote
from sheerwater.interfaces import get_data

from sheerwater.tasks.onset_dates import onset_dates

if __name__ == "__main__":
    start_remote(remote_name="deep_dive")

    """Chosen location"""
    lat = 21.5
    lon = 81.25
    # onset definition of interest
    onset_def = "moron_and_robertson_onset"


    """Get precip time series and onset dates"""
    region = "india"
    grid = "global0_25"
    mask = "lsm"

    start_time = "2015-01-01"
    end_time = "2025-12-31"
    time_grouping = "year"

    # precip
    imerg_final = get_data("imerg_final")(start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region)
    chirps_v3 = get_data("chirps_v3")(start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region)
    # onset
    datesi = onset_dates(start_time, end_time,"imerg_final",grid, region, onset_def, time_grouping)
    datesc = onset_dates(start_time, end_time,"chirps_v3", grid, region, onset_def, time_grouping)
    
    # summary statistics at this location go in title.
    # calculate mean, std, and max of absolute date differences across all groups
    date_diff = np.abs(datesi.sel(lat=lat, lon=lon).doy - datesc.sel(lat=lat, lon=lon).doy)
    mean = date_diff.mean("group").compute()
    std = date_diff.std("group").compute()
    max_diff = date_diff.max("group").compute()

    # select to lat/lon
    imerg_final = imerg_final.sel(lat=lat, lon=lon)
    chirps_v3 = chirps_v3.sel(lat=lat, lon=lon)
    datesi = datesi.sel(lat=lat, lon=lon).time
    datesc = datesc.sel(lat=lat, lon=lon).time


    """Plotting"""
    chirps_color = "purple"
    imerg_color = "green"

    # plot rainfall time series
    fig, ax = plt.subplots(figsize=(10, 5))
    imerg_final.precip.plot(ax=ax, label="IMERG", color=imerg_color)
    chirps_v3.precip.plot(ax=ax, label="CHIRPS", color=chirps_color)

    # plot onset dates for each group as a vertical line
    for group in datesi.group.values:
        dayi = datesi.sel(group=group).values
        dayc = datesc.sel(group=group).values
        ax.axvline(dayi, linewidth=1, color=imerg_color)
        ax.axvline(dayc, linewidth=1, linestyle="--", color=chirps_color)

    ax.legend()
    # add mean, std, and max to title
    ax.set_title(f"Mean: {mean:.2f}, Std: {std:.2f}, Max: {max_diff:.2f}")

    plt.show()
