"""Test configuration and fixtures."""

import tempfile
from pathlib import Path
import pytest
from xml.etree.ElementTree import Element


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_svg_content():
    """Simple SVG content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <path d="M 10,10 L 90,10 L 90,90 L 10,90 Z" stroke="black" fill="none"/>
    <line x1="20" y1="20" x2="80" y2="20" stroke="black"/>
    <path d="M 30,30 Q 50,10 70,30" stroke="black" fill="none"/>
</svg>"""


@pytest.fixture
def sample_dxf_content():
    """Simple DXF content for testing."""
    return """0
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
90.0
20
10.0
30
0.0
11
90.0
21
90.0
31
0.0
0
ENDSEC
0
EOF
"""


@pytest.fixture
def sample_svg_file(temp_dir, sample_svg_content):
    """Create a temporary SVG file."""
    svg_file = temp_dir / "test.svg"
    svg_file.write_text(sample_svg_content)
    return svg_file


@pytest.fixture
def sample_dxf_file(temp_dir, sample_dxf_content):
    """Create a temporary DXF file."""
    dxf_file = temp_dir / "test.dxf"
    dxf_file.write_text(sample_dxf_content)
    return dxf_file


# Validation helper functions
def validate_svg_element(element, expected_namespace="http://www.w3.org/2000/svg"):
    """Validate that an element is a proper SVG root element."""
    assert isinstance(element, Element)
    assert element.tag == "svg"
    assert element.get("xmlns") == expected_namespace


def validate_line_element(line, expected_stroke="black", expected_fill="none"):
    """Validate that a line element has the expected attributes."""
    assert line.tag == "line"
    assert line.get("stroke") == expected_stroke
    assert line.get("fill") == expected_fill

    # All coordinate attributes should be present and numeric
    for attr in ["x1", "y1", "x2", "y2"]:
        value = line.get(attr)
        assert value is not None, f"Missing {attr} attribute"
        try:
            float(value)
        except (ValueError, TypeError):
            pytest.fail(f"Non-numeric {attr} value: {value}")

    # Should have an ID
    assert line.get("id") is not None


def validate_path_element(path, expected_stroke="black", expected_fill="none"):
    """Validate that a path element has the expected attributes."""
    assert path.tag == "path"
    assert path.get("stroke") == expected_stroke
    assert path.get("fill") == expected_fill

    # Should have a 'd' attribute with path data
    d_attr = path.get("d")
    assert d_attr is not None, "Missing 'd' attribute"
    assert len(d_attr.strip()) > 0, "Empty path data"

    # Should have an ID
    assert path.get("id") is not None


def validate_coordinates(element, x1, y1, x2, y2, tolerance=1e-6):
    """Validate that a line element has the expected coordinates."""
    actual_coords = (
        float(element.get("x1")),
        float(element.get("y1")),
        float(element.get("x2")),
        float(element.get("y2")),
    )
    expected_coords = (x1, y1, x2, y2)

    for actual, expected in zip(actual_coords, expected_coords):
        assert (
            abs(actual - expected) <= tolerance
        ), f"Coordinate mismatch: {actual} != {expected}"


def validate_viewbox(svg_element):
    """Validate that an SVG element has a proper viewBox."""
    viewbox = svg_element.get("viewBox")
    if viewbox is not None:
        values = viewbox.split()
        assert len(values) == 4, f"viewBox should have 4 values, got {len(values)}"

        # All should be numeric
        parsed_values = []
        for val in values:
            try:
                parsed_values.append(float(val))
            except (ValueError, TypeError):
                pytest.fail(f"Non-numeric viewBox value: {val}")

        # Width and height should be positive
        min_x, min_y, width, height = parsed_values
        assert width > 0, f"Width should be positive, got {width}"
        assert height > 0, f"Height should be positive, got {height}"


@pytest.fixture
def output_file(temp_dir):
    """Create a temporary output file path."""
    return temp_dir / "output.svg"


@pytest.fixture
def mock_svg_element():
    """Create a mock SVG element for testing."""
    return Element("svg", xmlns="http://www.w3.org/2000/svg")
