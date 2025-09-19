"""Tests for DXF processing functionality."""

import sys
from pathlib import Path

# Add the parent directory to sys.path to import the main module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import functions from the main script
with open(Path(__file__).parent.parent / "decompose-vector.py", "r") as f:
    exec(f.read(), globals())


class TestDXFProcessing:
    """Test DXF processing functionality."""

    def test_decompose_dxf_simple_line(self, sample_dxf_file, output_file):
        """Test decomposing DXF with simple line entities."""
        # Process the DXF
        result = decompose_dxf(str(sample_dxf_file), str(output_file))

        # Verify result is an SVG element with correct namespace
        assert result.tag == "svg"
        assert result.get("xmlns") == "http://www.w3.org/2000/svg"

        # Should have line elements from the DXF
        children = list(result)
        line_elements = [child for child in children if child.tag == "line"]

        # The sample DXF has exactly 2 lines based on conftest.py fixture
        assert len(line_elements) == 2

        # Validate common attributes for all lines
        for line in line_elements:
            assert line.get("stroke") == "black"
            assert line.get("fill") == "none"
            assert line.get("id").startswith("dxf_seg")

            # All coordinate attributes should be present and numeric
            for attr in ["x1", "y1", "x2", "y2"]:
                value = line.get(attr)
                assert value is not None
                float(value)  # Should not raise exception

    def test_decompose_dxf_with_arc(self, temp_dir, output_file):
        """Test decomposing DXF with arc entities."""
        # Create DXF with an arc (center at 50,50, radius 25, from 0° to 180°)
        dxf_content = """0
SECTION
2
ENTITIES
0
ARC
8
0
10
50.0
20
50.0
30
0.0
40
25.0
50
0.0
51
180.0
0
ENDSEC
0
EOF
"""
        dxf_file = temp_dir / "test_arc.dxf"
        dxf_file.write_text(dxf_content)

        # Process the DXF
        result = decompose_dxf(str(dxf_file), str(output_file))

        # Should have exactly one path element for the arc
        children = list(result)
        path_elements = [child for child in children if child.tag == "path"]
        assert len(path_elements) == 1

        # Validate the arc path element
        arc_path = path_elements[0]
        d_attr = arc_path.get("d")
        assert d_attr is not None

        # Arc should start at (75, 50) and end at (25, 50)
        # Math: center(50,50) + radius*cos(angle), radius*sin(angle)
        assert "M 75.0,50.0" in d_attr
        assert "A 25.0,25.0" in d_attr
        assert "25.0,50.0" in d_attr

        # Validate common attributes
        assert arc_path.get("stroke") == "black"
        assert arc_path.get("fill") == "none"
        assert arc_path.get("id") == "dxf_seg0"

    def test_decompose_dxf_with_lwpolyline(self, temp_dir, output_file):
        """Test decomposing DXF with LWPOLYLINE entities."""
        # Create a minimal DXF with a rectangular LWPOLYLINE
        # This creates a rectangle that should decompose into 4 line segments
        dxf_content = """0
SECTION
2
HEADER
9
$ACADVER
1
AC1015
0
ENDSEC
0
SECTION
2
TABLES
0
TABLE
2
LTYPE
70
1
0
LTYPE
2
CONTINUOUS
70
64
3
Solid line
72
65
73
0
40
0.0
0
ENDTAB
0
TABLE
2
LAYER
70
1
0
LAYER
2
0
70
64
62
7
6
CONTINUOUS
0
ENDTAB
0
ENDSEC
0
SECTION
2
ENTITIES
0
LWPOLYLINE
5
2F
8
0
100
AcDbEntity
100
AcDbPolyline
90
4
70
1
10
10.0
20
10.0
10
90.0
20
10.0
10
90.0
20
90.0
10
10.0
20
90.0
0
ENDSEC
0
EOF
"""
        dxf_file = temp_dir / "test_polyline.dxf"
        dxf_file.write_text(dxf_content)

        # Process the DXF
        result = decompose_dxf(str(dxf_file), str(output_file))

        # LWPOLYLINE should be exploded into individual line segments
        children = list(result)
        line_elements = [child for child in children if child.tag == "line"]

        # Rectangular polyline should create exactly 4 lines
        # Due to the "close" flag (70=1), it creates a closed rectangle
        assert len(line_elements) == 4

        # Expected rectangle lines: (10,10)-(90,10), (90,10)-(90,90), (90,90)-(10,90), (10,90)-(10,10)
        expected_lines = [
            ("10.0", "10.0", "90.0", "10.0"),  # Bottom edge
            ("90.0", "10.0", "90.0", "90.0"),  # Right edge
            ("90.0", "90.0", "10.0", "90.0"),  # Top edge
            ("10.0", "90.0", "10.0", "10.0"),  # Left edge (closes rectangle)
        ]

        actual_lines = [
            (line.get("x1"), line.get("y1"), line.get("x2"), line.get("y2"))
            for line in line_elements
        ]

        # All expected lines should be present (order doesn't matter)
        for expected_line in expected_lines:
            assert expected_line in actual_lines

        # Validate common attributes
        for line in line_elements:
            assert line.get("stroke") == "black"
            assert line.get("fill") == "none"
            assert line.get("id").startswith("dxf_seg")

    def test_decompose_dxf_removes_duplicates(self, temp_dir, output_file):
        """Test that duplicate lines are removed in DXF processing."""
        # Create DXF with duplicate lines
        dxf_content = """0
SECTION
2
ENTITIES
0
LINE
8
0
10
10.0
20
10.0
30
0.0
11
90.0
21
10.0
31
0.0
0
LINE
8
0
10
10.0
20
10.0
30
0.0
11
90.0
21
10.0
31
0.0
0
LINE
8
0
10
90.0
20
10.0
30
0.0
11
10.0
21
10.0
31
0.0
0
ENDSEC
0
EOF
"""
        dxf_file = temp_dir / "test_duplicates.dxf"
        dxf_file.write_text(dxf_content)

        # Process the DXF
        result = decompose_dxf(str(dxf_file), str(output_file))

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
        assert line.get("id") == "dxf_seg0"

    def test_decompose_dxf_sets_viewbox(self, sample_dxf_file, output_file):
        """Test that DXF processing sets appropriate viewBox attributes."""
        # Process the DXF
        result = decompose_dxf(str(sample_dxf_file), str(output_file))

        # Should have viewBox set based on extents (sample DXF has known extents)
        viewbox = result.get("viewBox")
        assert viewbox is not None

        # viewBox should have exactly 4 numeric values
        viewbox_values = viewbox.split()
        assert len(viewbox_values) == 4

        # All values should be numeric and reasonable
        parsed_values = []
        for val in viewbox_values:
            parsed_val = float(val)
            parsed_values.append(parsed_val)

        # Basic sanity checks: width and height should be positive
        min_x, min_y, width, height = parsed_values
        assert width > 0
        assert height > 0

    def test_decompose_dxf_assigns_unique_ids(self, sample_dxf_file, output_file):
        """Test that each decomposed element gets a unique ID in DXF processing."""
        # Process the DXF
        result = decompose_dxf(str(sample_dxf_file), str(output_file))

        children = list(result)

        # Sample DXF has exactly 2 line elements
        assert len(children) == 2

        # All elements should have IDs
        ids = [child.get("id") for child in children]
        assert all(element_id is not None for element_id in ids)

        # All IDs should be unique
        assert len(ids) == len(set(ids))

        # IDs should follow the sequential pattern for DXF
        expected_ids = ["dxf_seg0", "dxf_seg1"]
        assert ids == expected_ids

    def test_decompose_dxf_handles_empty_file(self, temp_dir, output_file):
        """Test handling of DXF files with no entities."""
        # Create minimal DXF with no entities
        dxf_content = """0
SECTION
2
ENTITIES
0
ENDSEC
0
EOF
"""
        dxf_file = temp_dir / "test_empty.dxf"
        dxf_file.write_text(dxf_content)

        # Process the DXF - should not crash
        result = decompose_dxf(str(dxf_file), str(output_file))

        # Should return a valid SVG element even if empty
        assert result.tag == "svg"
        assert result.get("xmlns") == "http://www.w3.org/2000/svg"

        # Should have no child elements
        children = list(result)
        assert len(children) == 0
