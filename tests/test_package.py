"""Test the package itself."""

import importlib.metadata

import optional_deps as m


def test_version():
    """Test the version."""
    assert importlib.metadata.version("optional_deps") == m.__version__
