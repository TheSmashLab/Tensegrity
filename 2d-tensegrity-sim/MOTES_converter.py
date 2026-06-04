"""MOTES_converter.py

Read a YAML tensegrity file and generate a MATLAB .m file containing the
node matrix `N` in the format expected (each row a 3-number node, then
transposed in the assignment as in the example).

Usage:
  python MOTES_converter.py path/to/file.yaml [--out out.m] [--scale 1.0]

If `--out` is omitted the output file is the same basename with `.m`.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from typing import Dict, List, Sequence, Tuple

import yaml


def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Expected YAML document to be a mapping")
    return data


def _extract_node_items(data: dict) -> List[Tuple[str, Sequence[float]]]:
    """Return ordered (node_name, coordinates) pairs from the YAML."""
    nodes_section = data.get("nodes", data)

    if not isinstance(nodes_section, dict):
        raise ValueError("No nodes mapping found in YAML file")

    node_items: List[Tuple[str, Sequence[float]]] = []
    for node_name, raw_value in nodes_section.items():
        if isinstance(raw_value, dict) and "points" in raw_value:
            coord = raw_value["points"]
        else:
            coord = raw_value

        if not isinstance(coord, (list, tuple)) or len(coord) < 2:
            continue

        node_items.append((str(node_name), coord))

    return node_items


def parse_nodes_from_yaml(path: str) -> Tuple[List[Tuple[float, float, float]], Dict[str, int]]:
    """Load YAML and extract node positions plus a name->index lookup."""
    data = _load_yaml(path)
    node_items = _extract_node_items(data)

    nodes_list: List[Tuple[float, float, float]] = []
    node_index: Dict[str, int] = {}

    for index, (node_name, coord) in enumerate(node_items, start=1):
        x = float(coord[0])
        y = float(coord[1])
        z = float(coord[2]) if len(coord) > 2 else 0.0
        nodes_list.append((x, y, z))
        node_index[node_name] = index

    return nodes_list, node_index


def _project_nodes_to_cylinder(nodes: List[Tuple[float, float, float]], radius: float) -> List[Tuple[float, float, float]]:
    """Project planar node positions onto a cylinder around the k axis."""
    if radius <= 0:
        raise ValueError("Cylinder radius must be positive")

    projected_nodes: List[Tuple[float, float, float]] = []
    for x, y, z in nodes:
        angle = x / (radius)
        projected_nodes.append((radius * math.sin(angle), -radius * math.cos(angle), y))
    return projected_nodes


def _get_cylinder_radius(data: dict) -> float | None:
    """Return the cylinder radius from the YAML surface definition, if present."""
    surface = data.get("surface")
    if not isinstance(surface, dict):
        return None
    cylinder = surface.get("cylinder")
    if not isinstance(cylinder, dict):
        return None
    radius = cylinder.get("radius")
    if radius is None:
        return None
    return float(radius)


def _collect_pinned_nodes(data: dict, node_index: Dict[str, int]) -> List[Tuple[int, int, int, int]]:
    """Collect pinned nodes as (node_index, x_pin, y_pin, z_pin) rows."""
    pins_section = data.get("pin", data.get("pins", {}))
    if not isinstance(pins_section, dict):
        return []

    pinned_nodes: List[Tuple[int, int, int, int]] = []
    for node_name, pin_values in pins_section.items():
        if node_name not in node_index:
            raise ValueError(f"Pin references unknown node: {node_name}")
        if not isinstance(pin_values, (list, tuple)) or len(pin_values) != 3:
            raise ValueError(f"Pin values for {node_name} must contain exactly 3 booleans")

        pinned_nodes.append(
            (
                node_index[node_name],
                int(bool(pin_values[0])),
                int(bool(pin_values[1])),
                int(bool(pin_values[2])),
            )
        )

    return pinned_nodes


def _extract_bar_pairs(data: dict) -> List[Tuple[str, str]]:
    """Extract bar connections as ordered node-name pairs."""
    connections = data.get("connections", {})
    if not isinstance(connections, dict):
        return []

    bars = []
    for key in ("bars", "bar"):
        value = connections.get(key, [])
        if isinstance(value, list):
            bars.extend(value)

    bar_pairs: List[Tuple[str, str]] = []
    for entry in bars:
        if isinstance(entry, dict):
            # Accept forms like {Bar1: [Node1, Node2]}
            if len(entry) != 1:
                continue
            entry = next(iter(entry.values()))

        if isinstance(entry, (list, tuple)) and len(entry) == 2:
            bar_pairs.append((str(entry[0]), str(entry[1])))

    return bar_pairs


def _normalize_connection_entry(entry) -> List[str]:
    """Return a list of node names from a connection entry."""
    if isinstance(entry, dict):
        if len(entry) != 1:
            return []
        entry = next(iter(entry.values()))

    if isinstance(entry, (list, tuple)):
        return [str(node_name) for node_name in entry]

    return []


def _collect_string_entries(data: dict) -> List[List[str]]:
    """Collect string-like connection entries as ordered lists of node names.

    Keeps multi-node paths intact (e.g. [Node1, Node2, Node3]).
    """
    connections = data.get("connections", {})
    if not isinstance(connections, dict):
        return []

    entries: List[List[str]] = []
    for key, value in connections.items():
        if key in ("bar", "bars"):
            continue
        if isinstance(value, list):
            for entry in value:
                node_names = _normalize_connection_entry(entry)
                if len(node_names) >= 2:
                    entries.append(node_names)

    return entries


def _extract_string_pairs(data: dict) -> List[Tuple[str, str]]:
    """Extract string connections expanded into adjacent node-name pairs."""
    connections = data.get("connections", {})
    if not isinstance(connections, dict):
        return []

    pairs: List[Tuple[str, str]] = []
    for key, value in connections.items():
        if key in ("bar", "bars"):
            continue
        if isinstance(value, list):
            for entry in value:
                node_names = _normalize_connection_entry(entry)
                if len(node_names) < 2:
                    continue
                for i in range(len(node_names) - 1):
                    pairs.append((node_names[i], node_names[i + 1]))
    return pairs


def format_matlab_N(nodes: List[Tuple[float, float, float]], scale: float = 1.0, decimals: int = 6) -> str:
    """Format nodes into a MATLAB assignment string.

    Produces e.g.
      N = 1*[0.5 0 0; 0 0.866 0; -0.5 0 0]';
    """
    if not nodes:
        return "N = [];"

    fmt = f"{{:.{decimals}f}}"
    rows = []
    for x, y, z in nodes:
        rows.append(" ".join((fmt.format(x), fmt.format(y), fmt.format(z))))

    matrix = "; ".join(rows)
    # include scale factor (keep as integer if possible)
    scale_str = (str(int(scale)) if float(scale).is_integer() else str(scale))
    return f"N = {scale_str}*[{matrix}]';\n"


def _format_matlab_pin_indices(indices: List[int]) -> str:
    """Format a MATLAB-style index expression for a pin axis."""
    if not indices:
        return "[]"

    sorted_indices = sorted(indices)
    if sorted_indices == list(range(sorted_indices[0], sorted_indices[-1] + 1)):
        if len(sorted_indices) == 1:
            return f"{sorted_indices[0]}"
        return f"{sorted_indices[0]}:{sorted_indices[-1]}"

    return "[" + " ".join(str(index) for index in sorted_indices) + "]"


def format_matlab_pinned_nodes(pinned_nodes: List[Tuple[int, int, int, int]]) -> str:
    """Format pinned node indices for MATLAB."""
    pinned_x = [node_idx for node_idx, x_pin, _, _ in pinned_nodes if x_pin]
    pinned_y = [node_idx for node_idx, _, y_pin, _ in pinned_nodes if y_pin]
    pinned_z = [node_idx for node_idx, _, _, z_pin in pinned_nodes if z_pin]

    return (
        f"pinned_X=({_format_matlab_pin_indices(pinned_x)})';\n"
        f"pinned_Y=({_format_matlab_pin_indices(pinned_y)})';\n"
        f"pinned_Z=({_format_matlab_pin_indices(pinned_z)})';\n"
        f"[Ia,Ib,a,b]=tenseg_boundary(pinned_X,pinned_Y,pinned_Z,nn);\n"
    )


def format_matlab_Cb_in(bar_pairs: List[Tuple[str, str]], node_index: Dict[str, int]) -> str:
    """Format bar connectivity as MATLAB indices into N."""
    if not bar_pairs:
        return "Cb_in = [];\n"

    rows = []
    for node_a, node_b in bar_pairs:
        if node_a not in node_index or node_b not in node_index:
            raise ValueError(f"Bar references unknown node(s): {node_a}, {node_b}")
        rows.append(f"{node_index[node_a]} {node_index[node_b]}")

    return f"Cb_in = [{'; '.join(rows)}];\nC_b = tenseg_ind2C(Cb_in,N);\n"


def format_matlab_Cs_in(string_pairs: List[Tuple[str, str]], node_index: Dict[str, int]) -> str:
    """Format string connectivity (expanded pairs) as MATLAB indices into N."""
    if not string_pairs:
        return "Cs_in = [];\nC_s = tenseg_ind2C(Cs_in,N);\nC=[C_b;C_s];\n[ne,nn]=size(C);% ne:No.of element;nn:No.of node\ntenseg_plot(N,C_b,C_s);\n"

    rows = []
    for node_a, node_b in string_pairs:
        if node_a not in node_index or node_b not in node_index:
            raise ValueError(f"String references unknown node(s): {node_a}, {node_b}")
        rows.append(f"{node_index[node_a]} {node_index[node_b]}")

    return f"Cs_in = [{'; '.join(rows)}];\nC_s = tenseg_ind2C(Cs_in,N);\nC=[C_b;C_s];\n[ne,nn]=size(C);% ne:No.of element;nn:No.of node\ntenseg_plot(N,C_b,C_s);\n"


def write_m_file(out_path: str, content: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert YAML nodes to MATLAB .m file (N matrix)")
    parser.add_argument("yaml", nargs='?', help="Path to input YAML file")
    parser.add_argument("--out", "-o", help="Output .m file path")
    parser.add_argument("--scale", "-s", type=float, default=1.0, help="Scale multiplier for N (default 1.0)")
    parser.add_argument("--decimals", "-d", type=int, default=6, help="Decimal places for coordinates")
    args = parser.parse_args(argv)

    yaml_path = args.yaml
    # If no YAML provided on the command line, open a file picker
    if not yaml_path:
        try:
            import tkinter as _tk
            from tkinter import filedialog as _fd

            _root = _tk.Tk()
            _root.withdraw()
            # Use a tuple of patterns so files show correctly on all platforms
            yaml_path = _fd.askopenfilename(
                title="Select YAML file to convert",
                initialdir=os.getcwd(),
                filetypes=(
                    ("YAML files", ("*.yaml", "*.yml")),
                    ("All files", "*.*"),
                ),
            )
            _root.destroy()
        except Exception as e:
            print("No YAML file specified and file dialog failed:", e)
            return 2
    if not os.path.exists(yaml_path):
        print(f"YAML file not found: {yaml_path}")
        return 2

    try:
        data = _load_yaml(yaml_path)
        nodes, node_index = parse_nodes_from_yaml(yaml_path)
        cylinder_radius = _get_cylinder_radius(data)
        if cylinder_radius is not None:
            nodes = _project_nodes_to_cylinder(nodes, cylinder_radius)
        pinned_nodes = _collect_pinned_nodes(data, node_index)
        bar_pairs = _extract_bar_pairs(data)
        string_pairs = _extract_string_pairs(data)
    except Exception as e:
        print(f"Failed to parse YAML data: {e}")
        return 3

    try:
        content = format_matlab_N(nodes, scale=args.scale, decimals=args.decimals)
        content += format_matlab_Cb_in(bar_pairs, node_index)
        content += format_matlab_Cs_in(string_pairs, node_index)
        content += format_matlab_pinned_nodes(pinned_nodes)
    except Exception as e:
        print(f"Failed to format MATLAB output: {e}")
        return 4

    out_path = args.out or (os.path.splitext(os.path.basename(yaml_path))[0] + ".m")
    write_m_file(out_path, content)
    print(f"Wrote MATLAB file: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
