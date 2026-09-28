"""The test suite runs in 2 modes, with numba's JIT off and on; tests that need compiled code skip with JIT off.

coverage.py cannot see inside a numba-compiled function, so CI runs the suite in both modes:

- **JIT off** (`NUMBA_DISABLE_JIT=1`): `@njit` returns the plain Python function, so coverage.py
  measures the lines inside sunnbear's numba-compiled functions.
- **JIT on** (default): the compiled code runs; coverage.py measures everything outside the
  numba-compiled functions.

The coverage gate applies to both modes' data combined. A test marked `only_with_numba_jit` is
skipped with JIT off: it runs no line inside sunnbear's own numba-compiled functions, and would run
too slowly as plain Python, e.g. because it calls into max-div.
"""

import numba
import pytest

from sunnbear.solvers import SolverConfigRegistry


@pytest.fixture
def isolated_solver_config_registry(monkeypatch):
    """Give the test its own copy of the registry, so test-defined SolverConfig subclasses don't leak past the test."""
    monkeypatch.setattr(SolverConfigRegistry, "_configs_by_id", dict(SolverConfigRegistry._configs_by_id))


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip `only_with_numba_jit` tests when numba runs with JIT disabled.

    The check reads `numba.config.DISABLE_JIT`, the value numba itself parses from `NUMBA_DISABLE_JIT`,
    so tests are skipped exactly when numba runs with JIT disabled.
    """
    if numba.config.DISABLE_JIT:
        skip = pytest.mark.skip(reason="requires numba JIT (running with NUMBA_DISABLE_JIT)")
        for item in items:
            if "only_with_numba_jit" in item.keywords:
                item.add_marker(skip)
