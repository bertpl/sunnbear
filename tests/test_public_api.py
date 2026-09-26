"""The public modules re-export exactly the public names of the implementation packages that they stand for."""

import pytest

import sunnbear._core.builtin_artifact_listing
import sunnbear._core.data.exceptions
import sunnbear._core.exceptions
import sunnbear._core.functions.core
import sunnbear._core.functions.core.exceptions
import sunnbear._core.solvers.bracketing
import sunnbear._core.solvers.core
import sunnbear._core.solvers.core.exceptions
import sunnbear._core.stats
import sunnbear.data
import sunnbear.exceptions
import sunnbear.functions
import sunnbear.solvers
import sunnbear.stats


def _public_names(*modules) -> set[str]:
    """Return the names that the modules expose without a leading underscore, submodules excluded."""
    names = set()
    for module in modules:
        names |= {name for name in dir(module) if not name.startswith("_") and not _is_submodule(module, name)}
    return names


def _is_submodule(module, name: str) -> bool:
    """Return whether the module's attribute `name` refers to one of its own submodules."""
    attr = getattr(module, name)
    return getattr(attr, "__name__", "").startswith(module.__name__ + ".")


@pytest.mark.parametrize(
    "public_module, implementation_modules",
    [
        (sunnbear.stats, (sunnbear._core.stats,)),
        (sunnbear.data, (sunnbear._core.builtin_artifact_listing,)),
        (sunnbear.functions, (sunnbear._core.functions.core,)),
        (sunnbear.solvers, (sunnbear._core.solvers.core, sunnbear._core.solvers.bracketing)),
        (
            sunnbear.exceptions,
            (
                sunnbear._core.data.exceptions,
                sunnbear._core.exceptions,
                sunnbear._core.functions.core.exceptions,
                sunnbear._core.solvers.core.exceptions,
            ),
        ),
    ],
)
def test_public_module_re_exports_every_public_name(public_module, implementation_modules):
    """A public module's `__all__` matches every public name of its implementation modules."""
    # --- arrange ----------------------
    expected = _public_names(*implementation_modules)

    # --- act --------------------------
    exported = set(public_module.__all__)

    # --- assert -----------------------
    assert exported == expected
