"""Utility functions for benchmarking."""
from .data_utils import get_anomalies, regrid, roll_and_agg
from .forecaster_utils import convert_init_time_to_pred_time, get_variable
from .general_utils import load_netcdf, load_object, load_zarr, plot_ds, plot_ds_map, run_in_parallel, write_zarr
from .grouping_utils import groupby_region, groupby_time, latitude_weights, mean_or_sum
from .plotting_utils import plot_by_region
from .remote import dask_remote, start_remote
from .secrets import cdsapi_secret, ecmwf_secret, gap_secret, salient_secret, tahmo_secret, huggingface_read_token
from .space_utils import (
    get_grid_ds,
    get_globe_slice,
    get_grid,
    is_wrapped,
    lon_base_change,
    snap_point_to_grid,
    base180_to_base360,
    base360_to_base180,
    check_bases,
    add_spatial_attrs,
    check_spatial_attr,
    is_station_grid,
)
from .task_utils import first_satisfied_date
from .time_utils import (
    add_dayofyear,
    assign_grouping_coordinates,
    convert_group_to_time,
    date_mean,
    doy_mean,
    generate_dates_in_between,
    get_dates,
    is_valid_forecast_date,
    pad_with_leapdays,
    shift_by_days,
)

# Use __all__ to define what is part of the public API.
__all__ = [
    "dask_remote",
    "start_remote",
    "cdsapi_secret",
    "ecmwf_secret",
    "salient_secret",
    "tahmo_secret",
    "gap_secret",
    "huggingface_read_token",
    "roll_and_agg",
    "get_anomalies",
    "regrid",
    "load_netcdf",
    "load_zarr",
    "write_zarr",
    "load_object",
    "plot_ds",
    "plot_ds_map",
    "plot_by_region",
    "run_in_parallel",
    "get_grid",
    "get_grid_ds",
    "is_wrapped",
    "base360_to_base180",
    "base180_to_base360",
    "check_bases",
    "lon_base_change",
    "get_globe_slice",
    "snap_point_to_grid",
    "is_valid_forecast_date",
    "generate_dates_in_between",
    "get_dates",
    "pad_with_leapdays",
    "add_dayofyear",
    "shift_by_days",
    "groupby_region",
    "latitude_weights",
    "mean_or_sum",
    "groupby_time",
    "assign_grouping_coordinates",
    "convert_group_to_time",
    "date_mean",
    "doy_mean",
    "get_variable",
    "convert_init_time_to_pred_time",
    "first_satisfied_date",
    "add_spatial_attrs",
    "check_spatial_attr",
]
