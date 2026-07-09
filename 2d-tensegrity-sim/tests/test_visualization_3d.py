import os
import sys

import matplotlib

matplotlib.use("Agg")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from TensegritySim import Visualization, YamlParser
from TensegritySim.data_structures import Connection, Node, Tensegrity


def test_plain_3d_bar_plot_handles_z_interpolation():
    node_a = Node("A", [0.0, 0.0, 0.0])
    node_b = Node("B", [1.0, 1.0, 2.0])
    tensegrity = Tensegrity(
        nodes=[node_a, node_b],
        connections=[
            Connection(
                [node_a, node_b],
                Connection.ConnectionType.BAR,
                stiffness=100.0,
            )
        ],
    )

    viz = Visualization(tensegrity, dim=3)
    viz.plot(label_nodes=False, label_connections=False)

    assert viz.dim == 3


def test_needle_trunk_yaml_plots_as_plain_3d_without_surface():
    tensegrity = YamlParser.parse(os.path.join("yaml", "needle_trunk.yaml"))
    viz = Visualization(tensegrity, dim=3)

    viz.plot(label_nodes=False, label_connections=True)

    assert viz.dim == 3
