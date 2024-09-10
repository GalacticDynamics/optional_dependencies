"""Optional dependencies."""

from __future__ import annotations

__all__: list[str] = []

import operator
from dataclasses import dataclass
from enum import Enum
from types import MethodType
from typing import Callable, Literal, cast

from packaging.utils import canonicalize_name
from packaging.version import Version

from .utils import InstalledState, get_version


@dataclass(frozen=True)
class Comparator:
    """A comparison operator for versions."""

    operator: Callable[[Version, Version], bool]
    """The comparison operator to use."""

    def __get__(
        self,
        instance: OptionalDependencyEnum | None,
        owner: type[OptionalDependencyEnum] | None,
    ) -> Comparator | MethodType:
        """Get the descriptor.

        Parameters
        ----------
        instance : OptionalDependencyEnum
            The instance of the descriptor.
        owner : OptionalDependencyEnum
            The owner of the descriptor.

        Returns
        -------
        Comparator
            The descriptor.

        """
        # Access the descriptor on the class
        if instance is None:
            return self
        # Bind the descriptor to the instance
        return MethodType(self.__call__, instance)

    def __call__(self, enum: OptionalDependencyEnum, other: object) -> bool:
        """Compare two versions.

        Returns
        -------
        bool
            True if the comparison is successful, False otherwise.

        """
        # Defer to the other object if it is not a Version
        if not isinstance(other, Version):
            return NotImplemented

        # If the optional dependency is not installed, it is not greater than
        # the other version.
        if not enum.installed:
            return False

        # Compare the versions
        return self.operator(enum.version, other)


# ===================================================================


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
    def installed(self) -> bool:
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

        >>> OptDeps.PACKAGING.installed
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
        <Version('...')>

        """
        if not self.installed:
            msg = f"{self.name} is not installed"
            raise ImportError(msg)

        return cast(Version, self.value)

    # ===============================================================

    __lt__ = Comparator(operator.__lt__)
    __le__ = Comparator(operator.__le__)
    __ge__ = Comparator(operator.__ge__)
    __gt__ = Comparator(operator.__gt__)

    def __eq__(self, other: object) -> bool:
        """Check if two optional dependencies are equal.

        Returns
        -------
        bool
            True if the optional dependencies are equal, False otherwise.

        """
        # First support comparison with other OptionalDependencyEnum instances
        if isinstance(other, OptionalDependencyEnum):
            return super().__eq__(other)

        # Defer to the other object if it is not a Version
        if not isinstance(other, Version):
            return NotImplemented

        # If the optional dependency is not installed, it is not greater than
        # the other version.
        if not self.installed:
            return False

        # Compare the versions
        return self.version == other
