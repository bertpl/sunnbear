"""Each public module re-exports only names that it chooses from the implementation packages that it stands for.

A name of an implementation package stays private unless its public module lists it in `__all__`.
"""

import pytest

import sunnbear._core.artifacts.exceptions
import sunnbear._core.artifacts.listing
import sunnbear._core.benchmark
import sunnbear._core.benchmark.runner.exceptions
import sunnbear._core.exceptions
import sunnbear._core.functions.core
import sunnbear._core.solvers.bracketing
import sunnbear._core.solvers.core
import sunnbear._core.solvers.core.exceptions
import sunnbear._core.solvers.open
import sunnbear.benchmark
import sunnbear.data
import sunnbear.exceptions
import sunnbear.functions
import sunnbear.solvers


def _public_names(*modules) -> set[str]:
    """Return the names that the modules expose: their `__all__` if they define one, else every name without a
    leading underscore, submodules excluded."""
    names = set()
    for module in modules:
        if hasattr(module, "__all__"):
            names |= set(module.__all__)
        else:
            names |= {name for name in dir(module) if not name.startswith("_") and not _is_submodule(module, name)}
    return names


def _is_submodule(module, name: str) -> bool:
    """Return whether the module's attribute `name` refers to one of its own submodules."""
    attr = getattr(module, name)
    return getattr(attr, "__name__", "").startswith(module.__name__ + ".")


# Each entry pairs a public module with the implementation modules whose names it re-exports.
PUBLIC_AND_IMPLEMENTATION_MODULES = [
    (sunnbear.benchmark, (sunnbear._core.benchmark,)),
    (sunnbear.data, (sunnbear._core.artifacts.listing,)),
    (sunnbear.functions, (sunnbear._core.functions.core,)),
    (sunnbear.solvers, (sunnbear._core.solvers.core, sunnbear._core.solvers.bracketing, sunnbear._core.solvers.open)),
    (
        sunnbear.exceptions,
        (
            sunnbear._core.artifacts.exceptions,
            sunnbear._core.benchmark.runner.exceptions,
            sunnbear._core.exceptions,
            sunnbear._core.solvers.core.exceptions,
        ),
    ),
]


@pytest.mark.parametrize("public_module, implementation_modules", PUBLIC_AND_IMPLEMENTATION_MODULES)
def test_public_module_re_exports_names_of_its_implementation_modules(public_module, implementation_modules):
    """Every name in a public module's `__all__` refers to the same object as the same public name in its implementation
    modules."""
    # --- arrange ----------------------
    objects_by_name = {
        name: getattr(module, name) for module in implementation_modules for name in _public_names(module)
    }

    # --- act --------------------------
    exported = {name: getattr(public_module, name) for name in public_module.__all__}

    # --- assert -----------------------
    assert exported == {name: objects_by_name.get(name) for name in exported}


@pytest.mark.parametrize("public_module", [public_module for public_module, _ in PUBLIC_AND_IMPLEMENTATION_MODULES])
def test_public_module_has_no_public_attribute_beyond_its_all(public_module):
    """A public module has no public attribute that its `__all__` leaves out, so a user can import no other public name
    from it."""
    # --- arrange / act ----------------
    public_attributes = {
        name for name in dir(public_module) if not name.startswith("_") and not _is_submodule(public_module, name)
    }

    # --- assert -----------------------
    assert public_attributes == set(public_module.__all__)
