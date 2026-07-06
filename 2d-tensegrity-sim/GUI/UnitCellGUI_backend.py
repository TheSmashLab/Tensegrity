import numpy as np
from yaml_utils import BlockList, clean_control_names, point_name, point_name_2d, round_coord, write_yaml_file


def prune_multinode_segments(segment_pairs, multinode_strings):
    """Remove any single-segment strings that are covered by multinode string paths."""
    excluded_segments = set()
    for entry in multinode_strings or []:
        points = entry.get("points", entry) if isinstance(entry, dict) else entry
        if len(points) < 2:
            continue
        for i in range(len(points) - 1):
            excluded_segments.add(frozenset((tuple(points[i]), tuple(points[i + 1]))))

    filtered_segments = []
    for pair in segment_pairs or []:
        segment_key = frozenset((tuple(pair[0]), tuple(pair[1])))
        if segment_key not in excluded_segments:
            filtered_segments.append(pair)
    return filtered_segments


class UnitCell:
    def __init__(self):
        self.selected_points = []
        self.bars = []
        self.strings = []
        self.hw = []
        self.vw = []

    def generate_grid(self, x_count, y_count, x_spacing, y_spacing):
        """Generate a uniform grid of points based on user input."""
        points = [(x * x_spacing, y * y_spacing) for y in range(y_count) for x in range(x_count)]
        return points
    
    def create_lines(self, clicked_point, line_style):
        """Handle click events for selecting points and drawing lines."""
       
        if clicked_point in self.selected_points:
            return  # Ignore duplicate selections
        
        self.selected_points.append(clicked_point)
        
        # Draw a line if two points are selected
        if len(self.selected_points) == 2:
            match line_style:
                case "bar":
                    self.bars.append(self.selected_points.copy())
                case "string":
                    self.strings.append(self.selected_points.copy())
                case "horizontal wrap":
                    self.hw.append(self.selected_points.copy())
                case "vertical wrap":
                    self.vw.append(self.selected_points.copy())
                case "delete":
                    for pair in self.bars[:]:
                        if set(pair) == set(self.selected_points.copy()):
                            self.bars.remove(pair)
                    for pair in self.strings[:]:
                        if set(pair) == set(self.selected_points.copy()):
                            self.strings.remove(pair)
                    for pair in self.hw[:]:
                        if set(pair) == set(self.selected_points.copy()):
                            self.hw.remove(pair)
                    for pair in self.vw[:]:
                        if set(pair) == set(self.selected_points.copy()):
                            self.vw.remove(pair)
                case _:
                    self.strings.append(self.selected_points.copy())
            self.selected_points.clear()
        return self.bars, self.strings, self.hw, self.vw
    
    def clear_lines(self):
        """Clear all drawn lines."""
        self.bars.clear()
        self.strings.clear()
        self.hw.clear()
        self.vw.clear()

    def submit_values(self):
        """Submit the selected lines."""
        print("Bars:", self.bars)
        print("Strings:", self.strings)
        print("Horizontal Wraps:", self.hw)
        print("Vertical Wraps:", self.vw)


class UnitCell3D:
    def __init__(self):
        self.selected_points = []
        self.bars = []
        self.strings = []
        self.x_connectors = []
        self.y_connectors = []
        self.z_connectors = []

    def generate_grid(self, x_count, y_count, z_count, x_spacing, y_spacing, z_spacing):
        """Generate a uniform 3D grid of points based on user input."""
        return [
            (x * x_spacing, y * y_spacing, z * z_spacing)
            for z in range(z_count)
            for y in range(y_count)
            for x in range(x_count)
        ]

    def create_lines(self, clicked_point, line_style):
        """Handle 3D point selections and create or delete the selected line type."""
        if clicked_point in self.selected_points:
            return self.bars, self.strings, self.x_connectors, self.y_connectors, self.z_connectors

        self.selected_points.append(clicked_point)

        if len(self.selected_points) == 2:
            match line_style:
                case "bar":
                    self.bars.append(self.selected_points.copy())
                case "string":
                    self.strings.append(self.selected_points.copy())
                case "x_connector":
                    self.x_connectors.append(self.selected_points.copy())
                case "y_connector":
                    self.y_connectors.append(self.selected_points.copy())
                case "z_connector":
                    self.z_connectors.append(self.selected_points.copy())
                case "delete":
                    self._delete_selected_line()
                case _:
                    self.strings.append(self.selected_points.copy())
            self.selected_points.clear()

        return self.bars, self.strings, self.x_connectors, self.y_connectors, self.z_connectors

    def clear_lines(self):
        """Clear all drawn 3D lines and connectors."""
        self.selected_points.clear()
        self.bars.clear()
        self.strings.clear()
        self.x_connectors.clear()
        self.y_connectors.clear()
        self.z_connectors.clear()

    def _delete_selected_line(self):
        selected = set(self.selected_points)
        for collection in (self.bars, self.strings, self.x_connectors, self.y_connectors, self.z_connectors):
            for pair in collection[:]:
                if set(pair) == selected:
                    collection.remove(pair)


class Structure:
    def __init__(self):
        self.multinode_strings = []
        self.x_pins = []
        self.y_pins = []
        self.selected_points2 = []
        self.outside_strings = []
        self.inside_strings = []
        self.linked_nodes = []

    def pattern_vectors(self, hwraps, vwraps):
        xvector = []
        yvector = []
        for pair in hwraps:
            xlength = abs(pair[0][0] - pair[1][0])
  
        for pair in vwraps:
            ylength = abs(pair[0][1] - pair[1][1])
        
        for pair in hwraps:
            vector = np.array((pair[1][0] - pair[0][0], pair[1][1] - pair[0][1]))*np.sign(pair[1][0] - pair[0][0])
  
            invvector = vector @ np.array([[1, 0], [0, -1/ylength]])

            # if xvector exists
            if len(xvector) == 0:
                xvector = np.array(vector)
            else:
                if np.array_equal(invvector, xvector):
                    xvector = invvector
                else:
                    xvector = vector
            
        for pair in vwraps:
            vector = np.array((pair[1][0] - pair[0][0], pair[1][1] - pair[0][1]))*np.sign(pair[1][1] - pair[0][1])
            
            invvector = vector @ [[1, 0], [0, -xlength]]
            
            # if xvector exists
            if len(yvector) == 0:
                yvector = np.array(vector)
            else:
                if np.array_equal(invvector, vector):
                    yvector = invvector
                else:
                    yvector = yvector

        return xvector, yvector

    def classify_strings(self, strings, x_pattern, y_pattern, x_vector, y_vector):
        """Classify strings into strings (both endpoints on edges) and inside_strings (at least one endpoint not on edges)."""
        # Calculate the boundaries of the structure
        all_x_coords = []
        all_y_coords = []
        
        for string in strings:
            all_x_coords.extend([string[0][0], string[1][0]])
            all_y_coords.extend([string[0][1], string[1][1]])
        
        min_x = min(all_x_coords)
        max_x = max(all_x_coords)
        min_y = min(all_y_coords)
        max_y = max(all_y_coords)
        
        # Tolerance for floating point comparison
        tolerance = 1e-9
        
        self.outside_strings = []
        self.inside_strings = []
        
        for string in strings:
            point1 = string[0]
            point2 = string[1]
            
            # Check if both endpoints are on the outside edges
            def is_on_edge(point):
                x, y = point
                return (abs(x - min_x) < tolerance or abs(x - max_x) < tolerance or 
                        abs(y - min_y) < tolerance or abs(y - max_y) < tolerance)
            
            both_on_edge = is_on_edge(point1) and is_on_edge(point2)
            
            if both_on_edge:
                self.outside_strings.append(string)
            else:
                self.inside_strings.append(string)

    def generate_self_similar_grid(self, bars, strings, hwraps, vwraps, axis, count):
        """Build self-similar 2D sequence aligned using horizontal/vertical connectors."""
        if count < 1:
            return [], [], []

        connector_pairs = hwraps + vwraps
        base_points = sorted({tuple(p) for pair in (bars + strings + connector_pairs) for p in pair})
        if not base_points:
            return [], [], []

        x_coords = [p[0] for p in base_points]
        y_coords = [p[1] for p in base_points]
        fallback_x = (max(x_coords) - min(x_coords), 0.0)
        fallback_y = (0.0, max(y_coords) - min(y_coords))

        x_vec = self.connector_vector_2d(hwraps, fallback_x)
        y_vec = self.connector_vector_2d(vwraps, fallback_y)

        basis = np.column_stack((x_vec, y_vec))
        if abs(np.linalg.det(basis)) < 1e-9:
            basis = np.array([[1.0, 0.0], [0.0, 1.0]])
        inv_basis = np.linalg.inv(basis)

        origin = np.array(base_points[0], dtype=float)
        local_points = [inv_basis @ (np.array(p, dtype=float) - origin) for p in base_points]

        min_a = min(lp[0] for lp in local_points)
        max_a = max(lp[0] for lp in local_points)
        min_b = min(lp[1] for lp in local_points)
        max_b = max(lp[1] for lp in local_points)
        span_a = max_a - min_a if (max_a - min_a) > 1e-9 else 1.0
        span_b = max_b - min_b if (max_b - min_b) > 1e-9 else 1.0

        if axis == "x":
            low_side = self.boundary_span_local_2d(local_points, "x", min_a)
            high_side = self.boundary_span_local_2d(local_points, "x", max_a)
            span_axis = span_a
        else:
            low_side = self.boundary_span_local_2d(local_points, "y", min_b)
            high_side = self.boundary_span_local_2d(local_points, "y", max_b)
            span_axis = span_b

        if high_side <= low_side:
            in_side = "low"
            delta = span_axis
            scale_ratio = high_side / low_side
        else:
            in_side = "high"
            delta = -span_axis
            scale_ratio = low_side / high_side

        if not np.isfinite(scale_ratio) or scale_ratio <= 1e-9:
            scale_ratio = 1.0

        boundary_offset = 0.0
        structure_bars = []
        structure_strings = []
        structure_points = []

        for i in range(count):
            scale = scale_ratio ** i

            def transform_point(point):
                local = inv_basis @ (np.array(point, dtype=float) - origin)

                if axis == "x":
                    in_val = min_a if in_side == "low" else max_a
                    a = (local[0] - in_val) * scale + boundary_offset
                    b = (local[1] - min_b) * scale
                else:
                    in_val = min_b if in_side == "low" else max_b
                    b = (local[1] - in_val) * scale + boundary_offset
                    a = (local[0] - min_a) * scale

                local_out = np.array([a, b], dtype=float)
                world = origin + basis @ local_out
                return (float(world[0]), float(world[1]))

            for pair in bars:
                p1 = transform_point(pair[0])
                p2 = transform_point(pair[1])
                structure_bars.append([p1, p2])
                structure_points.extend([p1, p2])

            for pair in strings:
                p1 = transform_point(pair[0])
                p2 = transform_point(pair[1])
                structure_strings.append([p1, p2])
                structure_points.extend([p1, p2])

            boundary_offset += delta * scale

        unique_points = list({tuple(p) for p in structure_points})
        return unique_points, structure_bars, structure_strings

    @staticmethod
    def connector_vector_2d(connectors, fallback):
        """Get a stable direction vector from connector pairs, with fallback."""
        for pair in connectors:
            vector = np.array([
                pair[1][0] - pair[0][0],
                pair[1][1] - pair[0][1],
            ], dtype=float)
            if np.linalg.norm(vector) > 1e-9:
                return vector
        return np.array(fallback, dtype=float)

    @staticmethod
    def boundary_span_local_2d(local_points, axis, side_value):
        """Measure side length on a local boundary line (used for side-matching scale ratio)."""
        tol = 1e-7
        if axis == "x":
            boundary = [p for p in local_points if abs(p[0] - side_value) < tol]
            values = [p[1] for p in boundary] if boundary else [p[1] for p in local_points]
        else:
            boundary = [p for p in local_points if abs(p[1] - side_value) < tol]
            values = [p[0] for p in boundary] if boundary else [p[0] for p in local_points]

        if len(values) < 2:
            return 1.0
        span = max(values) - min(values)
        return span if span > 1e-9 else 1.0

    def generate_grid(self, bars, strings, hwraps, vwraps, x_pattern, y_pattern):
        x_vector, y_vector = self.pattern_vectors(hwraps, vwraps)
        # Bars
        new_bars = []

        for bar in bars:
            for i in range(x_pattern):
                new_start = np.array([
                    bar[0][0] + i * x_vector[0],
                    bar[0][1] + i * x_vector[1]
                ])
                new_end = np.array([
                    bar[1][0] + i * x_vector[0],
                    bar[1][1] + i * x_vector[1]
                ])
                new_bars.append((new_start, new_end))

        # Convert NumPy arrays to simple tuples
        reshaped_bars = [[tuple(start), tuple(end)] for start, end in new_bars]
        new_bars = []

        for bar in reshaped_bars:
            for i in range(y_pattern):
                new_start = np.array([
                    bar[0][0] + i * y_vector[0],
                    bar[0][1] + i * y_vector[1]
                ])
                new_end = np.array([
                    bar[1][0] + i * y_vector[0],
                    bar[1][1] + i * y_vector[1]
                ])
                new_bars.append((new_start, new_end))
        bar_structure = [[tuple(start), tuple(end)] for start, end in new_bars]
        seen = set()
        self.unique_bars = []
        for bar in bar_structure:
            segment_key = frozenset(bar)
            if segment_key not in seen:
                seen.add(segment_key)
                self.unique_bars.append(bar)


        # Strings
        new_strings = []

        for string in strings:
            for i in range(x_pattern):
                new_start = np.array([
                    string[0][0] + i * x_vector[0],
                    string[0][1] + i * x_vector[1]
                ])
                new_end = np.array([
                    string[1][0] + i * x_vector[0],
                    string[1][1] + i * x_vector[1]
                ])
                new_strings.append((new_start, new_end))

        # Convert NumPy arrays to simple tuples
        reshaped_strings = [[tuple(start), tuple(end)] for start, end in new_strings]
        new_strings = []

        for string in reshaped_strings:
            for i in range(y_pattern):
                new_start = np.array([
                    string[0][0] + i * y_vector[0],
                    string[0][1] + i * y_vector[1]
                ])
                new_end = np.array([
                    string[1][0] + i * y_vector[0],
                    string[1][1] + i * y_vector[1]
                ])
                new_strings.append((new_start, new_end))
        string_structure = [[tuple(start), tuple(end)] for start, end in new_strings]

        self.unique_strings = []
        seen = set()
        for string in string_structure:
            segment_key = frozenset(string)
            if segment_key not in seen:
                seen.add(segment_key)
                self.unique_strings.append(string)
        """Generate a grid of points based on user input."""

        self.points = [point for group in (string_structure, bar_structure) 
                    for pair in group 
                    for point in pair]
        
        # Classify strings into outside and inside strings
        self.classify_strings(self.unique_strings, x_pattern, y_pattern, x_vector, y_vector)
        
        # Generate linked nodes for horizontal wrapping
        self.generate_linked_nodes()
        
        return self.points, self.unique_bars, self.unique_strings

    def generate_linked_nodes(self):
        """Generate linked nodes by finding leftmost and rightmost nodes at each y-level."""
        self.linked_nodes = []
        
        # Group nodes by y-coordinate
        nodes_by_y = {}
        for point in self.points:
            y = point[1]
            if y not in nodes_by_y:
                nodes_by_y[y] = []
            nodes_by_y[y].append(point)
        
        # For each y-level, find leftmost and rightmost nodes
        for y in sorted(nodes_by_y.keys()):
            nodes_at_y = nodes_by_y[y]
            if len(nodes_at_y) > 1:
                # Sort by x-coordinate
                nodes_at_y.sort(key=lambda p: p[0])
                leftmost = nodes_at_y[0]
                rightmost = nodes_at_y[-1]
                # Store as list with node names (without stringifying)
                self.linked_nodes.append([point_name_2d(leftmost), point_name_2d(rightmost)])

    def generate_yaml(self, string_stiffness, bar_stiffness, string_initial_length_ratio, inside_string_initial_length_ratio, controls, file_name, cylinder_enabled=False, radius=0.0):
        """Generate YAML file with separated strings and inside_strings."""
        data = {
            "nodes": {},
            "connections": {"bars": [], "strings": [], "inside_strings": []},
            "pins": {},
            "builders": {},
        }

        for i, point in enumerate(self.points):
            node_name = point_name_2d(point)
            data["nodes"].update({
                node_name: [round_coord(point[0]), round_coord(point[1]), 0.0]
            })
            if point in self.x_pins and point in self.y_pins:
                data["pins"].update({node_name: [True, True, False]})
            elif point in self.x_pins:
                data["pins"].update({node_name: [True, False, False]})
            elif point in self.y_pins:
                data["pins"].update({node_name: [False, True, False]})
        
        # Add outside strings (both endpoints on edges)
        for string in self.outside_strings:
            path = []
            for i in range(len(string)):
                path.append(point_name_2d(string[i]))
            data["connections"]["strings"].append(path)

        # Add inside strings (at least one endpoint not on edges)
        for string in self.inside_strings:
            path = []
            for i in range(len(string)):
                path.append(point_name_2d(string[i]))
            data["connections"]["inside_strings"].append(path)

        # Add multinode strings to strings
        for entry in self.multinode_strings:
            string = entry["points"]
            path = []
            for i in range(len(string)):
                path.append(point_name_2d(string[i]))
            data["connections"]["strings"].append({entry["name"]: path})

        # Add bars
        for bar in self.unique_bars:
            point1 = point_name_2d(bar[0])
            point2 = point_name_2d(bar[1])
            data["connections"]["bars"].append([point1, point2])

        cleaned_control_values = clean_control_names(controls)
        if cleaned_control_values:
            data["control"] = BlockList(cleaned_control_values)

        data["builders"] = {
            "bars": {"stiffness": bar_stiffness, "type": "bar"},
            "strings": {"stiffness": string_stiffness, "type": "string", "initial_length_ratio": string_initial_length_ratio},
            "inside_strings": {"stiffness": string_stiffness, "type": "string", "initial_length_ratio": inside_string_initial_length_ratio},
        }

        if cylinder_enabled and radius > 0:
            data["surface"] = {
                "cylinder": {"radius": radius},
                "linked_nodes": self.linked_nodes,
            }

        if not data.get("pins"):
            data.pop("pins", None)

        write_yaml_file(f"{file_name}.yaml", data)
        return


class Structure3D:
    def generate_self_similar_grid(self, bars, strings, axis, count):
        """Build repeated 3D bars/strings with uniform scaling along one selected axis."""
        if count < 1:
            return [], [], []

        base_points = sorted({tuple(p) for pair in (bars + strings) for p in pair})
        if not base_points:
            return [], [], []

        min_x = min(p[0] for p in base_points)
        min_y = min(p[1] for p in base_points)
        min_z = min(p[2] for p in base_points)
        span_x = max(p[0] for p in base_points) - min_x
        span_y = max(p[1] for p in base_points) - min_y
        span_z = max(p[2] for p in base_points) - min_z

        axis_span_map = {"x": span_x, "y": span_y, "z": span_z}
        axis_span = axis_span_map[axis] if axis_span_map[axis] > 1e-9 else 1.0

        min_face = self.axis_boundary_measure(base_points, axis, "min")
        max_face = self.axis_boundary_measure(base_points, axis, "max")
        scale_ratio = max_face / min_face if min_face > 1e-9 else 1.0
        if not np.isfinite(scale_ratio) or scale_ratio <= 1e-9:
            scale_ratio = 1.0

        offset = 0.0
        structure_bars = []
        structure_strings = []
        structure_points = []

        for i in range(count):
            scale = scale_ratio ** i

            def transform_point(point):
                x = (point[0] - min_x) * scale
                y = (point[1] - min_y) * scale
                z = (point[2] - min_z) * scale
                if axis == "x":
                    x += offset
                elif axis == "y":
                    y += offset
                else:
                    z += offset
                return (x, y, z)

            for pair in bars:
                p1 = transform_point(pair[0])
                p2 = transform_point(pair[1])
                structure_bars.append([p1, p2])
                structure_points.extend([p1, p2])

            for pair in strings:
                p1 = transform_point(pair[0])
                p2 = transform_point(pair[1])
                structure_strings.append([p1, p2])
                structure_points.extend([p1, p2])

            offset += scale * axis_span

        unique_points = list({tuple(p) for p in structure_points})
        return unique_points, structure_bars, structure_strings

    @staticmethod
    def axis_boundary_measure(points, axis, side):
        """Approximate boundary face size (diagonal) for self-similar scaling ratio."""
        if not points:
            return 1.0
        tol = 1e-9
        idx = {"x": 0, "y": 1, "z": 2}[axis]
        values = [p[idx] for p in points]
        target = min(values) if side == "min" else max(values)
        boundary = [p for p in points if abs(p[idx] - target) < tol]
        if not boundary:
            boundary = points

        if axis == "x":
            span_a = max(p[1] for p in boundary) - min(p[1] for p in boundary) if len(boundary) > 1 else 0.0
            span_b = max(p[2] for p in boundary) - min(p[2] for p in boundary) if len(boundary) > 1 else 0.0
        elif axis == "y":
            span_a = max(p[0] for p in boundary) - min(p[0] for p in boundary) if len(boundary) > 1 else 0.0
            span_b = max(p[2] for p in boundary) - min(p[2] for p in boundary) if len(boundary) > 1 else 0.0
        else:
            span_a = max(p[0] for p in boundary) - min(p[0] for p in boundary) if len(boundary) > 1 else 0.0
            span_b = max(p[1] for p in boundary) - min(p[1] for p in boundary) if len(boundary) > 1 else 0.0

        diag = float(np.sqrt(span_a ** 2 + span_b ** 2))
        return diag if diag > tol else 1.0

    def generate_grid(
        self,
        points,
        bars,
        strings,
        x_connectors,
        y_connectors,
        z_connectors,
        x_reps,
        y_reps,
        z_reps,
        multinode_strings=None,
    ):
        structure_bars = self.repeat_pairs(
            bars,
            points,
            x_connectors,
            y_connectors,
            z_connectors,
            x_reps,
            y_reps,
            z_reps,
        )
        structure_strings = self.repeat_pairs(
            strings,
            points,
            x_connectors,
            y_connectors,
            z_connectors,
            x_reps,
            y_reps,
            z_reps,
        )
        structure_strings = prune_multinode_segments(structure_strings, multinode_strings)
        structure_points = self.connected_nodes(structure_bars, structure_strings, multinode_strings)
        return structure_points, structure_bars, structure_strings

    def repeat_pairs(self, pairs, points, x_connectors, y_connectors, z_connectors, x_reps, y_reps, z_reps):
        x_vector, y_vector, z_vector = self.pattern_vectors(points, x_connectors, y_connectors, z_connectors)
        repeated = []
        for x_rep in range(x_reps):
            for y_rep in range(y_reps):
                for z_rep in range(z_reps):
                    offset = np.array(x_vector) * x_rep + np.array(y_vector) * y_rep + np.array(z_vector) * z_rep
                    for pair in pairs:
                        repeated.append([
                            (
                                pair[0][0] + offset[0],
                                pair[0][1] + offset[1],
                                pair[0][2] + offset[2],
                            ),
                            (
                                pair[1][0] + offset[0],
                                pair[1][1] + offset[1],
                                pair[1][2] + offset[2],
                            ),
                        ])
        return repeated

    def pattern_vectors(self, points, x_connectors, y_connectors, z_connectors):
        x_span, y_span, z_span = self.cell_spans(points)
        x_fallback = (x_span, 0.0, 0.0)
        y_fallback = (0.0, y_span, 0.0)
        z_fallback = (0.0, 0.0, z_span)

        x_vector = self.connector_vector(x_connectors, 0, x_fallback)
        y_vector = self.connector_vector(y_connectors, 1, y_fallback)
        z_vector = self.connector_vector(z_connectors, 2, z_fallback)
        return x_vector, y_vector, z_vector

    @staticmethod
    def cell_spans(points):
        if not points:
            return 1.0, 1.0, 1.0
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        z_coords = [p[2] for p in points]
        x_span = max(x_coords) - min(x_coords)
        y_span = max(y_coords) - min(y_coords)
        z_span = max(z_coords) - min(z_coords)
        return x_span if x_span > 0 else 1.0, y_span if y_span > 0 else 1.0, z_span if z_span > 0 else 1.0

    @staticmethod
    def connector_vector(connectors, axis_index, fallback_vector):
        if not connectors:
            return fallback_vector

        pair = connectors[0]
        vector = np.array([
            pair[1][0] - pair[0][0],
            pair[1][1] - pair[0][1],
            pair[1][2] - pair[0][2],
        ], dtype=float)

        if np.linalg.norm(vector) < 1e-9:
            return fallback_vector

        if abs(vector[axis_index]) < 1e-9:
            return fallback_vector

        if vector[axis_index] < 0:
            vector = -vector

        return (float(vector[0]), float(vector[1]), float(vector[2]))

    @staticmethod
    def connected_nodes(bars, strings, multinode_strings=None):
        connected = set()
        for pair in bars:
            connected.add(tuple(pair[0]))
            connected.add(tuple(pair[1]))
        for pair in strings:
            connected.add(tuple(pair[0]))
            connected.add(tuple(pair[1]))
        for entry in multinode_strings or []:
            points = entry.get("points", entry) if isinstance(entry, dict) else entry
            for point in points:
                connected.add(tuple(point))
        return list(connected)

    def generate_yaml(
        self,
        structure_points,
        structure_bars,
        structure_strings,
        multinode_strings,
        x_pins,
        y_pins,
        z_pins,
        string_stiffness,
        bar_stiffness,
        string_initial_length_ratio,
        controls,
        file_name,
    ):
        data = {
            "nodes": {},
            "connections": {
                "bars": [],
                "strings": [],
            },
            "pins": {},
            "builders": {
                "bars": {"stiffness": bar_stiffness, "type": "bar"},
                "strings": {
                    "stiffness": string_stiffness,
                    "type": "string",
                    "initial_length_ratio": string_initial_length_ratio,
                },
            },
        }

        selected_controls = clean_control_names(controls)
        if selected_controls:
            data["control"] = BlockList(selected_controls)

        for point in structure_points:
            node_name = point_name(point)
            data["nodes"][node_name] = [round_coord(point[0]), round_coord(point[1]), round_coord(point[2])]
            in_x = point in x_pins
            in_y = point in y_pins
            in_z = point in z_pins
            if in_x or in_y or in_z:
                data["pins"][node_name] = [in_x, in_y, in_z]

        self._append_pairs(data["connections"]["bars"], structure_bars)
        self._append_pairs(data["connections"]["strings"], structure_strings)

        for entry in multinode_strings:
            path = [point_name(point) for point in entry["points"]]
            data["connections"]["strings"].append({entry["name"]: path})

        if not data["pins"]:
            data.pop("pins")

        write_yaml_file(f"{file_name}.yaml", data)

    @staticmethod
    def _append_pairs(target, pairs):
        for pair in pairs:
            target.append([point_name(pair[0]), point_name(pair[1])])
    
if __name__ == "__main__":
    pass
