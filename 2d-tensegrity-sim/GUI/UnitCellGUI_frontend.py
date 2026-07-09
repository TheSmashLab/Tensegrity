import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import UnitCellGUI_backend as be

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

from TensegritySim import TensegrityError


def _show_gui_error(title, error):
    messagebox.showerror(title, str(error))


def _configure_ui_defaults(root):
    """Normalize Tk scaling and default fonts so widget sizes stay consistent."""
    if getattr(root, "_ui_defaults_configured", False):
        return

    try:
        scaling = root.winfo_fpixels("1i") / 72.0
        if scaling > 0:
            root.tk.call("tk", "scaling", scaling)
    except tk.TclError:
        pass

    try:
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkTextFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkMenuFont").configure(family="Segoe UI", size=10)
        if "TkHeadingFont" in tkfont.names():
            tkfont.nametofont("TkHeadingFont").configure(family="Segoe UI", size=10, weight="bold")
        if "TkFixedFont" in tkfont.names():
            tkfont.nametofont("TkFixedFont").configure(family="Consolas", size=10)
    except tk.TclError:
        pass

    root.option_add("*Button.Font", "TkDefaultFont")
    root.option_add("*TButton.Font", "TkDefaultFont")
    root._ui_defaults_configured = True


class InstructionsWindow(tk.Toplevel):
    """Scrollable modal window that shows workflow or window-specific instructions."""

    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title(title)
        self.geometry("720x520")
        self.minsize(560, 380)
        self.resizable(True, True)

        if parent.winfo_exists() and parent.winfo_viewable():
            self.transient(parent)

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        tk.Label(frm, text=title, font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 8))

        text_frame = ttk.Frame(frm)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set, relief="solid", bd=1)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        text_widget.insert("1.0", content.strip())
        text_widget.config(state="disabled")

        button_frame = ttk.Frame(frm)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Button(button_frame, text="Close", command=self.destroy, width=12).pack(side=tk.RIGHT)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.after(10, self._safe_grab_set)

    def _safe_grab_set(self):
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass


_WORKFLOW_OVERVIEW_TEXT = """
1. Choose 2D / 2.5D or 3D when the app starts.
2. In the unit cell window, draw the unit cell that will be patterned to make the tensegrity structure.
3. Use Submit to send the finished unit cell to the structure window.
4. In the structure window, place pins and draw cluster strings.
5. Open Builder Details to set stiffness, file name, active strings, and available surface options.
6. Generate YAML when the structure is ready to export.
"""

_UNIT_CELL_2D_INSTRUCTIONS = """
2D Unit Cell Window
- Grid Settings changes the grid size and spacing. You can also add custom nodes there.
- Use the Line Style menu to switch between bars, strings, horizontal wraps, vertical wraps, and delete.
- Hold Ctrl and use the mouse wheel to cycle line styles quickly.
- Click the canvas to pick grid points and draw or remove connections.
- Show Node Positions only toggles coordinate labels; existing lines stay visible.
- Hide unconnected nodes hides and disables clicking on nodes that are not part of any drawn unit-cell element.
- Clear Lines removes every connection in the current unit cell.
- Submit sends the finished unit cell to the structure window.
"""

_STRUCTURE_2D_INSTRUCTIONS = """
2D Structure Window
- Structure Settings controls the pattern length and generates the full structure.
- Use the Structure Element menu to switch between pins, unpin, and clustered strings.
- Click the canvas to place the currently selected element.
- Press Enter to finish a clustered string.
- Horizontal Wrapping draws wrapped clustered-string links as short outward stubs instead of direct cross-structure lines.
- Builder Details controls stiffness, file name, active strings, and 2D cylinder surface options.
- Generate YAML writes the current structure to a YAML file.
"""

_UNIT_CELL_3D_INSTRUCTIONS = """
3D Unit Cell Window
- Grid Settings changes the 3D grid size and spacing. You can also add custom nodes there.
- Use the Line Style menu to switch between bars, strings, X connectors, Y connectors, Z connectors, and delete.
- Hold Ctrl and use the mouse wheel to cycle line styles quickly.
- Click the canvas to pick grid points and draw or remove connections.
- Show Node Positions only toggles coordinate labels; existing lines stay visible.
- Hide unconnected nodes hides and disables picking on nodes that are not part of any drawn unit-cell element.
- Clear Lines removes every connection in the current unit cell.
- Submit sends the finished unit cell to the structure window.
"""

_STRUCTURE_3D_INSTRUCTIONS = """
3D Structure Window
- Structure Settings controls the pattern length and generates the full 3D structure.
- Use the Structure Element menu to switch between pins, unpin, and clustered strings.
- Click the canvas to place the currently selected element.
- Press Enter to finish a clustered string.
- Builder Details controls stiffness, file name, and active strings. 3D cylinder surface controls are intentionally unavailable.
- Generate YAML writes the current structure to a YAML file.
"""


def _show_instructions_window(parent, title, content):
    return InstructionsWindow(parent, title, content)

def close_root_if_last_window(root):
    """Close the Tk root if no visible root and no child toplevel windows remain."""
    try:
        if root is None or not root.winfo_exists():
            return

        visible_toplevel_exists = False
        for child in root.winfo_children():
            if isinstance(child, tk.Toplevel) and child.winfo_exists():
                visible_toplevel_exists = True
                break

        if (not root.winfo_viewable()) and (not visible_toplevel_exists):
            root.quit()
            root.destroy()
    except tk.TclError:
        pass

def quit_entire_program(window):
    """Quit and destroy the full Tk application from any child window."""
    try:
        current = window
        while getattr(current, "master", None) is not None:
            current = current.master
        current.quit()
        current.destroy()
    except tk.TclError:
        pass

def set_equal_axes_limits(ax, points, padding_ratio=0.08, min_padding=0.25):
    """Set x/y limits to fit all points with padding while preserving equal unit scaling."""
    if not points:
        return

    x_vals = [p[0] for p in points]
    y_vals = [p[1] for p in points]

    min_x, max_x = min(x_vals), max(x_vals)
    min_y, max_y = min(y_vals), max(y_vals)

    span_x = max_x - min_x
    span_y = max_y - min_y

    effective_span_x = span_x if span_x > 1e-9 else 1.0
    effective_span_y = span_y if span_y > 1e-9 else 1.0
    padding_x = max(effective_span_x * padding_ratio, min_padding)
    padding_y = max(effective_span_y * padding_ratio, min_padding)

    ax.set_xlim(min_x - padding_x, max_x + padding_x)
    ax.set_ylim(min_y - padding_y, max_y + padding_y)
    ax.set_aspect('equal', adjustable='box')


def is_widget_in_control_frame(event, main_frame) -> bool:
    """Shared helper: check if an event occurred inside a top control frame or control widget."""
    widget = getattr(event, 'widget', None)
    if widget is None:
        return False

    widget_class = widget.__class__.__name__
    if widget_class in ['Button', 'Label', 'Checkbutton', 'Entry', 'Combobox', 'OptionMenu']:
        return True

    current = widget
    while current:
        try:
            if current.winfo_name() == 'frame':
                parent = current.nametowidget(current.winfo_parent())
                if parent == main_frame and current.winfo_y() < 200:
                    return True
        except Exception:
            pass
        current = current.master if hasattr(current, 'master') else None
    return False

class UnitCellBuilderApp:
    def __init__(self, root):

        self.unit = be.UnitCell()
        self.path = []
        self.structure_window = None

        self.root = root
        _configure_ui_defaults(self.root)
        self.root.title("Unit Cell Builder")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create a frame for the unit cell builder
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        # Frame for line creation controls
        line_control_frame = tk.Frame(self.main_frame)
        line_control_frame.pack(side=tk.TOP, fill=tk.X)

        # Submenu for grid generation controls
        self.grid_settings_btn = tk.Button(line_control_frame, text="Grid Settings ▶", command=self.grid_settings)
        self.grid_settings_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.grid_settings_btn, "Adjust grid size and spacing")

        self.instructions_btn = tk.Button(line_control_frame, text="Instructions", command=self.open_instructions)
        self.instructions_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.instructions_btn, "Open instructions for the unit cell window")

        # Line style selection with dropdown menu
        self.line_style = tk.StringVar(value="bar")

        tk.Label(line_control_frame, text="Line Style:").pack(side=tk.LEFT, padx=5)

        LINE_STYLES = {
            "Bar": "bar",
            "String": "string",
            "Horizontal Connector": "horizontal wrap",
            "Vertical Connector": "vertical wrap",
            "Delete": "delete",
        }

        self.line_style_label = tk.StringVar(value="Bar")

        def set_line_style(value):
            self.line_style.set(value)
            for label, v in LINE_STYLES.items():
                if v == value:
                    self.line_style_label.set(label)
                    break
            self.update_cursor()

        def on_menu_change(label):
            set_line_style(LINE_STYLES[label])

        # Dropdown
        line_style_menu = tk.OptionMenu(
            line_control_frame,
            self.line_style_label,
            *LINE_STYLES.keys(),
            command=on_menu_change
        )
        line_style_menu.config(width=17)
        line_style_menu.pack(side=tk.LEFT)

        # Hint label for keyboard shortcut
        hint_label = tk.Label(line_control_frame, text="(Ctrl + scroll wheel)", font=("Arial", 8), fg="gray")
        hint_label.pack(side=tk.LEFT, padx=2)

        # --- Ctrl+scroll wheel to change line style ---
        # Define the line styles in order
        self.line_styles_list = ["bar", "string", "horizontal wrap", "vertical wrap", "delete"]
        self.current_style_index = 0  # Start with "bar"

        def on_ctrl_scroll(event):
            """Handle Ctrl+scroll wheel to change line style."""
            if event.state & 0x4:  # Check if Ctrl is pressed (0x4 is Ctrl modifier)
                if event.delta > 0 or event.num == 4:  # Scroll up
                    self.current_style_index = (self.current_style_index - 1) % len(self.line_styles_list)
                elif event.delta < 0 or event.num == 5:  # Scroll down
                    self.current_style_index = (self.current_style_index + 1) % len(self.line_styles_list)
                set_line_style(self.line_styles_list[self.current_style_index])

        root = self.root
        root.bind_all("<MouseWheel>", on_ctrl_scroll)  # Windows
        root.bind_all("<Button-4>", on_ctrl_scroll)    # Linux scroll up
        root.bind_all("<Button-5>", on_ctrl_scroll)    # Linux scroll down

        # Add tooltip to the dropdown menu
        def on_enter_menu(event):
            self.show_tooltip("Ctrl + mouse wheel to change line style", event.x_root, event.y_root)

        def on_leave_menu(event):
            self.hide_tooltip()

        line_style_menu.bind("<Enter>", on_enter_menu)
        line_style_menu.bind("<Leave>", on_leave_menu)

        # Initialize tooltip
        self.tooltip_window = None

        # Clear Lines Button
        self.clear_btn = tk.Button(line_control_frame, text="Clear Lines", command=self.clear_lines)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.clear_btn, "Clear all drawn lines")

        # Submit Button
        self.submit_btn = tk.Button(line_control_frame, text="Submit", command=self.submit_values)
        self.submit_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.submit_btn, "Submit and prepare for structure generation")

        # Quit Program Button
        self.quit_btn = tk.Button(line_control_frame, text="Quit Program", command=self.quit_program)
        self.quit_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.quit_btn, "Quit the entire program")

        # Toggle switch for node positions
        self.show_node_positions = tk.BooleanVar(value=False)
        self.node_positions_toggle = tk.Checkbutton(
            line_control_frame,
            text="Show Node Positions",
            variable=self.show_node_positions,
            command=self.update_grid_display
        )
        self.node_positions_toggle.pack(side=tk.LEFT, padx=5)

        self.hide_unconnected_nodes = tk.BooleanVar(value=False)
        self.hide_unconnected_toggle = tk.Checkbutton(
            line_control_frame,
            text="Hide unconnected nodes",
            variable=self.hide_unconnected_nodes,
            command=self.update_grid_display
        )
        self.hide_unconnected_toggle.pack(side=tk.LEFT, padx=5)

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_aspect('equal', adjustable='box')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas_widget.bind("<Enter>", self.enter_canvas)
        self.canvas1message = "Click to draw a bar"
        self.help_prompt = GlobalHoverPrompt(self.root, text=self.canvas1message, delay=500)

        # Initialize grid settings
        self.x_count = 5
        self.y_count = 5
        self.x_spacing = 1.0
        self.y_spacing = 1.0
        
        # Initialize tk variables for grid distances (used in generate_graph)
        self.x_distance = tk.DoubleVar(value=1.0)
        self.y_distance = tk.DoubleVar(value=1.0)
        
        # Initialize data structures
        self.points = []
        self.custom_points = []
        self.selected_points = []
        self.bars = []
        self.strings = []
        self.visible_points = []
    
        # Generate initial grid
        self.generate_grid()
        self.canvas.mpl_connect("button_press_event", self.on_left_click)

    def update_cursor(self):
        """Update the cursor style based on the selected line style."""
        line_style = self.line_style.get()
        if line_style == "bar":
            self.canvas1message = "Click to draw a bar"
        elif line_style == "string":
            self.canvas1message = "Click to draw a string"
        elif line_style == "horizontal wrap":
            self.canvas1message = "Click to draw a horizontal connector"
        elif line_style == "vertical wrap":
            self.canvas1message = "Click to draw a vertical connector"
        elif line_style == "delete":
            self.canvas1message = "Click to delete a line or string"
        if hasattr(self, "help_prompt") and self.help_prompt:
            self.help_prompt.set_message(self.canvas1message)

    def enter_canvas(self, event):
        # Only show message if not in the control frame
        if not self.is_in_control_frame(event):
            if hasattr(self, "help_prompt") and self.help_prompt:
                self.help_prompt.set_message(self.canvas1message)

    def is_in_control_frame(self, event):
        """Check if event is within a top control frame or over a button/control widget."""
        widget = event.widget
        return is_widget_in_control_frame(event, self.main_frame)

    def grid_settings(self):
        """Open the grid settings window."""
        initial_settings = {
            "x_points": self.x_count,
            "x_distance": self.x_spacing,
            "y_points": self.y_count,
            "y_distance": self.y_spacing
        }
        GridSettingsWindow(self.root, initial_settings, self.apply_grid_settings, self.add_custom_node)

    def open_instructions(self):
        _show_instructions_window(self.root, "Unit Cell Instructions", _UNIT_CELL_2D_INSTRUCTIONS)

    def generate_grid(self, reset_lines=True):
        """Generate a uniform grid of points based on user input."""
        # Create grid points
        self.points = self.unit.generate_grid(self.x_count, self.y_count, self.x_spacing, self.y_spacing)
        for point in self.custom_points:
            if point not in self.points:
                self.points.append(point)

        if reset_lines:
            self.unit.clear_lines()
            self.selected_points.clear()
            self.bars.clear()
            self.strings.clear()
        self._redraw_unit_cell_graph()

    def add_custom_node(self, point):
        """Add a custom node to the current grid and redraw."""
        if point in self.custom_points:
            return False
        self.custom_points.append(point)
        self.points.append(point)
        self.update_grid_display()
        return True

    def update_grid_display(self):
        """Redraw unit-cell display after visibility-only toggles change."""
        self._redraw_unit_cell_graph()

    def _visible_unit_points(self):
        return be.visible_unit_points(
            self.points,
            self.hide_unconnected_nodes.get(),
            self.unit.bars,
            self.unit.strings,
            self.unit.hw,
            self.unit.vw,
        )

    def _draw_unit_cell_points(self):
        if not self.points:
            return
        self.visible_points = self._visible_unit_points()
        if not self.visible_points:
            return

        # Scatter plot of points
        x_vals, y_vals = zip(*self.visible_points)
        self.ax.scatter(x_vals, y_vals, color="black", s=50)

        # Label points only if toggle is enabled
        if self.show_node_positions.get():
            for i, (x, y) in enumerate(self.visible_points):
                self.ax.text(x, y, f"[{x}, {y}]", fontsize=10, verticalalignment="bottom", horizontalalignment="right")

    def _redraw_unit_cell_graph(self):
        """Redraw points, labels, and all existing unit-cell elements."""
        self.ax.clear()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_aspect('equal', adjustable='box')

        self._draw_unit_cell_points()

        for bar in self.unit.bars:
            x_vals, y_vals = zip(*bar)
            self.ax.plot(x_vals, y_vals, linestyle='-', color="blue")
        for string in self.unit.strings:
            x_vals, y_vals = zip(*string)
            self.ax.plot(x_vals, y_vals, linestyle='--', color="red")
        for hwrap in self.unit.hw:
            x_vals, y_vals = zip(*hwrap)
            stub = (self.x_spacing if hasattr(self, 'x_spacing') else self.x_distance.get()) * 0.1
            self.ax.plot([max(x_vals), max(x_vals) + stub], [y_vals[x_vals.index(max(x_vals))], y_vals[x_vals.index(max(x_vals))]], linestyle='--', color="green")
            self.ax.plot([min(x_vals), min(x_vals) - stub], [y_vals[x_vals.index(min(x_vals))], y_vals[x_vals.index(min(x_vals))]], linestyle='--', color="green")
        for vwrap in self.unit.vw:
            x_vals, y_vals = zip(*vwrap)
            stub = (self.y_spacing if hasattr(self, 'y_spacing') else self.y_distance.get()) * 0.1
            self.ax.plot([x_vals[y_vals.index(max(y_vals))], x_vals[y_vals.index(max(y_vals))]], [max(y_vals), max(y_vals) + stub], linestyle='--', color="green")
            self.ax.plot([x_vals[y_vals.index(min(y_vals))], x_vals[y_vals.index(min(y_vals))]], [min(y_vals), min(y_vals) - stub], linestyle='--', color="green")

        set_equal_axes_limits(self.ax, self.points)
        self.canvas.draw()

    def apply_grid_settings(self, settings):
        """Apply the grid settings from the settings window."""
        self.x_count = settings["x_points"]
        self.x_spacing = settings["x_distance"]
        self.y_count = settings["y_points"]
        self.y_spacing = settings["y_distance"]
        self.generate_grid()

    def on_left_click(self, event):
        """Handle click events for selecting points and drawing lines."""
        if event.xdata is None or event.ydata is None:
            return  # Ignore clicks outside the plot
        if not self.visible_points:
            self.visible_points = self._visible_unit_points()
        if not self.visible_points:
            return
        
        # Find the closest point
        clicked_point = min(self.visible_points, key=lambda p: np.linalg.norm([p[0] - event.xdata, p[1] - event.ydata]))
        line_style = self.line_style.get()       
        bars, strings, hw, vw = self.unit.create_lines(clicked_point, line_style)
        self.generate_graph(bars, strings, hw, vw)

    def generate_graph(self, bars, strings, hw, vw):
        """Generate a graph of the unit cell."""
        self._redraw_unit_cell_graph()

    def quit_program(self):
        """Quit the entire application."""
        self.hide_tooltip()
        quit_entire_program(self.root)

    def clear_lines(self):
        """Clear all drawn lines with confirmation."""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all lines?"):
            self.unit.clear_lines()
            self.ax.clear()
            self.generate_grid()

    def submit_values(self):
        """Submit the selected lines and open the structure builder window."""
        
        # Validate that connection parameters are set
        if not self.unit.hw or not self.unit.vw:
            messagebox.showerror("Validation Error", "Please set connection parameters and resubmit.")
            return
        
        self.unit.submit_values()
        
        # Open structure builder in a new window
        if self.structure_window is None or not self.structure_window.root.winfo_exists():
            structure_root = tk.Toplevel(self.root)
            self.structure_window = StructureBuilderApp(structure_root, self.unit)
        else:
            # Bring existing window to front
            self.structure_window.root.lift()
            self.structure_window.root.focus()

    def on_closing(self):
        """Handle closing the window."""
        self.hide_tooltip()
        if self.structure_window is not None and self.structure_window.root.winfo_exists():
            self.structure_window.root.destroy()
        self.root.quit()
        self.root.destroy()

    def show_tooltip(self, text, x, y):
        """Display a tooltip at the specified coordinates."""
        self.hide_tooltip()
        self.tooltip_window = tk.Toplevel(self.root)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self.tooltip_window, text=text, bg="lightyellow", relief="solid", bd=1, padx=5, pady=2)
        label.pack()

    def hide_tooltip(self):
        """Hide the tooltip if it exists."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def add_button_tooltip(self, button, text):
        """Add a hover tooltip to a button."""
        def on_enter(event):
            self.show_tooltip(text, event.x_root, event.y_root)

        def on_leave(event):
            self.hide_tooltip()

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

class StructureBuilderApp:
    def __init__(self, root, unit_cell):
        
        self.root = root
        _configure_ui_defaults(self.root)
        self.root.title("Structure Builder")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.unit = unit_cell
        self.structure = be.Structure()
        self.supports_cylinder_surface = True
        
        # Create a frame for the structure builder
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        # Frame for top controls (Pattern Length and Generate Structure)
        top_control_frame = tk.Frame(self.main_frame)
        top_control_frame.pack(side=tk.TOP, fill=tk.X)

        # Horizontal Wrapping Checkbox
        self.cylinder_enabled = tk.BooleanVar(value=False)
        horizontal_wrap_check = tk.Checkbutton(
            top_control_frame,
            text="Horizontal Wrapping",
            variable=self.cylinder_enabled,
            command=self.on_horizontal_wrapping_toggle
        )
        horizontal_wrap_check.pack(side=tk.LEFT, padx=5)
        self.horizontal_wrap_check = horizontal_wrap_check
        self.add_button_tooltip(horizontal_wrap_check, "Enable cylindrical wrapping")

        self.instructions_btn = tk.Button(top_control_frame, text="Instructions", command=self.open_instructions)
        self.instructions_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.instructions_btn, "Open instructions for the structure window")

        self.x_pattern = tk.IntVar(value=5)
        self.y_pattern = tk.IntVar(value=5)
        self.self_similar_pattern = tk.StringVar(value="none")
        self.self_similar_pattern.trace_add("write", self._on_self_similar_pattern_changed)
        self.structure_settings_window = None
        self.structure_settings_btn = tk.Button(top_control_frame, text="Structure Settings ▶", command=self.open_structure_settings)
        self.structure_settings_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.structure_settings_btn, "Set pattern lengths and generate structure")

        # Structure element dropdown menu
        self.structure_element = tk.StringVar(value="x_pin")
        tk.Label(top_control_frame, text="Structure Element:").pack(side=tk.LEFT, padx=5)

        structure_options = ["X Pin", "Y Pin", "Unpin", "Clustered String"]
        structure_values = ["x_pin", "y_pin", "unpin", "multinode_string"]
        
        self.structure_element_dropdown = ttk.Combobox(
            top_control_frame,
            values=structure_options,
            state="readonly",
            width=15
        )
        self.structure_element_dropdown.set("X Pin")
        self.structure_element_dropdown.bind("<<ComboboxSelected>>", lambda e: (
            self.structure_element.set(structure_values[structure_options.index(self.structure_element_dropdown.get())]),
            self.update_cursor()
        ))
        self.structure_element_dropdown.pack(side=tk.LEFT, padx=5)

        # Generate delete Button
        delete_btn = tk.Button(top_control_frame, text="Delete Clustered String:", command=self.delete_string)
        delete_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(delete_btn, "Delete the selected clustered string")

        self.MNSdropdown = ttk.Combobox(top_control_frame, values=[""])
        self.MNSdropdown.current(0)
        self.MNSdropdown.pack(side=tk.LEFT, padx=5)

        # Frame for bottom controls (Builder Details and Generate YAML)
        bottom_control_frame = tk.Frame(self.main_frame)
        bottom_control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Generate YAML Button
        yaml_btn = tk.Button(bottom_control_frame, text="Generate YAML", command=self.generate_yaml)
        yaml_btn.pack(side=tk.RIGHT, padx=5)
        self.add_button_tooltip(yaml_btn, "Generate YAML file for the structure")

        # Builder Details Button
        builder_details_btn = tk.Button(bottom_control_frame, text="Builder Details ▶", command=self.open_builder_details)
        builder_details_btn.pack(side=tk.RIGHT, padx=5)
        self.add_button_tooltip(builder_details_btn, "Configure stiffness and other builder parameters")

        # Quit Program Button
        quit_btn = tk.Button(bottom_control_frame, text="Quit Program", command=self.quit_program)
        quit_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(quit_btn, "Quit the entire program")

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_aspect('equal', adjustable='box')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas_widget.bind("<Enter>", self.enter_canvas)
        self.canvas_message = "Open Structure Settings to generate the entire structure"

        # Hover prompt for structure window
        self.help_prompt = GlobalHoverPrompt(self.root, text=self.canvas_message, delay=500)
        
        # Initialize tooltip
        self.tooltip_window = None

        # Initialize data structures
        self.structure_points = []
        self.structure_bars = []
        self.structure_strings = []
        self.MNSindex = 0
        self.manual_view_active = False
        self.view_limits_2d = None
        
        # Initialize builder details variables
        self.string_stiffness = tk.IntVar(value=100)
        self.bar_stiffness = tk.IntVar(value=1000)
        self.string_initial_length_ratio = tk.DoubleVar(value=0.95)
        self.inside_string_initial_length_ratio = tk.DoubleVar(value=0.95)
        self.file_name = tk.StringVar(value="test_tensegrity")
        self.radius = tk.DoubleVar(value=0.0)
        self.selected_controls = []
        self.builder_details_window = None

        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)
        self.canvas.mpl_connect("scroll_event", self.on_plot_scroll)
        self.root.bind("<Return>", self.on_enter_pressed)

        # Open structure settings automatically when this window is created.
        self.open_structure_settings()
        self._update_cylinder_controls_for_self_similar()

    def _on_self_similar_pattern_changed(self, *_args):
        self._update_cylinder_controls_for_self_similar()

    def _update_cylinder_controls_for_self_similar(self):
        mode = self.self_similar_pattern.get().lower()
        enabled = (mode == "none")

        if hasattr(self, "horizontal_wrap_check") and self.horizontal_wrap_check.winfo_exists():
            self.horizontal_wrap_check.config(state="normal" if enabled else "disabled")

        if not enabled and self.cylinder_enabled.get():
            self.cylinder_enabled.set(False)

        if self.builder_details_window and self.builder_details_window.winfo_exists():
            self.builder_details_window._update_cylinder_availability()

    def open_structure_settings(self):
        """Open the structure settings window for pattern lengths and generation."""
        if self.structure_settings_window is not None and self.structure_settings_window.winfo_exists():
            self.structure_settings_window.lift()
            self.structure_settings_window.focus()
            return

        self.structure_settings_window = StructureSettingsWindow(
            self.root,
            title="Structure Settings",
            x_var=self.x_pattern,
            y_var=self.y_pattern,
            self_similar_var=self.self_similar_pattern,
            axis_options=("x", "y", "none"),
            on_generate=self.generate_structure,
            generate_button_text="Generate Structure",
        )

    def open_instructions(self):
        _show_instructions_window(self.root, "Structure Instructions", _STRUCTURE_2D_INSTRUCTIONS)

    def _build_pattern_geometry_2d(self):
        """Generate either regular tiled pattern or self-similar sequence based on settings."""
        mode = self.self_similar_pattern.get().lower()
        if mode in ("x", "y"):
            count = self.x_pattern.get() if mode == "x" else self.y_pattern.get()
            points, bars, strings = self.structure.generate_self_similar_grid(
                self.unit.bars,
                self.unit.strings,
                self.unit.hw,
                self.unit.vw,
                mode,
                count,
            )
            return points, bars, strings, True

        x_pattern = self.x_pattern.get()
        y_pattern = self.y_pattern.get()
        points, bars, strings = self.structure.generate_grid(self.unit.bars, self.unit.strings, self.unit.hw, self.unit.vw, x_pattern, y_pattern)
        return points, bars, strings, False

    def _sync_structure_backend_state(self, is_self_similar):
        """Keep backend Structure attributes in sync for YAML generation and surfaces."""
        self.structure_strings = be.prune_multinode_segments(self.structure_strings, self.structure.multinode_strings)
        self.structure.points = list({tuple(p) for p in self.structure_points})
        self.structure.unique_bars = [list(pair) for pair in self.structure_bars]
        self.structure.unique_strings = [list(pair) for pair in self.structure_strings]

        if is_self_similar:
            self.structure.outside_strings = [list(pair) for pair in self.structure_strings]
            self.structure.inside_strings = []
        else:
            self.structure.outside_strings = be.prune_multinode_segments(
                self.structure.outside_strings,
                self.structure.multinode_strings,
            )
            self.structure.inside_strings = be.prune_multinode_segments(
                self.structure.inside_strings,
                self.structure.multinode_strings,
            )

        try:
            self.structure.generate_linked_nodes()
        except Exception:
            self.structure.linked_nodes = []

    def update_cursor(self):
        """Update the cursor style based on the selected structure element."""
        structure_element = self.structure_element.get()
        if structure_element != "multinode_string":
            self.finalize_multinode_string()
        if structure_element == "x_pin":
            self.canvas_message = "Click to place an X pin"
        elif structure_element == "y_pin":
            self.canvas_message = "Click to place a Y pin"
        elif structure_element == "unpin":
            self.canvas_message = "Click to unpin a pin"
        elif structure_element == "multinode_string":
            self.canvas_message = 'Click to select next connected node. Press "Enter" when the string is done.'
        self.help_prompt.set_message(self.canvas_message)

    def enter_canvas(self, event):
        # Only show message if not in the control frame
        if not self.is_in_control_frame(event):
            self.help_prompt.set_message(self.canvas_message)

    def is_in_control_frame(self, event):
        return is_widget_in_control_frame(event, self.main_frame)

    def on_canvas_click(self, event):
        if event.inaxes is not None and event.inaxes.figure == self.fig:
            if not self.structure_points:
                return
            
            nearest_node, distance = be.nearest_point_2d(self.structure_points, event.xdata, event.ydata)
            selection_radius = be.selection_radius_2d(self.structure_points)

            if distance < selection_radius:  # Only register clicks within a certain distance
                pin_half = be.pin_half_length_2d(self.structure_points)

                if self.structure_element.get() == "x_pin":
                    if self.structure.apply_pin_action(nearest_node, "x_pin"):
                        self.ax.plot([nearest_node[0], nearest_node[0]], [nearest_node[1] - pin_half, nearest_node[1] + pin_half], color="black", linewidth=4)
                        self.canvas.draw()
                elif self.structure_element.get() == "y_pin":
                    if self.structure.apply_pin_action(nearest_node, "y_pin"):
                        self.ax.plot([nearest_node[0] - pin_half, nearest_node[0] + pin_half], [nearest_node[1], nearest_node[1]], color="black", linewidth=4)
                        self.canvas.draw()
                elif self.structure_element.get() == "unpin":
                    had_x_pin = nearest_node in self.structure.x_pins
                    had_y_pin = nearest_node in self.structure.y_pins
                    if self.structure.apply_pin_action(nearest_node, "unpin"):
                        if had_x_pin:
                            self.ax.plot([nearest_node[0], nearest_node[0]], [nearest_node[1] - pin_half, nearest_node[1] + pin_half], color="white", linewidth=4)
                        if had_y_pin:
                            self.ax.plot([nearest_node[0] - pin_half, nearest_node[0] + pin_half], [nearest_node[1], nearest_node[1]], color="white",linewidth=4)
                        self.ax.plot(nearest_node[0], nearest_node[1], color="black", linewidth=4)
                        self.canvas.draw()
                elif self.structure_element.get() == "multinode_string":
                    # Add node to current multinode string
                    if not self.structure.selected_points2 or nearest_node != self.structure.selected_points2[-1]:
                        self.structure.selected_points2.append(nearest_node)
                        self.redraw_current_multinode_string()

    def on_enter_pressed(self, event):
        """Handle Enter key press to finish multinode string."""
        if self.structure_element.get() == "multinode_string":
            self.finalize_multinode_string()

    def finalize_multinode_string(self):
        if len(self.structure.selected_points2) > 1:
            # Create the multinode string
            self.MNSindex += 1
            var_name = f"String{self.MNSindex}"
            copied_points = self.structure.selected_points2.copy()
            self.structure.multinode_strings.append({"name": var_name, "points": copied_points})
            self.structure_strings = be.prune_multinode_segments(self.structure_strings, self.structure.multinode_strings)
            self.update_dropdown()
            self.structure.selected_points2.clear()
            self.generate_structure()
        elif len(self.structure.selected_points2) > 0:
            # Clear incomplete string
            self.structure.selected_points2.clear()
            self.generate_structure()

    def on_horizontal_wrapping_toggle(self):
        if self.structure.selected_points2:
            self.redraw_current_multinode_string()
        else:
            self.generate_structure()

    def on_plot_scroll(self, event):
        """Zoom 2D structure plot with mouse wheel."""
        if event.inaxes != self.ax:
            return

        zoom_in = event.button == 'up'
        scale = 0.9 if zoom_in else 1.1

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_center = event.xdata if event.xdata is not None else (xlim[0] + xlim[1]) / 2.0
        y_center = event.ydata if event.ydata is not None else (ylim[0] + ylim[1]) / 2.0

        new_half_x = (xlim[1] - xlim[0]) * scale / 2.0
        new_half_y = (ylim[1] - ylim[0]) * scale / 2.0

        self.ax.set_xlim(x_center - new_half_x, x_center + new_half_x)
        self.ax.set_ylim(y_center - new_half_y, y_center + new_half_y)
        self.manual_view_active = True
        self.view_limits_2d = (self.ax.get_xlim(), self.ax.get_ylim())
        self.canvas.draw()

    def _point_to_node_name(self, point):
        return f"({point[0]} {point[1]})"

    def _is_linked_pair(self, point_a, point_b):
        return self.structure.is_linked_pair(point_a, point_b)

    def _draw_horizontal_stub(self, point, min_x, max_x, stub_length, color, linewidth=2, linestyle='--'):
        x, y = point
        x2, y2 = be.horizontal_stub_endpoint(point, min_x, max_x, stub_length)
        self.ax.plot([x, x2], [y, y2], linestyle=linestyle, color=color, linewidth=linewidth)

    def _draw_multinode_segments(self, points, color, linewidth=2, linestyle='--'):
        if len(points) < 2:
            return
        if self.structure_points:
            xs = [p[0] for p in self.structure_points]
            min_x, max_x = min(xs), max(xs)
        else:
            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
        span = max_x - min_x
        stub_length = span * 0.05 if span > 0 else 0.2

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            if self.cylinder_enabled.get() and self._is_linked_pair(p1, p2):
                self._draw_horizontal_stub(p1, min_x, max_x, stub_length, color, linewidth, linestyle)
                self._draw_horizontal_stub(p2, min_x, max_x, stub_length, color, linewidth, linestyle)
            else:
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], linestyle=linestyle, color=color, linewidth=linewidth)

    def redraw_current_multinode_string(self):
        """Redraw the structure with the current multinode string being drawn."""
        # Regenerate the structure view
        self.ax.clear()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_aspect('equal', adjustable='box')
        self.structure_points, self.structure_bars, self.structure_strings, is_self_similar = self._build_pattern_geometry_2d()
        self._sync_structure_backend_state(is_self_similar)
        # Scatter plot of points
        x_vals, y_vals = zip(*self.structure_points)
        self.ax.scatter(x_vals, y_vals, color="black", s=25)
        for bar in self.structure_bars:
            x_vals, y_vals = zip(*bar)
            line, = self.ax.plot(x_vals, y_vals, linestyle='-', color="blue")
        
        # Plot all strings in red (both outside and inside)
        for string in self.structure.outside_strings:
            x_vals, y_vals = zip(*string)
            line, = self.ax.plot(x_vals, y_vals, linestyle='--', color="red")
        
        for string in self.structure.inside_strings:
            x_vals, y_vals = zip(*string)
            line, = self.ax.plot(x_vals, y_vals, linestyle='--', color="red")
        
        # Compute pin half-length proportional to structure span
        if self.structure_points:
            pin_half_all = be.pin_half_length_2d(self.structure_points)
        else:
            pin_half_all = be.pin_half_length_2d([])

        for x_pin in self.structure.x_pins:
            self.ax.plot([x_pin[0], x_pin[0]], [x_pin[1] - pin_half_all, x_pin[1] + pin_half_all], color="black", linewidth=4)
        for y_pin in self.structure.y_pins:
            self.ax.plot([y_pin[0] - pin_half_all, y_pin[0] + pin_half_all], [y_pin[1], y_pin[1]], color="black", linewidth=4)
        for mns in self.structure.multinode_strings:
            self._draw_multinode_segments(mns["points"], color="green", linewidth=2, linestyle='--')
            x_vals, y_vals = zip(*mns["points"])
            self.ax.text(x_vals[0], y_vals[0], mns["name"], fontsize=10, verticalalignment="bottom", horizontalalignment="right")
        
        # Draw the current multinode string being constructed in a different color (blue/orange)
        if len(self.structure.selected_points2) > 0:
            self._draw_multinode_segments(self.structure.selected_points2, color="orange", linewidth=2, linestyle='--')
            
            # Highlight the nodes being selected
            for point in self.structure.selected_points2:
                self.ax.plot(point[0], point[1], 'o', color="orange", markersize=8)

        if self.manual_view_active and self.view_limits_2d:
            self.ax.set_xlim(self.view_limits_2d[0])
            self.ax.set_ylim(self.view_limits_2d[1])
        else:
            set_equal_axes_limits(self.ax, self.structure_points)
        self.canvas.draw()

    def generate_structure(self):
        """Generate a graph of the entire structure."""
        self.ax.clear()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_aspect('equal', adjustable='box')
        self.structure_points, self.structure_bars, self.structure_strings, is_self_similar = self._build_pattern_geometry_2d()
        self._sync_structure_backend_state(is_self_similar)
        # Scatter plot of points
        x_vals, y_vals = zip(*self.structure_points)
        self.ax.scatter(x_vals, y_vals, color="black", s=25)
        for bar in self.structure_bars:
            x_vals, y_vals = zip(*bar)
            line, = self.ax.plot(x_vals, y_vals, linestyle='-', color="blue")
        
        # Plot all strings in red (both outside and inside)
        for string in self.structure.outside_strings:
            x_vals, y_vals = zip(*string)
            line, = self.ax.plot(x_vals, y_vals, linestyle='--', color="red")
        
        for string in self.structure.inside_strings:
            x_vals, y_vals = zip(*string)
            line, = self.ax.plot(x_vals, y_vals, linestyle='--', color="red")
        
        # Compute pin half-length proportional to structure span
        if self.structure_points:
            pin_half_all = be.pin_half_length_2d(self.structure_points)
        else:
            pin_half_all = be.pin_half_length_2d([])

        for x_pin in self.structure.x_pins:
            self.ax.plot([x_pin[0], x_pin[0]], [x_pin[1] - pin_half_all, x_pin[1] + pin_half_all], color="black", linewidth=4)
        for y_pin in self.structure.y_pins:
            self.ax.plot([y_pin[0] - pin_half_all, y_pin[0] + pin_half_all], [y_pin[1], y_pin[1]], color="black", linewidth=4)
        for mns in self.structure.multinode_strings:
            self._draw_multinode_segments(mns["points"], color="green", linewidth=2, linestyle='--')
            x_vals, y_vals = zip(*mns["points"])
            self.ax.text(x_vals[0], y_vals[0], mns["name"], fontsize=10, verticalalignment="bottom", horizontalalignment="right")

        if self.manual_view_active and self.view_limits_2d:
            self.ax.set_xlim(self.view_limits_2d[0])
            self.ax.set_ylim(self.view_limits_2d[1])
        else:
            set_equal_axes_limits(self.ax, self.structure_points)
        self.canvas.draw()

    def quit_program(self):
        """Quit the entire application."""
        self.hide_tooltip()
        quit_entire_program(self.root)

    def delete_string(self):
        """Delete the selected multinode string."""
        selected_name = self.MNSdropdown.get()
        for mns in self.structure.multinode_strings:
            if mns["name"] == selected_name:
                self.structure.multinode_strings.remove(mns)
                break
        self.update_dropdown()
        self.generate_structure()

    def update_dropdown(self):
        """Update the dropdown menu with the names of the multinode strings."""
        names = [mns["name"] for mns in self.structure.multinode_strings]
        self.selected_controls = [name for name in self.selected_controls if name in names]

        try:
            if names:
                self.MNSdropdown['values'] = names
            else:
                self.MNSdropdown['values'] = [""]
            self.MNSdropdown.current(0)
        except tk.TclError:
            # Widget was destroyed, silently ignore
            pass

        try:
            if self.builder_details_window and self.builder_details_window.winfo_exists():
                self.builder_details_window.refresh_control_checkboxes(names, self.selected_controls)
        except tk.TclError:
            self.builder_details_window = None
    
    def open_builder_details(self):
        """Open the builder details window."""
        names = [mns["name"] for mns in self.structure.multinode_strings]
        self.selected_controls = [name for name in self.selected_controls if name in names]
        initial_settings = {
            "string_stiffness": self.string_stiffness.get(),
            "bar_stiffness": self.bar_stiffness.get(),
            "string_initial_length_ratio": self.string_initial_length_ratio.get(),
            "inside_string_initial_length_ratio": self.inside_string_initial_length_ratio.get(),
            "file_name": self.file_name.get(),
            "cylinder_enabled": self.cylinder_enabled.get(),
            "radius": self.radius.get(),
            "control_names": self.selected_controls.copy(),
            "multinode_strings": names,
        }
        self.builder_details_window = BuilderDetailsWindow(self.root, initial_settings, self.apply_builder_details, self)
    
    def apply_builder_details(self, settings):
        """Apply the builder details from the settings window."""
        self.string_stiffness.set(settings["string_stiffness"])
        self.bar_stiffness.set(settings["bar_stiffness"])
        self.string_initial_length_ratio.set(settings["string_initial_length_ratio"])
        self.inside_string_initial_length_ratio.set(settings["inside_string_initial_length_ratio"])
        self.file_name.set(settings["file_name"])
        self.cylinder_enabled.set(settings.get("cylinder_enabled", False))
        self.radius.set(settings.get("radius", 0.0))
        self.selected_controls = settings.get("control_names", [])
    
    def generate_yaml(self):
        file_name = self.file_name.get()
        if not file_name:
            messagebox.showerror("Input Error", "Please set a file name in Builder Details.")
            return

        names = [mns["name"] for mns in self.structure.multinode_strings]
        selected_controls = [name for name in self.selected_controls if name in names]
        self.selected_controls = selected_controls
        try:
            self.structure.generate_yaml(
                self.string_stiffness.get(),
                self.bar_stiffness.get(),
                self.string_initial_length_ratio.get(),
                self.inside_string_initial_length_ratio.get(),
                selected_controls,
                file_name,
                self.cylinder_enabled.get(),
                self.radius.get(),
            )
        except TensegrityError as error:
            _show_gui_error("YAML Generation Error", error)
            return
        except Exception as error:
            _show_gui_error("Unexpected YAML Error", error)
            return

    def on_closing(self):
        """Handle closing the window."""
        self.hide_tooltip()
        parent_root = self.root.master if isinstance(self.root.master, tk.Tk) else None
        self.root.destroy()
        if parent_root is not None:
            parent_root.after(10, lambda: close_root_if_last_window(parent_root))

    def show_tooltip(self, text, x, y):
        """Display a tooltip at the specified coordinates."""
        self.hide_tooltip()
        self.tooltip_window = tk.Toplevel(self.root)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self.tooltip_window, text=text, bg="lightyellow", relief="solid", bd=1, padx=5, pady=2)
        label.pack()

    def hide_tooltip(self):
        """Hide the tooltip if it exists."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def add_button_tooltip(self, button, text):
        """Add a hover tooltip to a button."""
        def on_enter(event):
            self.show_tooltip(text, event.x_root, event.y_root)

        def on_leave(event):
            self.hide_tooltip()

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

class BuilderDetailsWindow(tk.Toplevel):
    def __init__(self, parent, initial_settings: dict, on_save, parent_app=None):
        super().__init__(parent)
        self.title("Builder Details")
        self.resizable(False, False)

        self.on_save = on_save
        self.parent_app = parent_app

        # Make it behave like a modal dialog
        self.transient(parent)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # File Name Input
        tk.Label(frm, text="File Name:").grid(row=4, column=0, sticky="w", pady=4)
        self.file_name = tk.StringVar(value=initial_settings["file_name"])
        tk.Entry(frm, textvariable=self.file_name, width=20).grid(row=4, column=1, sticky="w", pady=4)

        self.selected_controls = set(initial_settings.get("control_names", []))

        # String Stiffness Input
        tk.Label(frm, text="String Stiffness:").grid(row=0, column=0, sticky="w", pady=4)
        self.string_stiffness = tk.IntVar(value=initial_settings["string_stiffness"])
        tk.Entry(frm, textvariable=self.string_stiffness, width=10).grid(row=0, column=1, sticky="w", pady=4)

        # Bar Stiffness Input
        tk.Label(frm, text="Bar Stiffness:").grid(row=1, column=0, sticky="w", pady=4)
        self.bar_stiffness = tk.IntVar(value=initial_settings["bar_stiffness"])
        tk.Entry(frm, textvariable=self.bar_stiffness, width=10).grid(row=1, column=1, sticky="w", pady=4)

        # String Initial Length Ratio Input
        tk.Label(frm, text="String Initial Length Ratio:").grid(row=2, column=0, sticky="w", pady=4)
        self.string_initial_length_ratio = tk.DoubleVar(value=initial_settings["string_initial_length_ratio"])
        tk.Entry(frm, textvariable=self.string_initial_length_ratio, width=10).grid(row=2, column=1, sticky="w", pady=4)

        # Inside String Initial Length Ratio Input
        tk.Label(frm, text="Inside String Initial Length Ratio:").grid(row=3, column=0, sticky="w", pady=4)
        self.inside_string_initial_length_ratio = tk.DoubleVar(value=initial_settings["inside_string_initial_length_ratio"])
        tk.Entry(frm, textvariable=self.inside_string_initial_length_ratio, width=10).grid(row=3, column=1, sticky="w", pady=4)

        self.cylinder_checkbox = None
        self.radius_entry = None
        self.cylinder_enabled = tk.BooleanVar(value=initial_settings.get("cylinder_enabled", False))
        # Use parent app's cylinder_enabled if available (for synchronization)
        if parent_app and hasattr(parent_app, 'cylinder_enabled'):
            self.cylinder_enabled = parent_app.cylinder_enabled
        self.radius = tk.DoubleVar(value=initial_settings.get("radius", 0.0))

        if self._parent_supports_cylinder():
            self.cylinder_checkbox = tk.Checkbutton(frm, text="Cylinder", variable=self.cylinder_enabled, command=self._toggle_radius)
            self.cylinder_checkbox.grid(row=5, column=0, sticky="w", pady=4)

            tk.Label(frm, text="Radius:").grid(row=5, column=1, sticky="w", padx=(0, 5), pady=4)
            self.radius_entry = tk.Entry(frm, textvariable=self.radius, width=10)
            self.radius_entry.grid(row=5, column=1, sticky="e", pady=4)
        
        # Set initial state of radius entry
        self._toggle_radius()
        self._update_cylinder_availability()

        # Control Strings Checklist
        tk.Label(frm, text="Control Strings:").grid(row=6, column=0, sticky="nw", pady=4)
        checklist_frame = tk.Frame(frm)
        checklist_frame.grid(row=6, column=1, sticky="w", pady=4)
        self.control_canvas = tk.Canvas(checklist_frame, width=180, height=120, highlightthickness=1, highlightbackground="#c8c8c8")
        self.control_scrollbar = ttk.Scrollbar(checklist_frame, orient="vertical", command=self.control_canvas.yview)
        self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)

        self.control_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.control_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.control_checkbox_frame = tk.Frame(self.control_canvas)
        self.control_canvas_window = self.control_canvas.create_window((0, 0), window=self.control_checkbox_frame, anchor="nw")
        self.control_checkbox_frame.bind("<Configure>", self._sync_control_scrollregion)
        self.control_canvas.bind("<Configure>", self._sync_control_canvas_width)
        self._bind_control_mousewheel(self.control_canvas)
        self._bind_control_mousewheel(self.control_checkbox_frame)

        self.control_vars = {}
        self.refresh_control_checkboxes(initial_settings.get("multinode_strings", []), list(self.selected_controls))

        # Buttons Frame
        button_frame = ttk.Frame(frm)
        button_frame.grid(row=7, column=0, columnspan=2, pady=12)

        tk.Button(button_frame, text="Cancel", command=self.destroy, padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Generate YAML", command=self._generate_yaml_and_close, padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save", command=self._save, padx=20).pack(side=tk.LEFT, padx=5)

        # Press Enter to save
        self.bind("<Return>", lambda e: self._save())
        # Press Esc to cancel
        self.bind("<Escape>", lambda e: self.destroy())

    def _toggle_radius(self):
        """Enable or disable radius entry based on cylinder checkbox."""
        if self.radius_entry is None:
            return
        if self._parent_supports_cylinder() and self.cylinder_enabled.get():
            self.radius_entry.config(state="normal")
        else:
            self.radius_entry.config(state="disabled")

    def _parent_supports_cylinder(self):
        if not self.parent_app:
            return True
        return getattr(self.parent_app, "supports_cylinder_surface", True)

    def _update_cylinder_availability(self):
        """Disable cylinder option when unavailable for this mode or pattern."""
        enabled = self._parent_supports_cylinder()
        if self.parent_app and hasattr(self.parent_app, "self_similar_pattern"):
            enabled = enabled and self.parent_app.self_similar_pattern.get().lower() == "none"

        if not enabled:
            self.cylinder_enabled.set(False)

        if self.cylinder_checkbox is not None:
            self.cylinder_checkbox.config(state="normal" if enabled else "disabled")
        self._toggle_radius()

    def _save(self):
        new_settings = {
            "string_stiffness": self.string_stiffness.get(),
            "bar_stiffness": self.bar_stiffness.get(),
            "string_initial_length_ratio": self.string_initial_length_ratio.get(),
            "inside_string_initial_length_ratio": self.inside_string_initial_length_ratio.get(),
            "file_name": self.file_name.get(),
            "cylinder_enabled": self._parent_supports_cylinder() and self.cylinder_enabled.get(),
            "radius": self.radius.get(),
            "control_names": self._selected_controls(),
        }
        self.on_save(new_settings)
        self.destroy()

    def _generate_yaml_and_close(self):
        """Save settings, close the window, and generate YAML."""
        new_settings = {
            "string_stiffness": self.string_stiffness.get(),
            "bar_stiffness": self.bar_stiffness.get(),
            "string_initial_length_ratio": self.string_initial_length_ratio.get(),
            "inside_string_initial_length_ratio": self.inside_string_initial_length_ratio.get(),
            "file_name": self.file_name.get(),
            "cylinder_enabled": self._parent_supports_cylinder() and self.cylinder_enabled.get(),
            "radius": self.radius.get(),
            "control_names": self._selected_controls(),
        }
        self.on_save(new_settings)
        self.destroy()
        if self.parent_app and hasattr(self.parent_app, 'generate_yaml'):
            self.parent_app.generate_yaml()

    def refresh_control_checkboxes(self, names, selected_controls):
        for child in self.control_checkbox_frame.winfo_children():
            child.destroy()

        self.control_vars = {}
        valid_names = [name for name in names if name]
        selected_set = set(selected_controls)

        if not valid_names:
            empty_label = tk.Label(self.control_checkbox_frame, text="(No multinode strings)", fg="gray")
            empty_label.pack(anchor="w")
            self._bind_control_mousewheel(empty_label)
            return

        for name in valid_names:
            var = tk.BooleanVar(value=name in selected_set)
            self.control_vars[name] = var
            checkbox = tk.Checkbutton(self.control_checkbox_frame, text=name, variable=var)
            checkbox.pack(anchor="w")
            self._bind_control_mousewheel(checkbox)

        self._sync_control_scrollregion()

    def _sync_control_scrollregion(self, _event=None):
        self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all"))

    def _sync_control_canvas_width(self, event):
        self.control_canvas.itemconfigure(self.control_canvas_window, width=event.width)

    def _bind_control_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_control_mousewheel)
        widget.bind("<Button-4>", self._on_control_mousewheel)
        widget.bind("<Button-5>", self._on_control_mousewheel)

    def _on_control_mousewheel(self, event):
        if getattr(event, "num", None) == 4:
            self.control_canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            self.control_canvas.yview_scroll(1, "units")
        else:
            delta = int(event.delta)
            if delta != 0:
                self.control_canvas.yview_scroll(-int(delta / 120), "units")
        return "break"

    def _selected_controls(self):
        return [name for name, var in self.control_vars.items() if var.get()]

class GlobalHoverPrompt:
    def __init__(self, root, text="Need help?", delay=1000):
        self.root = root
        self.text = text
        self.label = None
        self.delay = delay
        self.tipwindow = None
        self.job = None

        root.bind("<Motion>", self.on_mouse_move)
        root.bind("<Leave>", self.hide_prompt)

    def on_mouse_move(self, event):
        if self.job:
            self.root.after_cancel(self.job)
        self.hide_prompt()

        # Schedule the tooltip to show if mouse is idle
        self.job = self.root.after(self.delay, lambda e=event: self.show_prompt(e.x_root, e.y_root))
   
    def show_prompt(self, x, y):
        self.tipwindow = tk.Toplevel(self.root)
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self.tipwindow, text=self.text, bg="lightyellow", relief="solid", bd=1)
        label.pack()

    def hide_prompt(self, event=None): 
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

    def set_message(self, new_text):
        self.text = new_text
        if self.label:
            self.label.config(text=self.text)

class GridSettingsWindow(tk.Toplevel):
    def __init__(self, parent, initial_settings: dict, on_save, on_add_custom_node):
        super().__init__(parent)
        self.title(" Grid Settings")
        self.resizable(False, False)

        self.on_save = on_save
        self.on_add_custom_node = on_add_custom_node

        # Make it behave like a modal dialog (optional but nice)
        self.transient(parent)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # X Points Input
        tk.Label(frm, text="Number of X Points:").grid(row=0, column=0, sticky="w", pady=4)
        self.x_points = tk.IntVar(value=initial_settings["x_points"])
        self.x_entry = tk.Entry(frm, textvariable=self.x_points, width=5).grid(row=0, column=1, sticky="w", pady=4)

        # X Points Distance
        tk.Label(frm, text="Distance Between X Points:").grid(row=0, column=2, sticky="w", pady=4)
        self.x_distance = tk.DoubleVar(value=initial_settings["x_distance"])
        self.x_distance_entry = tk.Entry(frm, textvariable=self.x_distance, width=5).grid(row=0, column=3, sticky="w", pady=4)
    

        # Y Points Input
        tk.Label(frm, text="Number of Y Points:").grid(row=1, column=0, sticky="w", pady=4)
        self.y_points = tk.IntVar(value=initial_settings["y_points"])
        self.y_entry = tk.Entry(frm, textvariable=self.y_points, width=5).grid(row=1, column=1, sticky="w", pady=4)

        # Y Points Distance
        tk.Label(frm, text="Distance Between Y Points:").grid(row=1, column=2, sticky="w", pady=4)
        self.y_distance = tk.DoubleVar(value=initial_settings["y_distance"])
        self.y_distance_entry = tk.Entry(frm, textvariable=self.y_distance, width=5).grid(row=1, column=3, sticky="w", pady=4)

        # Custom node controls
        tk.Button(frm, text="Add Custom Node", command=self._add_custom_node).grid(row=2, column=0, sticky="w", pady=6)
        tk.Label(frm, text="x").grid(row=2, column=1, sticky="e", pady=6)
        self.custom_x = tk.StringVar(value="")
        tk.Entry(frm, textvariable=self.custom_x, width=7).grid(row=2, column=2, sticky="w", pady=6)
        tk.Label(frm, text="y").grid(row=2, column=2, sticky="e", padx=(0, 48), pady=6)
        self.custom_y = tk.StringVar(value="")
        tk.Entry(frm, textvariable=self.custom_y, width=7).grid(row=2, column=3, sticky="w", pady=6)

        tk.Button(frm, text="Cancel", command=self.destroy, padx=40).grid(row=3, column=0, padx=6)
        tk.Button(frm, text="Save", command=self._save, padx=40).grid(row=3, column=2)

        # Press Enter to save
        self.bind("<Return>", lambda e: self._save())
        # Press Esc to cancel
        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        new_settings = {
            "x_points": self.x_points.get(),
            "x_distance": self.x_distance.get(),
            "y_points": self.y_points.get(),
            "y_distance": self.y_distance.get()
        }
        self.on_save(new_settings)
        self.destroy()

    def _add_custom_node(self):
        try:
            x = float(self.custom_x.get())
            y = float(self.custom_y.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter numeric x and y values.")
            return

        was_added = self.on_add_custom_node((x, y))
        if was_added:
            self.custom_x.set("")
            self.custom_y.set("")
        else:
            messagebox.showinfo("Node Exists", f"Node ({x}, {y}) is already in the grid.")

class UnitCellBuilderApp3D:
    """3D version of the Unit Cell Builder App."""
    def __init__(self, root):
        self.unit = be.UnitCell3D()
        self.path = []
        self.structure_window = None

        self.root = root
        _configure_ui_defaults(self.root)
        self.root.title("Unit Cell Builder - 3D Mode")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create a frame for the unit cell builder
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        # Frame for line creation controls
        line_control_frame = tk.Frame(self.main_frame)
        line_control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Submenu for grid generation controls
        self.grid_settings_btn = tk.Button(line_control_frame, text="Grid Settings ▶", command=self.grid_settings)
        self.grid_settings_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.grid_settings_btn, "Adjust 3D grid size and spacing")

        self.instructions_btn = tk.Button(line_control_frame, text="Instructions", command=self.open_instructions)
        self.instructions_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.instructions_btn, "Open instructions for the 3D unit cell window")

        # Line style selection with dropdown menu
        self.line_style = tk.StringVar(value="bar")

        tk.Label(line_control_frame, text="Line Style:").pack(side=tk.LEFT, padx=5)

        LINE_STYLES = {
            "Bar": "bar",
            "String": "string",
            "X Connector": "x_connector",
            "Y Connector": "y_connector",
            "Z Connector": "z_connector",
            "Delete": "delete",
        }

        self.line_style_label = tk.StringVar(value="Bar")

        def set_line_style(value):
            self.line_style.set(value)
            for label, v in LINE_STYLES.items():
                if v == value:
                    self.line_style_label.set(label)
                    break
            self.update_cursor()

        def on_menu_change(label):
            set_line_style(LINE_STYLES[label])

        # Dropdown
        line_style_menu = tk.OptionMenu(
            line_control_frame,
            self.line_style_label,
            *LINE_STYLES.keys(),
            command=on_menu_change
        )
        line_style_menu.config(width=15)
        line_style_menu.pack(side=tk.LEFT)

        # Hint label for keyboard shortcut
        hint_label = tk.Label(line_control_frame, text="(Ctrl + scroll wheel)", font=("Arial", 8), fg="gray")
        hint_label.pack(side=tk.LEFT, padx=2)

        # Clear Lines Button
        self.clear_btn = tk.Button(line_control_frame, text="Clear Lines", command=self.clear_lines)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.clear_btn, "Clear all drawn lines")

        # Submit Button
        self.submit_btn = tk.Button(line_control_frame, text="Submit", command=self.submit_values)
        self.submit_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.submit_btn, "Submit and prepare for structure generation")

        # Toggle switch for node positions
        self.show_node_positions = tk.BooleanVar(value=False)
        self.node_positions_toggle = tk.Checkbutton(
            line_control_frame,
            text="Show Node Positions",
            variable=self.show_node_positions,
            command=self.update_grid_display
        )
        self.node_positions_toggle.pack(side=tk.LEFT, padx=5)

        self.hide_unconnected_nodes = tk.BooleanVar(value=False)
        self.hide_unconnected_toggle = tk.Checkbutton(
            line_control_frame,
            text="Hide unconnected nodes",
            variable=self.hide_unconnected_nodes,
            command=self.update_grid_display
        )
        self.hide_unconnected_toggle.pack(side=tk.LEFT, padx=5)

        # Initialize tooltip
        self.tooltip_window = None

        # 3D matplotlib canvas
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas_widget.bind("<Enter>", self.enter_canvas)
        self.canvas1message = "Click to draw a bar"
        self.help_prompt = GlobalHoverPrompt(self.root, text=self.canvas1message, delay=500)

        # --- Ctrl+scroll wheel to change line style ---
        # Define the line styles in order
        self.line_styles_list = ["bar", "string", "x_connector", "y_connector", "z_connector", "delete"]
        self.current_style_index = 0  # Start with "bar"

        def on_ctrl_scroll(event):
            """Handle Ctrl+scroll wheel to change line style."""
            if event.state & 0x4:  # Check if Ctrl is pressed (0x4 is Ctrl modifier)
                if event.delta > 0 or event.num == 4:  # Scroll up
                    self.current_style_index = (self.current_style_index - 1) % len(self.line_styles_list)
                elif event.delta < 0 or event.num == 5:  # Scroll down
                    self.current_style_index = (self.current_style_index + 1) % len(self.line_styles_list)
                set_line_style(self.line_styles_list[self.current_style_index])

        root = self.root
        root.bind_all("<MouseWheel>", on_ctrl_scroll)  # Windows
        root.bind_all("<Button-4>", on_ctrl_scroll)    # Linux scroll up
        root.bind_all("<Button-5>", on_ctrl_scroll)    # Linux scroll down

        # Initialize grid settings
        self.x_count = 3
        self.y_count = 3
        self.z_count = 3
        self.x_spacing = 1.0
        self.y_spacing = 1.0
        self.z_spacing = 1.0
        
        # Initialize data structures
        self.points = []
        self.custom_points = []
        self.selected_points = self.unit.selected_points
        self.bars = self.unit.bars
        self.strings = self.unit.strings
        self.x_connectors = self.unit.x_connectors
        self.y_connectors = self.unit.y_connectors
        self.z_connectors = self.unit.z_connectors
        self.visible_points = []
    
        # Generate initial grid
        self.generate_grid()
        self.canvas.mpl_connect("pick_event", self.on_left_click)

    def grid_settings(self):
        """Open the grid settings window for 3D."""
        initial_settings = {
            "x_points": self.x_count,
            "x_distance": self.x_spacing,
            "y_points": self.y_count,
            "y_distance": self.y_spacing,
            "z_points": self.z_count,
            "z_distance": self.z_spacing
        }
        GridSettingsWindow3D(self.root, initial_settings, self.apply_grid_settings, self.add_custom_node)

    def open_instructions(self):
        _show_instructions_window(self.root, "3D Unit Cell Instructions", _UNIT_CELL_3D_INSTRUCTIONS)

    def generate_grid(self):
        """Generate a uniform 3D grid of points."""
        self.ax.clear()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        # Create 3D grid points
        self.points = self.unit.generate_grid(
            self.x_count,
            self.y_count,
            self.z_count,
            self.x_spacing,
            self.y_spacing,
            self.z_spacing,
        )
        for point in self.custom_points:
            if point not in self.points:
                self.points.append(point)

        self.unit.clear_lines()
        self.redraw_3d_graph()

    def add_custom_node(self, point):
        """Add a custom 3D node to the current grid and redraw."""
        if point in self.custom_points:
            return False
        self.custom_points.append(point)
        self.points.append(point)
        self.update_grid_display()
        return True

    def apply_grid_settings(self, settings):
        """Apply the grid settings from the settings window."""
        self.x_count = settings["x_points"]
        self.x_spacing = settings["x_distance"]
        self.y_count = settings["y_points"]
        self.y_spacing = settings["y_distance"]
        self.z_count = settings.get("z_points", 3)
        self.z_spacing = settings.get("z_distance", 1.0)
        self.generate_grid()

    def update_cursor(self):
        """Update the cursor style based on the selected line style."""
        line_style = self.line_style.get()
        if line_style == "bar":
            self.canvas1message = "Click to draw a bar"
        elif line_style == "string":
            self.canvas1message = "Click to draw a string"
        elif line_style == "x_connector":
            self.canvas1message = "Click to draw an X connector"
        elif line_style == "y_connector":
            self.canvas1message = "Click to draw a Y connector"
        elif line_style == "z_connector":
            self.canvas1message = "Click to draw a Z connector"
        elif line_style == "delete":
            self.canvas1message = "Click to delete a line or string"

    def enter_canvas(self, event):
        # Only show message if not in the control frame
        if not self.is_in_control_frame(event):
            if hasattr(self, "help_prompt") and self.help_prompt:
                self.help_prompt.set_message(self.canvas1message)

    def is_in_control_frame(self, event):
        return is_widget_in_control_frame(event, self.main_frame)

    def on_left_click(self, event):
        """Handle click events for selecting points and drawing lines in 3D."""
        try:
            if not self.visible_points:
                self.visible_points = self._visible_unit_points_3d()
            if not self.visible_points:
                return
            
            if not hasattr(event, 'ind') or event.ind is None or len(event.ind) == 0:
                return

            # Get the index of the clicked point
            ind_value = event.ind[0]
            ind = ind_value.item() if hasattr(ind_value, "item") else int(ind_value)
            
            if ind < 0 or ind >= len(self.visible_points):
                return
            
            clicked_point = self.visible_points[ind]
            self.unit.create_lines(clicked_point, self.line_style.get())
            
            self.redraw_3d_graph()
        except Exception as e:
            print(f"Error in on_left_click: {e}")
            import traceback
            traceback.print_exc()

    def redraw_3d_graph(self):
        """Redraw the 3D graph with current bars, strings, and connector guides."""
        self.ax.clear()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        self.visible_points = self._visible_unit_points_3d()
        if self.visible_points:
            x_vals, y_vals, z_vals = zip(*self.visible_points)
            self.ax.scatter(x_vals, y_vals, z_vals, color="black", s=50, picker=5)

            if self.show_node_positions.get():
                for i, (x, y, z) in enumerate(self.visible_points):
                    self.ax.text(x, y, z, f"[{x}, {y}, {z}]", fontsize=8)

        for bar in self.bars:
            x_vals = [bar[0][0], bar[1][0]]
            y_vals = [bar[0][1], bar[1][1]]
            z_vals = [bar[0][2], bar[1][2]]
            self.ax.plot(x_vals, y_vals, z_vals, linestyle='-', color="blue", linewidth=2)

        for string in self.strings:
            x_vals = [string[0][0], string[1][0]]
            y_vals = [string[0][1], string[1][1]]
            z_vals = [string[0][2], string[1][2]]
            self.ax.plot(x_vals, y_vals, z_vals, linestyle='--', color="red", linewidth=2)

        for connector in self.x_connectors:
            self._draw_connector_guides(connector, axis="x", color="green")

        for connector in self.y_connectors:
            self._draw_connector_guides(connector, axis="y", color="purple")

        for connector in self.z_connectors:
            self._draw_connector_guides(connector, axis="z", color="orange")

        self.canvas.draw()

    def clear_lines(self):
        """Clear all drawn lines with confirmation."""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all lines?"):
            self.unit.clear_lines()
            self.generate_grid()

    def _draw_connector_guides(self, connector, axis, color):
        axis_map = {"x": 0, "y": 1, "z": 2}
        idx = axis_map[axis]
        values = [connector[0][idx], connector[1][idx]]
        min_val = min(values)
        max_val = max(values)

        spacing_map = {"x": self.x_spacing, "y": self.y_spacing, "z": self.z_spacing}
        stub_length = max(spacing_map[axis] * 0.1, 0.1)

        for point in connector:
            p = list(point)
            p2 = list(point)
            if abs(point[idx] - min_val) < 1e-9 and abs(min_val - max_val) > 1e-9:
                p2[idx] = point[idx] - stub_length
            elif abs(point[idx] - max_val) < 1e-9 and abs(min_val - max_val) > 1e-9:
                p2[idx] = point[idx] + stub_length
            else:
                p2[idx] = point[idx] + (stub_length if point == connector[1] else -stub_length)

            self.ax.plot(
                [p[0], p2[0]],
                [p[1], p2[1]],
                [p[2], p2[2]],
                linestyle='--',
                color=color,
                linewidth=2,
            )

    def submit_values(self):
        """Submit the selected lines and open the structure builder window."""
        # Open structure builder in a new window
        try:
            if self.structure_window is None or not self.structure_window.root.winfo_exists():
                structure_root = tk.Toplevel(self.root)
                self.structure_window = StructureBuilderApp3D(
                    structure_root,
                    self.unit,
                    self.bars,
                    self.strings,
                    self.x_connectors,
                    self.y_connectors,
                    self.z_connectors,
                    self.points,
                )
            else:
                # Bring existing window to front
                self.structure_window.root.lift()
                self.structure_window.root.focus()
        except Exception as error:
            messagebox.showerror("3D Builder Error", f"Failed to open 3D structure builder:\n{error}")
            import traceback
            traceback.print_exc()

    def show_tooltip(self, text, x, y):
        """Display a tooltip at the specified coordinates."""
        self.hide_tooltip()
        self.tooltip_window = tk.Toplevel(self.root)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self.tooltip_window, text=text, bg="lightyellow", relief="solid", bd=1, padx=5, pady=2)
        label.pack()

    def hide_tooltip(self):
        """Hide the tooltip if it exists."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def add_button_tooltip(self, button, text):
        """Add a hover tooltip to a button."""
        def on_enter(event):
            self.show_tooltip(text, event.x_root, event.y_root)

        def on_leave(event):
            self.hide_tooltip()

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def _visible_unit_points_3d(self):
        return be.visible_unit_points(
            self.points,
            self.hide_unconnected_nodes.get(),
            self.bars,
            self.strings,
            self.x_connectors,
            self.y_connectors,
            self.z_connectors,
        )

    def update_grid_display(self):
        """Update the grid display when node positions toggle changes."""
        self.redraw_3d_graph()

    def on_closing(self):
        """Handle window closing."""
        self.hide_tooltip()
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.structure_window is not None and self.structure_window.root.winfo_exists():
                self.structure_window.root.destroy()
            self.root.destroy()

class GridSettingsWindow3D(tk.Toplevel):
    """Grid settings window with support for Z dimension."""
    def __init__(self, parent, initial_settings, on_save, on_add_custom_node):
        super().__init__(parent)
        self.title("Grid Settings - 3D")
        self.geometry("500x300")
        self.on_save = on_save
        self.on_add_custom_node = on_add_custom_node
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # X Points Input
        tk.Label(frm, text="Number of X Points:").grid(row=0, column=0, sticky="w", pady=4)
        self.x_points = tk.IntVar(value=initial_settings["x_points"])
        tk.Entry(frm, textvariable=self.x_points, width=5).grid(row=0, column=1, sticky="w", pady=4)

        # X Points Distance
        tk.Label(frm, text="Distance Between X Points:").grid(row=0, column=2, sticky="w", pady=4)
        self.x_distance = tk.DoubleVar(value=initial_settings["x_distance"])
        tk.Entry(frm, textvariable=self.x_distance, width=5).grid(row=0, column=3, sticky="w", pady=4)
    
        # Y Points Input
        tk.Label(frm, text="Number of Y Points:").grid(row=1, column=0, sticky="w", pady=4)
        self.y_points = tk.IntVar(value=initial_settings["y_points"])
        tk.Entry(frm, textvariable=self.y_points, width=5).grid(row=1, column=1, sticky="w", pady=4)

        # Y Points Distance
        tk.Label(frm, text="Distance Between Y Points:").grid(row=1, column=2, sticky="w", pady=4)
        self.y_distance = tk.DoubleVar(value=initial_settings["y_distance"])
        tk.Entry(frm, textvariable=self.y_distance, width=5).grid(row=1, column=3, sticky="w", pady=4)

        # Z Points Input
        tk.Label(frm, text="Number of Z Points:").grid(row=2, column=0, sticky="w", pady=4)
        self.z_points = tk.IntVar(value=initial_settings.get("z_points", 3))
        tk.Entry(frm, textvariable=self.z_points, width=5).grid(row=2, column=1, sticky="w", pady=4)

        # Z Points Distance
        tk.Label(frm, text="Distance Between Z Points:").grid(row=2, column=2, sticky="w", pady=4)
        self.z_distance = tk.DoubleVar(value=initial_settings.get("z_distance", 1.0))
        tk.Entry(frm, textvariable=self.z_distance, width=5).grid(row=2, column=3, sticky="w", pady=4)

        # Custom node controls
        tk.Button(frm, text="Add Custom Node", command=self._add_custom_node).grid(row=3, column=0, sticky="w", pady=6)
        custom_node_frame = ttk.Frame(frm)
        custom_node_frame.grid(row=3, column=1, columnspan=3, sticky="w", pady=6)

        self.custom_x = tk.StringVar(value="")
        self.custom_y = tk.StringVar(value="")
        self.custom_z = tk.StringVar(value="")

        tk.Label(custom_node_frame, text="x").grid(row=0, column=0, sticky="w")
        tk.Entry(custom_node_frame, textvariable=self.custom_x, width=6).grid(row=0, column=1, sticky="w", padx=(4, 10))
        tk.Label(custom_node_frame, text="y").grid(row=0, column=2, sticky="w")
        tk.Entry(custom_node_frame, textvariable=self.custom_y, width=6).grid(row=0, column=3, sticky="w", padx=(4, 10))
        tk.Label(custom_node_frame, text="z").grid(row=0, column=4, sticky="w")
        tk.Entry(custom_node_frame, textvariable=self.custom_z, width=6).grid(row=0, column=5, sticky="w", padx=(4, 0))

        tk.Button(frm, text="Cancel", command=self.destroy, padx=40).grid(row=4, column=0, padx=6)
        tk.Button(frm, text="Save", command=self._save, padx=40).grid(row=4, column=2)

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        new_settings = {
            "x_points": self.x_points.get(),
            "x_distance": self.x_distance.get(),
            "y_points": self.y_points.get(),
            "y_distance": self.y_distance.get(),
            "z_points": self.z_points.get(),
            "z_distance": self.z_distance.get()
        }
        self.on_save(new_settings)
        self.destroy()

    def _add_custom_node(self):
        try:
            x = float(self.custom_x.get())
            y = float(self.custom_y.get())
            z = float(self.custom_z.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter numeric x, y, and z values.")
            return

        was_added = self.on_add_custom_node((x, y, z))
        if was_added:
            self.custom_x.set("")
            self.custom_y.set("")
            self.custom_z.set("")
        else:
            messagebox.showinfo("Node Exists", f"Node ({x}, {y}, {z}) is already in the grid.")

class StructureSettingsWindow(tk.Toplevel):
    """Popup window containing pattern lengths and structure generation action."""
    def __init__(self, parent, title, x_var, y_var, self_similar_var, axis_options, on_generate, z_var=None, generate_button_text="Generate Structure"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.on_generate = on_generate
        self.self_similar_var = self_similar_var
        self.axis_options = axis_options

        self.transient(parent)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        tk.Label(frm, text="Pattern Length X:").grid(row=0, column=0, sticky="w", pady=4)
        self.x_entry = tk.Entry(frm, textvariable=x_var, width=6)
        self.x_entry.grid(row=0, column=1, sticky="w", pady=4)

        tk.Label(frm, text="Pattern Length Y:").grid(row=1, column=0, sticky="w", pady=4)
        self.y_entry = tk.Entry(frm, textvariable=y_var, width=6)
        self.y_entry.grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(frm, text="Self-Similar Pattern:").grid(row=2, column=0, sticky="w", pady=4)
        self.self_similar_dropdown = ttk.Combobox(
            frm,
            values=list(axis_options),
            textvariable=self.self_similar_var,
            state="readonly",
            width=10,
        )
        self.self_similar_dropdown.grid(row=2, column=1, sticky="w", pady=4)
        self.self_similar_dropdown.bind("<<ComboboxSelected>>", lambda _e: self._update_axis_field_state())

        button_row = 3
        if z_var is not None:
            tk.Label(frm, text="Pattern Length Z:").grid(row=3, column=0, sticky="w", pady=4)
            self.z_entry = tk.Entry(frm, textvariable=z_var, width=6)
            self.z_entry.grid(row=3, column=1, sticky="w", pady=4)
            button_row = 4
        else:
            self.z_entry = None

        tk.Button(frm, text=generate_button_text, command=self._generate, padx=16).grid(row=button_row, column=0, sticky="w", pady=(10, 0))
        tk.Button(frm, text="Close", command=self.destroy, padx=16).grid(row=button_row, column=1, sticky="e", pady=(10, 0))

        self.bind("<Return>", lambda e: self._generate())
        self.bind("<Escape>", lambda e: self.destroy())
        self._update_axis_field_state()

    def _update_axis_field_state(self):
        mode = self.self_similar_var.get().lower()
        entries = {
            "x": self.x_entry,
            "y": self.y_entry,
        }
        if self.z_entry is not None:
            entries["z"] = self.z_entry

        if mode == "none":
            for entry in entries.values():
                entry.config(state="normal")
            return

        for axis, entry in entries.items():
            entry.config(state="normal" if axis == mode else "disabled")

    def _generate(self):
        self.on_generate()
        self.destroy()

class StructureBuilderApp3D:
    """3D Structure Builder for generating patterns from 3D unit cells."""
    def __init__(self, root, unit_cell, bars, strings, x_connectors, y_connectors, z_connectors, points):
        
        self.root = root
        _configure_ui_defaults(self.root)
        self.root.title("3D Structure Builder")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.unit = unit_cell
        self.bars = bars
        self.strings = strings
        self.x_connectors = x_connectors
        self.y_connectors = y_connectors
        self.z_connectors = z_connectors
        self.points = points
        self.supports_cylinder_surface = False
        self.structure_exporter = be.Structure3D()

        self.x_pins = []
        self.y_pins = []
        self.z_pins = []
        self.selected_points2 = []
        self.multinode_strings = []
        self.MNSindex = 0

        self.string_stiffness = tk.IntVar(value=100)
        self.bar_stiffness = tk.IntVar(value=1000)
        self.string_initial_length_ratio = tk.DoubleVar(value=0.95)
        self.inside_string_initial_length_ratio = tk.DoubleVar(value=0.95)
        self.file_name = tk.StringVar(value="test_tensegrity_3d")
        self.cylinder_enabled = tk.BooleanVar(value=False)
        self.radius = tk.DoubleVar(value=0.0)
        self.selected_controls = []
        self.builder_details_window = None

        self.structure_points = []
        self.structure_bars = []
        self.structure_strings = []
        self.manual_view_active = False
        self.view_limits_3d = None
        
        # Create a frame for the structure builder
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        # Frame for top controls
        top_control_frame = tk.Frame(self.main_frame)
        top_control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.x_pattern = tk.IntVar(value=3)
        self.y_pattern = tk.IntVar(value=3)
        self.z_pattern = tk.IntVar(value=3)
        self.self_similar_pattern = tk.StringVar(value="none")
        self.self_similar_pattern.trace_add("write", self._on_self_similar_pattern_changed)
        self.structure_settings_window = None
        self.structure_settings_btn = tk.Button(top_control_frame, text="Structure Settings ▶", command=self.open_structure_settings)
        self.structure_settings_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.structure_settings_btn, "Set pattern lengths and generate 3D structure")

        self.instructions_btn = tk.Button(top_control_frame, text="Instructions", command=self.open_instructions)
        self.instructions_btn.pack(side=tk.LEFT, padx=5)
        self.add_button_tooltip(self.instructions_btn, "Open instructions for the 3D structure window")

        self.structure_element = tk.StringVar(value="x_pin")
        tk.Label(top_control_frame, text="Structure Element:").pack(side=tk.LEFT, padx=5)
        structure_options = ["X Pin", "Y Pin", "Z Pin", "Unpin", "Multi-node String"]
        structure_values = ["x_pin", "y_pin", "z_pin", "unpin", "multinode_string"]
        self.structure_element_dropdown = ttk.Combobox(
            top_control_frame,
            values=structure_options,
            state="readonly",
            width=15,
        )
        self.structure_element_dropdown.set("X Pin")
        self.structure_element_dropdown.bind(
            "<<ComboboxSelected>>",
            lambda e: self.structure_element.set(structure_values[structure_options.index(self.structure_element_dropdown.get())]),
        )
        self.structure_element_dropdown.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(top_control_frame, text="Delete Multinode String:", command=self.delete_string)
        delete_btn.pack(side=tk.LEFT, padx=5)
        self.MNSdropdown = ttk.Combobox(top_control_frame, values=[""])
        self.MNSdropdown.current(0)
        self.MNSdropdown.pack(side=tk.LEFT, padx=5)

        bottom_control_frame = tk.Frame(self.main_frame)
        bottom_control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        yaml_btn = tk.Button(bottom_control_frame, text="Generate YAML", command=self.generate_yaml)
        yaml_btn.pack(side=tk.RIGHT, padx=5)

        builder_details_btn = tk.Button(bottom_control_frame, text="Builder Details ▶", command=self.open_builder_details)
        builder_details_btn.pack(side=tk.RIGHT, padx=5)

        # Matplotlib Figure for 3D visualization
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("pick_event", self.on_canvas_click)
        self.canvas.mpl_connect("scroll_event", self.on_plot_scroll)
        self.root.bind("<Return>", self.on_enter_pressed)

        # Display the initial unit cell
        self.generate_structure()
        
        # Initialize tooltip
        self.tooltip_window = None

        # Open structure settings automatically when this window is created.
        self.open_structure_settings()

    def _on_self_similar_pattern_changed(self, *_args):
        if self.builder_details_window and self.builder_details_window.winfo_exists():
            self.builder_details_window._update_cylinder_availability()

    def on_plot_scroll(self, event):
        """Zoom 3D structure plot with mouse wheel."""
        if event.inaxes != self.ax:
            return

        zoom_in = event.button == 'up'
        scale = 0.9 if zoom_in else 1.1

        xlim = self.ax.get_xlim3d()
        ylim = self.ax.get_ylim3d()
        zlim = self.ax.get_zlim3d()

        x_center = (xlim[0] + xlim[1]) / 2.0
        y_center = (ylim[0] + ylim[1]) / 2.0
        z_center = (zlim[0] + zlim[1]) / 2.0

        new_half_x = (xlim[1] - xlim[0]) * scale / 2.0
        new_half_y = (ylim[1] - ylim[0]) * scale / 2.0
        new_half_z = (zlim[1] - zlim[0]) * scale / 2.0

        self.ax.set_xlim3d(x_center - new_half_x, x_center + new_half_x)
        self.ax.set_ylim3d(y_center - new_half_y, y_center + new_half_y)
        self.ax.set_zlim3d(z_center - new_half_z, z_center + new_half_z)
        self.manual_view_active = True
        self.view_limits_3d = (
            self.ax.get_xlim3d(),
            self.ax.get_ylim3d(),
            self.ax.get_zlim3d(),
        )
        self.canvas.draw()

    def open_structure_settings(self):
        """Open the structure settings window for 3D pattern lengths and generation."""
        if self.structure_settings_window is not None and self.structure_settings_window.winfo_exists():
            self.structure_settings_window.lift()
            self.structure_settings_window.focus()
            return

        self.structure_settings_window = StructureSettingsWindow(
            self.root,
            title="Structure Settings - 3D",
            x_var=self.x_pattern,
            y_var=self.y_pattern,
            self_similar_var=self.self_similar_pattern,
            axis_options=("x", "y", "z", "none"),
            z_var=self.z_pattern,
            on_generate=self.generate_structure,
            generate_button_text="Generate 3D Structure",
        )

    def open_instructions(self):
        _show_instructions_window(self.root, "3D Structure Instructions", _STRUCTURE_3D_INSTRUCTIONS)

    def _prune_pins_to_structure(self):
        self.x_pins, self.y_pins, self.z_pins = be.prune_pin_lists_to_points(
            self.structure_points,
            self.x_pins,
            self.y_pins,
            self.z_pins,
        )

    def _draw_structure(self):
        self.ax.clear()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        self.structure_strings = be.prune_multinode_segments(self.structure_strings, self.multinode_strings)

        visible_nodes = self.structure_exporter.connected_nodes(
            self.structure_bars,
            self.structure_strings,
            self.multinode_strings,
        )
        if visible_nodes:
            x_vals, y_vals, z_vals = zip(*visible_nodes)
            self.ax.scatter(x_vals, y_vals, z_vals, color="black", s=30, picker=5)
        self.structure_points = visible_nodes

        for bar in self.structure_bars:
            x_vals = [bar[0][0], bar[1][0]]
            y_vals = [bar[0][1], bar[1][1]]
            z_vals = [bar[0][2], bar[1][2]]
            self.ax.plot(x_vals, y_vals, z_vals, linestyle='-', color="blue", linewidth=1.5)

        for string in self.structure_strings:
            x_vals = [string[0][0], string[1][0]]
            y_vals = [string[0][1], string[1][1]]
            z_vals = [string[0][2], string[1][2]]
            self.ax.plot(x_vals, y_vals, z_vals, linestyle='--', color="red", linewidth=1.5)

        for x_pin in self.x_pins:
            self.ax.plot([x_pin[0] - 0.15, x_pin[0] + 0.15], [x_pin[1], x_pin[1]], [x_pin[2], x_pin[2]], color="black", linewidth=3)
        for y_pin in self.y_pins:
            self.ax.plot([y_pin[0], y_pin[0]], [y_pin[1] - 0.15, y_pin[1] + 0.15], [y_pin[2], y_pin[2]], color="black", linewidth=3)
        for z_pin in self.z_pins:
            self.ax.plot([z_pin[0], z_pin[0]], [z_pin[1], z_pin[1]], [z_pin[2] - 0.15, z_pin[2] + 0.15], color="black", linewidth=3)

        for mns in self.multinode_strings:
            points = mns["points"]
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], linestyle='--', color="cyan", linewidth=2)
            if points:
                self.ax.text(points[0][0], points[0][1], points[0][2], mns["name"], fontsize=8)

        if len(self.selected_points2) > 1:
            for i in range(len(self.selected_points2) - 1):
                p1 = self.selected_points2[i]
                p2 = self.selected_points2[i + 1]
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], linestyle='--', color="orange", linewidth=2)

        if self.selected_points2:
            x_vals = [p[0] for p in self.selected_points2]
            y_vals = [p[1] for p in self.selected_points2]
            z_vals = [p[2] for p in self.selected_points2]
            self.ax.scatter(x_vals, y_vals, z_vals, color="orange", s=45)

        if self.manual_view_active and self.view_limits_3d:
            self.ax.set_xlim3d(self.view_limits_3d[0])
            self.ax.set_ylim3d(self.view_limits_3d[1])
            self.ax.set_zlim3d(self.view_limits_3d[2])

        self.canvas.draw()

    def on_canvas_click(self, event):
        if not self.structure_points or not hasattr(event, "ind") or event.ind is None or len(event.ind) == 0:
            return

        ind_value = event.ind[0]
        ind = ind_value.item() if hasattr(ind_value, "item") else int(ind_value)
        if ind < 0 or ind >= len(self.structure_points):
            return

        nearest_node = self.structure_points[ind]
        element = self.structure_element.get()

        if element in ("x_pin", "y_pin", "z_pin", "unpin"):
            be.apply_pin_action_3d(self.x_pins, self.y_pins, self.z_pins, nearest_node, element)
        elif element == "multinode_string":
            if not self.selected_points2 or nearest_node != self.selected_points2[-1]:
                self.selected_points2.append(nearest_node)

        self._draw_structure()

    def on_enter_pressed(self, event):
        if self.structure_element.get() == "multinode_string":
            self.finalize_multinode_string()

    def finalize_multinode_string(self):
        if len(self.selected_points2) > 1:
            self.MNSindex += 1
            self.multinode_strings.append({"name": f"String{self.MNSindex}", "points": self.selected_points2.copy()})
            self.structure_strings = be.prune_multinode_segments(self.structure_strings, self.multinode_strings)
            self.selected_points2.clear()
            self.update_dropdown()
            self._draw_structure()
        elif len(self.selected_points2) == 1:
            self.selected_points2.clear()
            self._draw_structure()

    def generate_structure(self):
        """Generate the full 3D structure by repeating the unit cell pattern."""
        try:
            mode = self.self_similar_pattern.get().lower()
            if mode in ("x", "y", "z"):
                count = {
                    "x": self.x_pattern.get(),
                    "y": self.y_pattern.get(),
                    "z": self.z_pattern.get(),
                }[mode]
                (
                    self.structure_points,
                    self.structure_bars,
                    self.structure_strings,
                ) = self.structure_exporter.generate_self_similar_grid(
                    self.bars,
                    self.strings,
                    mode,
                    count,
                )
            else:
                x_reps = self.x_pattern.get()
                y_reps = self.y_pattern.get()
                z_reps = self.z_pattern.get()
                (
                    self.structure_points,
                    self.structure_bars,
                    self.structure_strings,
                ) = self.structure_exporter.generate_grid(
                    self.points,
                    self.bars,
                    self.strings,
                    self.x_connectors,
                    self.y_connectors,
                    self.z_connectors,
                    x_reps,
                    y_reps,
                    z_reps,
                    self.multinode_strings,
                )

            self._prune_pins_to_structure()
            self._draw_structure()
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integer values for pattern repetitions")

    def delete_string(self):
        selected_name = self.MNSdropdown.get()
        for mns in self.multinode_strings:
            if mns["name"] == selected_name:
                self.multinode_strings.remove(mns)
                break
        self.update_dropdown()
        self.generate_structure()

    def update_dropdown(self):
        names = [mns["name"] for mns in self.multinode_strings]
        self.selected_controls = [name for name in self.selected_controls if name in names]

        try:
            if names:
                self.MNSdropdown['values'] = names
            else:
                self.MNSdropdown['values'] = [""]
            self.MNSdropdown.current(0)
        except tk.TclError:
            pass

        try:
            if self.builder_details_window and self.builder_details_window.winfo_exists():
                self.builder_details_window.refresh_control_checkboxes(names, self.selected_controls)
        except tk.TclError:
            self.builder_details_window = None

    def open_builder_details(self):
        names = [mns["name"] for mns in self.multinode_strings]
        self.selected_controls = [name for name in self.selected_controls if name in names]
        initial_settings = {
            "string_stiffness": self.string_stiffness.get(),
            "bar_stiffness": self.bar_stiffness.get(),
            "string_initial_length_ratio": self.string_initial_length_ratio.get(),
            "inside_string_initial_length_ratio": self.inside_string_initial_length_ratio.get(),
            "file_name": self.file_name.get(),
            "cylinder_enabled": self.cylinder_enabled.get(),
            "radius": self.radius.get(),
            "control_names": self.selected_controls.copy(),
            "multinode_strings": names,
        }
        self.builder_details_window = BuilderDetailsWindow(self.root, initial_settings, self.apply_builder_details, self)

    def apply_builder_details(self, settings):
        self.string_stiffness.set(settings["string_stiffness"])
        self.bar_stiffness.set(settings["bar_stiffness"])
        self.string_initial_length_ratio.set(settings["string_initial_length_ratio"])
        self.inside_string_initial_length_ratio.set(settings["inside_string_initial_length_ratio"])
        self.file_name.set(settings["file_name"])
        self.cylinder_enabled.set(settings.get("cylinder_enabled", False))
        self.radius.set(settings.get("radius", 0.0))
        self.selected_controls = settings.get("control_names", [])

    def generate_yaml(self):
        file_name = self.file_name.get()
        if not file_name:
            messagebox.showerror("Input Error", "Please set a file name in Builder Details.")
            return

        names = [mns["name"] for mns in self.multinode_strings]
        selected_controls = [name for name in self.selected_controls if name in names]
        self.selected_controls = selected_controls
        try:
            self.structure_exporter.generate_yaml(
                self.structure_points,
                self.structure_bars,
                self.structure_strings,
                self.multinode_strings,
                self.x_pins,
                self.y_pins,
                self.z_pins,
                self.string_stiffness.get(),
                self.bar_stiffness.get(),
                self.string_initial_length_ratio.get(),
                selected_controls,
                file_name,
            )
        except TensegrityError as error:
            _show_gui_error("YAML Generation Error", error)
            return
        except Exception as error:
            _show_gui_error("Unexpected YAML Error", error)
            return
        messagebox.showinfo("Success", f"Generated YAML file: {file_name}.yaml")

    def show_tooltip(self, text, x, y):
        """Display a tooltip at the specified coordinates."""
        self.hide_tooltip()
        self.tooltip_window = tk.Toplevel(self.root)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self.tooltip_window, text=text, bg="lightyellow", relief="solid", bd=1, padx=5, pady=2)
        label.pack()

    def hide_tooltip(self):
        """Hide the tooltip if it exists."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def add_button_tooltip(self, button, text):
        """Add a hover tooltip to a button."""
        def on_enter(event):
            self.show_tooltip(text, event.x_root, event.y_root)

        def on_leave(event):
            self.hide_tooltip()

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def on_closing(self):
        """Handle window closing."""
        self.hide_tooltip()
        if messagebox.askokcancel("Quit", "Close 3D Structure Builder?"):
            parent_root = self.root.master if isinstance(self.root.master, tk.Tk) else None
            self.root.destroy()
            if parent_root is not None:
                parent_root.after(10, lambda: close_root_if_last_window(parent_root))

class StartupDialog(tk.Toplevel):
    """Dialog to choose between 2D and 3D structure modes."""
    def __init__(self, parent):
        super().__init__(parent)
        _configure_ui_defaults(parent)
        self.title("Unit Cell Builder - Dimension Selection")
        self.geometry("500x500")
        if parent.winfo_viewable():
            self.transient(parent)
        self.resizable(False, False)
        
        self.selected_mode = None
        
        # Center the dialog on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.winfo_width() // 2)
        y = (screen_height // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Title
        title_frame = tk.Frame(self)
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame, 
            text="Select Structure Dimension", 
            font=("Arial", 14, "bold")
        )
        title_label.pack()

        workflow_frame = ttk.LabelFrame(self, text="Workflow Overview", padding=10)
        workflow_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        workflow_scrollbar = ttk.Scrollbar(workflow_frame, orient="vertical")
        workflow_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        workflow_text = tk.Text(
            workflow_frame,
            wrap="word",
            height=10,
            yscrollcommand=workflow_scrollbar.set,
            relief="solid",
            bd=1,
        )
        workflow_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        workflow_scrollbar.config(command=workflow_text.yview)
        workflow_text.insert("1.0", _WORKFLOW_OVERVIEW_TEXT.strip())
        workflow_text.config(state="disabled")
        
        # Buttons frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        
        # 2D/2.5D Button
        btn_2d = tk.Button(
            button_frame,
            text="2D / 2.5D Structure",
            command=lambda: self.select_mode("2d"),
            width=20,
            height=2,
            font=("Arial", 11)
        )
        btn_2d.pack(pady=5)
        
        # 3D Button
        btn_3d = tk.Button(
            button_frame,
            text="3D Structure",
            command=lambda: self.select_mode("3d"),
            width=20,
            height=2,
            font=("Arial", 11)
        )
        btn_3d.pack(pady=5)
        
        # Cancel Button
        btn_cancel = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=20,
            height=2,
            font=("Arial", 11)
        )
        btn_cancel.pack(pady=5)
        
        # Handle window close button
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # Grab after window is viewable to avoid TclError on hidden-root startup.
        self.after(10, self._safe_grab_set)

    def _safe_grab_set(self):
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass
    
    def select_mode(self, mode):
        self.selected_mode = mode
        self.destroy()
    
    def cancel(self):
        self.selected_mode = None
        self.destroy()

if __name__ == "__main__":
    print("Starting Unit Cell Builder...")
    print("Creating startup dialog...")

    # Use a single root for both startup dialog and main app to avoid Tk instability.
    root = tk.Tk()
    root.withdraw()

    startup_dialog = StartupDialog(root)
    startup_dialog.deiconify()
    startup_dialog.lift()
    startup_dialog.focus_force()

    print("Waiting for user selection...")
    root.wait_window(startup_dialog)

    selected_mode = startup_dialog.selected_mode
    print(f"User selected: {selected_mode}")

    if selected_mode == "2d":
        print("Launching 2D/2.5D mode...")
        root.deiconify()
        help_prompt = GlobalHoverPrompt(root, text=f"Click to draw a bar", delay=500)
        app = UnitCellBuilderApp(root)
        root.mainloop()
    elif selected_mode == "3d":
        print("Launching 3D mode...")
        root.deiconify()
        app = UnitCellBuilderApp3D(root)
        root.mainloop()
    else:
        print("User cancelled. Exiting.")
        root.destroy()
