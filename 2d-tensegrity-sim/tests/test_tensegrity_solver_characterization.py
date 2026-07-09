import os
import sys
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from TensegritySim.data_structures import Connection, Node, Surface, Tensegrity
from TensegritySim.tensegrity_solver import TensegritySolver


def _two_node_tensegrity(connection_type=Connection.ConnectionType.BAR, initial_length=1.0):
    node_a = Node("A", [0.0, 0.0, 0.0])
    node_b = Node("B", [2.0, 0.0, 0.0])
    connection = Connection(
        [node_a, node_b],
        connection_type=connection_type,
        stiffness=10.0,
        initial_length=initial_length,
    )
    return Tensegrity([node_a, node_b], [connection]), connection


def test_set_forces_places_forces_by_node_order_and_resets_previous_values():
    tensegrity, _ = _two_node_tensegrity()
    solver = TensegritySolver(tensegrity, dim=2)

    solver.set_forces({"B": np.array([3.0, -2.0])})
    np.testing.assert_array_equal(solver.forces, np.array([0.0, 0.0, 3.0, -2.0]))

    solver.set_forces({"A": np.array([1.0, 2.0])})
    np.testing.assert_array_equal(solver.forces, np.array([1.0, 2.0, 0.0, 0.0]))


def test_set_forces_rejects_force_vectors_with_wrong_dimension():
    tensegrity, _ = _two_node_tensegrity()
    solver = TensegritySolver(tensegrity, dim=2)

    with pytest.raises(ValueError, match="same dimension"):
        solver.set_forces({"A": np.array([1.0, 2.0, 3.0])})


def test_initial_guess_omits_pinned_coordinates_in_flattened_order():
    nodes = [
        Node("A", [1.0, 2.0, 0.0]),
        Node("B", [3.0, 4.0, 0.0]),
        Node("C", [5.0, 6.0, 0.0]),
    ]
    tensegrity = Tensegrity(
        nodes,
        [],
        pins={"A": [True, False, False], "C": [False, True, False]},
    )
    solver = TensegritySolver(tensegrity, dim=2)

    np.testing.assert_array_equal(solver._create_initial_guess(), np.array([2.0, 3.0, 4.0, 5.0]))


def test_objective_removes_pinned_coordinates_and_keeps_external_force_residuals():
    tensegrity, _ = _two_node_tensegrity(initial_length=2.0)
    tensegrity.pins = {"A": [True, True, False]}
    solver = TensegritySolver(tensegrity, dim=2)
    solver.set_forces({"A": np.array([99.0, 99.0]), "B": np.array([5.0, -3.0])})

    objective = solver._objective(solver._create_initial_guess())

    np.testing.assert_allclose(objective, np.array([5.0, -3.0]))


def test_string_connections_have_no_energy_or_derivative_when_slack():
    tensegrity, connection = _two_node_tensegrity(
        connection_type=Connection.ConnectionType.STRING,
        initial_length=3.0,
    )
    solver = TensegritySolver(tensegrity, dim=2)
    nodes = np.array([node.position[:2] for node in tensegrity.nodes])

    assert solver._spring_connection_energy(connection, nodes) == 0
    np.testing.assert_array_equal(
        solver._spring_connection_energy_derivative(connection, nodes),
        np.zeros(4),
    )


def test_bar_connection_energy_derivative_points_along_connection_axis():
    tensegrity, connection = _two_node_tensegrity(
        connection_type=Connection.ConnectionType.BAR,
        initial_length=1.0,
    )
    solver = TensegritySolver(tensegrity, dim=2)
    nodes = np.array([node.position[:2] for node in tensegrity.nodes])

    np.testing.assert_allclose(
        solver._spring_connection_energy_derivative(connection, nodes),
        np.array([10.0, 0.0, -10.0, 0.0]),
    )


def test_multinode_connection_length_sums_adjacent_segments():
    node_a = Node("A", [0.0, 0.0, 0.0])
    node_b = Node("B", [3.0, 4.0, 0.0])
    node_c = Node("C", [6.0, 8.0, 0.0])
    connection = Connection(
        [node_a, node_b, node_c],
        Connection.ConnectionType.STRING,
        stiffness=1.0,
        initial_length=10.0,
    )
    tensegrity = Tensegrity([node_a, node_b, node_c], [connection])
    solver = TensegritySolver(tensegrity, dim=2)

    assert solver._connection_length(connection, np.array([[0.0, 0.0], [3.0, 4.0], [6.0, 8.0]])) == 10.0


def test_surface_linked_nodes_have_zero_distance_and_cylinder_constraints():
    node_a = Node("A", [0.0, 2.0, 0.0])
    node_b = Node("B", [2.0 * np.pi, 3.5, 0.0])
    surface = Surface({"surface_type": "cylinder", "properties": {"radius": 1.0}}, [{"A", "B"}])
    tensegrity = Tensegrity([node_a, node_b], [], surface=surface)
    solver = TensegritySolver(tensegrity, dim=2)

    assert solver._node_distance("A", "B", np.array([[0.0, 2.0], [2.0 * np.pi, 3.5]])) == 0
    constraints = solver._surface_constraints(solver._create_initial_guess())
    assert abs(constraints[0]) == 1.5
    assert constraints[1] == pytest.approx(0.0, abs=1e-12)


def test_solve_success_updates_only_optimized_dimensions_and_refreshes_forces(monkeypatch):
    tensegrity, connection = _two_node_tensegrity(initial_length=1.0)
    tensegrity.pins = {"A": [True, True, False]}

    def successful_least_squares(*args, **kwargs):
        return SimpleNamespace(success=True, message="ok", x=np.array([1.0, 0.0]), fun=np.zeros(2))

    monkeypatch.setattr("TensegritySim.tensegrity_solver.least_squares", successful_least_squares)

    result = TensegritySolver(tensegrity, dim=2).solve()

    assert result.success
    np.testing.assert_allclose(tensegrity.nodes[0].position, np.array([0.0, 0.0, 0.0]))
    np.testing.assert_allclose(tensegrity.nodes[1].position, np.array([1.0, 0.0, 0.0]))
    assert connection.force == 0.0


def test_3d_solve_updates_z_coordinate_when_dim_is_three(monkeypatch):
    tensegrity, _ = _two_node_tensegrity(initial_length=1.0)
    tensegrity.pins = {"A": [True, True, True]}

    def successful_least_squares(*args, **kwargs):
        return SimpleNamespace(success=True, message="ok", x=np.array([1.0, 2.0, 3.0]), fun=np.zeros(3))

    monkeypatch.setattr("TensegritySim.tensegrity_solver.least_squares", successful_least_squares)

    result = TensegritySolver(tensegrity, dim=3).solve()

    assert result.success
    np.testing.assert_allclose(tensegrity.nodes[1].position, np.array([1.0, 2.0, 3.0]))


def test_solve_rejects_null_force_solution_for_prestressed_strings(monkeypatch):
    tensegrity, connection = _two_node_tensegrity(
        connection_type=Connection.ConnectionType.STRING,
        initial_length=1.0,
    )
    tensegrity.pins = {"A": [True, True, False]}
    original_position = tensegrity.nodes[1].position.copy()

    def slack_least_squares(*args, **kwargs):
        return SimpleNamespace(success=True, message="ok", x=np.array([0.5, 0.0]), fun=np.zeros(2))

    monkeypatch.setattr("TensegritySim.tensegrity_solver.least_squares", slack_least_squares)

    result = TensegritySolver(tensegrity, dim=2).solve(attempts=1)

    assert not result.success
    assert "null-force" in result.message
    np.testing.assert_allclose(tensegrity.nodes[1].position, original_position)
    assert connection.force == pytest.approx(10.0)


def test_solve_rejects_null_solution_even_if_current_positions_are_slack(monkeypatch):
    tensegrity, _ = _two_node_tensegrity(
        connection_type=Connection.ConnectionType.STRING,
        initial_length=1.0,
    )
    tensegrity.pins = {"A": [True, True, False]}
    tensegrity.nodes[1].position = np.array([0.5, 0.0, 0.0])
    tensegrity.update_forces()

    def slack_least_squares(*args, **kwargs):
        return SimpleNamespace(success=True, message="ok", x=np.array([0.5, 0.0]), fun=np.zeros(2))

    monkeypatch.setattr("TensegritySim.tensegrity_solver.least_squares", slack_least_squares)

    result = TensegritySolver(tensegrity, dim=2).solve(attempts=1)

    assert not result.success
    assert "1/1 members" in result.message


def test_solve_retries_and_accepts_non_null_force_solution(monkeypatch):
    tensegrity, _ = _two_node_tensegrity(
        connection_type=Connection.ConnectionType.STRING,
        initial_length=1.0,
    )
    tensegrity.pins = {"A": [True, True, False]}
    results = iter(
        [
            SimpleNamespace(success=True, message="slack", x=np.array([0.5, 0.0]), fun=np.zeros(2)),
            SimpleNamespace(success=True, message="taut", x=np.array([1.25, 0.0]), fun=np.zeros(2)),
        ]
    )

    def retrying_least_squares(*args, **kwargs):
        return next(results)

    monkeypatch.setattr("TensegritySim.tensegrity_solver.least_squares", retrying_least_squares)

    result = TensegritySolver(tensegrity, dim=2).solve(attempts=2)

    assert result.success
    np.testing.assert_allclose(tensegrity.nodes[1].position, np.array([1.25, 0.0, 0.0]))
