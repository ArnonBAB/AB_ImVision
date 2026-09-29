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
# slice_viewer(volume, '[1 0 0]')

############################################################################################################################
############################################################################################################################
############################################################################################################################

from io import BytesIO

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.colors import Colormap
from matplotlib.backends.backend_agg import FigureCanvasAgg

from IPython.display import display
from ipywidgets import Dropdown, FloatSlider, IntSlider, HBox, VBox, Image, Layout


def slice_viewer(
    volume: np.ndarray,
    voxel_size: tuple = (1.0, 1.0, 1.0),
    unit: str = "um",
    default_slice_direction: str = "[0 0 1]",
    cmap: Colormap | str = "gray",
    vmin: float | None = None,
    vmax: float | None = None,
    figsize: tuple = (4, 4),
):
    """
    Interactive slice viewer for a 3D NumPy array.

    The volume axes are interpreted as:

        volume[x, y, z]

    Args:
        volume:
            Three-dimensional array to display.
        voxel_size:
            Physical voxel size in the X, Y and Z directions.
        unit:
            Unit used for the axis labels.
        default_slice_direction:
            Initial slicing direction. Must be '[1 0 0]',
            '[0 1 0]' or '[0 0 1]'.
        cmap:
            Matplotlib colormap.
        vmin:
            Initial lower color limit.
        vmax:
            Initial upper color limit.
        figsize:
            Matplotlib figure size.
    """

    volume = np.asarray(volume)

    if volume.ndim != 3:
        raise ValueError(
            f"volume must be three-dimensional, but has shape {volume.shape}"
        )

    directions = {
        "[1 0 0]": 0,
        "[0 1 0]": 1,
        "[0 0 1]": 2,
    }

    if default_slice_direction not in directions:
        raise ValueError(
            "default_slice_direction must be "
            "'[1 0 0]', '[0 1 0]' or '[0 0 1]'"
        )

    if len(voxel_size) != 3:
        raise ValueError("voxel_size must contain exactly three values")

    if vmin is None:
        vmin = float(np.nanmin(volume))

    if vmax is None:
        vmax = float(np.nanmax(volume))

    if vmax < vmin:
        raise ValueError("vmax must be greater than or equal to vmin")

    # FloatSlider requires a nonzero step.
    value_range = vmax - vmin
    slider_step = value_range / 1000 if value_range > 0 else 1.0

    # ------------------------------------------------------------------
    # Widgets
    # ------------------------------------------------------------------

    direction_widget = Dropdown(
        options=list(directions),
        value=default_slice_direction,
        description="Direction:",
        style={"description_width": "initial"},
    )

    initial_axis = directions[default_slice_direction]

    slice_widget = IntSlider(
        min=0,
        max=volume.shape[initial_axis] - 1,
        value=volume.shape[initial_axis] // 2,
        step=1,
        description="Slice:",
        continuous_update=True,
        style={"description_width": "initial"},
    )

    vmin_widget = FloatSlider(
        min=vmin,
        max=vmax,
        value=vmin,
        step=slider_step,
        description="Color min:",
        readout_format=".4g",
        continuous_update=True,
        style={"description_width": "initial"},
    )

    vmax_widget = FloatSlider(
        min=vmin,
        max=vmax,
        value=vmax,
        step=slider_step,
        description="Color max:",
        readout_format=".4g",
        continuous_update=True,
        style={"description_width": "initial"},
    )

    # This is the widget that remains visible in the notebook.
    image_widget = Image(format="png", layout = Layout(width="500px", height ="auto"))

    # ------------------------------------------------------------------
    # Create the Matplotlib figure once
    # ------------------------------------------------------------------

    fig, ax = plt.subplots(figsize=figsize, dpi = 160)

    # Prevent the inline backend from displaying this figure separately.
    plt.close(fig)

    # Use a non-interactive canvas to render the figure to PNG.
    canvas = FigureCanvasAgg(fig)

    initial_image, initial_extent, labels = _get_slice(
        volume=volume,
        voxel_size=voxel_size,
        direction=default_slice_direction,
        index=slice_widget.value,
    )

    im = ax.imshow(
        initial_image,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        extent=initial_extent,
        origin="lower",
        aspect="equal",
    )

    colorbar = fig.colorbar(im, ax=ax)

    # Leave enough room for labels and colorbar.
    fig.tight_layout()

    # ------------------------------------------------------------------
    # Rendering and updating
    # ------------------------------------------------------------------

    def render_figure():
        """Render the existing figure into the Image widget."""

        canvas.draw()

        buffer = BytesIO()
        canvas.print_png(buffer)

        image_widget.value = buffer.getvalue()
        buffer.close()

    def update_plot(change=None):
        """Update the existing Matplotlib image."""

        direction = direction_widget.value
        index = slice_widget.value

        image_data, extent, labels = _get_slice(
            volume=volume,
            voxel_size=voxel_size,
            direction=direction,
            index=index,
        )

        # Update the existing image. No new axes or figure are created.
        im.set_data(image_data)
        im.set_extent(extent)
        im.set_clim(vmin_widget.value, vmax_widget.value)

        ax.set_xlabel(f"{labels['horizontal']} axis ({unit})")
        ax.set_ylabel(f"{labels['vertical']} axis ({unit})")
        ax.set_title(
            f"{labels['fixed']} slice {index} "
            f"at {index * labels['spacing']:.4g} {unit}"
        )

        # The image shape and extent may have changed after choosing
        # another slicing direction.
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])

        render_figure()

    def update_direction(change):
        """Adjust the slider range when the direction changes."""

        axis = directions[change["new"]]

        slice_widget.max = volume.shape[axis] - 1
        slice_widget.value = volume.shape[axis] // 2

        update_plot()

    # Direction gets its own callback because it also changes slider limits.
    direction_widget.observe(update_direction, names="value")

    # These controls only require a plot update.
    slice_widget.observe(update_plot, names="value")
    vmin_widget.observe(update_plot, names="value")
    vmax_widget.observe(update_plot, names="value")

    controls = VBox(
        [
            HBox([direction_widget, slice_widget]),
            HBox([vmin_widget, vmax_widget]),
        ]
    )

    viewer = VBox([controls, image_widget])

    # Draw the initial image.
    update_plot()

    display(viewer)

    # Returning the widgets can be useful if you want to modify them later.
    return None


def _get_slice(
    volume: np.ndarray,
    voxel_size: tuple,
    direction: str,
    index: int,
):
    """Return image data, physical extent and axis information."""

    nx, ny, nz = volume.shape
    dx, dy, dz = voxel_size

    if direction == "[1 0 0]":
        # Fix X, display the Y-Z plane.
        image = volume[index, :, :]

        extent = (0, nz * dz, 0, ny * dy)

        labels = {
            "horizontal": "Z",
            "vertical": "Y",
            "fixed": "X",
            "spacing": dx,
        }

    elif direction == "[0 1 0]":
        # Fix Y, display the X-Z plane.
        image = volume[:, index, :]

        extent = (0, nz * dz, 0, nx * dx)

        labels = {
            "horizontal": "Z",
            "vertical": "X",
            "fixed": "Y",
            "spacing": dy,
        }

    elif direction == "[0 0 1]":
        # Fix Z, display the X-Y plane.
        image = volume[:, :, index]

        extent = (0, ny * dy, 0, nx * dx)

        labels = {
            "horizontal": "Y",
            "vertical": "X",
            "fixed": "Z",
            "spacing": dz,
        }

    else:
        raise ValueError(f"Invalid slicing direction: {direction}")

    return image, extent, labels