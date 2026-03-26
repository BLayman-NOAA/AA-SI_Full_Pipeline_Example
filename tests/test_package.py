# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: NOAA Fisheries
"""
Tests for AA-SI pipeline example notebooks.

Run tests with: pytest
"""

from pathlib import Path


EXAMPLE_NOTEBOOKS_DIR = Path(__file__).parent.parent / "example_notebooks"


def test_example_notebooks_exist():
    """Verify that example notebook directories contain .ipynb files."""
    notebooks = list(EXAMPLE_NOTEBOOKS_DIR.rglob("*.ipynb"))
    assert len(notebooks) > 0, "No example notebooks found"


# =============================================================================
# TODO: Add your own tests below
# =============================================================================
#
# Example test structure:
#
# def test_my_function():
#     """Test description."""
#     from mypackagename.module import my_function
#     result = my_function(input_value)
#     assert result == expected_value
#
# For more pytest features, see: https://docs.pytest.org/
# =============================================================================
