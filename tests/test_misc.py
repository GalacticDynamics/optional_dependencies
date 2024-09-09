"""Test the package."""

import pytest
from packaging.version import Version

from optional_deps import OptionalDependencyEnum, auto


class OptDeps(OptionalDependencyEnum):
    PACKAGING = auto()  # Runtime dependency
    PYTEST = auto()  # Test dependency
    NOTINSTALLED = auto()  # Not installed


def test_enum_member_exists():
    assert hasattr(OptDeps, "PACKAGING"), "PACKAGING member should exist in OptDeps"
    assert hasattr(OptDeps, "PYTEST"), "PYTEST member should exist in OptDeps"
    assert hasattr(
        OptDeps, "NOTINSTALLED"
    ), "NOTINSTALLED member should exist in OptDeps"


def test_is_installed():
    assert OptDeps.PACKAGING.is_installed, "PACKAGING should be installed"
    assert OptDeps.PYTEST.is_installed, "PYTEST should be installed"
    assert not OptDeps.NOTINSTALLED.is_installed, "NOTINSTALLED should not be installed"


def test_version():
    assert isinstance(OptDeps.PACKAGING.version, Version)
    assert isinstance(OptDeps.PYTEST.version, Version)

    with pytest.raises(ImportError):
        _ = OptDeps.NOTINSTALLED.version
