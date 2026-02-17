"""Plotting utilities for metrics and regions."""
import os

import matplotlib.pyplot as plt


def to_name(name):
    """Convert a name to a more readable format."""
    if name == 'mae':
        return 'Mean Absolute Error'
    elif name == 'mse':
        return 'Mean Squared Error'
    elif name == 'rmse':
        return 'Root Mean Squared Error'
    elif name == 'bias':
        return 'Bias'
    elif name == 'crps':
        return 'Continuous Ranked Probability Score'
    elif name == 'brier':
        return 'Brier Score'
    elif name == 'smape':
        return 'Symmetric Mean Absolute Percentage Error'
    elif name == 'mape':
        return 'Mean Absolute Percentage Error'
    elif name == 'seeps':
        return 'Spatial Error in Ensemble Prediction Scale'
    elif 'heidke' in name:
        return f'Heidke Skill Score at {", ".join([mm.split("-")[-1] for mm in name.split("-")[:-1]])} mm'
    elif 'pod' in name:
        return f'Probability of Detection at {name.split("-")[-1]} mm'
    elif 'far' in name:
        return f'False Alarm Rate at {name.split("-")[-1]} mm'
    elif 'ets' in name:
        return f'Equitable Threat Score at {name.split("-")[-1]} mm'
    elif 'csi' in name:
        return f'Critical Success Index at {name.split("-")[-1]} mm'
    elif 'frequency_bias' in name:
        return f'Frequency Bias at {name.split("-")[-1]} mm'
    elif name == 'acc':
        return 'Anomaly Correlation Coefficient'
    elif name == 'pearson':
        return 'Pearson Correlation'
    else:
        return name


def bounds(variable):
    """Get the bounds for a variable."""
    if variable == 'mae':
        return (0.0, None)
    elif variable == 'mse':
        return (0.0, None)
    elif variable == 'rmse':
        return (0.0, None)
    elif variable == 'bias':
        return (None, None)
    elif variable == 'crps':
        return (0.0, None)
    elif variable == 'brier':
        return (0.0, None)
    elif variable == 'smape':
        return (0.0, None)
    elif variable == 'mape':
        return (0.0, None)
    elif variable == 'seeps':
        return (0.0, 3.0)
    elif 'heidke' in variable:
        return (0.0, 1.0)
    elif 'pod' in variable:
        return (0.0, 1.0)
    elif 'far' in variable:
        return (0.0, 1.0)
    elif 'ets' in variable:
        return (0.0, 1.0)
    elif 'csi' in variable:
        return (0.0, 1.0)
    elif 'frequency_bias' in variable:
        return (None, None)
    elif variable == 'acc':
        return (-1.0, 1.0)
    elif variable == 'pearson':
        return (-1.0, 1.0)
    elif variable == 'coverage':
        return (0.0, None)
    else:
        return (None, None)


def plot_by_region(ds, space_grouping, region=None, variable=None, file_string='none', title='Regional Map', plot_kwargs=None):
    """Plot a variable from an xarray dataset as (lon, lat) points with region boundaries overlaid.

    Uses polygon_subdivision_geodataframe for the overlay. When region is provided
    with space_grouping 'admin_1' or 'admin_2', overlays all admin1 or admin2
    subdivisions within that country.

    Args:
        ds: xarray DataArray or Dataset with 'lat' and 'lon' coordinates.
        space_grouping: Polygon subdivision level for the overlay, e.g. 'country',
            'admin_1', 'admin_2', 'continent', 'subregion', 'region_un', 'region_wb',
            or custom levels like 'sheerwater_region', 'meteorological_zone'.
        region: Optional. If provided, only overlay subdivisions within this region
            (e.g. country name like 'ghana' or 'kenya' to overlay admin_1 or
            admin_2 boundaries for that country). If None, overlay all regions at
            the given space_grouping level.
        variable: Variable name if ds is a Dataset. If None and ds is a
            DataArray, ds is plotted directly.
        file_string: File path string for saving the plot.
        title: Title for the plot.

    Returns:
        matplotlib axes object
    """
    from sheerwater.spatial_subdivisions import (
        polygon_subdivision_geodataframe,
        clean_spatial_subdivision_name,
    )

    gdf = polygon_subdivision_geodataframe(space_grouping)

    if region is not None:
        region_clean = clean_spatial_subdivision_name(region)
        if space_grouping == 'country':
            gdf = gdf[gdf['region_name'] == region_clean]
        else:
            # admin_1, admin_2, etc.: region_name is "country-..." or "country-admin1-..."
            gdf = gdf[gdf['region_name'].str.startswith(region_clean + '-')]
        if gdf.empty:
            raise ValueError(
                f"No regions found for space_grouping={space_grouping!r} "
                f"and region={region!r} (cleaned: {region_clean!r})."
            )

    # Extract the data
    if variable is not None:
        try:
            data = ds[variable]
        except KeyError:
            data = ds
    else:
        data = ds

    if hasattr(data, 'compute'):
        data = data.compute()

    if 'time' in data.dims:
        data = data.isel(time=0)

    # vmin, vmax = bounds(variable) if variable else (None, None)
    plot_kwargs.update({'x': 'lon'})
    # if vmin is not None:
    #     # plot_kwargs['vmin'] = vmin
    #     plot_kwargs['vmin'] = -2.0
    # if vmax is not None:
    #     # plot_kwargs['vmax'] = vmax
    #     plot_kwargs['vmax'] = 2.0

    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    data.plot(ax=ax, **plot_kwargs)

    # Overlay region boundaries on top
    gdf.plot(ax=ax, facecolor='none', edgecolor='grey', linewidth=0.5, alpha=0.5)

    ax.set_title(title, fontsize=14, pad=10)
    plt.tight_layout()

    if not os.path.exists('metric_maps'):
        os.makedirs('metric_maps')
    region_slug = region if region is not None else space_grouping
    var_slug = variable if variable is not None else 'value'
    plt.savefig(f'metric_maps/{var_slug}_{region_slug}_{file_string}_map.png')
    return ax
