import os
import sys
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import _parse_control_input
from TensegritySim.data_structures import Connection, Node, Tensegrity
from TensegritySim.errors import TensegrityInputError, TensegrityParseError
from TensegritySim.tensegrity_solver import TensegritySolver
from TensegritySim.yaml_parser import YamlParser


def test_parse_control_input_reports_non_numeric_values():
    with pytest.raises(TensegrityInputError, match="numeric"):
        _parse_control_input("1.0, nope", 2)


def test_parse_control_input_reports_wrong_value_count():
    with pytest.raises(TensegrityInputError, match="Expected 2"):
        _parse_control_input("1.0", 2)


def test_yaml_parser_reports_missing_required_section(tmp_path):
    yaml_path = tmp_path / "missing_connections.yaml"
    yaml_path.write_text(
        """
nodes:
  A: [0, 0, 0]
builders: {}
""",
        encoding="utf-8",
    )

    with pytest.raises(TensegrityParseError, match="Missing required section: connections"):
        YamlParser.parse(str(yaml_path))


def test_yaml_parser_reports_unknown_connection_node(tmp_path):
    yaml_path = tmp_path / "unknown_node.yaml"
    yaml_path.write_text(
        """
nodes:
  A: [0, 0, 0]
connections:
  bars:
    - [A, B]
builders:
  bars:
    stiffness: 1
    type: bar
""",
        encoding="utf-8",
    )

    with pytest.raises(TensegrityParseError, match="unknown node B"):
        YamlParser.parse(str(yaml_path))


def test_yaml_parser_reports_non_boolean_pin_values(tmp_path):
    yaml_path = tmp_path / "bad_pin.yaml"
    yaml_path.write_text(
        """
nodes:
  A: [0, 0, 0]
  B: [1, 0, 0]
connections:
  bars:
    - [A, B]
builders:
  bars:
    stiffness: 1
    type: bar
pins:
  A: [true, 1, false]
""",
        encoding="utf-8",
    )

    with pytest.raises(TensegrityParseError, match="must be booleans"):
        YamlParser.parse(str(yaml_path))


def test_yaml_parser_reports_connections_that_are_not_lists(tmp_path):
    yaml_path = tmp_path / "bad_connections.yaml"
    yaml_path.write_text(
        """
nodes:
  A: [0, 0, 0]
  B: [1, 0, 0]
connections:
  bars:
    A: B
builders:
  bars:
    stiffness: 1
    type: bar
""",
        encoding="utf-8",
    )

    with pytest.raises(TensegrityParseError, match="Connections for bars must be a list"):
        YamlParser.parse(str(yaml_path))


def test_yaml_parser_reports_invalid_cylinder_radius(tmp_path):
    yaml_path = tmp_path / "bad_surface.yaml"
    yaml_path.write_text(
        """
nodes:
  A: [0, 0, 0]
  B: [1, 0, 0]
connections:
  bars:
    - [A, B]
builders:
  bars:
    stiffness: 1
    type: bar
surface:
  cylinder:
    radius: 0
  linked_nodes:
    - [A, B]
""",
        encoding="utf-8",
    )

    with pytest.raises(TensegrityParseError, match="radius must be positive"):
        YamlParser.parse(str(yaml_path))


def test_solver_returns_failure_result_without_updating_positions(monkeypatch):
    node1 = Node(name="A", position=np.array([0.0, 0.0, 0.0]))
    node2 = Node(name="B", position=np.array([2.0, 0.0, 0.0]))
    connection = Connection(
        nodes=[node1, node2],
        connection_type=Connection.ConnectionType.BAR,
        stiffness=1.0,
        initial_length=1.0,
    )
    tensegrity = Tensegrity([node1, node2], [connection])
    original_positions = [node.position.copy() for node in tensegrity.nodes]

    def fail_root(*args, **kwargs):
        return SimpleNamespace(success=False, message="forced failure", x=np.array([100.0, 100.0, 100.0, 100.0]))

    monkeypatch.setattr("TensegritySim.tensegrity_solver.root", fail_root)

    result = TensegritySolver(tensegrity, dim=2).solve()

    assert not result.success
    assert "forced failure" in result.message
    for node, original_position in zip(tensegrity.nodes, original_positions):
        np.testing.assert_array_equal(node.position, original_position)
