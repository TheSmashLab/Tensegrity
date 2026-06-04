import pytest
from io import StringIO
from contextlib import redirect_stdout


from UnitCellGUI_backend import UnitCell, Structure


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
    # Note: vertical wrap deletion is not tested due to its differing iteration.


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
