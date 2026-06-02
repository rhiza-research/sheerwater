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
                import pdb
                pdb.set_trace()
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
def qqmap(ds, target, target_grid, time_grouping="month_of_year", margin_in_days=None, **kwargs):
    """Map source data onto the target statistics and grid with quantile-quantile mapping."""
    # get data attributes
    from sheerwater.datasets import data_quantile_regridded, quantile_ranks

    source = kwargs['func_name']
    source_grid = kwargs['grid']
    start_time = kwargs['start_time']
    end_time = kwargs['end_time']
    region = kwargs['region']
    variable = kwargs['variable']
    prob_type = ds.attrs.get('prob_type', 'deterministic')  # datasets do not have a prob_type attribute

    # Call the regridded data quantile mapper
    source_dsq_regrid = data_quantile_regridded(
        start_time=start_time, end_time=end_time, data=source, variable=variable,
        prob_type=prob_type, time_grouping=time_grouping, margin_in_days=margin_in_days,
        source_grid=source_grid, grid=target_grid,
        region=region, recompute=False)

    # Add the grouping coordinate
    # TODO: this exists in the computation, but I'm having problems caching it, so re-adding it here
    if time_grouping is not None:
        source_dsq_regrid = groupby_time(source_dsq_regrid, time_grouping, agg_fn=None)
    elif margin_in_days is not None:
        source_dsq_regrid = groupby_time(source_dsq_regrid, 'day_of_year', agg_fn=None)

    # Question: are we always QQ-mapping the daily data?
    target_q = quantile_ranks(variable=variable, data=target, time_grouping=time_grouping,
                              margin_in_days=margin_in_days, agg_days=1, grid=target_grid,
                              region=region, recompute=False)

    # After regridding, we need to ensure that the lat/lon values are the same between target_q and source_dsq_regrid
    target_q = target_q.assign_coords(
        lat=np.round(target_q['lat'].values, 5).astype(np.float32),
        lon=np.round(target_q['lon'].values, 5).astype(np.float32),
    )
    source_dsq_regrid = source_dsq_regrid.assign_coords(
        lat=np.round(source_dsq_regrid['lat'].values, 5).astype(np.float32),
        lon=np.round(source_dsq_regrid['lon'].values, 5).astype(np.float32),
    )
    target_q = target_q.sel(lat=source_dsq_regrid['lat'].values, lon=source_dsq_regrid['lon'].values)

    """Step 3: Convert quantiles to corresponding values in target distribution"""
    import pdb; pdb.set_trace()
    # For each cell, find the target quantile probability closest to the source
    # quantile, then look up the corresponding target value at that quantile.
    tgt_vals = target_q.sel(group=source_dsq_regrid.group)  # has dim 'quantile'
    # closest_q = abs(target_q['quantile'] - source_dsq_regrid).fillna(np.inf).idxmin(dim='quantile')
    diff = abs(target_q['quantile'] - source_dsq_regrid[variable]).fillna(np.inf)
    quantile_idx = diff.argmin(dim='quantile')
    source_ds_mapped = target_q.isel(quantile=quantile_idx)


    # source_ds_mapped = tgt_vals.sel(quantile=closest_q[variable].compute())

    # Restore NaNs where input was NaN or the entire target row was NaN.
    valid = source_dsq_regrid.notnull() & tgt_vals.notnull().any(dim='quantile')
    source_ds_mapped = source_ds_mapped.where(valid, drop=False)

    # make into a dataset
    return source_ds_mapped
