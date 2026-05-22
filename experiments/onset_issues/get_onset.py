"""Get the onset date for a given event."""
import numpy as np
from sheerwater.interfaces import get_data

def get_sos_dates(
    datasource,
    event_name,
    start_time="2000-01-01",
    end_time="2025-12-31",
    grid="global0_25",
    mask="lsm",
    region="kenya",
    time_grouping="kenya_rainy_season ",
):
    """
    Generate start of season (SoS) dates for a given event.

    Parameters
    ----------
    datasource : str
        Datasource name (e.g. 'chirps_v3', 'imerg_final').
    event : str
        Event name to pass to get_data().
    event_kwargs : dict
        Keyword arguments for the event definition.
    start_time : str
        Start date for the dataset.
    end_time : str
        End date for the dataset.
    grid : str
        Grid resolution.
    mask : str
        Mask to apply.
    region : str
        Region name.

    Returns
    -------
    xarray.Dataset
        Dataset containing SoS times and day-of-year values.
    """

    detect_in_time = {
        "detect": "first",
        "time_grouping": time_grouping,
        "criteria": "greater",
        "criteria_kwargs": {
            "threshold": 0.5,
        },
    }

    event_kwargs = {
        "event_name": event_name,
        "detect_in_time": detect_in_time,
    }

    # Load event data
    ds = get_data(datasource)(
        start_time=start_time,
        end_time=end_time,
        event="start_of_season_by_spells",
        event_kwargs=event_kwargs,
        grid=grid,
        mask=mask,
        region=region,
    )

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