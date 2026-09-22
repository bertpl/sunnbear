"""These tests check the shipped solvers against their `scipy.optimize` counterparts through the `ScipySolver` twin."""

import pytest
import scipy.optimize
from counted_float import FlopCounts

from sunnbear.solvers import Bisection, RegulaFalsi, SolveStatus
from tests.solvers.scipy_twin import ScipySolver


def _cubic(x: float) -> float:
    return x**3 - x - 1.0


def _sine_like(x: float) -> float:
    return x**5 - 2.0 * x + 0.5


PROBLEMS = [(_cubic, 1.0, 2.0), (_sine_like, 0.0, 1.0), (lambda x: -_cubic(x), 1.0, 2.0)]  # The last is decreasing.


# ==================================================================================================
#  The twin itself
# ==================================================================================================
def test_the_twin_counts_evaluations_but_no_solver_arithmetic():
    # --- act --------------------------
    result = ScipySolver(scipy.optimize.bisect).solve(_cubic, 1.0, 2.0, xtol=1e-6, max_fevals=200)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals > 2  # The 2 bound evaluations, then SciPy's own.
    # SciPy runs on plain floats, so only the framework's own checks and bookkeeping are counted.
    assert result.flop_counts == FlopCounts(COMP=4, ADD=1, MUL=1)


# ==================================================================================================
#  Agreement
# ==================================================================================================
@pytest.mark.parametrize("f, a, b", PROBLEMS)
@pytest.mark.parametrize("xtol", [1e-4, 1e-8])
def test_bisection_agrees_with_scipy_bisect(f, a, b, xtol):
    # --- act --------------------------
    ours = Bisection().solve(f, a, b, xtol=xtol, max_fevals=200)
    twin = ScipySolver(scipy.optimize.bisect).solve(f, a, b, xtol=xtol, max_fevals=200)

    # --- assert -----------------------
    assert ours.status is twin.status is SolveStatus.CONVERGED
    assert abs(ours.x - twin.x) <= xtol
    # SciPy stops on a slightly different width rule, so its own call count is ours within 1; it also re-evaluates
    # both bounds, which the twin's count includes.
    assert abs((twin.n_fevals - 2) - ours.n_fevals) <= 1


@pytest.mark.parametrize("f, a, b", PROBLEMS)
def test_regula_falsi_iterates_reach_the_root_that_scipy_brentq_finds(f, a, b):
    # --- act --------------------------
    ours = RegulaFalsi().solve(f, a, b, xtol=1e-9, max_fevals=100, history_enabled=True)
    twin = ScipySolver(scipy.optimize.brentq).solve(f, a, b, xtol=1e-9, max_fevals=200)

    # --- assert -----------------------
    # Regula Falsi's iterates converge even where its interval does not, so the last iterate is what agrees.
    x_last, _ = ours.history[-1]
    assert twin.status is SolveStatus.CONVERGED
    assert abs(x_last - twin.x) <= 1e-8
