from types import SimpleNamespace

import pytest

from TensegritySim.data_structures import Connection, Node, Tensegrity
from TensegritySim.simulation_ui import SimulationUI


class _FakeRoot:
    def __init__(self):
        self.quit_calls = 0
        self.destroy_calls = 0

    def quit(self):
        self.quit_calls += 1

    def destroy(self):
        self.destroy_calls += 1


class _FakeVariable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def test_close_stops_event_loop_destroys_window_and_closes_figure(monkeypatch):
    ui = SimulationUI.__new__(SimulationUI)
    ui.root = _FakeRoot()
    ui.viz = SimpleNamespace(fig=object())
    ui._closed = False
    closed_figures = []
    monkeypatch.setattr(
        "TensegritySim.simulation_ui.plt.close",
        lambda figure: closed_figures.append(figure),
    )

    ui.close()
    ui.close()

    assert closed_figures == [ui.viz.fig]
    assert ui.root.quit_calls == 1
    assert ui.root.destroy_calls == 1


def test_apply_uses_persistent_offset_instead_of_reapplying_delta():
    node_a = Node("A", [0.0, 0.0, 0.0])
    node_b = Node("B", [1.0, 0.0, 0.0])
    control = Connection(
        [node_a, node_b],
        Connection.ConnectionType.STRING,
        stiffness=1.0,
        initial_length=1.0,
    )
    tensegrity = Tensegrity([node_a, node_b], [control], controls=[control])
    ui = SimulationUI.__new__(SimulationUI)
    ui.tensegrity = tensegrity
    ui.control_delta_vars = [_FakeVariable(0.1)]
    ui._last_snapshot = None
    ui.solve_and_render = lambda reason: SimpleNamespace(success=True)

    ui.apply_controls()
    ui.apply_controls()
    assert control.initial_length == pytest.approx(1.1)

    ui.control_delta_vars[0].set(0.2)
    ui.apply_controls()
    assert control.initial_length == pytest.approx(1.2)
