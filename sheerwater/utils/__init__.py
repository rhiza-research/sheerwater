"""Utility functions for benchmarking."""
from .remote import dask_remote, start_remote
from .secrets import cdsapi_secret, ecmwf_secret, salient_secret, salient_auth, tahmo_secret, gap_secret
from .data_utils import (roll_and_agg, get_anomalies, regrid)
from .general_utils import (load_netcdf, write_zarr, load_zarr, load_object, plot_ds,
                            plot_ds_map, run_in_parallel, get_datasource_fn)

from .region_utils import get_region_level, get_region_data, plot_by_region

from .space_utils import (get_grid, get_grid_ds, is_wrapped,
                          base360_to_base180, base180_to_base360, check_bases, clip_region,
                          lon_base_change, get_globe_slice, apply_mask,
                          get_mask, snap_point_to_grid)

from .time_utils import (is_valid_forecast_date, generate_dates_in_between, get_dates,
                         pad_with_leapdays, add_dayofyear, shift_by_days,
                         groupby_time, assign_grouping_coordinates,
                         convert_group_to_time, date_mean, doy_mean)

from .forecaster_utils import (get_variable, forecast, convert_init_time_to_pred_time)

from .task_utils import first_satisfied_date

# Use __all__ to define what is part of the public API.
__all__ = [
    "dask_remote",
    "start_remote",
    "cdsapi_secret",
    "ecmwf_secret",
    "salient_secret",
    "salient_auth",
    "tahmo_secret",
    "gap_secret",
    "roll_and_agg",
    "get_anomalies",
    "regrid",
    "load_netcdf",
    "write_zarr",
    "load_zarr",
    "load_object",
    "plot_ds",
    "plot_ds_map",
    "run_in_parallel",
    "get_datasource_fn",
    "get_region_level",
    "get_region_data",
    "get_grid",
    "get_grid_ds",
    "is_wrapped",
    "base360_to_base180",
    "base180_to_base360",
    "check_bases",
    "clip_region",
    "lon_base_change",
    "get_globe_slice",
    "apply_mask",
    "get_mask",
    "is_valid_forecast_date",
    "generate_dates_in_between",
    "get_dates",
    "pad_with_leapdays",
    "add_dayofyear",
    "shift_by_days",
    "groupby_time",
    "assign_grouping_coordinates",
    "convert_group_to_time",
    "date_mean",
    "doy_mean",
    "forecast",
    "get_variable",
    "convert_init_time_to_pred_time",
    "first_satisfied_date",
    "snap_point_to_grid",
    "plot_by_region",
]
