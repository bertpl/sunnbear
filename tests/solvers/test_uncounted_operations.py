"""The tests in this module check, in 2 ways, that counted-float counts every float operation of a built-in solver.

- At runtime, every built-in config solves the test cases of the twin tests (which compare a solver with a reference
  implementation), with counted-float raising at each operation that it cannot count.
- Statically, the solver packages import no numpy, and the algorithm packages (every solver subpackage except `core/`)
  convert no value to a plain `float`: counted-float cannot detect either, so no runtime check reports them.
"""

import ast
import functools
import math
from pathlib import Path

import pytest
from counted_float import FlopCountingContext, UncountedOperationError, Verbosity

import sunnbear._core.solvers as solvers_package
from sunnbear._core.solvers.core import solver as solver_module
from sunnbear._core.utils.class_origin import is_defined_in_sunnbear
from sunnbear.solvers import BracketingSolver, Interval, SolverConfigRegistry, SolveState
from tests.solvers.twins import TWIN_TEST_CASES

_SOLVERS_DIR = Path(solvers_package.__file__).parent

# The algorithm packages, which hold the solvers' algorithms, are every subpackage except `core/`. The framework in
# `core/` converts to `float` on purpose, where values pass between the solver and the function or the caller.
_ALGORITHM_DIRS = sorted(path.parent for path in _SOLVERS_DIR.glob("*/__init__.py") if path.parent.name != "core")

# Defining a SolverConfig subclass registers it, so the registry also holds the configs that test modules define;
# the built-in configs are the ones defined inside the sunnbear package.
_BUILT_IN_CONFIGS = [config for config in SolverConfigRegistry.configs() if is_defined_in_sunnbear(type(config))]


# ==================================================================================================
#  Runtime check
# ==================================================================================================
class FrexpBisectionSolver(BracketingSolver):
    """A bisection solver that calls `math.frexp` in each step, an operation that counted-float cannot count; with the
    `uncounted_operations_raise` fixture active, its solve must fail."""

    name = "frexp_bisection"
    version = 1

    def _next_x(self, state: SolveState, interval: Interval) -> float:
        """Call `math.frexp` on the interval width, then return the midpoint."""
        math.frexp(interval.width)
        return interval.midpoint


@pytest.fixture
def uncounted_operations_raise(monkeypatch):
    """Make counted-float raise `UncountedOperationError` at each solver operation that it cannot count, and let that
    error fail the test.

    The verbosity of a `FlopCountingContext` decides whether counted-float raises at an operation that it cannot count.
    The fixture patches 2 names in the solver module, because of how `Solver.solve` works:

    - `FlopCountingContext`: `Solver.solve` opens its own context, whose verbosity replaces the verbosity of any context
      that the test opens around the call;
    - `_ending_of`, the function that maps an exception to a status: `Solver.solve` records any exception that is not a
      `SolveException` as `SOLVER_ERROR`, so the patched function re-raises an `UncountedOperationError`.
    """
    original_ending_of = solver_module._ending_of

    def ending_of_that_reraises(exc, x_best):
        """Re-raise an `UncountedOperationError`, and hand any other exception to the original `_ending_of`."""
        if not isinstance(exc, UncountedOperationError):
            return original_ending_of(exc, x_best)
        else:
            raise exc

    monkeypatch.setattr(
        solver_module, "FlopCountingContext", functools.partial(FlopCountingContext, verbosity=Verbosity.ERROR)
    )
    monkeypatch.setattr(solver_module, "_ending_of", ending_of_that_reraises)


@pytest.mark.usefixtures("uncounted_operations_raise")
def test_a_solver_that_calls_an_uncounted_operation_raises():
    """With the fixture active, a solve that calls `math.frexp` raises `UncountedOperationError`."""
    # --- act / assert -----------------
    with pytest.raises(UncountedOperationError, match="frexp"):
        TWIN_TEST_CASES[0].solve(FrexpBisectionSolver())


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
    """No module of the solver packages imports numpy, because counted-float cannot detect numpy functions applied
    to plain floats."""
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
    """No module of the algorithm packages calls `float(...)`, which silently stops counted-float from counting the
    operations on its result."""
    # --- act --------------------------
    float_calls = []
    for algorithm_dir in _ALGORITHM_DIRS:
        for path in sorted(algorithm_dir.rglob("*.py")):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float":
                    float_calls.append(f"{path.relative_to(_SOLVERS_DIR)}:{node.lineno}")

    # --- assert -----------------------
    assert float_calls == []
