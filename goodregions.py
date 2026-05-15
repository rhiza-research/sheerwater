from dashboard_data.rainfall_regions import get_rainfall_regions, masks_to_polygons
from sheerwater.utils import start_remote
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import xarray as xr

from sheerwater.spatial_subdivisions import get_spatial_subdivision_level, polygon_subdivision_geodataframe
from sheerwater.spatial_subdivisions import rainfall_region_labels

import matplotlib.pyplot as plt

from matplotlib.patches import Patch


def plot_regions(region_masks):
    fig, ax = plt.subplots(figsize=(10, 6))

    # --- country boundaries (Africa) ---
    try:
        region = "africa"
        level = get_spatial_subdivision_level(region)[0]
        country_gdf = polygon_subdivision_geodataframe(level=level, merged=False)
        country_gdf = country_gdf[country_gdf["region_name"] == region]

        country_gdf.boundary.plot(ax=ax, color="black", linewidth=0.5)
    except Exception as e:
        print(f"country plot failed: {e}")

    # --- data ---
    da = region_masks.region.load()

    valid = da != "no_region"

    unique_vals = np.unique(da.values[valid.values])

    # stable mapping: label -> integer code
    mapping = {v: i for i, v in enumerate(unique_vals)}

    codes = xr.apply_ufunc(
        np.vectorize(mapping.get),
        da,
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float],
    )

    codes = codes.where(valid)

    # --- plot raster ---
    im = codes.plot(
        ax=ax,
        x="lon",
        y="lat",
        cmap="tab10",
        add_colorbar=False,
        vmin=0,
        vmax=len(unique_vals) - 1,
    )

    # --- white background ---
    ax.set_facecolor("white")

    # --- legend (color key instead of labels on map) ---
    cmap = plt.get_cmap("tab10")

    legend_patches = [
        Patch(color=cmap(mapping[name] / max(1, len(unique_vals) - 1)),
              label=name)
        for name in unique_vals
    ]

    ax.legend(
        handles=legend_patches,
        loc="lower left",
        fontsize=8,
        frameon=True,
        title="Regions",
    )

    ax.set_title("Region Masks")

    plt.show()


if __name__ == "__main__":
    start_remote(remote_name="mohini")
    rainfall_region_labels = rainfall_region_labels()
    plot_regions(rainfall_region_labels)