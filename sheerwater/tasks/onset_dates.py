"""Cache onset dates for regions, definitions, and time groupings.
regions: india, western_africa, eastern_africa
definitions: moron_and_robertson_onset, chc_onset, icpac_onset
time_groupings: year, imd_season, two_seasons
"""

from sheerwater.interfaces import get_data
from sheerwater.utils import dask_remote    
from nuthatch import cache
from sheerwater.utils import start_remote

import numpy as np

@dask_remote
@cache(cache_args=['source', 'grid', 'region', 'event_name', 'time_grouping'])
def onset_dates(start_time, end_time, source, grid, region, event_name, time_grouping, mask="lsm", recompute=False):
    detect_in_time = {
        "detect": "first",
        "time_grouping": time_grouping,
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
        event=event_name,
        event_kwargs=event_kwargs,
        grid=grid,
        mask=mask,
        region=region,
        recompute=recompute
    )

    onset_dates = extract_dates(ds)
    return onset_dates
    

def extract_dates(ds):
    # Compute day-of-year
    ds = ds.assign_coords(doy=ds.time.dt.dayofyear)

    # Remove null seasonal groups
    is_null_group = ds["group"].astype(str).str.contains("None")
    ds = ds.where(~is_null_group, drop=True)

    # Determine where SoS exists
    has_sos = ds["precip"].groupby("group").sum(
        dim="time",
        skipna=True,
        min_count=1,
    )

    # Get first occurrence of SoS
    is_sos = ds["precip"].groupby("group").map(
        lambda x: x.idxmax(dim="time", skipna=True)
    )

    is_sos = is_sos.compute()

    # Select matching timestamps
    sos_time = ds.drop_vars("group").sel(
        time=is_sos,
        method="nearest",
    )

    # Mask invalid SoS locations
    sos_time["doy"] = sos_time["doy"].where(
        has_sos > 0,
        np.nan,
        drop=False,
    )

    sos_time["time"] = sos_time["time"].where(
        has_sos > 0,
        np.datetime64("NaT"),
        drop=False,
    )

    return sos_time

if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster', remote_name='onset_dates')

    # Run caching for all onset dates
    start_time = "2015-01-01"
    end_time = "2025-12-31"
    grid = "global0_25"
    mask = "lsm"

    definitions = ["moron_and_robertson_onset", "chc_onset", "icpac_onset"]

    """India"""
    region = "india"
    india_time_groups = ["year", "imd_season"]
    for definition in definitions:
        for time_group in india_time_groups:
            print(f"------{region} {definition} {time_group}------")
            onset_dates(start_time, end_time, "imerg_final", grid, region, definition, time_group, mask, recompute=True)
            onset_dates(start_time, end_time, "chirps_v3", grid, region, definition, time_group, mask, recompute=True)
    
    """Western Africa"""
    region = "nimbus_west_africa"
    western_africa_time_groups = ["year"]
    for definition in definitions:
        for time_group in western_africa_time_groups:
            print(f"------{region} {definition} {time_group}------")
            onset_dates(start_time, end_time, "imerg_final", grid, region, definition, time_group, mask, recompute=True)
            onset_dates(start_time, end_time, "chirps_v3", grid, region, definition, time_group, mask, recompute=True)

    """Eastern Africa"""
    region = "nimbus_east_africa"
    eastern_africa_time_groups = ["two_seasons", "year"]
    for definition in definitions:
        for time_group in eastern_africa_time_groups:
            print(f"------{region} {definition} {time_group}------")
            onset_dates(start_time, end_time, "imerg_final", grid, region, definition, time_group, mask, recompute=True)
            onset_dates(start_time, end_time, "chirps_v3", grid, region, definition, time_group, mask, recompute=True)
