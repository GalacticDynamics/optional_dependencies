"""Test the package."""

import re

import pytest
from packaging.version import Version

from optional_dependencies import OptionalDependencyEnum, auto
from optional_dependencies._core import Comparator


class OptDeps(OptionalDependencyEnum):
    PACKAGING = auto()  # Runtime dependency
    PYTEST = auto()  # Test dependency
    NOTINSTALLED = auto()  # Not installed


def test_enum_member_exists():
    assert hasattr(OptDeps, "PACKAGING"), "PACKAGING member should exist in OptDeps"
    assert hasattr(OptDeps, "PYTEST"), "PYTEST member should exist in OptDeps"
    assert hasattr(OptDeps, "NOTINSTALLED"), (
        "NOTINSTALLED member should exist in OptDeps"
    )


def test_installed():
    assert OptDeps.PACKAGING.installed, "PACKAGING should be installed"
    assert OptDeps.PYTEST.installed, "PYTEST should be installed"
    assert not OptDeps.NOTINSTALLED.installed, "NOTINSTALLED should not be installed"


def test_version():
    assert isinstance(OptDeps.PACKAGING.version, Version)
    assert isinstance(OptDeps.PYTEST.version, Version)

    with pytest.raises(ImportError):
        _ = OptDeps.NOTINSTALLED.version


def test_lt():
    # Compare with an unsupported type
    with pytest.raises(TypeError, match=re.escape("'<' not supported")):
        _ = OptDeps.PACKAGING < 1

    # Compare with a Version
    assert not OptDeps.PACKAGING < Version("1.0")  # noqa: SIM300

    # Something not installed
    assert not OptDeps.NOTINSTALLED <= Version("1.0")  # noqa: SIM300


def test_le():
    # Compare with an unsupported type
    with pytest.raises(TypeError, match=re.escape("'<=' not supported")):
        _ = OptDeps.PACKAGING <= 1

    # Compare with a Version
    assert not OptDeps.PACKAGING <= Version("0.1")  # noqa: SIM300

    # Something not installed
    assert not OptDeps.NOTINSTALLED <= Version("1.0")  # noqa: SIM300


def test_ge():
    # Compare with an unsupported type
    with pytest.raises(TypeError, match=re.escape("'>=' not supported")):
        assert OptDeps.PACKAGING >= 1

    # Compare with a Version
    assert OptDeps.PACKAGING >= Version("0.1")  # noqa: SIM300

    # Something not installed
    assert not OptDeps.NOTINSTALLED == Version("1.0")  # noqa: SIM201, SIM300


def test_gt():
    # Compare with an unsupported type
    with pytest.raises(TypeError, match=re.escape("'>' not supported")):
        _ = OptDeps.PACKAGING > 1

    # Compare with a Version
    assert OptDeps.PACKAGING > Version("0.1")  # noqa: SIM300

    # Something not installed
    assert not OptDeps.NOTINSTALLED > Version("1.0")  # noqa: SIM300


def test_eq():
    # Compare with other OptionalDependencyEnum instances
    assert OptDeps.PACKAGING == OptDeps.PACKAGING
    assert not OptDeps.PACKAGING == OptDeps.PYTEST  # noqa: SIM201

    # Compare with an unsupported type
    assert OptDeps.PACKAGING != 1

    # Other Versions
    assert not OptDeps.PACKAGING == Version("1.0")  # noqa: SIM201, SIM300

    # Something not installed
    assert not OptDeps.NOTINSTALLED == Version("1.0")  # noqa: SIM201, SIM300


def test_comparator():
    assert isinstance(type(OptDeps.PACKAGING).__lt__, Comparator)
    assert isinstance(type(OptDeps.PACKAGING).__le__, Comparator)
    assert isinstance(type(OptDeps.PACKAGING).__ge__, Comparator)
    assert isinstance(type(OptDeps.PACKAGING).__gt__, Comparator)
