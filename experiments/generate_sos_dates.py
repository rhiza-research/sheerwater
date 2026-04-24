"""Generate the start of season (SoS) dates for a given region and datasource."""
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
from sheerwater.interfaces import get_data
from sheerwater.spatial_subdivisions import polygon_subdivision_geodataframe, get_spatial_subdivision_level
from sheerwater.utils import start_remote

import numpy as np
import matplotlib.colors as mcolors
import pandas as pd


def lighten_color(color, factor):
    rgb = np.array(mcolors.to_rgb(color))
    return tuple(rgb + (1 - rgb) * factor)


def sos_cmap(season):
    # Base colors mapped by "position in season", not literal month
    # (so OND reuses same visual progression as MAM)
    season_base_colors = [
        "#d95f0e",  # early season (orange)
        "#238b45",  # mid-early (green)
        "#0868ac",  # mid (blue)
        "#6a51a3",  # late (purple)
        "#dd3497",  # very late (pink)
    ]

    lightening_steps = [0.0, 0.25, 0.5, 0.7]

    season_type, year = season.split('-')
    year = int(year)

    # Define months per season
    if season_type == "MAM":
        months = [2, 3, 4, 5, 6]  # Mar–Jun
    elif season_type == "OND":
        months = [9, 10, 11, 12]  # Sep–Dec
    else:
        raise ValueError("season must be 'MAM' or 'OND'")

    colors = []
    bounds = []
    ticks = []
    labels = []

    for i, month in enumerate(months):
        base_color = season_base_colors[i]

        start = pd.Timestamp(year=year, month=month, day=1)

        for week in range(4):
            date = start + pd.Timedelta(days=7 * week)
            doy = date.dayofyear

            colors.append(lighten_color(base_color, lightening_steps[week]))
            bounds.append(doy)
            ticks.append(doy)
            labels.append(date.strftime("%b %d"))

    # close final bin
    bounds.append(bounds[-1] + 7)

    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    return cmap, norm, bounds, ticks, labels


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate start of season (SoS) dates for a region and datasource."
    )
    parser.add_argument(
        "--output",
        choices=("plots", "data", "both"),
        default="both",
        help="Generate map plots only, zarr/csv data only, or both (default: both).",
    )
    args = parser.parse_args()
    do_plots = args.output in ("plots", "both")
    do_data = args.output in ("data", "both")

    start_time = "2000-01-01"  # start time of the data
    end_time = "2025-12-31"  # end time of the data
    mask = 'lsm'  # apply a land-sea mask to the data
    region = 'nimbus_horn_and_east_africa'  # clip the data to a specific region

    # Select the datasource to use. Options are:
    # - imerg_final, imerg_late, chirps_v3, chirp_v3, tahmo, rain_over_africa, tamsat, oya, ...
    datasource = 'imerg_final'

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
    onset_definition = 'chc'
    wet_spell_agg_days = 10
    wet_spell_threshold = 20.0
    dry_spell_agg_days = 20
    dry_spell_threshold = 25.0

    # We then detect the first time the event criteria is met in the rainy season.
    # The rainy season defines two periods:
    # - MAM: Starting Feb 1st and ending June 30th
    # - OND: Starting Sept 1st and ending Dec 31st
    detect_in_time = {'detect': 'first', 'time_grouping': 'rainy_season'}
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
    save_dir = f'sos_plots/{datasource}/{grid}/{region}/{onset_definition}'
    os.makedirs(save_dir, exist_ok=True)

    if do_plots:
        plot_dir = f'{save_dir}/plots'
        os.makedirs(plot_dir, exist_ok=True)

        # Get country boundaries for plotting for the region
        try:
            level = get_spatial_subdivision_level(region)[0]
            country_gdf = polygon_subdivision_geodataframe(level=level, merged=False)
            country_gdf = country_gdf[country_gdf['region_name'] == region]
        except Exception as e:
            print(f"Error getting country boundaries for region {region}: {e}")
            country_gdf = None

        # For each season, generate a plot
        for season in np.unique(sos_time['group'].values):
            print("Plotting season: ", season)
            season_ds = sos_time.where(sos_time["group"] == season, drop=True)

            # Get colormap for this season
            cmap, norm, bounds, ticks, labels = sos_cmap(season)

            # Create the figure and axis explicitly
            fig, ax = plt.subplots()
            im = season_ds.doy.plot(
                x='lon',
                y='lat',
                cmap=cmap,
                norm=norm,
                cbar_kwargs={
                    'label': 'Start of Season',
                    'ticks': ticks,
                    'spacing': 'proportional'
                },
                ax=ax,
            )

            # Apply labels cleanly
            cbar = im.colorbar
            cbar.set_ticklabels(labels)
            # Overlay the country boundaries
            if country_gdf is not None:
                country_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5, facecolor='none')

            ax.set_title(f'Start of Season (SoS): {season}')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            plt.savefig(os.path.join(plot_dir, f'sos_{season}_{onset_definition}_{datasource}.png'))
            plt.close(fig)

    if do_data:
        # Save the underlying data as a zarr file
        sos_time_out = sos_time.rename({'precip': 'start_of_season'}).compute()
        sos_time_out.to_zarr(os.path.join(save_dir, 'sos_time.zarr'), mode='w')

        # Convert to a table
        sos_table = sos_time_out.to_dataframe()
        sos_table = sos_table.reset_index()

        # Write to a csv file, with and without NaN values
        sos_table.to_csv(os.path.join(save_dir, 'sos_table.csv'), index=False)
        sos_table.dropna().to_csv(os.path.join(save_dir, 'sos_table_no_nan.csv'), index=False)
