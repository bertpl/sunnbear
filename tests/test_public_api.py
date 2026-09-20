"""The public modules re-export exactly the public names of the implementation packages they stand for."""

import pytest

import sunnbear._core.exceptions
import sunnbear._core.functions
import sunnbear._core.functions.exceptions
import sunnbear._core.stats
import sunnbear.exceptions
import sunnbear.functions
import sunnbear.stats


def _public_names(*modules) -> set[str]:
    """Return the names the modules expose without a leading underscore, submodules excluded."""
    names = set()
    for module in modules:
        names |= {name for name in dir(module) if not name.startswith("_") and not _is_submodule(module, name)}
    return names


def _is_submodule(module, name: str) -> bool:
    attr = getattr(module, name)
    return getattr(attr, "__name__", "").startswith(module.__name__ + ".")


@pytest.mark.parametrize(
    "public_module, implementation_modules",
    [
        (sunnbear.stats, (sunnbear._core.stats,)),
        (sunnbear.functions, (sunnbear._core.functions,)),
        (sunnbear.exceptions, (sunnbear._core.exceptions, sunnbear._core.functions.exceptions)),
    ],
)
def test_public_module_re_exports_every_public_name(public_module, implementation_modules):
    # --- arrange ----------------------
    expected = _public_names(*implementation_modules)

    # --- act --------------------------
    exported = set(public_module.__all__)

    # --- assert -----------------------
    assert exported == expected
