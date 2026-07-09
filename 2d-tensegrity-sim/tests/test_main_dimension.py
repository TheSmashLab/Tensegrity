import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import infer_visualization_dimension
from TensegritySim import YamlParser
from TensegritySim.data_structures import Node, Tensegrity


def test_infer_visualization_dimension_uses_nonzero_z_coordinates():
    tensegrity = Tensegrity(
        nodes=[
            Node("A", [0.0, 0.0, 0.0]),
            Node("B", [1.0, 0.0, 2.0]),
        ],
        connections=[],
    )

    assert infer_visualization_dimension(tensegrity) == 3


def test_infer_visualization_dimension_keeps_flat_structures_2d():
    tensegrity = Tensegrity(
        nodes=[
            Node("A", [0.0, 0.0, 0.0]),
            Node("B", [1.0, 0.0, 0.0]),
        ],
        connections=[],
    )

    assert infer_visualization_dimension(tensegrity) == 2


def test_infer_visualization_dimension_uses_z_pins():
    tensegrity = Tensegrity(
        nodes=[
            Node("A", [0.0, 0.0, 0.0]),
            Node("B", [1.0, 0.0, 0.0]),
        ],
        connections=[],
        pins={"A": [True, True, True]},
    )

    assert infer_visualization_dimension(tensegrity) == 3


def test_needle_trunk_yaml_is_inferred_as_3d():
    tensegrity = YamlParser.parse(os.path.join("yaml", "needle_trunk.yaml"))

    assert infer_visualization_dimension(tensegrity) == 3
