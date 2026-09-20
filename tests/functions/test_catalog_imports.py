import importlib
import pkgutil

import sunnbear._core.functions.catalog as catalog
from sunnbear.functions import FormulaRegistry


def test_every_catalog_module_is_imported_by_its_package():
    """Importing every module found by walking the catalog registers nothing that the package's imports missed."""
    # --- arrange ----------------------
    registered_before = {type(f) for f in FormulaRegistry.formulas()}

    # --- act --------------------------
    for module_info in pkgutil.walk_packages(catalog.__path__, prefix=f"{catalog.__name__}."):
        importlib.import_module(module_info.name)

    # --- assert -----------------------
    not_imported_by_package = [type(f) for f in FormulaRegistry.formulas() if type(f) not in registered_before]
    modules = [cls.__module__ for cls in not_imported_by_package]
    assert not not_imported_by_package, f"catalog modules not imported by their package: {modules}"
