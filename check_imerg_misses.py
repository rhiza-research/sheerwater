"""Analyze IMERG misses against stations and plot miss rates."""
from sheerwater.utils import start_remote
import matplotlib.pyplot as plt
from sheerwater.spatial_subdivisions import spatial_subdivisions as ss
from sheerwater.data import imerg_late, tahmo_avg, stations
import xarray as xr


def get_misses(ds, satellite_below, stations_above):
    ds["miss"] = (ds["satellite_precip"] < satellite_below) & (ds["stations_precip"] > stations_above)
    ds["event"] = (ds["stations_precip"] > stations_above)
    ds["sample"] = ds["stations_precip"].notnull() & ds["satellite_precip"].notnull()

    # sum over time, keeping lat/lon as dimensions
    ds = ds.sum(dim="time", skipna=True, min_count=1)
    ds["miss_rate"] = ds["miss"] / ds["event"]

    # stack and filter
    ds = ds.stack(points=("lat", "lon"))
    select = ds["sample"] > 0
    ds = ds.isel(points=select.compute())

    return ds

if __name__ == "__main__":
    start_remote(remote_name="check_imerg_misses")

    start_time, end_time = "2020-01-01", "2025-12-31"

    # ---------------------------------------------------
    agg_days = 5
    imerg_ds = imerg_late(
        start_time=start_time,
        end_time=end_time,
        grid="global0_25",
        region="global",
        agg_days=agg_days,
    )
    stations_ds = stations(
        start_time=start_time,
        end_time=end_time,
        grid="global0_25",
        region="global",
        agg_days=agg_days,
    )
    stations_ds = stations_ds.rename({"precip": "stations_precip"})
    imerg_ds = imerg_ds.rename({"precip": "satellite_precip"})
    ds = xr.merge([imerg_ds, stations_ds])
    satellite_below, stations_above = 1, 5
    result = get_misses(ds, satellite_below, stations_above)


    # ---------------------------------------------------

    event_defs = [(1, 5)]
    event_agg_days = [1, 5, 10]
    nevents = len(event_defs)
    naggs = len(event_agg_days)

    # get africa outline for plotting
    gdf = ss["continent"][1]()
    gdf = gdf[gdf["region_name"] == "africa"]

    fig, axes = plt.subplots(nevents, naggs, figsize=(5*naggs, 4*nevents))
    axes = axes.flatten()
    vmin, vmax = 0, 0.2
    for i in range(naggs):
        agg_days = event_agg_days[i]
        imerg_ds = imerg_late(
            start_time=start_time,
            end_time=end_time,
            grid="global0_25",
            region="africa",
            agg_days=agg_days,
        )
        tahmo_ds = tahmo_avg(
            start_time=start_time,
            end_time=end_time,
            grid="global0_25",
            region="africa",
            agg_days=agg_days,
        )
        imerg_ds = imerg_ds.rename({"precip": "imerg_late_precip"})
        tahmo_ds = tahmo_ds.rename({"precip": "tahmo_avg_precip"})
        ds = xr.merge([imerg_ds, tahmo_ds])
        for j in range(nevents):
            imerg_below, tahmo_above = event_defs[j]
            result = get_misses(ds, imerg_below, tahmo_above)
            ax = axes[j*naggs + i]
            sc = ax.scatter(result["lon"].values, result["lat"].values, c=result["miss_rate"].values, s=5, cmap="plasma", vmin=vmin, vmax=vmax)
            gdf.plot(ax=ax, color="none", edgecolor="black")
            # split title across two lines and shorten
            ax.set_title(f"IMERG < {imerg_below}mm, TAHMO > {tahmo_above}mm\n{agg_days}-day agg", fontsize=9)
            ax.set_xticks([])
            ax.set_yticks([])

    fig.subplots_adjust(right=0.88, hspace=0.35, wspace=0.15)
    cbar_ax = fig.add_axes([0.9, 0.15, 0.02, 0.7])  # [left, bottom, width, height]
    cbar = fig.colorbar(sc, cax=cbar_ax, label="Miss Rate")
 
