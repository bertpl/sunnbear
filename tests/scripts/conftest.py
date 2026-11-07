"""The fixtures give the tests the modules of `scripts/literature_test_problems/` and `scripts/release.py`."""

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

_PACKAGE_DIR = Path(__file__).resolve().parents[2] / "scripts" / "literature_test_problems"
_RELEASE_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "release.py"


@pytest.fixture(scope="session")
def script_modules() -> dict[str, ModuleType]:
    """Return the script's modules that the tests use, keyed by name.

    They are imported by path, because the `scripts` folder is not an installed package.
    """
    spec = importlib.util.spec_from_file_location(
        "literature_test_problems", _PACKAGE_DIR / "__init__.py", submodule_search_locations=[str(_PACKAGE_DIR)]
    )
    package = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = package
    spec.loader.exec_module(package)
    return {
        name: importlib.import_module(f"literature_test_problems.{name}")
        for name in (
            "data_files",
            "statuses",
            "overview",
            "formulas",
            "formula_expressions",
            "published_test_problems",
            "formula_modules",
        )
    }


@pytest.fixture(scope="session")
def release() -> ModuleType:
    """Return `scripts/release.py`, imported by path: the script is not part of the package."""
    spec = importlib.util.spec_from_file_location("release_script", _RELEASE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    # `dataclasses` looks the module up in `sys.modules` while the script's dataclass is defined.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
