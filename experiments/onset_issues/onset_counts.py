"""Show that onset does not trigger the same number of times across different datasources and definitions"""

from sheerwater.utils import start_remote
from sheerwater.interfaces import get_data
from sheerwater.spatial_subdivisions import polygon_subdivision_geodataframe, get_spatial_subdivision_level

import get_onset as go

import matplotlib.pyplot as plt

if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster', remote_name='onset_issues')

    onset_definition = 'chc'
    if onset_definition == 'chc':
        wet_spell_agg_days = 10
        wet_spell_threshold = 20.0
        dry_spell_agg_days = 20
        dry_spell_threshold = 25.0
    elif onset_definition == 'icpac':
        wet_spell_agg_days = 3
        wet_spell_threshold = 21.0
        dry_spell_agg_days = 7
        dry_spell_threshold = 10.5
    elif onset_definition == 'moron-robertson':
        wet_spell_agg_days = 5
        wet_spell_threshold = 38.0
        dry_spell_agg_days = 10
        dry_spell_threshold = 5.0

    # various fixed parameters
    start_time = "2000-01-01"
    end_time = "2025-12-31"
    mask = "lsm"
    region = "nimbus_horn_and_east_africa"
    grid = "global0_25"

    imerg_dates = go.get_sos_dates(datasource="imerg_final", event="planting_suitability", event_kwargs={
        "wet_spell_threshold": wet_spell_threshold,
        "dry_spell_threshold": dry_spell_threshold,
        "wet_spell_agg_days": wet_spell_agg_days,
        "dry_spell_agg_days": dry_spell_agg_days,
    }, start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region)
    chirps_dates = go.get_sos_dates(datasource="chirps_v3", event="planting_suitability", event_kwargs={
        "wet_spell_threshold": wet_spell_threshold,
        "dry_spell_threshold": dry_spell_threshold,
        "wet_spell_agg_days": wet_spell_agg_days,
        "dry_spell_agg_days": dry_spell_agg_days,
    }, start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region)
    tahmo_dates = go.get_sos_dates(datasource="tahmo_avg", event="planting_suitability", event_kwargs={
        "wet_spell_threshold": wet_spell_threshold,
        "dry_spell_threshold": dry_spell_threshold,
        "wet_spell_agg_days": wet_spell_agg_days,
        "dry_spell_agg_days": dry_spell_agg_days,
    }, start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region)


    # get counts of onset for each season
    mam_groups = [g for g in imerg_dates.group.values if 'MAM' in str(g)]
    ond_groups = [g for g in imerg_dates.group.values if 'OND' in str(g)]

    import pdb; pdb.set_trace()

    imerg_mam_counts = imerg_dates.sel(group=mam_groups).doy.notnull().sum(dim="group")
    imerg_ond_counts = imerg_dates.sel(group=ond_groups).doy.notnull().sum(dim="group")
    chirps_mam_counts = chirps_dates.sel(group=mam_groups).doy.notnull().sum(dim="group")
    chirps_ond_counts = chirps_dates.sel(group=ond_groups).doy.notnull().sum(dim="group")
    tahmo_mam_counts = tahmo_dates.reindex(group=mam_groups).doy.notnull().sum(dim="group")
    tahmo_ond_counts = tahmo_dates.reindex(group=ond_groups).doy.notnull().sum(dim="group")

    # plot counts
    fig, axs = plt.subplots(2, 2, figsize=(10, 5), constrained_layout=True)
    cmap = "turbo"
    vmin = 0
    vmax = 25
    imerg_mam_counts.plot(ax=axs[0, 0], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
    imerg_ond_counts.plot(ax=axs[0, 1], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
    chirps_mam_counts.plot(ax=axs[1, 0], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)
    im = chirps_ond_counts.plot(ax=axs[1, 1], x="lon", cmap=cmap, add_colorbar=False, vmin=vmin, vmax=vmax)

    # turn off all axis labels
    for ax in axs.flatten():
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_title('')
    axs[0, 0].set_ylabel('IMERG')
    axs[1, 0].set_ylabel('CHIRPS')
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

    # create shared colorbar
    cbar = fig.colorbar(im, ax=axs, orientation="vertical", shrink=0.5, pad=0.02)
    cbar.set_label('Onset Counts')
    cbar.set_ticks([0, 5, 10, 15, 20, 25])
    plt.show()
    import pdb; pdb.set_trace()





    