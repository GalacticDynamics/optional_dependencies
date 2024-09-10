"""Copyright (c) 2024 GalacticDynamics Maintainers. All rights reserved.

optional_dependencies: Check for Optional Dependencies
"""
# pylint: disable=import-outside-toplevel

__all__ = [
    # High-level API
    "OptionalDependencyEnum",
    "auto",  # re-export
    # Lower-level API
    "utils",
]


from enum import auto

from . import utils
from ._core import OptionalDependencyEnum
from ._version import version as __version__  # noqa: F401
