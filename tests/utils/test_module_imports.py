"""`worker_pool_for_modules` returns a worker pool whose workers import the given modules before their first task, and
refuses more than 1 worker when the modules include the `__main__` module of an interactive session.
"""

import sys
import types
from dataclasses import dataclass

import pytest

from sunnbear._core.utils.module_imports import import_modules, worker_pool_for_modules

_IMPORTED_MODULE_NAME = f"{__name__.rpartition('.')[0]}.module_to_import"


@dataclass(frozen=True)
class IsModuleImportedTask:
    """`IsModuleImportedTask` returns whether the process that runs it has imported `module_name`."""

    module_name: str

    def run(self) -> bool:
        """Return whether this process has imported `module_name`."""
        return self.module_name in sys.modules


@pytest.mark.parametrize("module_names, is_imported_expected", [([], False), ([_IMPORTED_MODULE_NAME], True)])
def test_each_worker_imports_the_given_modules(module_names, is_imported_expected):
    """A worker imports the given modules before its first task; a worker of a pool for no modules has not imported
    `_IMPORTED_MODULE_NAME`."""
    # --- act --------------------------
    with worker_pool_for_modules(n_workers=2, module_names=module_names) as worker_pool:
        [(_, is_imported)] = list(worker_pool.run({0: IsModuleImportedTask(_IMPORTED_MODULE_NAME)}))

    # --- assert -----------------------
    assert is_imported == is_imported_expected


def test_a_pool_with_workers_refuses_a_main_module_of_an_interactive_session(monkeypatch):
    """A `__main__` module without a file cannot be imported by a worker, so only 1 worker is allowed."""
    # --- arrange ----------------------
    monkeypatch.setitem(sys.modules, "__main__", types.ModuleType("__main__"))

    # --- act / assert -----------------
    worker_pool_for_modules(n_workers=1, module_names={"__main__"})
    with pytest.raises(ValueError, match="defined in an interactive session"):
        worker_pool_for_modules(n_workers=2, module_names={"__main__"})


def test_importing_the_modules_imports_every_given_module():
    """`import_modules`, which each worker runs first, imports every given module.

    The test calls `import_modules` in this process, because coverage does not measure the code that runs in a worker
    process."""
    # --- act --------------------------
    import_modules([_IMPORTED_MODULE_NAME])

    # --- assert -----------------------
    assert _IMPORTED_MODULE_NAME in sys.modules
