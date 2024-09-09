"""Test the package itself."""

import importlib.metadata

import optional_deps as pkg


def test_version():
    """Test the version."""
    assert importlib.metadata.version("optional_deps") == pkg.__version__
