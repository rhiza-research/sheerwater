"""Generate the start of season (SoS) dates for a given region and datasource."""
import matplotlib.pyplot as plt
import numpy as np
import os
from sheerwater.interfaces import get_data
from sheerwater.spatial_subdivisions import multinational_gdf, get_spatial_subdivision_level
from sheerwater.utils import start_remote


if __name__ == "__main__":
    start_time = "2000-01-01"  # start time of the data
    end_time = "2025-12-31"  # end time of the data
    mask = 'lsm'  # apply a land-sea mask to the data
    region = 'eastern_africa'  # clip the data to a specific region

    # Select the datasource to use. Options are:
    # - imerg_final, imerg_late, chirps_v3, chirp_v3, tahmo, rain_over_africa, tamsat, oya, ...
    datasource = 'imerg_final'

    ############################################################################################
    # Event definition parameters:
    # wet_spell_threshold: threshold for the wet spell
    # dry_spell_threshold: threshold for the dry spell
    # wet_spell_agg_days: number of days in the wet spell
    # dry_spell_agg_days: number of days in the dry spell
    # detect_in_time: detect the event in time
    # time_grouping: time grouping to use for the event
    ############################################################################################
    # The ICPAC definition of the planting suitability event is:
    # - Wet spell: 3 consecutive days with precipitation >= 21 mm
    # - Dry spell: 7 consecutive days with precipitation < 10.5 mm
    # - Planting suitability: Wet spell AND NOT dry spell
    wet_spell_threshold = 21.0
    dry_spell_threshold = 10.5
    wet_spell_agg_days = 3
    dry_spell_agg_days = 7

    # We then detect the first time the event criteria is met in the rainy season.
    # The rainy season defines two periods:
    # - MAM: Starting Feb 1st and ending June 30th
    # - OND: Starting Sept 1st and ending Dec 31st
    detect_in_time = {'detect': 'first', 'time_grouping': 'rainy_season'}

    ############################################################################################
    # Choose a grid resolution. Options are:
    # global0_25: 0.25 degree global grid, 0.0 offset, 0.25 step. Matches ECMWF's grids
    # global1_5: 1.5 degree global grid, 0.0 offset, 1.5 step. Matches ECMWF's grids
    # global0_05: 0.05 degree global grid, 0.025 offset, 0.05 step. Matches CHIRPS source grid
    # global0_1: 0.1 degree global grid, 0.05 offset, 0.1 step. Matches IMERG source grid
    # NOTE: All data sources may not be pre-cached for all grids. If you get a message that
    # the data is not cached and regridding is happening, you should cancel the run.
    ############################################################################################
    grid = 'global0_25'

    # Start a remote dask cluster for fast processing. Can be commenteed out if you want to run locally.
    # If so, consider running on a short time period and smaller region and large resolution, to avoid
    # long processing times.
    start_remote(remote_config='xlarge_cluster')

    # Get the data for the planting suitability event.
    ds = get_data(datasource)(start_time=start_time, end_time=end_time,
                              event='planting_suitability',
                              event_kwargs={
                                  'wet_spell_threshold': wet_spell_threshold,
                                  'dry_spell_threshold': dry_spell_threshold,
                                  'wet_spell_agg_days': wet_spell_agg_days,
                                  'dry_spell_agg_days': dry_spell_agg_days,
                                  'detect_in_time': detect_in_time
                              },
                              grid=grid, mask=mask, region=region)

    # Get and save the start of season (SoS) dates for each season
    # The underlying dataframe ds will have a 1 in the precip variable for the SoS date
    # for each grid cell, and 0 otherwise.
    ds = ds.assign_coords(doy=ds.time.dt.dayofyear)
    has_sos = ds['precip'].groupby("group").sum(dim="time", skipna=True, min_count=1)
    is_sos = ds['precip'].groupby("group").map(lambda x: x.idxmax(dim="time", skipna=True))
    is_sos = is_sos.compute()

    # Select the value in the time dimension using is_sos as an index (for each grid cell)
    sos_time = ds.drop_vars('group').sel(time=is_sos)

    # Properly set to NaN areas where there isn't a SoS
    sos_time['doy'] = sos_time['doy'].where(has_sos > 0, np.nan, drop=False)
    sos_time['time'] = sos_time['time'].where(has_sos > 0, np.datetime64('NaT'), drop=False)

    """Save and plot the SoS dates for each season"""
    save_dir = 'sos_plots'
    os.makedirs(save_dir, exist_ok=True)

    # Get country boundaries for plotting for the region
    country_gdf = multinational_gdf()
    level = get_spatial_subdivision_level(region)[0]
    country_gdf = country_gdf[country_gdf[level] == region]

    # For each season, generate a plot
    for season in np.unique(sos_time['group'].values):
        print("Plotting season: ", season)
        season_ds = sos_time.where(sos_time["group"] == season, drop=True)

        # If 'MAM' in season
        if 'MAM' in season:
            vmin = 32
            vmax = 180
        elif 'OND' in season:
            vmin = 244
            vmax = 366

        # Create the figure and axis explicitly
        fig, ax = plt.subplots()
        season_ds.doy.plot(
            x='lon',
            y='lat',
            cmap='viridis',
            vmin=vmin,
            vmax=vmax,
            cbar_kwargs={'label': 'Day of Year', 'extend': 'both'},
            ax=ax,
        )
        # Overlay the country boundaries
        country_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5, facecolor='none')

        ax.set_title(f'Start of Season (SoS): {season}')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        plt.savefig(os.path.join(save_dir, f'sos_{season}.png'))
        plt.close(fig)

    # Save the underlying data as a zarr file
    sos_time = sos_time.rename({'precip': 'start_of_season'}).compute()
    sos_time.to_zarr(os.path.join(save_dir, 'sos_time.zarr'), mode='w')

    # Convert to a table
    sos_table = sos_time.to_dataframe()
    sos_table = sos_table.reset_index()

    # Write to a csv file, with and without NaN values
    sos_table.to_csv(os.path.join(save_dir, 'sos_table.csv'), index=False)
    sos_table.dropna().to_csv(os.path.join(save_dir, 'sos_table_no_nan.csv'), index=False)
