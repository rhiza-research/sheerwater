"""A decorator for processors definitions."""
from functools import wraps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr

from nuthatch import cache

from sheerwater.utils import regrid as regrid_util, assign_grouping_coordinates, groupby_time, dask_remote
from sheerwater.spatial_subdivisions import apply_mask, get_region_envelope


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


@cache(cache_args=['variable', 'data', 'time_grouping', 'agg_days', 'grid', 'region'])
def qqmap_outputs(variable, data, time_grouping, agg_days, grid, region):
    return source_q, target_q


@processor()
def qqmap(ds, source, target, target_grid, time_grouping="month_of_year", variable="precip", **kwargs):
    """Map source data onto the target statistics and grid with quantile-quantile mapping."""
    # get data attributes
    region = kwargs['region']
    source_grid = kwargs['grid']

    import pdb; pdb.set_trace()
    source_envelope = get_region_envelope(region)

    # get the source and target quantile values
    if 'prediction_timedelta' in ds.coords:
        forecast_or_data = 'forecast'
        input_core_dims = [["prediction_timedelta"], ["quantile"]]
    else:
        forecast_or_data = 'data'
        input_core_dims = [[], ["quantile"]]

    from sheerwater.climatology import quantile_ranks
    # Question: are we always QQ-mapping the daily data?
    source_q = quantile_ranks(variable=variable, data=source, time_grouping=time_grouping,
                              agg_days=1, grid=source_grid, region=region)
    target_q = quantile_ranks(variable=variable, data=target, time_grouping=time_grouping,
                              agg_days=1, grid=source_grid, region=region)

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
    source_dsq_regrid = regrid(source_dsq, target_grid, method="linear", region=region)

    """Step 3: Convert quantiles to corresponding values in target distribution"""
    target_qvalues = target_q['quantile'].values

    def quantiles_to_values(quantile, qvalues):
        if np.all(np.isnan(qvalues)) or np.isnan(quantile):
            return np.nan
        idx = np.argmin(np.abs(target_qvalues - quantile))
        value = qvalues[int(idx)]
        return value

    source_ds_mapped = xr.apply_ufunc(quantiles_to_values,
                                      source_dsq_regrid, target_q[variable].sel(group=source_dsq_regrid.group),
                                      input_core_dims=[[], ["quantile"]], output_core_dims=[[]],
                                      vectorize=True, dask="parallelized", output_dtypes=[float])

    # cleanup
    source_ds_mapped = source_ds_mapped.drop_vars("group")
    # make into a dataset
    source_ds_mapped = source_ds_mapped.to_dataset(name=variable)
    # apply the mask after downscaling
    import pdb
    pdb.set_trace()
    return source_ds_mapped
