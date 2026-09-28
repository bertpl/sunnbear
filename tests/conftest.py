"""The test suite runs in 2 modes, and tests that need numba's compiled code skip in 1 of them.

coverage.py cannot see inside a numba-compiled function, so CI runs the suite twice:

- **JIT off** (`NUMBA_DISABLE_JIT=1`): `@njit` returns the plain Python function, so coverage.py
  measures the formula bodies.
- **JIT on** (default): the compiled code runs; coverage.py measures everything outside numba.

The coverage gate applies to both modes' data combined. A test marked `only_with_numba_jit` is
skipped with JIT off: it covers no numba body of sunnbear's own, and would run too slowly as plain
Python, e.g. because it calls into max-div.
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

    The check reads `numba.config.DISABLE_JIT`, numba's own parse of `NUMBA_DISABLE_JIT`, so the
    skip always matches what numba does.
    """
    if numba.config.DISABLE_JIT:
        skip = pytest.mark.skip(reason="requires numba JIT (running with NUMBA_DISABLE_JIT)")
        for item in items:
            if "only_with_numba_jit" in item.keywords:
                item.add_marker(skip)
