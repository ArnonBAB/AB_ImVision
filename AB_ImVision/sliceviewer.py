# Functions for viewing data
# display_slice and interactive_slice_viewer together create a function that is similar to Matlab's sliceViewer
# Made by: Arnon A.B.
# Version 1.0.0
# 09/10/2024

############################################################################################################################
############################################################################################################################
############################################################################################################################

# Example, to use the function to view a volume, use: 

# from AB_ImVision import slice_viewer 
# interactive_slice_viewer(volume, '[1 0 0]')

############################################################################################################################
############################################################################################################################
############################################################################################################################

# TODO Removing the flickering caused by constantly using plot.show. Need to keep the figure open and just update the image data.

from matplotlib.colors import Colormap
from networkx import volume
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, IntSlider, FloatSlider, Dropdown, fixed

# Function to create and display an interactive viewer
def slice_viewer(volume: np.ndarray, voxel_size: tuple = (1.0,1.0,1.0), unit: str = 'um', default_slice_direction: str ='[0 0 1]', cmap: Colormap | str = 'gray', vmin: float=None, vmax: float=None, figsize: tuple=(8, 6)):
    """
    Creates a sliceviewer to scroll through the 2D slices of a 3D volume.

    Args:
        volume (numpy.ndarray): The 3D volume to be visualized.
        default_slice_direction (str, optional): The default slice direction to display. 
            Accepted values are '[1 0 0]', '[0 1 0]', '[0 0 1]'. Default is '[0 0 1]'.
        voxel_size (tuple, optional): The size of each voxel in the volume. Default is (1.0, 1.0, 1.0).
        unit (str, optional): The unit of measurement for the voxel size. Default is 'um'.
        cmap (str or Colormap), optional): Colormap to use for displaying the slices. Default is 'gray'.
        vmin (float, optional): Minimum value for color scaling. If None, it will be set to the minimum of the volume.
        vmax (float, optional): Maximum value for color scaling. If None, it will be set to the maximum of the volume.
        figsize (tuple, optional): Size of the figure in inches. Default is (8, 6).
    """

    if vmin is None:
        vmin = np.min(volume)
    if vmax is None:
        vmax = np.max(volume)

    # Create the dropdown for slice direction with a specified default value
    slice_direction_widget = Dropdown(
        options=['[1 0 0]', '[0 1 0]', '[0 0 1]'],
        value=default_slice_direction,  # Use the provided default value
        description='Slice Direction:',
        style={'description_width': 'initial'}
    )

    # Create the slider for slice index
    slice_index_widget = IntSlider(min=0, max=volume.shape[next((i for i, v in enumerate(default_slice_direction.strip('[]').split()) if v == '1'), -1)]-1, step=1, value=0, description='Slice Index')

    # Create the slider for vmin and vmax
    vmin_slider_widget = FloatSlider(min=vmin, max=vmax, step=(vmax - vmin) / 10000, value=np.min(volume), description='Colorbar Min', readout_format='.4g')
    vmax_slider_widget = FloatSlider(min=vmin, max=vmax, step=(vmax - vmin) / 10000, value=np.max(volume), description='Colorbar Max', readout_format='.4g')

    # Function to update the slice index range based on selected direction
    def update_slice_index_range(change):
        new_direction = change['new']  # Get the new value of slice_direction
        if new_direction == '[1 0 0]':  # X direction
            slice_index_widget.max = volume.shape[0] - 1
        elif new_direction == '[0 1 0]':  # Y direction
            slice_index_widget.max = volume.shape[1] - 1
        elif new_direction == '[0 0 1]':  # Z direction
            slice_index_widget.max = volume.shape[2] - 1
        slice_index_widget.value = 0  # Reset to the first slice when direction changes

    slice_direction_widget.observe(update_slice_index_range, names='value')

    # Call the interactive slice viewer using interact
    interact(_display_slice, volume=fixed(volume), voxel_size=fixed(voxel_size), unit=fixed(unit), slice_index=slice_index_widget, vmin=vmin_slider_widget, vmax=vmax_slider_widget, slice_direction=slice_direction_widget, figsize=fixed(figsize), cmap=fixed(cmap))


# Function to display a 2D slice from the 3D volume with a consistent color scale
def _display_slice(volume, slice_index, slice_direction, voxel_size = (1.0,1.0,1.0), unit='um', vmin=None, vmax=None, figsize=None, cmap='gray'):
    if slice_direction not in ['[1 0 0]', '[0 1 0]', '[0 0 1]']:
        raise ValueError(f"Invalid slice direction '{slice_direction}'. Accepted directions are :[1 0 0]', '[0 1 0]', '[0 0 1]")

    d1, d2, d3 = voxel_size
    n1, n2, n3 = volume.shape

    if vmin is None:
        vmin = np.min(volume)
    if vmax is None:
        vmax = np.max(volume)

    plt.figure(figsize=figsize)
    
    # Check which direction is selected by matching the vector
    if slice_direction == '[1 0 0]':  # 1st direction
        plt.xlabel(f'Z axis ({unit})')
        plt.ylabel(f'X axis ({unit})')
        plt.imshow(volume[slice_index, :, :], cmap=cmap, vmin=vmin, vmax=vmax, extent=(0, n3*d3 , 0, n2*d2), aspect='equal', origin='lower')
        plt.title(f'Slice {slice_index} along Y axis')
    elif slice_direction == '[0 1 0]':  # 2nd direction
        plt.xlabel(f'Z axis ({unit})')
        plt.ylabel(f'Y axis ({unit})')
        plt.imshow(volume[:, slice_index, :], cmap=cmap, vmin=vmin, vmax=vmax, extent=(0,n3*d3, 0, n1*d1), aspect='equal', origin='lower')
        plt.title(f'Slice {slice_index} along X axis')
    elif slice_direction == '[0 0 1]':  # 3rd direction
        plt.xlabel(f'Y axis ({unit})')
        plt.ylabel(f'X axis ({unit})')
        plt.imshow(volume[:, :, slice_index], cmap=cmap, vmin=vmin, vmax=vmax, extent=(0, n2*d2, 0, n1*d1), aspect='equal', origin='lower')
        plt.title(f'Slice {slice_index} along Z axis')

    plt.colorbar()
    plt.show()








