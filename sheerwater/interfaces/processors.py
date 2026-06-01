"""A decorator for processors definitions."""
from functools import wraps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr

from nuthatch import cache

from sheerwater.utils import regrid as regrid_util, assign_grouping_coordinates, groupby_time, dask_remote, get_grid, convert_init_time_to_pred_time
from sheerwater.spatial_subdivisions import apply_mask, clip_to_region_envelope


PROCESSOR_REGISTRY = {}


def processor():
    """Stub decorator for processor definitions."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            name = fn.__name__.lower()

            try:
                ds = fn(*args, **kwargs)
            except TypeError as e:
                raise ValueError(f"Processor {name} requires missing processor_kwargs key. \n{e}") from e

            # Add an attribute to the dataset to indicate the event name
            ds = ds.assign_attrs({'processor': name})
            return ds

        key = fn.__name__.lower()
        PROCESSOR_REGISTRY[key] = wrapper
        return wrapper

    return decorator


def get_processor_fn(name):
    """Get a processor function from the registry."""
    if name is None:
        return None
    if name not in PROCESSOR_REGISTRY:
        raise ValueError(f"Processor {name!r} not found.")
    return PROCESSOR_REGISTRY[name]


@processor()
def regrid(ds, target_grid, method='conservative', **kwargs):  # noqa: ARG001
    """Processor for dataset regridding."""
    return regrid_util(ds, target_grid, method=method)


@processor()
def qqmap(ds, target, target_grid, target_region,
          time_grouping="month_of_year", margin_in_days=None,
          variable="precip", **kwargs):
    """Map source data onto the target statistics and grid with quantile-quantile mapping."""
    # get data attributes
    source = kwargs['func_name']
    source_grid = kwargs['grid']
    _, _, grid_res, _ = get_grid(source_grid)

    ds = clip_to_region_envelope(ds, target_region, padding=grid_res)

    # If this is a forecast with lead time, switch to valid-time indexing so we
    # can group by month-of-year (or similar) on the valid time. `prediction_timedelta`
    # stays as a broadcast dim and gets auto-aligned by apply_ufunc against the
    # lead-time-resolved source quantiles (and broadcast against the lead-free target).
    is_forecast = 'prediction_timedelta' in ds.coords
    if is_forecast:
        ds = convert_init_time_to_pred_time(ds)

    # x is a scalar value, `values` is a 1-D array over quantile ranks.
    # prediction_timedelta is left as a broadcast dim on purpose: when present
    # on both operands xarray aligns it; when present on only one side it broadcasts.
    input_core_dims = [[], ["quantile"]]

    from sheerwater.datasets import quantile_ranks
    # Question: are we always QQ-mapping the daily data?
    source_q = quantile_ranks(variable=variable, data=source, time_grouping=time_grouping, recompute=True,
                              margin_in_days=margin_in_days, agg_days=1, grid=source_grid, region=target_region)
    target_q = quantile_ranks(variable=variable, data=target, time_grouping=time_grouping,
                              margin_in_days=margin_in_days, agg_days=1, grid=target_grid, region=target_region)

    # add time group
    ds = groupby_time(ds, time_grouping, agg_fn=None)

    """Step 1: Convert precip values to quantiles based on source distribution"""
    qvalues = source_q['quantile'].values

    def value_to_quantile(x, values):
        if np.all(np.isnan(values)) or np.isnan(x):
            return np.nan
        idx = np.argmin(np.abs(values - x))
        return qvalues[idx]

    source_dsq = xr.apply_ufunc(value_to_quantile,
                                ds[variable], source_q[variable].sel(group=ds.group),
                                input_core_dims=input_core_dims, output_core_dims=[[]],
                                vectorize=True, dask="parallelized", output_dtypes=[float])

    """Step 2: Regrid source quantiles to target grid"""
    source_dsq = source_dsq.sortby('lat')
    import pdb; pdb.set_trace()
    source_dsq_regrid = regrid_util(source_dsq, target_grid, method="linear", region=target_region)

    """Step 3: Convert quantiles to corresponding values in target distribution"""
    target_qvalues = target_q['quantile'].values

    def quantiles_to_values(quantile, qvalues):
        if np.all(np.isnan(qvalues)) or np.isnan(quantile):
            return np.nan
        idx = np.argmin(np.abs(target_qvalues - quantile))
        value = qvalues[int(idx)]
        return value

    # After regridding, we need to ensure that the lat/lon values are the same between target_q and source_dsq_regrid
    target_q['lat'] = np.round(target_q['lat'], 5).astype(np.float32)
    target_q['lon'] = np.round(target_q['lon'], 5).astype(np.float32)
    source_dsq_regrid['lat'] = np.round(source_dsq_regrid['lat'], 5).astype(np.float32)
    source_dsq_regrid['lon'] = np.round(source_dsq_regrid['lon'], 5).astype(np.float32)
    target_q = target_q.sel(lat=source_dsq_regrid['lat'].values, lon=source_dsq_regrid['lon'].values)

    # Select target_q to match the dimensions of source_dsq_regrid
    source_ds_mapped = xr.apply_ufunc(quantiles_to_values,
                                      source_dsq_regrid, target_q[variable].sel(group=source_dsq_regrid.group),
                                      input_core_dims=input_core_dims, output_core_dims=[[]],
                                      vectorize=True, dask="parallelized", output_dtypes=[float])

    # cleanup
    source_ds_mapped = source_ds_mapped.drop_vars("group")
    # make into a dataset
    source_ds_mapped = source_ds_mapped.to_dataset(name=variable)
    return source_ds_mapped
