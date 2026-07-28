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


def test_force_color_mapping_distinguishes_tension_compression_and_slack():
    node_a = Node("A", [0.0, 0.0, 0.0])
    node_b = Node("B", [1.0, 0.0, 0.0])
    connection = Connection([node_a, node_b], Connection.ConnectionType.BAR, stiffness=1.0)

    connection.force = 10.0
    tension_color = Visualization._force_color(connection, max_abs_force=10.0)
    assert tension_color[2] > tension_color[0]

    connection.force = -10.0
    compression_color = Visualization._force_color(connection, max_abs_force=10.0)
    assert compression_color[0] > compression_color[2]

    connection.force = 0.0
    slack_color = Visualization._force_color(connection, max_abs_force=10.0)
    assert abs(slack_color[0] - slack_color[1]) < 0.05
    assert abs(slack_color[1] - slack_color[2]) < 0.05
