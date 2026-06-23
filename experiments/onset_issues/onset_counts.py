"""Plot maps showing total onset counts sensitivity to product"""

from sheerwater.utils import start_remote
from sheerwater.interfaces import get_data
from sheerwater.spatial_subdivisions import polygon_subdivision_geodataframe, get_spatial_subdivision_level
from sheerwater.tasks.onset_dates import onset_dates

import matplotlib.pyplot as plt

if __name__ == "__main__":
    start_remote(remote_name='onset_counts')

    start_time = "2015-01-01"
    end_time = "2025-12-31"
    grid = "global0_25"
    region = "nimbus_west_africa"
    onset_def = "moron_and_robertson_onset"
    time_grouping = "year"

    imerg_dates = onset_dates(start_time, end_time, "imerg_final", grid, region, onset_def, time_grouping)
    chirps_dates = onset_dates(start_time, end_time, "chirps_v3", grid, region, onset_def, time_grouping)

    imerg_counts = imerg_dates.doy.notnull().sum(dim="group")
    chirps_counts = chirps_dates.doy.notnull().sum(dim="group")


    # plot counts
    fig, axs = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
    imerg_counts.plot(ax=axs[0], x="lon", cmap="viridis", vmin=0, vmax=25, add_colorbar=False, add_labels=False)
    im = chirps_counts.plot(ax=axs[1], x="lon", cmap="viridis", vmin=0, vmax=25, add_colorbar=False, add_labels=False)
    axs[0].set_title("IMERG")
    axs[1].set_title("CHIRPS")

    # add country boundaries to each axis
    try:
        level = get_spatial_subdivision_level(region)[0]
        country_gdf = polygon_subdivision_geodataframe(level=level, merged=False)
        country_gdf = country_gdf[country_gdf['region_name'] == region]
    except Exception as e:
        print(f"Error getting country boundaries for region {region}: {e}")
        country_gdf = None

    if country_gdf is not None:
        for ax in axs.flatten():
            country_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5, facecolor='none')

    # create shared colorbar
    cbar = fig.colorbar(im, ax=axs, orientation="vertical", shrink=0.5, pad=0.02)
    cbar.set_label('Onset Counts')
    cbar.set_ticks([0, 5, 10, 15, 20, 25])
    plt.show()
    import pdb; pdb.set_trace()





    