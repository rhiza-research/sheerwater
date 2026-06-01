from sheerwater.utils import start_remote
import utils as onset_utils
from sheerwater.interfaces import get_data
from sheerwater.spatial_subdivisions import polygon_subdivision_geodataframe, get_spatial_subdivision_level

import matplotlib.pyplot as plt
import numpy as np

def sensitivity_to_definition(region, grid, start_time="2015-01-01", end_time="2025-12-31", mask="lsm"):
    """Sensitivity of onset dates to definition"""


def sensitivity_to_product(region, grid, start_time="2015-01-01", end_time="2025-12-31", mask="lsm"):
    """Sensitivity of onset dates to product"""
    sources = ["imerg_final", "chirps_v3"]
    defs = ["moron_and_robertson_onset", "chc_onset", "icpac_onset"]


    all_dates = {}
    for source in sources:
        all_dates[source] = {}
        for onset_def in defs:
            print(f"Processing {source} with {onset_def} definition")
            detect_in_time = {
                "detect": "first",
                "time_grouping": "two_seasons",
                "criteria": "greater",
                "criteria_kwargs": {
                    "threshold": 0.5,
                },
            }

            event_kwargs = {
                "detect_in_time": detect_in_time,
            }

            ds = get_data(source)(
                start_time=start_time,
                end_time=end_time,
                event=onset_def,
                event_kwargs=event_kwargs,
                grid=grid,
                mask=mask,
                region=region,
            )

            onset_dates = onset_utils.extract_dates(ds)
            all_dates[source][onset_def] = onset_dates.doy
    return all_dates
    


if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster', remote_name='onset_issues')

    region = "africa"
    grid = "global0_25"
    mask = "lsm"

    start_time = "2015-01-01"
    end_time = "2025-12-31"

    """GET REGION BOUNDARIES FOR PLOTTING"""
    try:
        level = get_spatial_subdivision_level(region)[0]
        country_gdf = polygon_subdivision_geodataframe(level=level, merged=False)
        country_gdf = country_gdf[country_gdf['region_name'] == region]
    except Exception as e:
        print(f"Error getting country boundaries for region {region}: {e}")
        country_gdf = None

    """SENSITIVITY TO DEFINITION"""

    """SENSITIVITY TO PRODUCT"""
    all_dates = sensitivity_to_product(region, grid, start_time, end_time, mask)
    products = ["imerg_final", "chirps_v3"]
    defs = ["moron_and_robertson_onset", "chc_onset", "icpac_onset"]
    focus_countries = ["kenya", "ghana", "ethiopia"]
    results = {}
    for onset_def in defs:
        dates1 = all_dates[products[0]][onset_def]
        dates2 = all_dates[products[1]][onset_def]
        date_diff = dates1 - dates2
        # get summary statistics of date_diff for each season
        group1 = [g for g in date_diff.group.values if "first" in str(g)]
        group2 = [g for g in date_diff.group.values if "second" in str(g)]
        mu1 = date_diff.sel(group=group1).mean("group").compute()
        mu2 = date_diff.sel(group=group2).mean("group").compute()
        std1 = date_diff.sel(group=group1).std("group").compute()
        std2 = date_diff.sel(group=group2).std("group").compute()
        max1 = date_diff.sel(group=group1).max("group").compute()
        max2 = date_diff.sel(group=group2).max("group").compute()
        results[onset_def] = {
            "mean1": mu1,
            "mean2": mu2,
            "std1": std1,
            "std2": std2,
            "max1": max1,
            "max2": max2,
        }
    
        




    """SPATIAL COHERENCE"""

