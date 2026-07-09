from os.path import isfile
import re
import yaml
import numpy as np

from .data_structures import Node, Connection, Surface, Tensegrity
from .errors import TensegrityParseError

class YamlParser:
    """
    A class for parsing YAML files and creating a Tensegrity object.

    Methods:
        parse(file: str) -> Tensegrity:
            Parses the YAML file and returns a Tensegrity object.
    """

    @staticmethod
    def parse(file: str) -> Tensegrity:
        """
        Parses the YAML file and returns a Tensegrity object.

        Args:
            file (str): The path to the YAML file.

        Returns:
            Tensegrity: The tensegrity system containing Nodes and Connections.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            yaml.YAMLError: If the YAML file is invalid.
            KeyError: If a builder type does not have a builder.
            ValueError: If a connection type is not recognized.
        """
        if not isfile(file):
            raise TensegrityParseError(f"YAML file not found: {file}")

        with open(file, "r", encoding="utf-8") as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise TensegrityParseError(f"Invalid YAML file: {exc}") from exc

            if not isinstance(data, dict):
                raise TensegrityParseError("YAML file must contain a mapping at the top level.")

            for section in ("nodes", "connections", "builders"):
                if section not in data:
                    raise TensegrityParseError(f"Missing required section: {section}")

            if not isinstance(data["nodes"], dict):
                raise TensegrityParseError("Section 'nodes' must be a mapping of node names to coordinates.")
            if not isinstance(data["connections"], dict):
                raise TensegrityParseError("Section 'connections' must be a mapping of builder names to connections.")
            if not isinstance(data["builders"], dict):
                raise TensegrityParseError("Section 'builders' must be a mapping of builder names to settings.")
            if not data["nodes"]:
                raise TensegrityParseError("Section 'nodes' must contain at least one node.")

            # --- Nodes ---
            nodes = {} # Dictionary to store nodes so I can find them by name
            for node_name, position in data["nodes"].items():
                try:
                    nodes[node_name] = Node(node_name, position)
                except (TypeError, ValueError) as exc:
                    raise TensegrityParseError(f"Node {node_name} must have exactly 3 numeric coordinates.") from exc

            # --- Surface ---
            surface = None
            linked_nodes = []
            if "surface" in data:
                if not isinstance(data["surface"], dict):
                    raise TensegrityParseError("Section 'surface' must be a mapping.")
                if "linked_nodes" not in data["surface"]:
                    raise TensegrityParseError("Surface section is missing linked_nodes.")
                if not isinstance(data["surface"]["linked_nodes"], list):
                    raise TensegrityParseError("Surface linked_nodes must be a list.")
                for node_pairs in data["surface"]["linked_nodes"]:
                    if not isinstance(node_pairs, list) or len(node_pairs) != 2:
                        raise TensegrityParseError("Each surface linked_nodes entry must contain exactly 2 nodes.")
                    for node_name in node_pairs:
                        if node_name not in nodes:
                            raise TensegrityParseError(f"Surface linked_nodes references unknown node {node_name}.")
                    linked_nodes.append({node_pairs[0], node_pairs[1]})
                surface_types = [key for key in data["surface"].keys() if key != "linked_nodes"]
                if len(surface_types) != 1:
                    raise TensegrityParseError("Surface section must contain exactly one surface type.")
                surface_type = surface_types[0]
                shape = {"surface_type": surface_type, "properties": data["surface"][surface_type]}
                if surface_type == "cylinder":
                    try:
                        radius = float(shape["properties"]["radius"])
                    except (KeyError, TypeError, ValueError) as exc:
                        raise TensegrityParseError("Cylinder surface must define a numeric radius.") from exc
                    if radius <= 0:
                        raise TensegrityParseError("Cylinder surface radius must be positive.")
                surface = Surface(shape, linked_nodes)

            # --- Connections ---
            connections = [] # List to store connections used to create Tensegrity object
            connection_names = {} # Dictionary to store named connections

            for builder_type in data["connections"]:
                # --- Builders ---
                if builder_type not in data["builders"]:
                    raise TensegrityParseError(f"Builder type {builder_type} does not have a builder.")

                builder = data["builders"][builder_type]
                if not isinstance(builder, dict):
                    raise TensegrityParseError(f"Builder {builder_type} must be a mapping.")
                if "stiffness" not in builder:
                    raise TensegrityParseError(f"Builder {builder_type} is missing stiffness.")
                if "type" not in builder:
                    raise TensegrityParseError(f"Builder {builder_type} is missing type.")

                try:
                    stiffness = float(builder["stiffness"])
                except (TypeError, ValueError) as exc:
                    raise TensegrityParseError(f"Builder {builder_type} stiffness must be numeric.") from exc

                if builder["type"] == "string":
                    connection_type = Connection.ConnectionType.STRING
                elif builder["type"] == "bar":
                    connection_type = Connection.ConnectionType.BAR
                else:
                    raise TensegrityParseError(f"Connection type {builder['type']} not recognized for builder {builder_type}.")

                if "initial_length_ratio" in builder:
                    try:
                        initial_length_ratio = float(builder["initial_length_ratio"])
                    except (TypeError, ValueError) as exc:
                        raise TensegrityParseError(f"Builder {builder_type} initial_length_ratio must be numeric.") from exc
                else:
                    initial_length_ratio = 1.0

                # Create connections
                connection_entries = data["connections"][builder_type]
                if not isinstance(connection_entries, list):
                    raise TensegrityParseError(f"Connections for {builder_type} must be a list.")

                for connection in connection_entries:
                    if isinstance(connection, dict): # If the connection has a name
                        if len(connection) != 1:
                            raise TensegrityParseError(f"Named connection in {builder_type} must contain exactly one name.")
                        for name, nodes_list in connection.items():
                            if not name:
                                raise TensegrityParseError(f"Named connection in {builder_type} must have a non-empty name.")
                            _validate_connection_nodes(builder_type, nodes_list, nodes)
                            initial_length = 0
                            for i in range(len(nodes_list) - 1):
                                if {nodes_list[i], nodes_list[i+1]} in linked_nodes:
                                    continue
                                initial_length += np.linalg.norm(nodes[nodes_list[i]].position - nodes[nodes_list[i+1]].position)
                            initial_length *= initial_length_ratio

                            connection = Connection([nodes[n_name] for n_name in nodes_list], connection_type, stiffness, initial_length, name)
                            connections.append(connection)
                            connection_names[name] = connection
                    else:
                        _validate_connection_nodes(builder_type, connection, nodes)
                        initial_length = 0
                        for i in range(len(connection) - 1):
                            if {connection[i], connection[i+1]} in linked_nodes:
                                continue
                            initial_length += np.linalg.norm(nodes[connection[i]].position - nodes[connection[i+1]].position)
                        initial_length *= initial_length_ratio
                        connections.append(Connection([nodes[n_name] for n_name in connection], connection_type, stiffness, initial_length))

            # --- Pins ---
            pins = {}
            pin_key = "pin" if "pin" in data else "pins" if "pins" in data else None
            if pin_key is not None:
                if not isinstance(data[pin_key], dict):
                    raise TensegrityParseError(f"Section '{pin_key}' must be a mapping of node names to pin values.")
                for pin in data[pin_key]:
                    if pin not in nodes:
                        raise TensegrityParseError(f"Pin references unknown node {pin}.")
                    pin_values = data[pin_key][pin]
                    if not isinstance(pin_values, list) or len(pin_values) != 3:
                        raise TensegrityParseError(f"Pin values for {pin} must contain exactly 3 booleans.")
                    if any(type(value) is not bool for value in pin_values):
                        raise TensegrityParseError(f"Pin values for {pin} must be booleans.")
                    pins[pin] = pin_values # NodeName: <Array of bools>

            # --- Control ---
            controls = []
            control_key = "control" if "control" in data else "controls" if "controls" in data else None
            if control_key is not None:
                if not isinstance(data[control_key], list):
                    raise TensegrityParseError(f"Section '{control_key}' must be a list of named connections.")
                for connection_name in data[control_key]:
                    if connection_name not in connection_names:
                        raise TensegrityParseError(f"Control {connection_name} does not match any named connection.")
                    controls.append(connection_names[connection_name])

            # --- Positions ---
            positions = []
            if "positions" in data:
                raw_positions = data["positions"]
                if isinstance(raw_positions, str):
                    positions = [position.strip() for position in re.findall(r"\([^\)]+\)|\S+", raw_positions) if position.strip()]
                else:
                    positions = list(raw_positions)

        return Tensegrity(list(nodes.values()), connections, pins, controls, positions, surface)


def _validate_connection_nodes(builder_type, nodes_list, nodes):
    if not isinstance(nodes_list, list) or len(nodes_list) < 2:
        raise TensegrityParseError(f"Connection in {builder_type} must contain at least 2 nodes.")
    for node_name in nodes_list:
        if node_name not in nodes:
            raise TensegrityParseError(f"Connection in {builder_type} references unknown node {node_name}.")
