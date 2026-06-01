"""Show that onset dates change substantially between different datasources and definitions"""

from sheerwater.utils import start_remote
from sheerwater.interfaces import get_data
from sheerwater.spatial_subdivisions import polygon_subdivision_geodataframe, get_spatial_subdivision_level

import get_onset as go

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster', remote_name='onset_issues')

    # various fixed parameters
    start_time = "2000-01-01"
    end_time = "2025-12-31"
    mask = "lsm"
    region = "kenya"
    grid = "global0_25"

    onset_definition = "moron-and-robertson"

    if region in ["kenya", "nimbus_east_africa"]:
        time_grouping = "kenya_rainy_season "
    else:
        time_grouping = "year"

    imerg_dates = go.get_sos_dates(datasource="imerg_final", event_name=onset_definition,
    start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region, time_grouping=time_grouping)

    chirps_dates = go.get_sos_dates(datasource="chirps_v3", event_name=onset_definition,
    start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region, time_grouping=time_grouping)

    # calculate mean, std deviation, and max of the absolute date differences
    doy_diff = np.abs(imerg_dates.doy - chirps_dates.doy)


    if time_grouping == "kenya_rainy_season ":
        mam_groups = [g for g in doy_diff.group.values if 'MAM' in str(g)]
        ond_groups = [g for g in doy_diff.group.values if 'OND' in str(g)]

        import pdb; pdb.set_trace()

        results = {}

        for season in ["MAM", "OND"]:
            if season == "MAM":
                groups = mam_groups
            elif season == "OND":
                groups = ond_groups
            mu = doy_diff.sel(group=groups).mean(dim="group").compute()
            std = doy_diff.sel(group=groups).std(dim="group").compute()
            max_diff = doy_diff.sel(group=groups).max(dim="group").compute()

            results[season] = {
                "mean": mu,
                "std": std,
                "max": max_diff,
            }
            
        import pdb; pdb.set_trace()

        cmap = "turbo"
        vmin = 0
        vmax = 7*4
        import pdb; pdb.set_trace()
        fig, axs = plt.subplots(3, 2, figsize=(15, 10), constrained_layout=True)
        results["MAM"]["mean"].plot(ax=axs[0, 0], x="lon",cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
        results["MAM"]["std"].plot(ax=axs[1, 0], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
        results["MAM"]["max"].plot(ax=axs[2, 0], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
        results["OND"]["mean"].plot(ax=axs[0, 1], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
        results["OND"]["std"].plot(ax=axs[1, 1], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
        im = results["OND"]["max"].plot(ax=axs[2, 1], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
        cbar = fig.colorbar(im, ax=axs, orientation="vertical", shrink=0.5, pad=0.02)
        cbar.set_label('Absolute Date Difference (days)')
        cbar.set_ticks([0, 7, 14, 21, 28])

        # remove all axis labels
        for ax in axs.flatten():
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_title('')
        axs[0, 0].set_ylabel('mean absolute difference')
        axs[1, 0].set_ylabel('std absolute difference')
        axs[2, 0].set_ylabel('max absolute difference')
        axs[0, 0].set_title('MAM')
        axs[0, 1].set_title('OND')

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

        plt.show()
    else:
        mu = doy_diff.mean(dim="group").compute()
        std = doy_diff.std(dim="group").compute()
        max_diff = doy_diff.max(dim="group").compute()

        fig, axs = plt.subplots(3, 1, figsize=(15, 10), constrained_layout=True)
        vmin = 0
        vmax = 7*4
        cmap = "turbo"
        mu.plot(ax=axs[0], x="lon",cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
        std.plot(ax=axs[1], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
        im = max_diff.plot(ax=axs[2], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
        cbar = fig.colorbar(im, ax=axs, orientation="vertical", shrink=0.5, pad=0.02)
        cbar.set_label('Absolute Date Difference (days)')
        cbar.set_ticks([0, 7, 14, 21, 28])

        # remove all axis labels
        for ax in axs:
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_title('')
        axs[0].set_ylabel('mean absolute difference')
        axs[1].set_ylabel('std absolute difference')
        axs[2].set_ylabel('max absolute difference')

        # add country boundaries to each axis
        try:
            level = get_spatial_subdivision_level(region)[0]
            country_gdf = polygon_subdivision_geodataframe(level=level, merged=False)
            country_gdf = country_gdf[country_gdf['region_name'] == region]
        except Exception as e:
            print(f"Error getting country boundaries for region {region}: {e}")
            country_gdf = None

        if country_gdf is not None:
            for ax in axs:
                country_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5, facecolor='none')

        plt.show()


    import pdb; pdb.set_trace()


