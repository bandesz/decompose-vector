"""Tests for SVG processing functionality."""

import sys
from pathlib import Path

# Add the parent directory to sys.path to import the main module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import functions from the main script
with open(Path(__file__).parent.parent / "decompose-vector.py", "r") as f:
    exec(f.read(), globals())


class TestSVGProcessing:
    """Test SVG processing functionality."""

    def test_decompose_svg_simple_line(self, sample_svg_file, output_file):
        """Test decomposing SVG with simple line elements."""
        # Create a simple SVG with just a line
        simple_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <line x1="10" y1="10" x2="90" y2="10" stroke="black"/>
</svg>"""

        sample_svg_file.write_text(simple_svg)

        # Process the SVG
        result = decompose_svg(str(sample_svg_file), str(output_file))

        # Verify result is an SVG element with correct namespace
        assert result.tag == "svg"
        assert result.get("xmlns") == "http://www.w3.org/2000/svg"

        # Should have exactly one line element
        children = list(result)
        line_elements = [child for child in children if child.tag == "line"]
        assert len(line_elements) == 1

        # Validate the line element attributes
        line = line_elements[0]
        assert line.get("x1") == "10.0"
        assert line.get("y1") == "10.0"
        assert line.get("x2") == "90.0"
        assert line.get("y2") == "10.0"
        assert line.get("stroke") == "black"
        assert line.get("fill") == "none"
        assert line.get("id") == "path0_seg0"

    def test_decompose_svg_path_with_lines(self, sample_svg_file, output_file):
        """Test decomposing SVG path elements containing line commands."""
        # SVG with a rectangular path
        path_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <path d="M 10,10 L 90,10 L 90,90 L 10,90 Z" stroke="black" fill="none"/>
</svg>"""

        sample_svg_file.write_text(path_svg)

        # Process the SVG
        result = decompose_svg(str(sample_svg_file), str(output_file))

        # Verify result is an SVG element
        assert result.tag == "svg"

        # Should have decomposed the path into exactly 4 line segments
        children = list(result)
        line_elements = [child for child in children if child.tag == "line"]

        # Rectangle should create exactly 4 line segments
        assert len(line_elements) == 4

        # Check that we have the expected line coordinates for the rectangle
        expected_lines = [
            ("10.0", "10.0", "90.0", "10.0"),  # Top edge
            ("90.0", "10.0", "90.0", "90.0"),  # Right edge
            ("90.0", "90.0", "10.0", "90.0"),  # Bottom edge
            ("10.0", "90.0", "10.0", "10.0"),  # Left edge
        ]

        actual_lines = [
            (line.get("x1"), line.get("y1"), line.get("x2"), line.get("y2"))
            for line in line_elements
        ]

        # All expected lines should be present (order doesn't matter)
        for expected_line in expected_lines:
            assert expected_line in actual_lines

    def test_decompose_svg_removes_duplicates(self, sample_svg_file, output_file):
        """Test that duplicate lines are removed."""
        # SVG with duplicate lines (same coordinates, different styling)
        duplicate_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <line x1="10" y1="10" x2="90" y2="10" stroke="black"/>
    <line x1="10" y1="10" x2="90" y2="10" stroke="red"/>
    <line x1="90" y1="10" x2="10" y2="10" stroke="blue"/>
</svg>"""

        sample_svg_file.write_text(duplicate_svg)

        # Process the SVG
        result = decompose_svg(str(sample_svg_file), str(output_file))

        children = list(result)
        line_elements = [child for child in children if child.tag == "line"]

        # Should only have 1 line (duplicates removed, including reversed)
        assert len(line_elements) == 1

        # Validate the remaining line has expected attributes
        line = line_elements[0]
        assert line.get("x1") == "10.0"
        assert line.get("y1") == "10.0"
        assert line.get("x2") == "90.0"
        assert line.get("y2") == "10.0"
        assert line.get("stroke") == "black"
        assert line.get("fill") == "none"
        assert line.get("id") == "path0_seg0"

    def test_decompose_svg_handles_arcs(self, sample_svg_file, output_file):
        """Test processing of arc segments."""
        # SVG with an arc path
        arc_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <path d="M 30,30 A 20,20 0 0,1 70,30" stroke="black" fill="none"/>
</svg>"""

        sample_svg_file.write_text(arc_svg)

        # Process the SVG
        result = decompose_svg(str(sample_svg_file), str(output_file))

        children = list(result)
        path_elements = [child for child in children if child.tag == "path"]

        # Should have exactly one path element for the arc
        assert len(path_elements) == 1

        # Validate the arc path element
        arc_path = path_elements[0]
        d_attr = arc_path.get("d")
        assert d_attr is not None
        assert "M 30.0,30.0" in d_attr
        assert "A 20.0,20.0" in d_attr
        assert "70.0,30.0" in d_attr
        assert arc_path.get("stroke") == "black"
        assert arc_path.get("fill") == "none"
        assert arc_path.get("id") == "path0_seg0"

    def test_decompose_svg_handles_cubic_bezier(self, sample_svg_file, output_file):
        """Test processing of cubic Bezier curves."""
        # SVG with a cubic Bezier curve
        bezier_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <path d="M 10,90 C 30,10 70,10 90,90" stroke="black" fill="none"/>
</svg>"""

        sample_svg_file.write_text(bezier_svg)

        # Process the SVG
        result = decompose_svg(str(sample_svg_file), str(output_file))

        children = list(result)
        path_elements = [child for child in children if child.tag == "path"]

        # Should have exactly one path element for the curve
        assert len(path_elements) == 1

        # Validate the cubic Bezier path element
        bezier_path = path_elements[0]
        d_attr = bezier_path.get("d")
        assert d_attr is not None
        assert "M 10.0,90.0" in d_attr
        assert "C 30.0,10.0" in d_attr
        assert "70.0,10.0" in d_attr
        assert "90.0,90.0" in d_attr
        assert bezier_path.get("stroke") == "black"
        assert bezier_path.get("fill") == "none"
        assert bezier_path.get("id") == "path0_seg0"

    def test_decompose_svg_handles_quadratic_bezier(self, sample_svg_file, output_file):
        """Test processing of quadratic Bezier curves."""
        # SVG with a quadratic Bezier curve
        quad_bezier_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <path d="M 30,30 Q 50,10 70,30" stroke="black" fill="none"/>
</svg>"""

        sample_svg_file.write_text(quad_bezier_svg)

        # Process the SVG
        result = decompose_svg(str(sample_svg_file), str(output_file))

        children = list(result)
        path_elements = [child for child in children if child.tag == "path"]

        # Should have exactly one path element for the curve
        assert len(path_elements) == 1

        # Validate the quadratic Bezier path element
        quad_path = path_elements[0]
        d_attr = quad_path.get("d")
        assert d_attr is not None
        assert "M 30.0,30.0" in d_attr
        assert "Q 50.0,10.0" in d_attr
        assert "70.0,30.0" in d_attr
        assert quad_path.get("stroke") == "black"
        assert quad_path.get("fill") == "none"
        assert quad_path.get("id") == "path0_seg0"

    def test_decompose_svg_assigns_unique_ids(self, sample_svg_file, output_file):
        """Test that each decomposed element gets a unique ID."""
        # SVG with multiple elements
        multi_element_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <line x1="10" y1="10" x2="90" y2="10" stroke="black"/>
    <line x1="10" y1="20" x2="90" y2="20" stroke="black"/>
    <path d="M 30,30 Q 50,10 70,30" stroke="black" fill="none"/>
</svg>"""

        sample_svg_file.write_text(multi_element_svg)

        # Process the SVG
        result = decompose_svg(str(sample_svg_file), str(output_file))

        children = list(result)

        # Should have exactly 3 elements (2 lines + 1 path)
        assert len(children) == 3

        # All elements should have IDs
        ids = [child.get("id") for child in children]
        assert all(element_id is not None for element_id in ids)

        # All IDs should be unique
        assert len(ids) == len(set(ids))

        # Validate specific ID patterns and order
        expected_ids = ["path0_seg0", "path1_seg0", "path2_seg0"]
        assert ids == expected_ids

        # Validate element types match expectations
        line_elements = [child for child in children if child.tag == "line"]
        path_elements = [child for child in children if child.tag == "path"]
        assert len(line_elements) == 2  # Two line elements
        assert len(path_elements) == 1  # One path element
