"""Optional dependencies."""

from __future__ import annotations

__all__: list[str] = []

import importlib.metadata
import json
import pathlib
from typing import Literal

from packaging.version import Version, parse

# Read the file ``imports.json``
with (pathlib.Path(__file__).parent / "imports.json").open("r") as f:
    import_mapping = dict(json.load(f))


def get_version(package_name: str) -> Version | Literal[False]:
    """Get the version of a package."""
    try:
        # Get the version string of the package
        version_str = importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return False
    # Parse the version string using packaging.version.parse
    return parse(version_str)
