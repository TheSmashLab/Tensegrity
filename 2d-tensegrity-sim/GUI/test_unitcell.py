import yaml
from io import StringIO
from contextlib import redirect_stdout


from UnitCellGUI_backend import Structure, Structure3D, UnitCell, UnitCell3D


def test_generate_grid():
    uc = UnitCell()
    # Create a 2x2 grid with spacing 1
    grid = uc.generate_grid(2, 2, 1, 1)
    # Expected order: row by row, starting with y=0 then y=1
    expected = [(0, 0), (1, 0), (0, 1), (1, 1)]
    assert grid == expected


def test_create_lines_bar():
    uc = UnitCell()
    # Add first point with style "bar"
    uc.create_lines((0, 0), "bar")
    # At this point, no line should be drawn
    assert uc.bars == []
    # Add second point
    uc.create_lines((1, 1), "bar")
    # Now the line should be stored in bars and the selected_points list cleared
    assert uc.bars == [[(0, 0), (1, 1)]]
    assert uc.selected_points == []


def test_create_lines_duplicate():
    uc = UnitCell()
    uc.create_lines((0, 0), "bar")
    # Try clicking the same point twice; the duplicate should be ignored.
    uc.create_lines((0, 0), "bar")
    # Since the duplicate is ignored, selected_points should still contain one instance.
    assert uc.selected_points == [(0, 0)]
    # Now add a different point to complete a line.
    uc.create_lines((1, 1), "bar")
    assert uc.bars == [[(0, 0), (1, 1)]]
    # The selected_points list should have been cleared after drawing a line.
    assert uc.selected_points == []


def test_create_lines_string():
    uc = UnitCell()
    uc.create_lines((2, 2), "string")
    uc.create_lines((3, 3), "string")
    # Check that the line was added to the strings list.
    assert uc.strings == [[(2, 2), (3, 3)]]


def test_create_lines_horizontal_wrap():
    uc = UnitCell()
    uc.create_lines((0, 1), "horizontal wrap")
    uc.create_lines((1, 1), "horizontal wrap")
    # Check that the horizontal wrap line was added.
    assert uc.hw == [[(0, 1), (1, 1)]]


def test_create_lines_vertical_wrap():
    uc = UnitCell()
    uc.create_lines((1, 0), "vertical wrap")
    uc.create_lines((1, 1), "vertical wrap")
    # Check that the vertical wrap line was added.
    assert uc.vw == [[(1, 0), (1, 1)]]


def test_create_lines_unknown_style():
    uc = UnitCell()
    # Any unknown style should fall to the default case (which adds to strings)
    uc.create_lines((5, 5), "foo")
    uc.create_lines((6, 6), "foo")
    assert uc.strings == [[(5, 5), (6, 6)]]


def test_delete_lines_bar():
    uc = UnitCell()
    # First, add a bar line.
    uc.create_lines((0, 0), "bar")
    uc.create_lines((1, 1), "bar")
    assert uc.bars == [[(0, 0), (1, 1)]]

    # Now attempt deletion: use the same two points with style "delete".
    uc.create_lines((0, 0), "delete")
    uc.create_lines((1, 1), "delete")
    # The bar should be removed.
    assert uc.bars == []
    # Also, ensure other line lists remain unaffected (empty).
    assert uc.strings == []
    assert uc.hw == []


def test_delete_lines_vertical_wrap():
    uc = UnitCell()
    uc.create_lines((1, 0), "vertical wrap")
    uc.create_lines((1, 1), "vertical wrap")
    assert uc.vw == [[(1, 0), (1, 1)]]

    uc.create_lines((1, 1), "delete")
    uc.create_lines((1, 0), "delete")

    assert uc.vw == []


def test_clear_lines():
    uc = UnitCell()
    # Manually add lines to each list.
    uc.bars.append([(0, 0), (1, 1)])
    uc.strings.append([(2, 2), (3, 3)])
    uc.hw.append([(0, 1), (1, 1)])
    uc.vw.append([(1, 0), (1, 1)])
    # Clear all lines.
    uc.clear_lines()
    # Verify that all lists are empty.
    assert uc.bars == []
    assert uc.strings == []
    assert uc.hw == []
    assert uc.vw == []


def test_submit_values(capsys):
    uc = UnitCell()
    # Add one line to each list.
    uc.bars.append([(0, 0), (1, 1)])
    uc.strings.append([(2, 2), (3, 3)])
    uc.hw.append([(0, 1), (1, 1)])
    uc.vw.append([(1, 0), (1, 1)])
    
    # Capture printed output from submit_values().
    with StringIO() as buf, redirect_stdout(buf):
        uc.submit_values()
        output = buf.getvalue()
    
    # Verify that the printed output includes the expected labels and line points.
    assert "Bars:" in output
    assert "Strings:" in output
    assert "Horizontal Wraps:" in output
    assert "Vertical Wraps:" in output
    assert "[(0, 0), (1, 1)]" in output
    assert "[(2, 2), (3, 3)]" in output


def test_generate_grid_3d_unit_cell():
    uc = UnitCell3D()

    grid = uc.generate_grid(2, 1, 2, 1, 1, 2)

    assert grid == [(0, 0, 0), (1, 0, 0), (0, 0, 2), (1, 0, 2)]


def test_create_lines_3d_types_and_duplicate_clicks():
    uc = UnitCell3D()

    uc.create_lines((0, 0, 0), "bar")
    uc.create_lines((0, 0, 0), "bar")
    assert uc.selected_points == [(0, 0, 0)]
    uc.create_lines((1, 0, 0), "bar")
    assert uc.bars == [[(0, 0, 0), (1, 0, 0)]]
    assert uc.selected_points == []

    uc.create_lines((0, 0, 0), "string")
    uc.create_lines((0, 1, 0), "string")
    assert uc.strings == [[(0, 0, 0), (0, 1, 0)]]

    uc.create_lines((0, 0, 0), "x_connector")
    uc.create_lines((1, 0, 0), "x_connector")
    assert uc.x_connectors == [[(0, 0, 0), (1, 0, 0)]]

    uc.create_lines((0, 0, 0), "y_connector")
    uc.create_lines((0, 1, 0), "y_connector")
    assert uc.y_connectors == [[(0, 0, 0), (0, 1, 0)]]

    uc.create_lines((0, 0, 0), "z_connector")
    uc.create_lines((0, 0, 1), "z_connector")
    assert uc.z_connectors == [[(0, 0, 0), (0, 0, 1)]]


def test_create_lines_3d_unknown_style_defaults_to_string():
    uc = UnitCell3D()

    uc.create_lines((0, 0, 0), "unknown")
    uc.create_lines((1, 1, 1), "unknown")

    assert uc.strings == [[(0, 0, 0), (1, 1, 1)]]


def test_delete_lines_3d_and_clear_lines():
    uc = UnitCell3D()
    uc.create_lines((0, 0, 0), "bar")
    uc.create_lines((1, 0, 0), "bar")
    uc.create_lines((0, 0, 0), "x_connector")
    uc.create_lines((1, 0, 0), "x_connector")

    uc.create_lines((1, 0, 0), "delete")
    uc.create_lines((0, 0, 0), "delete")

    assert uc.bars == []
    assert uc.x_connectors == []

    uc.create_lines((0, 0, 0), "string")
    uc.create_lines((0, 1, 0), "string")
    uc.clear_lines()

    assert uc.selected_points == []
    assert uc.bars == []
    assert uc.strings == []
    assert uc.x_connectors == []
    assert uc.y_connectors == []
    assert uc.z_connectors == []


def test_generate_yaml_does_not_reuse_previous_pin_state(tmp_path):
    structure = Structure()
    structure.points = [(0, 0), (1, 0)]
    structure.unique_bars = [[(0, 0), (1, 0)]]
    structure.outside_strings = []
    structure.inside_strings = []
    structure.unique_strings = []

    first_file = tmp_path / "first"
    structure.x_pins = [(0, 0)]
    structure.generate_yaml(100, 1000, 0.95, 0.95, [], str(first_file))
    first_data = yaml.safe_load((tmp_path / "first.yaml").read_text())
    assert "pins" in first_data

    second_file = tmp_path / "second"
    structure.x_pins = []
    structure.y_pins = []
    structure.generate_yaml(100, 1000, 0.95, 0.95, [], str(second_file))
    second_data = yaml.safe_load((tmp_path / "second.yaml").read_text())
    assert "pins" not in second_data


def test_generate_self_similar_grid_2d_scales_along_axis():
    structure = Structure()

    points, bars, strings = structure.generate_self_similar_grid(
        bars=[
            [(0, 0), (0, 2)],
            [(2, 0), (2, 1)],
        ],
        strings=[
            [(0, 0), (2, 0)],
        ],
        hwraps=[[(0, 0), (2, 0)]],
        vwraps=[[(0, 0), (0, 1)]],
        axis="x",
        count=2,
    )

    assert [(0.0, 0.0), (0.0, 2.0)] in bars
    assert [(2.0, 0.0), (2.0, 1.0)] in bars
    assert [(2.0, 0.0), (2.0, 1.0)] in bars
    assert [(3.0, 0.0), (3.0, 0.5)] in bars
    assert [(0.0, 0.0), (2.0, 0.0)] in strings
    assert [(2.0, 0.0), (3.0, 0.0)] in strings
    assert (3.0, 0.5) in points


def test_generate_self_similar_grid_2d_handles_empty_or_zero_count():
    structure = Structure()

    assert structure.generate_self_similar_grid([], [], [], [], "x", 2) == ([], [], [])
    assert structure.generate_self_similar_grid(
        [[(0, 0), (1, 0)]],
        [],
        [],
        [],
        "x",
        0,
    ) == ([], [], [])


def test_generate_yaml_3d_exports_pins_controls_and_multinode_strings(tmp_path):
    structure = Structure3D()
    file_base = tmp_path / "structure_3d"

    structure.generate_yaml(
        structure_points=[(0, 0, 0), (1, 0, 0), (1, 1, 0)],
        structure_bars=[[(0, 0, 0), (1, 0, 0)]],
        structure_strings=[[(1, 0, 0), (1, 1, 0)]],
        multinode_strings=[{"name": "String1", "points": [(0, 0, 0), (1, 0, 0), (1, 1, 0)]}],
        x_pins=[(0, 0, 0)],
        y_pins=[(0, 0, 0), (1, 1, 0)],
        z_pins=[(1, 1, 0)],
        string_stiffness=100,
        bar_stiffness=1000,
        string_initial_length_ratio=0.95,
        controls=["String1", "", "String1"],
        file_name=str(file_base),
    )

    data = yaml.safe_load((tmp_path / "structure_3d.yaml").read_text())

    assert data["nodes"]["(0 0 0)"] == [0.0, 0.0, 0.0]
    assert data["pins"]["(0 0 0)"] == [True, True, False]
    assert data["pins"]["(1 1 0)"] == [False, True, True]
    assert data["connections"]["bars"] == [["(0 0 0)", "(1 0 0)"]]
    assert ["(1 0 0)", "(1 1 0)"] in data["connections"]["strings"]
    assert {"String1": ["(0 0 0)", "(1 0 0)", "(1 1 0)"]} in data["connections"]["strings"]
    assert data["control"] == ["String1"]


def test_generate_yaml_3d_omits_empty_pins_and_controls(tmp_path):
    structure = Structure3D()
    file_base = tmp_path / "minimal_3d"

    structure.generate_yaml(
        structure_points=[(0, 0, 0), (1, 0, 0)],
        structure_bars=[],
        structure_strings=[[(0, 0, 0), (1, 0, 0)]],
        multinode_strings=[],
        x_pins=[],
        y_pins=[],
        z_pins=[],
        string_stiffness=100,
        bar_stiffness=1000,
        string_initial_length_ratio=0.95,
        controls=[],
        file_name=str(file_base),
    )

    data = yaml.safe_load((tmp_path / "minimal_3d.yaml").read_text())

    assert "pins" not in data
    assert "control" not in data


def test_generate_grid_3d_repeats_with_connector_vectors():
    structure = Structure3D()

    points, bars, strings = structure.generate_grid(
        points=[(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)],
        bars=[[(0, 0, 0), (1, 0, 0)]],
        strings=[[(0, 0, 0), (0, 1, 0)]],
        x_connectors=[[(0, 0, 0), (2, 0, 0)]],
        y_connectors=[[(0, 0, 0), (0, 3, 0)]],
        z_connectors=[[(0, 0, 0), (0, 0, 4)]],
        x_reps=2,
        y_reps=1,
        z_reps=2,
    )

    assert [(0, 0, 0), (1, 0, 0)] in bars
    assert [(2.0, 0.0, 4.0), (3.0, 0.0, 4.0)] in bars
    assert [(0, 0, 0), (0, 1, 0)] in strings
    assert [(2.0, 0.0, 4.0), (2.0, 1.0, 4.0)] in strings
    assert set(points) == {
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 0),
        (0.0, 0.0, 4.0),
        (1.0, 0.0, 4.0),
        (0.0, 1.0, 4.0),
        (2.0, 0.0, 0.0),
        (3.0, 0.0, 0.0),
        (2.0, 1.0, 0.0),
        (2.0, 0.0, 4.0),
        (3.0, 0.0, 4.0),
        (2.0, 1.0, 4.0),
    }


def test_generate_grid_3d_prunes_multinode_segments():
    structure = Structure3D()

    points, bars, strings = structure.generate_grid(
        points=[(0, 0, 0), (1, 0, 0), (2, 0, 0)],
        bars=[],
        strings=[[(0, 0, 0), (1, 0, 0)], [(1, 0, 0), (2, 0, 0)]],
        x_connectors=[],
        y_connectors=[],
        z_connectors=[],
        x_reps=1,
        y_reps=1,
        z_reps=1,
        multinode_strings=[{"name": "String1", "points": [(0, 0, 0), (1, 0, 0), (2, 0, 0)]}],
    )

    assert bars == []
    assert strings == []
    assert set(points) == {(0, 0, 0), (1, 0, 0), (2, 0, 0)}


def test_generate_self_similar_grid_3d_scales_along_axis():
    structure = Structure3D()

    points, bars, strings = structure.generate_self_similar_grid(
        bars=[
            [(0, 0, 0), (0, 1, 0)],
            [(2, 0, 0), (2, 2, 0)],
        ],
        strings=[
            [(0, 0, 0), (2, 0, 0)],
        ],
        axis="x",
        count=2,
    )

    assert [(0, 0, 0), (0, 1, 0)] in bars
    assert [(2.0, 0.0, 0.0), (2.0, 2.0, 0.0)] in bars
    assert [(2.0, 0.0, 0.0), (2.0, 2.0, 0.0)] in bars
    assert [(6.0, 0.0, 0.0), (6.0, 4.0, 0.0)] in bars
    assert [(0, 0, 0), (2, 0, 0)] in strings
    assert [(2.0, 0.0, 0.0), (6.0, 0.0, 0.0)] in strings
    assert (6.0, 4.0, 0.0) in points


def test_generate_self_similar_grid_3d_handles_empty_or_zero_count():
    structure = Structure3D()

    assert structure.generate_self_similar_grid([], [], "x", 2) == ([], [], [])
    assert structure.generate_self_similar_grid(
        [[(0, 0, 0), (1, 0, 0)]],
        [],
        "x",
        0,
    ) == ([], [], [])
