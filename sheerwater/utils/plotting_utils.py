"""Plotting utilities for metrics and regions."""
import os

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .region_utils import region_data


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


def plot_by_region(ds, region, variable, file_string='none', title='Regional Map'):
    """Plot a variable from an xarray dataset by region.

    Args:
        ds: xarray DataArray or Dataset with a 'region' coordinate
        region: Region level or specific region name to plot
        variable: Variable name if ds is a Dataset (optional)
        file_string: File path string for saving the plot
        title: Title for the plot

    Returns:
        matplotlib axes object
    """
    # Get the region GeoDataFrame and metric bounds
    gdf = region_data(region)
    # Extract the data values
    try:
        data = ds[variable]
    except KeyError:
        data = ds

    # Convert to numpy array if it's a dask array
    if hasattr(data, 'compute'):
        data = data.compute()

    # Extract values for each region in the GeoDataFrame
    values = []
    for region_name in gdf.region_name:
        try:
            # Select the region and extract the scalar value
            region_value = data.sel(region=region_name)
            # Handle case where selection might still have dimensions
            if region_value.size > 1:
                # If there are multiple values, take the first or mean
                region_value = float(region_value.values.flatten()[0])
            else:
                region_value = float(region_value.values)
            values.append(region_value)
        except (KeyError, ValueError):
            # Region not found in dataset, use NaN
            values.append(np.nan)

    # Add values to GeoDataFrame
    gdf['value'] = values

    # Calculate 95th percentile for vmax (excluding NaNs)
    vmin, vmax = bounds(variable)
    values_array = np.array(values)
    valid_values = values_array[~np.isnan(values_array)]
    if vmin is None:
        vmin = np.percentile(valid_values, 5)
    if vmax is None:
        vmax = np.percentile(valid_values, 95)

    # Reproject to a better projection for world maps (Robinson projection)
    # Robinson is good for world maps, preserves area relationships well
    gdf_projected = gdf.to_crs('ESRI:54030')  # Robinson projection

    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))

    # Plot the choropleth map (without legend, we'll add it manually)
    gdf_projected.plot(column='value', ax=ax, legend=False,
                       cmap='viridis', edgecolor='black', linewidth=0.5,
                       vmin=vmin,
                       vmax=vmax,
                       missing_kwds={'color': 'red', 'edgecolor': 'black'})

    # Create colorbar with same height as plot and larger tick labels
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.1)
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis,
                               norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cax)
    cbar.ax.tick_params(labelsize=12)

    # Remove axis labels (not meaningful in projected coordinates)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Set title
    ax.set_title(title, fontsize=14, pad=10)

    plt.tight_layout()

    # Ensure colorbar height matches plot height exactly
    ax_pos = ax.get_position()
    cax_pos = cax.get_position()
    cax.set_position([cax_pos.x0, ax_pos.y0, cax_pos.width, ax_pos.height])
    # Save
    if not os.path.exists('metric_maps'):
        os.makedirs('metric_maps')
    plt.savefig(f'metric_maps/{variable}_{region}_{file_string}_map.png')
    return ax
