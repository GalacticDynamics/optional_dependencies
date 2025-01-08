"""Optional dependencies."""

from __future__ import annotations

__all__ = [
    "InstalledState",
    "NOT_INSTALLED",
    "is_installed",
    "get_version",
    "chain_checks",
]

import importlib.metadata
import importlib.util
from enum import Enum
from typing import Final, Literal, final, overload

from packaging.version import Version, parse


@final
class InstalledState(Enum):
    """Enumeration of the installed state of a package."""

    NOT_INSTALLED = False
    """The package is not installed."""


NOT_INSTALLED: Final = InstalledState.NOT_INSTALLED


def is_installed(pkg_name: str, /) -> bool:
    """Check if a package is installed.

    Parameters
    ----------
    pkg_name : str
        The name of the package to check.

    Returns
    -------
    bool
        `True` if the package is installed, `False` otherwise.

    Examples
    --------
    >>> is_installed("packaging")
    True

    """
    try:
        spec = importlib.util.find_spec(pkg_name)
    except ModuleNotFoundError:  # pragma: no cover
        return False
    return spec is not None


def get_version(pkg_name: str, /) -> Version | Literal[InstalledState.NOT_INSTALLED]:
    """Get the version of a package if it is installed.

    Parameters
    ----------
    pkg_name : str
        The name of the package to check.

    Returns
    -------
    packaging.version.Version | Literal[InstalledState.NOT_INSTALLED]
        The `packaging.versions.Version` of the package if it is installed, or
        `optional_dependencies.NotInstalled` if it is not.

    Examples
    --------
    >>> get_version("packaging")
    <Version('...')>

    """
    try:
        # Get the version string of the package
        version_str = importlib.metadata.version(pkg_name)
    except importlib.metadata.PackageNotFoundError:
        return InstalledState.NOT_INSTALLED
    # Parse the version string using packaging.version.parse
    return parse(version_str)


@overload
def chain_checks(version: Version, /, *checks: Literal[True]) -> Version: ...


@overload
def chain_checks(
    version: Version, /, *checks: bool
) -> Version | Literal[InstalledState.NOT_INSTALLED]: ...


@overload
def chain_checks(
    version: Literal[InstalledState.NOT_INSTALLED], /, *checks: bool
) -> Literal[InstalledState.NOT_INSTALLED]: ...


def chain_checks(
    version: Version | Literal[InstalledState.NOT_INSTALLED],
    /,
    *checks: bool,
) -> Version | Literal[InstalledState.NOT_INSTALLED]:
    """Chain checks for a package.

    Parameters
    ----------
    version : Version | Literal[InstalledState.NOT_INSTALLED]
        The version of the package or `InstalledState.NOT_INSTALLED` if the
        package is not installed.
    *checks : bool
        A series of checks to perform on the package.

    Returns
    -------
    Version | Literal[InstalledState.NOT_INSTALLED]
        The version of the package if it is installed and all checks pass, or
        `InstalledState.NOT_INSTALLED` if the package is not installed or any
        check fails.

    Examples
    --------
    >>> from packaging.version import Version
    >>> from optional_dependencies.utils import NOT_INSTALLED

    >>> version = Version("1.0")
    >>> chain_checks(version, version < Version("2.0"))
    <Version('1.0')>

    >>> chain_checks(version, version > Version("2.0"))
    <InstalledState.NOT_INSTALLED: False>

    >>> chain_checks(NOT_INSTALLED, True)
    <InstalledState.NOT_INSTALLED: False>

    >>> chain_checks(NOT_INSTALLED, False)
    <InstalledState.NOT_INSTALLED: False>

    """
    if version is NOT_INSTALLED:
        return version

    return version if all(checks) else NOT_INSTALLED
