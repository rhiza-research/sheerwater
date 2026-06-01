"""Get the onset date for a given event."""
import numpy as np
from sheerwater.interfaces import get_data

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