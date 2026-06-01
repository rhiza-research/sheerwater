from sheerwater.utils import start_remote
from sheerwater.interfaces import get_data

import numpy as np


if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster', remote_name='onset_issues')

    region = "kenya"
    grid = "global0_25"
    mask = "lsm"
    time_grouping = "kenya_rainy_season"
    start_time = "2015-01-01"
    end_time = "2025-12-31"

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

    datasource = "imerg_final"
    # Load event data
    ds = get_data(datasource)(
        start_time=start_time,
        end_time=end_time,
        event="chc_onset",
        event_kwargs=event_kwargs,
        grid=grid,
        mask=mask,
        region=region,
    )

    import pdb; pdb.set_trace()

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

    import pdb; pdb.set_trace()
    