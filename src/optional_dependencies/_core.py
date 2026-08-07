"""Optional dependencies."""

from __future__ import annotations

__all__: list[str] = []

import operator
from dataclasses import dataclass
from enum import Enum
from types import DynamicClassAttribute, MethodType
from typing import Callable, Literal, TypeVar, cast, final

from packaging.utils import canonicalize_name
from packaging.version import Version

from .utils import InstalledState, get_version

#: Stands in for `typing.Self`, which is 3.11+; this branch supports 3.9, and
#: `typing_extensions` is not a dependency.
_EnumT = TypeVar("_EnumT", bound="OptionalDependencyEnum")


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
            return NotImplemented  # type: ignore[no-any-return]

        # If the optional dependency is not installed, it is not greater than
        # the other version.
        if not enum.installed:
            return False

        # Compare the versions
        return self.operator(enum.version, other)


# ===================================================================


@final
class _MemberKey:
    """The internal ``_value_`` of an `OptionalDependencyEnum` member.

    `enum.Enum` folds any member whose ``_value_`` compares equal to an earlier
    one into an alias of that member -- silently, keeping the first name. A
    version cannot serve as that key: every uninstalled dependency carries the
    same `InstalledState.NOT_INSTALLED` sentinel, and distributions released
    together share a version number, so a second uninstalled member, or a second
    member of a co-released family, used to vanish into the first and report the
    wrong package's state.

    Wrapping the resolved version in one of these gives every member a key that
    is distinct by identity, so no two of them can ever compare equal. The
    wrapper is internal: `OptionalDependencyEnum.value` unwraps it, and `__repr__`
    delegates so members still show as ``<OptDeps.PACKAGING: <Version('...')>>``.

    Written out rather than a `dataclasses.dataclass` as on ``main``: this
    branch supports Python 3.9, where ``dataclass`` has no ``slots``. The
    generated ``__eq__`` would have to be turned off anyway -- comparing by
    field is exactly the aliasing this class exists to prevent.
    """

    __slots__ = ("resolved",)

    def __init__(
        self, resolved: Version | Literal[InstalledState.NOT_INSTALLED], /
    ) -> None:
        self.resolved = resolved

    def __repr__(self) -> str:
        return repr(self.resolved)


class OptionalDependencyEnum(Enum):
    """An enumeration of optional dependencies."""

    _value_: _MemberKey

    # PYI019 wants `typing.Self` here; see `_EnumT` for why it cannot be used.
    def __new__(  # noqa: PYI019
        cls: type[_EnumT], value: Version | Literal[InstalledState.NOT_INSTALLED]
    ) -> _EnumT:
        """Give the member an alias-proof ``_value_``.

        See `_MemberKey` for why the resolved version cannot be that key.

        This has to happen in ``__new__`` rather than ``__init__``: from Python
        3.11 on, `enum` snapshots ``_value_`` for the duplicate scan *before*
        calling ``__init__``, so a reassignment there comes too late. Every
        supported version (3.9+) honours a ``_value_`` set in ``__new__``.
        """
        obj = object.__new__(cls)
        obj._value_ = _MemberKey(value)
        return obj

    @classmethod
    def _missing_(cls, value: object) -> OptionalDependencyEnum | None:
        """Look a member up by its version, as ``Enum(value)`` used to.

        Members are keyed internally on `_MemberKey`, so the by-value map no
        longer holds bare versions. This restores the lookup, with the ambiguity
        it always had: where several members share a version, the first one
        declared wins.
        """
        return next((m for m in cls if m.value == value), None)

    def __reduce_ex__(self, proto: object) -> tuple[object, ...]:
        """Pickle by name.

        `enum.Enum` pickles by ``_value_``, which is now an identity-keyed
        wrapper that would not survive the round trip. The name is the exact
        key besides: versions do not distinguish members, which is the whole
        problem being fixed here.
        """
        return getattr, (self.__class__, self.name)

    @DynamicClassAttribute
    def value(self) -> Version | Literal[InstalledState.NOT_INSTALLED]:
        """The version of the optional dependency, or `NOT_INSTALLED`.

        Examples
        --------
        >>> from enum import auto
        >>> class OptDeps(OptionalDependencyEnum):
        ...     PACKAGING = auto()
        ...     NOTINSTALLED = auto()

        >>> OptDeps.PACKAGING.value
        <Version('...')>

        >>> OptDeps.NOTINSTALLED.value
        <InstalledState.NOT_INSTALLED: False>

        """
        return self._value_.resolved

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

        return cast("Version", self.value)

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

    __hash__ = Enum.__hash__
