"""The test suite runs in 2 modes, with numba's JIT off and on; tests that need compiled code skip with JIT off.

coverage.py cannot see inside a numba-compiled function, so CI runs the suite in both modes:

- **JIT off** (`NUMBA_DISABLE_JIT=1`): `@njit` returns the plain Python function, so coverage.py
  measures the lines inside sunnbear's numba-compiled functions.
- **JIT on** (default): the compiled code runs; coverage.py measures everything outside the
  numba-compiled functions.

The coverage gate applies to both modes' data combined. A test marked `only_with_numba_jit` is
skipped with JIT off, because as plain Python it would run too slowly, e.g. because it calls into
max-div. Skipping it loses no coverage, because it runs no line inside sunnbear's own numba-compiled
functions.
"""

import os
from pathlib import Path

import numba
import pytest

import sunnbear
from sunnbear.solvers import SolverConfigRegistry


@pytest.fixture
def isolated_solver_config_registry(monkeypatch):
    """Give the test its own copy of the registry, so test-defined SolverConfig subclasses don't leak past the test."""
    monkeypatch.setattr(SolverConfigRegistry, "_configs_by_id", dict(SolverConfigRegistry._configs_by_id))


def pytest_sessionstart(session: pytest.Session) -> None:
    """Fail the run when `SUNNBEAR_TESTS_NEEDS_INSTALLED_WHEEL` is `1` and sunnbear is not imported from site-packages.

    The `install-test` job in `.github/workflows/_package_check.yml` sets the variable, because that job
    tests the built wheel: without this check, a source checkout on `sys.path` would let every test
    import the checkout, and the job would pass without testing the wheel.
    """
    if (
        os.environ.get("SUNNBEAR_TESTS_NEEDS_INSTALLED_WHEEL") == "1"
        and "site-packages" not in Path(sunnbear.__file__).parts
    ):
        pytest.exit(f"sunnbear is imported from {sunnbear.__file__}, not from the installed wheel.", returncode=1)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip `only_with_numba_jit` tests when numba runs with JIT disabled.

    The check reads `numba.config.DISABLE_JIT`, numba's own parsed value of `NUMBA_DISABLE_JIT`, so a
    value such as `0` does not skip tests.
    """
    if numba.config.DISABLE_JIT:
        skip_marker = pytest.mark.skip(reason="requires numba JIT (running with NUMBA_DISABLE_JIT)")
        for item in items:
            if "only_with_numba_jit" in item.keywords:
                item.add_marker(skip_marker)
