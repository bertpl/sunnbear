import importlib
import pkgutil

import sunnbear._core.solvers as solvers_package
from sunnbear.solvers import SolverConfigRegistry


def test_every_solver_module_is_imported_by_its_package():
    """Importing every solver module registers nothing beyond what importing the solver packages already registers."""
    # --- arrange ----------------------
    registered_before = {type(config) for config in SolverConfigRegistry.configs()}

    # --- act --------------------------
    for module_info in pkgutil.walk_packages(solvers_package.__path__, prefix=f"{solvers_package.__name__}."):
        importlib.import_module(module_info.name)

    # --- assert -----------------------
    not_imported_by_package = [
        type(config) for config in SolverConfigRegistry.configs() if type(config) not in registered_before
    ]
    modules = [cls.__module__ for cls in not_imported_by_package]
    assert not not_imported_by_package, f"solver modules not imported by their package: {modules}"
