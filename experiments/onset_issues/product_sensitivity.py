"""Plot maps showing sensitivity of onset dates to product."""
from sheerwater.utils import start_remote
from sheerwater.spatial_subdivisions import clip_region
from sheerwater.spatial_subdivisions import polygon_subdivision_geodataframe, get_spatial_subdivision_level
from sheerwater.tasks.onset_dates import onset_dates

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

onset_definitions = [
    "chc_onset",
    "icpac_onset",
    "moron_and_robertson_onset",
]


def get_season_statistics(dates1, dates2, groups=("first", "second")):
    """Get season statistics for a given onset definition."""
    delta = dates1 - dates2
    results = {}

    for group in groups:
        vals = [g for g in delta.group.values if group in str(g)]
        da = np.abs(delta.sel(group=vals))

        results[group] = {
            "mean": da.mean("group").compute(),
            "std": da.std("group").compute(),
            "max": da.max("group").compute(),
        }

    return results


def clip_results(results, region, grid):
    """Clip results to a region."""
    out = {}

    for onset_def, seasons in results.items():
        out[onset_def] = {}

        for season, metrics in seasons.items():
            out[onset_def][season] = {}

            for metric, da in metrics.items():
                ds = da.to_dataset(name="doy")
                clipped = clip_region(ds, region=region, grid=grid, drop=True)
                # drop spatial_ref coordinate if it exists
                if "spatial_ref" in clipped.coords:
                    clipped = clipped.drop_vars("spatial_ref")
                # drop lon and lat where doy is all nan
                clipped = clipped.dropna("lon", how="all")
                clipped = clipped.dropna("lat", how="all")
                out[onset_def][season][metric] = clipped["doy"]

    return out


def plot_statistics(results, season="first", title="", add_country_boundaries="africa"):

    # color map for date difference - clearly shows weeks of difference
    bounds = [0, 7, 14, 21, 28, 35]

    colors = [
        "#31a354",  # 0 to +1 weeks (good)
        "#a1d99b",  # +1 to +2 weeks (good)
        "#fb6a4a",  # +2 to +3 weeks (bad)
        "#de2d26",  # +3 to +4 weeks (bad)
        "#67000d",  # > +4 weeks (bad)
    ]

    cmap = ListedColormap(colors)
    norm = BoundaryNorm(bounds, cmap.N)

    metrics = ["mean", "std", "max"]

    if add_country_boundaries:
        try:
            level = get_spatial_subdivision_level(add_country_boundaries)[0]
            country_gdf = polygon_subdivision_geodataframe(level=level, merged=False)
            country_gdf = country_gdf[country_gdf["region_name"] == add_country_boundaries]
        except Exception as e:
            print(f"Error getting country boundaries: {e}")
            country_gdf = None

    fig, axes = plt.subplots(
        3, len(onset_definitions),
        figsize=(3.8 * len(onset_definitions), 11),
    )

    plt.subplots_adjust(
        left=0.08,
        right=0.88,
        top=0.92,
        bottom=0.06,
        wspace=0.04,
        hspace=0.08,
    )

    mean_lim = 7 * 4
    spread_lim = 7 * 4

    pretty_defs = {
        "chc_onset": "CHC",
        "icpac_onset": "ICPAC",
        "moron_and_robertson_onset": "Moron–Robertson",
    }

    pretty_metrics = {"mean": "mean", "std": "std. dev.", "max": "maximum"}

    for col, onset_def in enumerate(onset_definitions):

        for row, metric in enumerate(metrics):

            ax = axes[row, col]
            da = results[onset_def][season][metric]

            kwargs = dict(ax=ax, x="lon", y="lat", cmap=cmap, norm=norm, add_colorbar=False, rasterized=True)

            if metric == "mean":
                im = da.plot(**kwargs)

            else:
                im = da.plot(**kwargs)

            if row == 0:
                ax.set_title(
                    pretty_defs[onset_def],
                    fontsize=12,
                    pad=10,
                    color="0.15",
                )

            if col == 0:
                ax.annotate(pretty_metrics[metric],
                xy=(-0.16, 0.5), xycoords="axes fraction", rotation=90, va="center", ha="center", fontsize=11, color="0.25")

            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.set_xticks([])
            ax.set_yticks([])

            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(0.6)
                spine.set_color("0.3")

    cax = fig.add_axes([0.9, 0.2, 0.02, 0.6])

    cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)

    cb.set_ticks([0, 7, 14, 21, 28])

    cb.set_ticklabels(["0", "+1w", "+2w", "+3w", "+4w"])

    fig.suptitle(title, fontsize=12, color="0.15", y=0.97)

    if country_gdf is not None:
        for ax in axes.flatten():
            country_gdf.plot(ax=ax, edgecolor="black", linewidth=0.5, facecolor="none")

    return fig, axes


if __name__ == "__main__":

    start_remote(remote_name="product_sensitivity")
    start_time = "2015-01-01"
    end_time = "2025-12-31"
    grid = "global0_25"

    """For India"""
    region = "india"
    time_grouping = "imd_season"
    results = {}

    for onset_def in onset_definitions:
        print(f"------{region} {onset_def} {time_grouping}------")
        imerg = onset_dates(start_time, end_time, "imerg_final", grid, region, onset_def, time_grouping)
        chirps = onset_dates(start_time, end_time, "chirps_v3", grid, region, onset_def, time_grouping)
        results[onset_def] = get_season_statistics(imerg.doy, chirps.doy, groups=("preimd", "imd"))


    plot_statistics(results, season="imd",
    title="monsoon onset sensitivity", add_country_boundaries="india")
    plt.show()

    """For Western Africa"""
    # can use similar approach for eastern africa to get plots for each rainfall region
    region = "nimbus_west_africa"
    time_grouping = "year"
    results = {}
    for onset_def in onset_definitions:
        print(f"------{region} {onset_def} {time_grouping}------")
        imerg = onset_dates(start_time, end_time, "imerg_final", grid, region, onset_def, time_grouping)
        chirps = onset_dates(start_time, end_time, "chirps_v3", grid, region, onset_def, time_grouping)
        results[onset_def] = get_season_statistics(imerg.doy, chirps.doy, groups=("first", "second"))
    rr_wa = ["west_africa_western_sahel", "west_africa_eastern_sahel", "west_africa_sudanian", "west_africa_coastal"]
    for rridx in range(len(rr_wa)):
        rr_results = clip_results(results, region=rr_wa[rridx], grid=grid)
        plot_statistics(rr_results, season="Y", title=f"{rr_wa[rridx]} sensitivity", add_country_boundaries="africa")
        plt.show()