"""These tests exercise the package's 3 layers (functions, solvers, and stats) together:

- solve a shipped function
- count flops
- compute a geometric pseudo-quantile (gpq)

That is the sequence that a benchmark run repeats at scale; here it runs once, with the smallest inputs,
so a mismatch between the layers' contracts is caught here.
"""

import numpy as np
import pytest

import sunnbear.functions as functions  # The module, so pytest does not try to collect the `TestFunction` class.
from sunnbear.solvers import Bisection, RegulaFalsi, Solver, SolveResult, SolveStatus
from sunnbear.stats import gpq

# A batch of shift values for the cubic fixture below, inside the range it is calibrated for.
C_VALUES = np.linspace(-1.0, 1.0, 5)


@pytest.fixture(scope="module")
def cubic() -> functions.TestFunction:
    """Return the shipped cubic, ``x^3 - 0.2 x - c`` on ``[-2, 2]``, calibrated to ``c`` in ``[-1, 1]``."""
    return functions.FormulaRegistry.candidate_from_id("f2.1.1-0.2").calibrated(c_min=-1.0, c_max=1.0)


def _solve_batch(solver: Solver, cubic: functions.TestFunction, xtol: float) -> list[SolveResult]:
    """Solve the cubic for every shift in ``C_VALUES`` and return the results in that order."""
    return [solver.solve(cubic.build_x_fun(c), cubic.a, cubic.b, xtol=xtol, max_fevals=200) for c in C_VALUES]


def test_a_shipped_function_is_solved_by_both_solvers_with_counted_flops(cubic):
    """Both solvers end inside the cubic's interval with counted flops; Bisection converges with a small residual."""
    # --- act --------------------------
    results = {solver.name: _solve_batch(solver, cubic, 1e-9) for solver in (Bisection(), RegulaFalsi())}

    # --- assert -----------------------
    for name, solve_results in results.items():
        for c, result in zip(C_VALUES, solve_results, strict=True):
            assert result.status in (SolveStatus.CONVERGED, SolveStatus.MAX_FEVALS), (name, c, result.status)
            assert result.flop_counts.total_count() > 0, (name, c)
            assert cubic.a <= result.x <= cubic.b, (name, c)
    for c, result in zip(C_VALUES, results["bisection"], strict=True):
        assert result.status is SolveStatus.CONVERGED
        # The slope on the cubic's interval is at most 12, so the residual at a converged estimate is small.
        assert abs(cubic.build_x_fun(c)(result.x)) < 1e-6


def test_a_gpq_over_a_batch_of_evaluation_counts(cubic):
    """The gpq at level 0.5 of a non-uniform batch of evaluation counts equals their geometric mean."""
    # --- act --------------------------
    n_fevals = [result.n_fevals for result in _solve_batch(Bisection(), cubic, 1e-6)]
    n_fevals_gpq = gpq(n_fevals, 0.5)

    # --- assert -----------------------
    # The evaluation counts are not uniform: at c = 0 the root sits at the first midpoint that Bisection evaluates.
    assert min(n_fevals) < max(n_fevals)
    assert n_fevals_gpq == pytest.approx(float(np.exp(np.mean(np.log(n_fevals)))))
