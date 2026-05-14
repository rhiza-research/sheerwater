from sheerwater.interfaces import get_data
from sheerwater.utils.data_utils import regrid
from sheerwater.utils.time_utils import assign_grouping_coordinates

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr


def qqmap(ds, source, target, target_grid, time_grouping="month_of_year", variable="precip"):
    """
    Map source data onto the target statistics and grid with quantile-quantile mapping.
    """
    # get data attributes
    region = ds.attrs['post_processed_region']
    source_grid = ds.attrs['post_processed_grid']
    # get the source and target quantile values
    source_q = get_rank(source, region=region, grid=source_grid, time_grouping=time_grouping)
    target_q = get_rank(target, region=region, grid=target_grid, time_grouping=time_grouping)

    # add time group
    ds = assign_grouping_coordinates(ds, time_grouping)

    """Step 1: Convert precip values to quantiles based on source distribution"""
    qvalues = source_q['quantile'].values
    def value_to_quantile(x, values):
        if np.all(np.isnan(values)) or np.isnan(x):
            return np.nan
        idx = np.argmin(np.abs(values - x))
        return qvalues[idx]
    source_dsq = xr.apply_ufunc(value_to_quantile,
                                ds[variable], source_q[variable].sel(group=ds.group), 
                                input_core_dims=[[], ["quantile"]], output_core_dims=[[]], 
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

    return source_ds_mapped


def get_rank(data_source, time_grouping, region="global", agg_days=5, grid="global1_5", start_year=2015, end_year=2024):
    """Get quantile ranks of a dataset using history from start_year to end_year."""
    start_time = f"{start_year}-01-01"
    end_time = f"{end_year}-12-31"
    ds = get_data(data_source)(start_time, end_time, grid=grid, region=region, agg_days=agg_days)
    ds = assign_grouping_coordinates(ds, time_grouping)

    ranks = np.arange(0, 1, 0.1)
    # round ranks to 1 decimal place
    ranks = np.round(ranks, 1)
    ds = ds.chunk({"time": -1})
    qs = ds.groupby("group").quantile(q=ranks, dim="time", skipna=True)
    return qs