"""Test the package itself."""

import importlib.metadata

import optional_dependencies as pkg


def test_version():
    """Test the version."""
    assert importlib.metadata.version("optional_dependencies") == pkg.__version__
