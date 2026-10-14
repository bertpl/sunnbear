"""Every float operation of a built-in solver is counted, which 2 kinds of test check.

- At runtime, every built-in config solves the twin test cases with counted-float raising at each operation that it
  cannot count.
- Statically, the solver code imports no numpy and converts no value to a plain `float`: counted-float cannot see
  either, so no runtime check reports them.
"""

import ast
import functools
import math
from pathlib import Path

import pytest
from counted_float import FlopCountingContext, UncountedOperationError, Verbosity

import sunnbear._core.solvers as solvers_package
from sunnbear._core.solvers.core import solver as solver_module
from sunnbear.solvers import BracketingSolver, Interval, SolverConfigRegistry, SolveState
from tests.solvers.twins import TWIN_TEST_CASES

_SOLVERS_DIR = Path(solvers_package.__file__).parent

# The packages that hold the solvers' algorithms; the framework in `core/` converts to `float` on purpose, outside the
# counted solve.
_ALGORITHM_DIRS = [_SOLVERS_DIR / "bracketing", _SOLVERS_DIR / "open"]

# The built-in configs are the registered configs defined inside the sunnbear package.
_BUILT_IN_CONFIGS = [
    config for config in SolverConfigRegistry.configs() if type(config).__module__.startswith("sunnbear.")
]


# ==================================================================================================
#  Runtime check
# ==================================================================================================
class FrexpSolver(BracketingSolver):
    """`FrexpSolver` bisects, after calling `math.frexp` on the interval width, which counted-float cannot count."""

    name = "frexp_bisection"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        """Call `math.frexp` on the interval width, then return the midpoint."""
        math.frexp(interval.width)
        return interval.midpoint


@pytest.fixture
def uncounted_operations_raise(monkeypatch):
    """Make each solve count at `Verbosity.ERROR`, and let the `UncountedOperationError` that it raises fail the test.

    `Solver.solve` opens its own `FlopCountingContext`, whose level replaces that of a context around the call, so the
    fixture patches the context class in the solver module. `Solver.solve` also records every exception inside a
    solve as `SOLVER_ERROR`, so the fixture makes `_ending_of` re-raise this one.
    """
    ending_of = solver_module._ending_of

    def ending_of_that_reraises(exc, x_best):
        """Re-raise an `UncountedOperationError`, and hand any other exception to the original `_ending_of`."""
        if isinstance(exc, UncountedOperationError):
            raise exc
        else:
            return ending_of(exc, x_best)

    monkeypatch.setattr(
        solver_module, "FlopCountingContext", functools.partial(FlopCountingContext, verbosity=Verbosity.ERROR)
    )
    monkeypatch.setattr(solver_module, "_ending_of", ending_of_that_reraises)


@pytest.mark.usefixtures("uncounted_operations_raise")
def test_a_solver_that_calls_an_uncountable_operation_fails_the_solve():
    """With the fixture active, a solve that calls `math.frexp` raises `UncountedOperationError`."""
    with pytest.raises(UncountedOperationError, match="frexp"):
        TWIN_TEST_CASES[0].solve(FrexpSolver())


@pytest.mark.usefixtures("uncounted_operations_raise")
@pytest.mark.parametrize("test_case", TWIN_TEST_CASES, ids=str)
@pytest.mark.parametrize("config", _BUILT_IN_CONFIGS, ids=lambda config: config.solver_id)
def test_built_in_config_counts_every_operation(config, test_case):
    """Each built-in config solves each twin test case without an operation that counted-float cannot count."""
    # --- act / assert -----------------
    test_case.solve(config.instantiate())


# ==================================================================================================
#  Static checks
# ==================================================================================================
def test_no_solver_module_imports_numpy():
    """No module of the solver packages imports numpy, whose functions on plain floats counted-float cannot see."""
    # --- act --------------------------
    numpy_imports = []
    for path in sorted(_SOLVERS_DIR.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                module_names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                module_names = [node.module or ""]
            else:
                module_names = []
            for module_name in module_names:
                if module_name.split(".")[0] == "numpy":
                    numpy_imports.append(f"{path.relative_to(_SOLVERS_DIR)}:{node.lineno}")

    # --- assert -----------------------
    assert numpy_imports == []


def test_no_algorithm_module_converts_to_a_plain_float():
    """No module of the algorithm packages calls `float(...)`, which ends the counting of a value without a report."""
    # --- act --------------------------
    float_calls = []
    for algorithm_dir in _ALGORITHM_DIRS:
        for path in sorted(algorithm_dir.rglob("*.py")):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float":
                    float_calls.append(f"{path.relative_to(_SOLVERS_DIR)}:{node.lineno}")

    # --- assert -----------------------
    assert float_calls == []
