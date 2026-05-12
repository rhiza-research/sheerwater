from dashboard_data.rainfall_regions import get_rainfall_regions, masks_to_polygons
from sheerwater.utils import start_remote
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd


if __name__ == "__main__":
    start_remote(remote_name="mohini")

    grid = "global0_25"
    mask = "lsm"

    region = "nimbus_horn_and_east_africa"
    kregions = 5
    ea_regions = get_rainfall_regions(
            data_source="imerg_final",
            kregions=kregions,
            region=region,
            grid=grid,
            mask=mask,
            agg_days=1,
            smooth_neighbors=50,
            spatial_coherence=5.0,
    )

    ea_polygons = masks_to_polygons(ea_regions.masks)

    region = "nimbus_west_africa"
    kregions = 4
    wa_regions = get_rainfall_regions(
            data_source="imerg_final",
            kregions=kregions,
            region=region,
            grid=grid,
            mask=mask,
            agg_days=1,
            smooth_neighbors=50,
            spatial_coherence=5.0,
    )

    wa_polygons = masks_to_polygons(wa_regions.masks)