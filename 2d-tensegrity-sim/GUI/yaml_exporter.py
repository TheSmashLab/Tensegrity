from yaml_utils import BlockList, clean_control_names, point_name, point_name_2d, round_coord, write_yaml_file


def build_structure_yaml_2d(
    points,
    bars,
    outside_strings,
    inside_strings,
    multinode_strings,
    x_pins,
    y_pins,
    linked_nodes,
    string_stiffness,
    bar_stiffness,
    string_initial_length_ratio,
    inside_string_initial_length_ratio,
    controls,
    cylinder_enabled=False,
    radius=0.0,
):
    """Build the 2D structure YAML payload without writing it to disk."""
    data = {
        "nodes": {},
        "connections": {"bars": [], "strings": [], "inside_strings": []},
        "pins": {},
        "builders": _builders_2d(
            string_stiffness,
            bar_stiffness,
            string_initial_length_ratio,
            inside_string_initial_length_ratio,
        ),
    }

    for point in points:
        node_name = point_name_2d(point)
        data["nodes"][node_name] = [round_coord(point[0]), round_coord(point[1]), 0.0]
        pin_state = _pin_state(point, x_pins, y_pins, [])
        if pin_state:
            data["pins"][node_name] = pin_state

    _append_2d_paths(data["connections"]["strings"], outside_strings)
    _append_2d_paths(data["connections"]["inside_strings"], inside_strings)

    for entry in multinode_strings:
        data["connections"]["strings"].append({
            entry["name"]: [point_name_2d(point) for point in entry["points"]]
        })

    _append_2d_paths(data["connections"]["bars"], bars)
    _append_controls(data, controls)

    if cylinder_enabled and radius > 0:
        data["surface"] = {
            "cylinder": {"radius": radius},
            "linked_nodes": linked_nodes,
        }

    _drop_empty_optional_sections(data)
    return data


def build_structure_yaml_3d(
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
):
    """Build the 3D structure YAML payload without writing it to disk."""
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

    _append_controls(data, controls)

    for point in structure_points:
        node_name = point_name(point)
        data["nodes"][node_name] = [round_coord(point[0]), round_coord(point[1]), round_coord(point[2])]
        pin_state = _pin_state(point, x_pins, y_pins, z_pins)
        if pin_state:
            data["pins"][node_name] = pin_state

    _append_3d_paths(data["connections"]["bars"], structure_bars)
    _append_3d_paths(data["connections"]["strings"], structure_strings)

    for entry in multinode_strings:
        data["connections"]["strings"].append({
            entry["name"]: [point_name(point) for point in entry["points"]]
        })

    _drop_empty_optional_sections(data)
    return data


def write_structure_yaml(file_name, data):
    write_yaml_file(f"{file_name}.yaml", data)


def _builders_2d(
    string_stiffness,
    bar_stiffness,
    string_initial_length_ratio,
    inside_string_initial_length_ratio,
):
    return {
        "bars": {"stiffness": bar_stiffness, "type": "bar"},
        "strings": {
            "stiffness": string_stiffness,
            "type": "string",
            "initial_length_ratio": string_initial_length_ratio,
        },
        "inside_strings": {
            "stiffness": string_stiffness,
            "type": "string",
            "initial_length_ratio": inside_string_initial_length_ratio,
        },
    }


def _pin_state(point, x_pins, y_pins, z_pins):
    in_x = point in x_pins
    in_y = point in y_pins
    in_z = point in z_pins
    if not (in_x or in_y or in_z):
        return None
    return [in_x, in_y, in_z]


def _append_controls(data, controls):
    selected_controls = clean_control_names(controls)
    if selected_controls:
        data["control"] = BlockList(selected_controls)


def _append_2d_paths(target, pairs):
    for pair in pairs:
        target.append([point_name_2d(pair[0]), point_name_2d(pair[1])])


def _append_3d_paths(target, pairs):
    for pair in pairs:
        target.append([point_name(pair[0]), point_name(pair[1])])


def _drop_empty_optional_sections(data):
    if not data.get("pins"):
        data.pop("pins", None)
