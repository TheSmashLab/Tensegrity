import numpy as np
import yaml


class InlineListDumper(yaml.SafeDumper):
    """Render flat lists inline and nested lists in block style."""


class BlockList(list):
    """Always render this list in block style."""


def _represent_list(dumper, data):
    is_flat_list = all(not isinstance(item, (list, dict, tuple)) for item in data)
    return dumper.represent_sequence(
        "tag:yaml.org,2002:seq",
        data,
        flow_style=is_flat_list,
    )


InlineListDumper.add_representer(list, _represent_list)
InlineListDumper.add_representer(
    BlockList,
    lambda dumper, data: dumper.represent_sequence(
        "tag:yaml.org,2002:seq",
        data,
        flow_style=False,
    ),
)
InlineListDumper.add_representer(
    np.float64,
    lambda dumper, data: dumper.represent_float(float(data)),
)
InlineListDumper.add_representer(
    np.int64,
    lambda dumper, data: dumper.represent_int(int(data)),
)
InlineListDumper.add_representer(
    np.int32,
    lambda dumper, data: dumper.represent_int(int(data)),
)
InlineListDumper.add_representer(
    np.bool_,
    lambda dumper, data: dumper.represent_bool(bool(data)),
)


def write_yaml_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        yaml.dump(
            data,
            file,
            Dumper=InlineListDumper,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
            width=120,
        )


def round_coord(value, decimals=6):
    rounded = round(float(value), decimals)
    if abs(rounded) < 10 ** (-decimals):
        return 0.0
    return rounded


def format_coord(value, decimals=6):
    text = f"{round_coord(value, decimals):.{decimals}f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def point_name(point, decimals=6):
    return "(" + " ".join(format_coord(value, decimals) for value in point) + ")"


def point_name_2d(point, decimals=6):
    return point_name(point[:2], decimals)
