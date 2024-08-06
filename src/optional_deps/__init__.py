"""Copyright (c) 2024 GalacticDynamics Maintainers. All rights reserved.

optional_deps: Check for Optional Dependencies
"""
# pylint: disable=import-outside-toplevel

from __future__ import annotations

from typing import TYPE_CHECKING as _TYPE_CHECKING

from ._version import version as __version__  # noqa: F401

if _TYPE_CHECKING:
    from typing import Literal

    from packaging.version import Version


def __dir__() -> list[str]:
    from ._core import import_mapping

    return sorted(import_mapping.keys())


def __getattr__(name: str) -> Version | Literal[False]:
    import sys

    from ._core import get_version, import_mapping

    if not name.startswith("HAS_"):
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)

    # Get the package name
    alias = name.strip("HAS_")
    if alias not in import_mapping:
        msg = f"package {alias!r} is not in the imports list"
        raise AttributeError(msg)

    # Get the package version
    has_x = get_version(import_mapping[alias])

    # Cache the result
    setattr(sys.modules[__name__], name, has_x)

    return has_x
