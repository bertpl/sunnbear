"""These tests assert that `Ridders` converges to a root of the test functions, and that each variant stops by its
own criterion."""

import itertools

import pytest

from sunnbear.solvers import Interval, Ridders, RiddersVariant, SolveStatus
from tests.solvers.example_functions import CONVERGENCE_TEST_CASES, cubic, ninth_power


@pytest.mark.parametrize("variant", RiddersVariant)
@pytest.mark.parametrize("f, a, b, root", CONVERGENCE_TEST_CASES)
def test_a_function_converges_to_its_root_except_commons_math_on_a_multiple_root(f, a, b, root, variant):
    """Every variant of `Ridders` returns an x-value within ``xtol`` of the root on each function of
    `CONVERGENCE_TEST_CASES`, except the commons_math variant on `ninth_power`.

    Near the multiple root of `ninth_power`, 2 successive iterates of the commons_math variant lie within ``xtol``
    of each other while both are still far from the root, so the variant stops there, as on the kinked function of
    `test_special_cases.py`.
    """
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    result = Ridders(variant=variant).solve(f, a, b, xtol=xtol, max_fevals=500)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    if variant is RiddersVariant.COMMONS_MATH and f is ninth_power:
        assert abs(result.x - root) > 100.0 * xtol
    else:
        assert abs(result.x - root) <= xtol


def test_the_commons_math_variant_stops_once_2_successive_iterates_lie_within_xtol():
    """The commons_math variant returns the last iterate, the first one that lies within ``xtol`` of the one before."""
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    result = Ridders(variant=RiddersVariant.COMMONS_MATH).solve(
        cubic, 1.0, 2.0, xtol=xtol, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    iterates = [x for x, _ in result.history[3::2]]  # Every second evaluation after the bounds is an iterate.
    assert result.x == iterates[-1]
    assert abs(iterates[-1] - iterates[-2]) <= xtol
    assert all(abs(x - x_previous) > xtol for x_previous, x in itertools.pairwise(iterates[:-1]))


def test_the_scipy_variant_stops_once_the_interval_is_narrower_than_xtol():
    """The scipy variant returns the last iterate, once the interval is narrower than ``xtol``."""
    # --- arrange ----------------------
    xtol = 1e-4

    # --- act --------------------------
    result = Ridders(variant=RiddersVariant.SCIPY).solve(
        cubic, 1.0, 2.0, xtol=xtol, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    assert result.x == result.history[-1][0]
    assert _final_interval(result.history).width < xtol


def test_the_bracketing_solver_variant_stops_once_the_interval_is_at_most_2_xtol_wide():
    """The bracketing_solver variant returns the midpoint of the final interval, which is at most ``2 * xtol``
    wide."""
    # --- arrange ----------------------
    xtol = 1e-4

    # --- act --------------------------
    result = Ridders(variant=RiddersVariant.BRACKETING_SOLVER).solve(
        cubic, 1.0, 2.0, xtol=xtol, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    interval = _final_interval(result.history)
    assert interval.width <= 2.0 * xtol
    assert result.x == interval.midpoint


def test_the_limit_on_the_step_lets_the_scipy_variant_stop_where_the_interval_would_only_halve():
    """On ``x^3 - x - 0.801``, SciPy's limit on the step lets the scipy variant stop after as few evaluations as the
    commons_math variant, while the bracketing_solver variant, whose interval only halves near the root, needs far
    more."""

    # --- arrange ----------------------
    def f(x: float) -> float:
        return x**3 - x - 0.801

    # --- act --------------------------
    n_fevals = {
        variant: Ridders(variant=variant).solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=100).n_fevals
        for variant in RiddersVariant
    }

    # --- assert -----------------------
    assert n_fevals == {RiddersVariant.COMMONS_MATH: 12, RiddersVariant.SCIPY: 12, RiddersVariant.BRACKETING_SOLVER: 66}


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _final_interval(history: list[tuple[float, float]]) -> Interval:
    """Return the interval that remains after splitting the initial interval at each later point of ``history``."""
    (a, fa), (b, fb), *evaluations = history
    interval = Interval.from_interval_bounds(a, b, fa, fb)
    for x, fx in evaluations:
        interval = interval.split_at(x, fx)
    return interval
