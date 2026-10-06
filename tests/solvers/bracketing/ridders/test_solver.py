"""These tests assert that `Ridders` takes the steps of Ridders' paper, and stops by the stopping criterion of its
variant."""

import itertools
import math

import pytest

from sunnbear.solvers import Interval, Ridders, RiddersVariant, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic


def _kinked_line(x: float) -> float:
    """Return a line through 0 at ``x = 0.41`` whose slope jumps from 1 to 1000 there; it is not smooth at its root."""
    if x < 0.41:
        return x - 0.41
    else:
        return 1000.0 * (x - 0.41)


# ==================================================================================================
#  The steps
# ==================================================================================================
@pytest.mark.parametrize("variant", RiddersVariant)
def test_the_first_iteration_reproduces_the_example_of_the_paper(variant):
    """On the paper's example, ``x^3 - x - 5`` on ``[-1, 3]``, the first iterate is 1.9128..., and the next interval
    is ``[1, 1.9128...]``, whose midpoint is the next point evaluated."""
    # --- act --------------------------
    result = Ridders(variant=variant).solve(
        lambda x: x**3 - x - 5.0, -1.0, 3.0, xtol=1e-10, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    (x1, f1), (x3, _), (x1_next, _) = result.history[2:5]
    assert (x1, f1) == (1.0, -5.0)
    assert x3 == 1.0 + 2.0 * 1.0 / math.sqrt(1.0 - 19.0 / -5.0)  # f1 / f0 = 1 and f2 / f0 = -19 / 5
    assert 1.9128 < x3 < 1.9129  # The paper prints the iterate as 1.9128..., truncated.
    assert x1_next == 0.5 * (1.0 + x3)


@pytest.mark.parametrize("variant", RiddersVariant)
@pytest.mark.parametrize(
    "f, root, n_fevals",
    [
        (lambda x: x - 0.5, 0.5, 3),  # The midpoint is the root.
        (lambda x: x - 0.3, 0.3, 4),  # The first iterate is the root, as on every straight line.
    ],
)
def test_an_exact_zero_ends_the_solve_at_that_point(f, root, n_fevals, variant):
    """An evaluation that returns exactly 0, at a midpoint or at an iterate, ends the solve in every variant."""
    # --- act --------------------------
    result = Ridders(variant=variant).solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (root, SolveStatus.CONVERGED, n_fevals)


@pytest.mark.parametrize("variant", RiddersVariant)
@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f, variant):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, every variant converges within ``xtol`` of
    the root."""
    # --- act --------------------------
    result = Ridders(variant=variant).solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10


# ==================================================================================================
#  The 3 stopping criteria
# ==================================================================================================
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


@pytest.mark.parametrize("variant", RiddersVariant)
def test_on_a_kinked_function_only_the_commons_math_variant_misses_the_root(variant):
    """On a function that is not smooth at its root, the commons_math variant stops more than ``xtol`` from the root,
    while the other 2 variants stay within ``xtol``."""
    # --- arrange ----------------------
    xtol = 1e-6

    # --- act --------------------------
    result = Ridders(variant=variant).solve(_kinked_line, 0.0, 1.0, xtol=xtol, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    if variant is RiddersVariant.COMMONS_MATH:
        assert abs(result.x - 0.41) > 100.0 * xtol
    else:
        assert abs(result.x - 0.41) <= xtol


def test_an_unknown_variant_is_rejected():
    """A value that is not a `RiddersVariant` raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="'original'"):
        Ridders(variant="original")  # ty: ignore[invalid-argument-type] — the test passes a wrong value


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`Ridders` is named ``ridders``, at version 1, and its arithmetic, square roots included, is flop-counted."""
    # --- act --------------------------
    result = Ridders(variant=RiddersVariant.SCIPY).solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Ridders.name, Ridders.version) == ("ridders", 1)
    assert result.flop_counts.SQRT > 0


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
