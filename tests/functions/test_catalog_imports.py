"""Importing the test-function package registers every module of the formula catalog, none forgotten."""

import importlib
import pkgutil

import sunnbear._core.functions.catalog as catalog
import sunnbear._core.functions.core.formula as formula_module


def test_every_catalog_module_is_imported_by_its_package():
    """Importing every module found by walking the catalog's directory registers nothing the package imports missed."""
    # --- arrange ----------------------
    registered_before = list(formula_module.registered_formula_classes)

    # --- act --------------------------
    for module_info in pkgutil.walk_packages(catalog.__path__, prefix=f"{catalog.__name__}."):
        importlib.import_module(module_info.name)

    # --- assert -----------------------
    forgotten = [cls for cls in formula_module.registered_formula_classes if cls not in registered_before]
    assert not forgotten, f"catalog modules not imported by their package: {[cls.__module__ for cls in forgotten]}"
