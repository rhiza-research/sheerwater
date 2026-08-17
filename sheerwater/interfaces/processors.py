"""A decorator for processors definitions."""
from functools import wraps
import numpy as np
import xarray as xr

from sheerwater.utils import regrid as regrid_util, groupby_time


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
def qqmap(ds, target, target_grid, time_grouping="month_of_year", margin_in_days=None, n_quantiles=20, **kwargs):
    """Map source data onto the target statistics and grid with quantile-quantile mapping."""
    # get data attributes
    from sheerwater.downscale_data import data_quantile_regridded, quantile_ranks

    source = kwargs['func_name']
    source_grid = kwargs['grid']
    start_time = kwargs['start_time']
    end_time = kwargs['end_time']
    region = kwargs['region']
    variable = kwargs['variable']
    agg_days = kwargs['agg_days']
    prob_type = ds.attrs.get('prob_type', 'deterministic')  # datasets do not have a prob_type attribute
    attrs = ds.attrs

    # Call the regridded data quantile mapper
    source_dsq_regrid = data_quantile_regridded(
        start_time=start_time, end_time=end_time, data=source, variable=variable,
        agg_days=agg_days,
        prob_type=prob_type, time_grouping=time_grouping, margin_in_days=margin_in_days,
        source_grid=source_grid, grid=target_grid, n_quantiles=n_quantiles,
        region=region, recompute=False)

    # Add the grouping coordinate
    # TODO: this exists in the computation, but I'm having problems caching it, so I
    # dropped it and am re-adding it here
    if margin_in_days is None:
        source_dsq_regrid = groupby_time(source_dsq_regrid, time_grouping, agg_fn=None)
    else:
        source_dsq_regrid = groupby_time(source_dsq_regrid, 'day_of_year', agg_fn=None)

    target_q = quantile_ranks(variable=variable, data=target, time_grouping=time_grouping,
                              agg_days=agg_days,
                              margin_in_days=margin_in_days, grid=target_grid,
                              n_quantiles=n_quantiles, region=region, recompute=False)

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
    target_qvalues = target_q['quantile'].values  # (Q,) probability levels, sorted

    def quantiles_to_values(rank, qvals):
        # Find the index of the closest target quantile to the source quantile
        idx = np.abs(target_qvalues - rank[..., None]).argmin(axis=-1)
        # Take the target value at the closest quantile
        out = np.take_along_axis(qvals, idx[..., None], axis=-1)[..., 0]
        # If the source quantile is nan, or all the target values are nan, return nan
        bad = np.isnan(rank) | np.all(np.isnan(qvals), axis=-1)
        return np.where(bad, np.nan, out)

    # Align the broadcast target table to source_dsq_regrid's chunking before
    # the gufunc so blockwise doesn't replicate a single big spatial chunk
    # into many small ones (causes "Increasing chunks by factor of N" warnings).
    tgt_table = target_q[variable].sel(group=source_dsq_regrid.group)
    chunks_align = {d: source_dsq_regrid.chunks[d]
                    for d in ("time", "lat", "lon") if d in source_dsq_regrid.chunks}
    tgt_table = tgt_table.chunk({**chunks_align, "quantile": -1})

    source_ds_mapped = xr.apply_ufunc(
        quantiles_to_values,
        source_dsq_regrid[variable],
        tgt_table,
        input_core_dims=[[], ["quantile"]],
        output_core_dims=[[]],
        dask="parallelized",
        output_dtypes=[np.float32],
    )

    # Clean up
    source_ds_mapped = source_ds_mapped.to_dataset(name=variable)
    # ensure attributes pass through, but not region and mask, as we've removed them from the source dataset
    if 'region' in attrs:
        del attrs['region']
    if 'mask' in attrs:
        del attrs['mask']
    source_ds_mapped = source_ds_mapped.assign_attrs(attrs)
    # Update the grid and agg attribute
    source_ds_mapped = source_ds_mapped.assign_attrs({'grid': target_grid, 'agg_days': agg_days})

    # make into a dataset
    return source_ds_mapped
