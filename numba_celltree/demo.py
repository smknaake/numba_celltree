from typing import Tuple

import numpy as np
from matplotlib import patches
from matplotlib.collections import LineCollection

from .constants import IntArray, IntDType


def close_polygons(face_node_connectivity: IntArray, fill_value: int) -> IntArray:
    # Wrap around and create closed polygon: put the first node at the end of the row
    # In case of fill values, replace all fill values
    n, m = face_node_connectivity.shape
    closed = np.full((n, m + 1), fill_value, dtype=IntDType)
    closed[:, :-1] = face_node_connectivity
    first_node = face_node_connectivity[:, 0]
    # Identify fill value, and replace by first node also
    isfill = closed == fill_value
    closed.ravel()[isfill.ravel()] = np.repeat(first_node, isfill.sum(axis=1))
    return closed


def edges(
    face_node_connectivity: IntArray, fill_value: int
) -> Tuple[IntArray, IntArray]:
    face_node_connectivity = np.atleast_2d(face_node_connectivity)
    n, m = face_node_connectivity.shape
    # Close the polygons: [0 1 2 3] -> [0 1 2 3 0]
    closed = close_polygons(face_node_connectivity, fill_value)
    # Allocate array for edge_node_connectivity: includes duplicate edges
    edge_node_connectivity = np.empty((n * m, 2), dtype=IntDType)
    edge_node_connectivity[:, 0] = closed[:, :-1].ravel()
    edge_node_connectivity[:, 1] = closed[:, 1:].ravel()
    # Cleanup: delete invalid edges (same node to same node)
    # this is a result of closing the polygons
    edge_node_connectivity = edge_node_connectivity[
        edge_node_connectivity[:, 0] != edge_node_connectivity[:, 1]
    ]
    # Now find the unique rows == unique edges
    edge_node_connectivity.sort(axis=1)
    edge_node_connectivity = np.unique(edge_node_connectivity, axis=0)
    return edge_node_connectivity


def plot_edges(node_x, node_y, edge_nodes, ax, *args, **kwargs):
    """
    Plots the edges at a given axes.
    `args` and `kwargs` will be used as parameters of the `plot` method.

    Parameters
    ----------
    node_x (ndarray): A 1D double array describing the x-coordinates of the nodes.
    node_y (ndarray): A 1D double array describing the y-coordinates of the nodes.
    edge_nodes (ndarray, optional): A 2D integer array describing the nodes composing each mesh 2d edge.
    ax (matplotlib.axes.Axes): The axes where to plot the edges
    """
    n_edge = len(edge_nodes)
    edge_coords = np.empty((n_edge, 2, 2), dtype=np.float64)
    node_0 = edge_nodes[:, 0]
    node_1 = edge_nodes[:, 1]
    edge_coords[:, 0, 0] = node_x[node_0]
    edge_coords[:, 0, 1] = node_y[node_0]
    edge_coords[:, 1, 0] = node_x[node_1]
    edge_coords[:, 1, 1] = node_y[node_1]
    line_segments = LineCollection(edge_coords, *args, **kwargs)
    ax.add_collection(line_segments)
    ax.set_aspect(1.0)
    ax.autoscale(enable=True)


def plot_boxes(box_coords, ax, *args, **kwargs):
    box_coords = np.atleast_2d(box_coords)
    nbox, ncoord = box_coords.shape
    if ncoord != 4:
        raise ValueError(f"four values describe a box, got instead {ncoord}")
    for i in range(nbox):
        xmin, xmax, ymin, ymax = box_coords[i]
        dx = xmax - xmin
        dy = ymax - ymin
        rect = patches.Rectangle((xmin, ymin), dx, dy, fill=False, *args, **kwargs)
        ax.add_patch(rect)
