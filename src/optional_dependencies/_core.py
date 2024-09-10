"""Optional dependencies."""

from __future__ import annotations

__all__: list[str] = []

from enum import Enum
from typing import Literal, cast

from packaging.utils import canonicalize_name
from packaging.version import Version

from .utils import InstalledState, get_version


class OptionalDependencyEnum(Enum):
    """An enumeration of optional dependencies."""

    @staticmethod
    def _generate_next_value_(
        name: str,
        start: int,  # noqa: ARG004
        count: int,  # noqa: ARG004
        last_values: list[Version | Literal[InstalledState.NOT_INSTALLED]],  # noqa: ARG004
    ) -> Version | Literal[InstalledState.NOT_INSTALLED]:
        """Generate the next value (optional dependency info) for the Enum.

        Parameters
        ----------
        name : str
            The name of the package to check.
        start : int
            The starting value for the enumeration.
        count : int
            The number of values in the enumeration.
        last_values : list[Version | Literal[False]]
            The last values generated for the enumeration

        Raises
        ------
        `packaging.utils.InvalidName`
            If the package name is invalid. See
            `packaging.utils.canonicalize_name` for more information.

        """
        name = canonicalize_name(name, validate=True)
        return get_version(name)

    @property
    def is_installed(self) -> bool:
        """Check if the optional dependency is installed.

        Returns
        -------
        bool
            True if the dependency is installed, False otherwise

        Examples
        --------
        >>> from enum import auto
        >>> class OptDeps(OptionalDependencyEnum):
        ...     PACKAGING = auto()

        >>> OptDeps.PACKAGING.is_installed
        True

        """
        return self.value is not InstalledState.NOT_INSTALLED

    @property
    def version(self) -> Version:
        """Get the version of the optional dependency.

        Returns
        -------
        Version
            The version of the optional dependency if it is installed

        Raises
        ------
        ImportError
            If the optional dependency is not installed

        Examples
        --------
        >>> from enum import auto
        >>> class OptDeps(OptionalDependencyEnum):
        ...     PACKAGING = auto()

        >>> OptDeps.PACKAGING.version
        <Version('20.9')>

        """
        if not self.is_installed:
            msg = f"{self.name} is not installed"
            raise ImportError(msg)

        return cast(Version, self.value)
