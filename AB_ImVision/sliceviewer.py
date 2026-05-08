# Functions for viewing data
# display_slice and interactive_slice_viewer together create a function that is similar to Matlab's sliceViewer
# Made by: Arnon A.B.
# Version 1.0.0
# 09/10/2024

############################################################################################################################
############################################################################################################################
############################################################################################################################

# Example, to use the function to view a volume, use: 

# from AB_ImVision import interactive_slice_viewer 
# interactive_slice_viewer(volume, '[1 0 0]')

############################################################################################################################
############################################################################################################################
############################################################################################################################

# TODO Removing the flickering caused by constantly using plot.show. Need to keep the figure open and just update the image data.

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, IntSlider, FloatSlider, Dropdown, fixed

# Function to display a 2D slice from the 3D volume with a consistent color scale
def display_slice(volume, slice_index, slice_direction, vmin=None, vmax=None, figsize=None):
    if slice_direction not in ['[1 0 0]', '[0 1 0]', '[0 0 1]']:
        raise ValueError(f"Invalid slice direction '{slice_direction}'. Accepted directions are :[1 0 0]', '[0 1 0]', '[0 0 1]")
    
    if vmin is None:
        vmin = np.min(volume)
    if vmax is None:
        vmax = np.max(volume)

    plt.figure(figsize=figsize)
    
    # Check which direction is selected by matching the vector
    if slice_direction == '[1 0 0]':  # X direction
        plt.imshow(volume[slice_index, :, :], cmap='gray', vmin=vmin, vmax=vmax)
        plt.title(f'Slice {slice_index} along X axis')
    elif slice_direction == '[0 1 0]':  # Y direction
        plt.imshow(volume[:, slice_index, :], cmap='gray', vmin=vmin, vmax=vmax)
        plt.title(f'Slice {slice_index} along Y axis')
    elif slice_direction == '[0 0 1]':  # Z direction
        plt.imshow(volume[:, :, slice_index], cmap='gray', vmin=vmin, vmax=vmax)
        plt.title(f'Slice {slice_index} along Z axis')

    plt.colorbar()
    plt.axis('off')
    plt.show()

# Function to create and display an interactive viewer
def interactive_slice_viewer(volume, default_slice_direction='[0 0 1]', vmin=None, vmax=None, figsize=(8, 6)):

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
    vmin_slider_widget = FloatSlider(min=vmin, max=vmax, step=0.001, value=np.min(volume), description='Colorbar Min')
    vmax_slider_widget = FloatSlider(min=vmin, max=vmax, step=0.001, value=np.max(volume), description='Colorbar Max')

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
    interact(display_slice, volume=fixed(volume), slice_index=slice_index_widget, vmin=vmin_slider_widget, vmax=vmax_slider_widget, slice_direction=slice_direction_widget, figsize=fixed(figsize))










