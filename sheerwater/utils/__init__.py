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
                         assign_grouping_coordinates,
                         convert_group_to_time, date_mean, doy_mean)

from .forecaster_utils import (get_variable, forecast, convert_init_time_to_pred_time)

from .grouping_utils import groupby_region,  latitude_weights, mean_or_sum, groupby_time

from .task_utils import first_satisfied_date

from .gpu_utils import (is_gpu_available, to_gpu, to_cpu,
                        gpu_context, maybe_to_gpu, maybe_to_cpu,
                        enable_gpu, is_gpu_enabled, is_gpu_mode_requested,
                        auto_gpu, auto_cpu, gpu_ones_like, gpu_zeros_like,
                        benchmark, benchmark_comparison,
                        get_dask_performance_report, print_dask_dashboard_link,
                        get_gpu_status, check_worker_gpu_status)

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
    "groupby_region",
    "latitude_weights",
    "mean_or_sum",
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
    "is_gpu_available",
    "to_gpu",
    "to_cpu",
    "gpu_context",
    "maybe_to_gpu",
    "maybe_to_cpu",
    "enable_gpu",
    "is_gpu_enabled",
    "is_gpu_mode_requested",
    "auto_gpu",
    "auto_cpu",
    "gpu_ones_like",
    "gpu_zeros_like",
    "benchmark",
    "benchmark_comparison",
    "get_dask_performance_report",
    "print_dask_dashboard_link",
    "get_gpu_status",
    "check_worker_gpu_status",
]
