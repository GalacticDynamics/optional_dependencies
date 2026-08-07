"""Every member stays its own member, whatever its value.

`enum.Enum` folds members whose values compare equal into a single member,
keeping the first name and aliasing the rest. The values here are versions, so
collisions are the norm rather than the exception: every uninstalled dependency
carries the same `NOT_INSTALLED` sentinel, and co-released distributions share a
version number.
"""

import pickle

import pytest
from packaging.version import Version

from optional_dependencies import OptionalDependencyEnum, auto
from optional_dependencies.utils import NOT_INSTALLED, get_version, is_installed


class OptDeps(OptionalDependencyEnum):
    PACKAGING = auto()  # runtime dependency
    PYTEST = auto()  # test dependency
    NOTINSTALLED = auto()  # not installed
    ALSONOTINSTALLED = auto()  # not installed either
    # Low-level API: an explicitly assigned value, colliding with PACKAGING.
    PACKAGING_AGAIN = get_version("packaging")


def test_all_members_are_distinct() -> None:
    """Iteration yields every member, none folded into an alias."""
    assert [m.name for m in OptDeps] == list(OptDeps.__members__)
    assert len(set(OptDeps)) == 5


@pytest.mark.parametrize("name", list(OptDeps.__members__))
def test_member_keeps_its_own_name(name: str) -> None:
    """Attribute lookup returns the member it was asked for."""
    assert OptDeps[name].name == name
    assert getattr(OptDeps, name).name == name


def test_two_uninstalled_members_do_not_collapse() -> None:
    """Both share the `NOT_INSTALLED` sentinel; neither becomes the other."""
    assert OptDeps.NOTINSTALLED is not OptDeps.ALSONOTINSTALLED
    assert not OptDeps.NOTINSTALLED.installed
    assert not OptDeps.ALSONOTINSTALLED.installed


def test_two_members_sharing_a_version_do_not_collapse() -> None:
    """An explicit value equal to another member's is still its own member."""
    assert OptDeps.PACKAGING is not OptDeps.PACKAGING_AGAIN
    assert OptDeps.PACKAGING.version == OptDeps.PACKAGING_AGAIN.version


def test_value_is_still_the_version() -> None:
    """`value` keeps its documented meaning: a `Version` or `NOT_INSTALLED`."""
    assert isinstance(OptDeps.PACKAGING.value, Version)
    assert OptDeps.PACKAGING.value == OptDeps.PACKAGING.version
    assert OptDeps.NOTINSTALLED.value is NOT_INSTALLED


@pytest.mark.parametrize("name", ["PACKAGING", "NOTINSTALLED"])
def test_repr_delegates_to_the_version(name: str) -> None:
    """The key wrapper is invisible: a member still renders as its version."""
    member = OptDeps[name]
    assert repr(member.value) in repr(member)
    assert "_MemberKey" not in repr(member)


def test_members_are_hashable_and_usable_as_keys() -> None:
    """Distinct members occupy distinct slots in a dict/set."""
    mapping = {m: m.name for m in OptDeps}
    assert len(mapping) == 5
    assert mapping[OptDeps.ALSONOTINSTALLED] == "ALSONOTINSTALLED"


@pytest.mark.parametrize("name", list(OptDeps.__members__))
def test_roundtrips_through_pickle(name: str) -> None:
    """Pickling resolves back to the same member, not to an alias."""
    member = OptDeps[name]
    assert pickle.loads(pickle.dumps(member)) is member  # noqa: S301


def test_lookup_by_value_still_works() -> None:
    """`Enum(value)` keeps resolving through the version, as before.

    It cannot distinguish members that share one -- that ambiguity is inherent
    to looking a member up by a non-unique key -- but it must still find *a*
    member rather than raise.
    """
    assert OptDeps(get_version("packaging")) in {
        OptDeps.PACKAGING,
        OptDeps.PACKAGING_AGAIN,
    }
    assert OptDeps(NOT_INSTALLED) in {OptDeps.NOTINSTALLED, OptDeps.ALSONOTINSTALLED}


def test_lookup_by_unknown_value_still_raises() -> None:
    """A version no member carries is still a `ValueError`."""
    with pytest.raises(ValueError, match="is not a valid OptDeps"):
        OptDeps(Version("0.0.0.dev0"))


def test_lookup_by_name_still_works() -> None:
    """`Enum[name]` is exact, and now the only exact lookup."""
    assert OptDeps["PACKAGING_AGAIN"] is OptDeps.PACKAGING_AGAIN
    assert OptDeps["ALSONOTINSTALLED"] is OptDeps.ALSONOTINSTALLED


def test_class_level_value_access_is_rejected() -> None:
    """`value` stays a per-member attribute, as on a plain `Enum`."""
    with pytest.raises(AttributeError):
        _ = OptDeps.value  # type: ignore[attr-defined]


def test_low_level_api_members_are_distinct() -> None:
    """`chain_checks`-style values do not collapse either."""

    class Chained(OptionalDependencyEnum):
        A = get_version("packaging")
        B = get_version("packaging")
        C = get_version("this-is-not-a-package")
        D = get_version("nor-is-this")

    assert len({Chained.A, Chained.B, Chained.C, Chained.D}) == 4
    assert Chained.A.installed
    assert Chained.B.installed
    assert not Chained.C.installed
    assert not Chained.D.installed
    assert is_installed("packaging")
