"""Tests for utility functions in decompose-vector."""

import sys
from pathlib import Path
import pytest

# Add the parent directory to sys.path to import the main module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import functions from the main script
# We need to use exec to import from the hyphenated filename
with open(Path(__file__).parent.parent / "decompose-vector.py", "r") as f:
    exec(f.read(), globals())


class TestUtilityFunctions:
    """Test the utility functions."""

    def test_normalize_point_basic(self):
        """Test basic point normalization."""
        point = complex(1.123456789, 2.987654321)
        result = normalize_point(point)
        assert result == (1.123457, 2.987654)

    def test_normalize_point_precision(self):
        """Test point normalization with different precision."""
        point = complex(1.123456789, 2.987654321)
        result = normalize_point(point, precision=2)
        assert result == (1.12, 2.99)

    def test_normalize_point_zero(self):
        """Test normalization of zero point."""
        point = complex(0, 0)
        result = normalize_point(point)
        assert result == (0.0, 0.0)

    def test_normalize_point_negative(self):
        """Test normalization of negative coordinates."""
        point = complex(-1.123456, -2.987654)
        result = normalize_point(point)
        assert result == (-1.123456, -2.987654)

    def test_line_key_consistent_ordering(self):
        """Test that line_key returns consistent ordering."""
        p1 = (1.0, 2.0)
        p2 = (3.0, 4.0)

        # Should return the same key regardless of point order
        key1 = line_key(p1, p2)
        key2 = line_key(p2, p1)

        assert key1 == key2
        assert key1 == ((1.0, 2.0), (3.0, 4.0))

    def test_line_key_same_points(self):
        """Test line_key with identical points."""
        p1 = (1.0, 2.0)
        key = line_key(p1, p1)
        assert key == ((1.0, 2.0), (1.0, 2.0))

    def test_line_length_horizontal(self):
        """Test length calculation for horizontal line."""
        length = line_length(0, 0, 5, 0)
        assert length == 5.0

    def test_line_length_vertical(self):
        """Test length calculation for vertical line."""
        length = line_length(0, 0, 0, 3)
        assert length == 3.0

    def test_line_length_diagonal(self):
        """Test length calculation for diagonal line."""
        # 3-4-5 triangle
        length = line_length(0, 0, 3, 4)
        assert length == pytest.approx(5.0)

    def test_line_length_zero(self):
        """Test length calculation for zero-length line."""
        length = line_length(1, 1, 1, 1)
        assert length == pytest.approx(0.0)

    def test_line_length_negative_coordinates(self):
        """Test length calculation with negative coordinates."""
        length = line_length(-2, -3, 1, 1)
        assert length == pytest.approx(
            5.0
        )  # sqrt((1-(-2))^2 + (1-(-3))^2) = sqrt(9+16) = 5

    def test_line_length_floating_point_precision(self):
        """Test length calculation with floating point coordinates."""
        # Test with non-integer coordinates that might have precision issues
        length = line_length(0.1, 0.2, 1.1, 1.2)
        expected = ((1.1 - 0.1) ** 2 + (1.2 - 0.2) ** 2) ** 0.5  # sqrt(1 + 1) = sqrt(2)
        assert length == pytest.approx(expected, rel=1e-9)
