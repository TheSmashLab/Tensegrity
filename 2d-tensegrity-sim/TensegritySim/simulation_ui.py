import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .data_structures import Tensegrity
from .tensegrity_solver import SolverResult, TensegritySolver
from .visualization import Visualization


class SimulationUI:
    """Tk-based simulation cockpit for solving and inspecting a tensegrity model."""

    def __init__(self, tensegrity: Tensegrity, dim: int = 2, title: str = "Tensegrity Simulator"):
        self.tensegrity = tensegrity
        self.dim = dim
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1220x780")
        self.root.minsize(980, 620)

        self.solver = TensegritySolver(self.tensegrity, dim=self.dim)
        self.viz = Visualization(self.tensegrity, dim=self.dim, auto_show=False)
        self.control_delta_vars = []
        self.control_ranges = []
        self._last_snapshot = None

        self.show_forces_var = tk.BooleanVar(value=False)
        self.show_connections_var = tk.BooleanVar(value=True)
        self.show_nodes_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")
        self.residual_var = tk.StringVar(value="Residual: -")
        self.force_stats_var = tk.StringVar(value="Forces: -")
        self.position_var = tk.StringVar(value="")

        self._configure_style()
        self._build_layout()
        self._bind_shortcuts()
        self.render()
        self.solve_and_render(reason="Initial solve")

    def run(self) -> int:
        """Starts the Tk event loop."""
        self.root.mainloop()
        return 0

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        default_font = ("Segoe UI", 10)
        self.root.option_add("*Font", default_font)
        style.configure("Status.TLabel", padding=(8, 4))
        style.configure("PanelHeader.TLabel", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        top_bar = ttk.Frame(self.root, padding=(10, 8, 10, 4))
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.columnconfigure(1, weight=1)
        ttk.Label(top_bar, textvariable=self.status_var, style="Status.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(top_bar, textvariable=self.residual_var, style="Status.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(top_bar, textvariable=self.force_stats_var, style="Status.TLabel").grid(row=0, column=2, sticky="e")

        body = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))

        canvas_frame = ttk.Frame(body)
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        self.canvas = FigureCanvasTkAgg(self.viz.fig, master=canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")
        body.add(canvas_frame, weight=5)

        side_panel = ttk.Frame(body, padding=(12, 8))
        side_panel.columnconfigure(0, weight=1)
        body.add(side_panel, weight=0)

        self._build_control_panel(side_panel)
        self._build_display_panel(side_panel)
        self._build_view_panel(side_panel)
        self._build_positions_panel(side_panel)

        bottom_bar = ttk.Frame(self.root, padding=(12, 4, 12, 8))
        bottom_bar.grid(row=2, column=0, sticky="ew")
        bottom_bar.columnconfigure(0, weight=1)
        hint = "Scroll zooms | drag pans in 2D | right/middle drag pans | double-click fits | Space applies controls"
        ttk.Label(bottom_bar, text=hint).grid(row=0, column=0, sticky="w")

    def _build_control_panel(self, parent) -> None:
        ttk.Label(parent, text="Controls", style="PanelHeader.TLabel").grid(row=0, column=0, sticky="w")

        control_container = ttk.Frame(parent)
        control_container.grid(row=1, column=0, sticky="nsew", pady=(6, 12))
        control_container.columnconfigure(0, weight=1)

        if not self.tensegrity.controls:
            ttk.Label(control_container, text="No control strings in this file.").grid(row=0, column=0, sticky="w")
        else:
            for row, control in enumerate(self.tensegrity.controls):
                self._add_control_row(control_container, row, control)

        button_row = ttk.Frame(parent)
        button_row.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        button_row.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(button_row, text="Apply", command=self.apply_controls).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(button_row, text="Reset", command=self.reset_controls).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(button_row, text="Undo", command=self.undo).grid(row=0, column=2, sticky="ew", padx=(4, 0))

    def _add_control_row(self, parent, row: int, control) -> None:
        frame = ttk.Frame(parent, padding=(0, 0, 0, 8))
        frame.grid(row=row, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        label = control.name or f"Control {row + 1}"
        var = tk.DoubleVar(value=0.0)
        length_scale = max(abs(float(control.initial_length)), 1.0)
        delta_range = max(0.05 * length_scale, 0.01)
        self.control_delta_vars.append(var)
        self.control_ranges.append(delta_range)

        ttk.Label(frame, text=label).grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Button(frame, text="-", width=3, command=lambda index=row: self._step_control(index, -1)).grid(row=1, column=0, sticky="w")
        scale = ttk.Scale(frame, from_=-delta_range, to=delta_range, variable=var, command=lambda _value: self._update_pending_status())
        scale.grid(row=1, column=1, sticky="ew", padx=6)
        ttk.Button(frame, text="+", width=3, command=lambda index=row: self._step_control(index, 1)).grid(row=1, column=2, sticky="e")
        entry = ttk.Entry(frame, textvariable=var, width=10)
        entry.grid(row=2, column=1, sticky="e", pady=(2, 0))
        ttk.Label(frame, text="pending delta").grid(row=2, column=0, sticky="w", pady=(2, 0))

    def _build_display_panel(self, parent) -> None:
        ttk.Separator(parent).grid(row=3, column=0, sticky="ew", pady=(4, 10))
        ttk.Label(parent, text="Display", style="PanelHeader.TLabel").grid(row=4, column=0, sticky="w")
        display = ttk.Frame(parent)
        display.grid(row=5, column=0, sticky="ew", pady=(6, 12))
        ttk.Checkbutton(display, text="Forces", variable=self.show_forces_var, command=self.render).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(display, text="Connection names", variable=self.show_connections_var, command=self.render).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(display, text="Node names", variable=self.show_nodes_var, command=self.render).grid(row=2, column=0, sticky="w")

    def _build_view_panel(self, parent) -> None:
        ttk.Separator(parent).grid(row=6, column=0, sticky="ew", pady=(4, 10))
        ttk.Label(parent, text="View", style="PanelHeader.TLabel").grid(row=7, column=0, sticky="w")
        view = ttk.Frame(parent)
        view.grid(row=8, column=0, sticky="ew", pady=(6, 12))
        view.columnconfigure((0, 1), weight=1)
        ttk.Button(view, text="Fit", command=self.fit_view).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(view, text="Reset Camera", command=self.reset_camera).grid(row=0, column=1, sticky="ew", padx=(4, 0))
        if self.dim == 3:
            ttk.Button(view, text="Top", command=lambda: self.set_camera(90, -90)).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(6, 0))
            ttk.Button(view, text="Front", command=lambda: self.set_camera(0, -90)).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(6, 0))

    def _build_positions_panel(self, parent) -> None:
        ttk.Separator(parent).grid(row=9, column=0, sticky="ew", pady=(4, 10))
        ttk.Label(parent, text="Requested Positions", style="PanelHeader.TLabel").grid(row=10, column=0, sticky="w")
        ttk.Label(parent, textvariable=self.position_var, justify=tk.LEFT).grid(row=11, column=0, sticky="ew", pady=(6, 0))

    def _bind_shortcuts(self) -> None:
        self.root.bind("<space>", lambda _event: self.apply_controls())
        self.root.bind("f", lambda _event: self.fit_view())
        self.root.bind("F", lambda _event: self.fit_view())
        self.root.bind("q", lambda _event: self.root.destroy())
        self.root.bind("Q", lambda _event: self.root.destroy())
        self.viz.fig.canvas.mpl_connect("button_press_event", self._on_canvas_double_click)

    def _on_canvas_double_click(self, event) -> None:
        if getattr(event, "dblclick", False):
            self.fit_view()

    def _snapshot(self):
        return {
            "positions": [node.position.copy() for node in self.tensegrity.nodes],
            "control_lengths": [control.initial_length for control in self.tensegrity.controls],
        }

    def _restore_snapshot(self, snapshot) -> None:
        for node, position in zip(self.tensegrity.nodes, snapshot["positions"]):
            node.position = position.copy()
        for control, length in zip(self.tensegrity.controls, snapshot["control_lengths"]):
            control.initial_length = length
        self.tensegrity.update_forces()

    def _read_deltas(self):
        deltas = []
        for var in self.control_delta_vars:
            try:
                deltas.append(float(var.get()))
            except (tk.TclError, ValueError):
                raise ValueError("Control deltas must be numeric.")
        return deltas

    def _step_control(self, index: int, direction: int) -> None:
        step = self.control_ranges[index] / 20.0
        var = self.control_delta_vars[index]
        next_value = float(var.get()) + direction * step
        next_value = float(np.clip(next_value, -self.control_ranges[index], self.control_ranges[index]))
        var.set(round(next_value, 6))
        self._update_pending_status()

    def _reset_pending_deltas(self) -> None:
        for var in self.control_delta_vars:
            var.set(0.0)

    def _update_pending_status(self) -> None:
        if not self.control_delta_vars:
            return
        try:
            max_delta = max(abs(float(var.get())) for var in self.control_delta_vars)
        except (tk.TclError, ValueError):
            self.status_var.set("Pending controls contain a nonnumeric value")
            return
        if max_delta > 0:
            self.status_var.set("Pending control changes")

    def apply_controls(self) -> None:
        """Applies pending control deltas, solves, and redraws."""
        try:
            deltas = self._read_deltas()
        except ValueError as exc:
            self.status_var.set(str(exc))
            return

        snapshot = self._snapshot()
        self._last_snapshot = snapshot
        if deltas:
            self.tensegrity.change_control_lengths(*deltas)
        result = self.solve_and_render(reason="Applied controls")
        if result.success:
            self._reset_pending_deltas()
        else:
            self._restore_snapshot(snapshot)
            self.render()

    def reset_controls(self) -> None:
        """Resets control rest lengths, solves, and redraws."""
        snapshot = self._snapshot()
        self._last_snapshot = snapshot
        self.tensegrity.reset_control_lengths()
        self._reset_pending_deltas()
        result = self.solve_and_render(reason="Reset controls")
        if not result.success:
            self._restore_snapshot(snapshot)
            self.render()

    def undo(self) -> None:
        """Restores the previous solved state."""
        if self._last_snapshot is None:
            self.status_var.set("Nothing to undo")
            return
        current = self._snapshot()
        self._restore_snapshot(self._last_snapshot)
        self._last_snapshot = current
        self.render()
        self.status_var.set("Undo restored previous state")
        self._update_stats(None)

    def solve_and_render(self, reason: str = "Solve") -> SolverResult:
        """Runs the solver, updates status text, and redraws on success."""
        result = self.solver.solve()
        if result.success:
            self.status_var.set(f"{reason}: {result.message}")
            self.render()
        else:
            self.status_var.set(result.message)
        self._update_stats(result)
        return result

    def render(self) -> None:
        """Redraws the structure with the current display settings."""
        self.viz.plot(
            label_nodes=self.show_nodes_var.get(),
            label_connections=self.show_connections_var.get(),
            label_forces=self.show_forces_var.get(),
        )
        self.canvas.draw_idle()
        self._update_position_text()
        self._update_force_stats_text()

    def fit_view(self) -> None:
        self.viz.fit_view()
        self.canvas.draw_idle()

    def reset_camera(self) -> None:
        self.viz.reset_camera()
        self.canvas.draw_idle()

    def set_camera(self, elev: float, azim: float) -> None:
        if self.dim != 3:
            return
        self.viz.ax.view_init(elev=elev, azim=azim)
        self.viz.set_3d_equal_scaling(self.viz.ax)
        self.canvas.draw_idle()

    def _update_stats(self, result: SolverResult | None) -> None:
        if result is None or result.scipy_result is None:
            self.residual_var.set("Residual: -")
            return
        scipy_result = result.scipy_result
        if hasattr(scipy_result, "fun"):
            residual = float(np.linalg.norm(scipy_result.fun))
        else:
            residual = float(np.linalg.norm(self.solver._objective(scipy_result.x)))
        self.residual_var.set(f"Residual: {residual:.3e}")

    def _update_force_stats_text(self) -> None:
        forces = np.array([connection.force for connection in self.tensegrity.connections if connection.force is not None], dtype=float)
        if len(forces) == 0:
            self.force_stats_var.set("Forces: -")
            return
        zero_count = int(np.count_nonzero(np.abs(forces) <= 1e-8))
        self.force_stats_var.set(
            f"Forces: max {np.max(np.abs(forces)):.3g} | zero {zero_count}/{len(forces)}"
        )

    def _update_position_text(self) -> None:
        if not self.tensegrity.positions:
            self.position_var.set("No requested positions.")
            return

        nodes_by_name = {node.name: node for node in self.tensegrity.nodes}
        lines = []
        for node_name in self.tensegrity.positions:
            node = nodes_by_name.get(node_name)
            if node is None:
                lines.append(f"{node_name}: unknown")
            else:
                values = ", ".join(f"{value:.3f}" for value in node.position)
                lines.append(f"{node_name}: ({values})")
        self.position_var.set("\n".join(lines))
