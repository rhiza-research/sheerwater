import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import pandas as pd
import xarray as xr
from sheerwater.spatial_subdivisions import polygon_subdivision_geodataframe, clip_region
from sheerwater.utils import roll_and_agg
from sheerwater.data.imerg import imerg_raw_live
from datetime import datetime

if __name__ == "__main__":
    start_time = "2026-02-19"
    now = datetime.now().strftime("%Y-%m-%d")
    ds_imerg = imerg_raw_live(start_time, now, version='late')
    ds_imerg = ds_imerg.rename({'precipitation': 'precip'})
    ds_imerg = clip_region(ds_imerg, region='kenya', grid='global0_1')
    # Get new imerg
    # Use a grey color for zero value on the colorbar instead of white.
    colors = ["#bdbdbd", "wheat", "lightgreen", "green", "lightblue", "blue", "yellow", "orange", "red", "purple"]
    cmap = LinearSegmentedColormap.from_list("wgbrp", colors)
    # df = pd.read_parquet("tahmo_data_kenya_2026-02-01_2026-03-18.parquet")
    # df = pd.read_parquet("../falconet/tahmo_data_kenya_2026-02-01_2026-03-18.parquet")
    df = pd.read_parquet("../falconet/tahmo_data_kenya_2025-08-01_2026-03-19.parquet")

    # Keep only stations with IDs that start with 'TA'
    df = df[df['station_id'].str.startswith('TA')]
    df = df.sort_values(by='time')
    df = df[['time', 'station_id', 'location_latitude', 'location_longitude', 'precipitation_1_tahmo']]
    df = df.rename(columns={'location_latitude': 'lat', 'location_longitude': 'lon', 'precipitation_1_tahmo': 'precip'})

    # Pull static station coords out before converting
    station_coords = df[['station_id', 'lat', 'lon']].groupby('station_id').first()
    df = df.drop(columns=['lat', 'lon'])
    df = df.set_index(['time', 'station_id'])

    # Convert to xarray
    ds = xr.Dataset.from_dataframe(df)
    # Assign lat/lon as 1D coordinates indexed only by station_id
    ds = ds.assign_coords(
        lat=('station_id', station_coords['lat'].values),
        lon=('station_id', station_coords['lon'].values),
    )
    # Resample daily by sum for precip
    ds_daily = ds.resample(time='1D').sum()

    # Roll over decads
    ds_decadal = roll_and_agg(ds_daily, agg=10, agg_col='time', agg_fn='sum')
    ds_imerg_decadal = roll_and_agg(ds_imerg, agg=10, agg_col='time', agg_fn='sum')

    # Convert to xarray dataset
    gdf = polygon_subdivision_geodataframe('admin_1')
    # Select down to kenya
    kenya_gdf = gdf[gdf['region_name'].str.contains('kenya')]

    bounds = [0, 10, 20, 40, 60, 80, 110, 150, 200, 250, 350]
    norm = BoundaryNorm(bounds, cmap.N)

    from matplotlib.gridspec import GridSpec

    fig = plt.figure(figsize=(18, 10))
    gs = GridSpec(2, 4, figure=fig, width_ratios=[1, 1, 1, 0.05], wspace=0.05, hspace=0.15)

    top_axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    bottom_axes = [fig.add_subplot(gs[1, i]) for i in range(3)]
    cbar_ax_top = fig.add_subplot(gs[0, 3])
    cbar_ax_bottom = fig.add_subplot(gs[1, 3])

    times = ["2026-02-19", "2026-03-01", "2026-03-07"]
    end_times = ["2026-02-28", "2026-03-10", "2026-03-16"]

    for i, t_idx in enumerate(times):
        # Top row: TAHMO station accumulations.
        ax_top = top_axes[i]
        vals_tahmo = ds_decadal.sel(time=t_idx).precip
        sc = ax_top.scatter(
            ds_daily.lon, ds_daily.lat,
            c=vals_tahmo.values,
            cmap=cmap,
            norm=norm,
            s=30,
        )
        kenya_gdf.boundary.plot(edgecolor='grey', linewidth=1.0, ax=ax_top)
        ax_top.set_title(f"TAHMO: {times[i]} to {end_times[i]}", fontsize=11)
        if i > 0:
            ax_top.tick_params(left=False)  # hide y ticks on middle/right panels

        # Bottom row: IMERG gridded accumulations.
        ax_bottom = bottom_axes[i]
        im = ds_imerg_decadal.sel(time=t_idx).precip.plot(
            x='lon',
            y='lat',
            ax=ax_bottom,
            cmap=cmap,
            norm=norm,
            add_colorbar=False,
        )
        kenya_gdf.boundary.plot(edgecolor='grey', linewidth=1.0, ax=ax_bottom)
        ax_bottom.set_title(f"IMERG: {times[i]} to {end_times[i]}", fontsize=11)
        if i > 0:
            ax_bottom.tick_params(left=False)

    fig.colorbar(sc, cax=cbar_ax_top, label='TAHMO Precipitation (mm)')
    fig.colorbar(im, cax=cbar_ax_bottom, label='IMERG Precipitation (mm)')
    plt.show()
