import numpy as np
from yaml_utils import BlockList, point_name_2d, round_coord, write_yaml_file


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
                        # TODO: Make this work for either order of points
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

        if isinstance(controls, str):
            control_values = [(controls or "").strip()]
        elif controls is None:
            control_values = []
        else:
            control_values = [str(name).strip() for name in controls]

        cleaned_control_values = []
        seen_controls = set()
        for name in control_values:
            if name and name not in seen_controls:
                seen_controls.add(name)
                cleaned_control_values.append(name)

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
    
if __name__ == "__main__":
    pass
