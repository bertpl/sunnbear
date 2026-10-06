"""These tests assert that `Ridders` takes the steps of Ridders' paper, and stops by the stopping criterion of its
config."""

import itertools
import math
import typing

import pytest

from sunnbear.solvers import Ridders, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic

# The parametrized tests run under every stopping criterion that the annotation of `Ridders.__init__` names.
_STOPPING_CRITERIA = typing.get_args(typing.get_type_hints(Ridders.__init__)["stopping_criterion"])


def _kinked_line(x: float) -> float:
    """Return a line through 0 at ``x = 0.41`` whose slope jumps from 1 to 1000 there; it is not smooth at its root."""
    if x < 0.41:
        return x - 0.41
    else:
        return 1000.0 * (x - 0.41)


# ==================================================================================================
#  The steps
# ==================================================================================================
@pytest.mark.parametrize("stopping_criterion", _STOPPING_CRITERIA)
def test_the_first_iteration_reproduces_the_example_of_the_paper(stopping_criterion):
    """On the paper's example, ``x^3 - x - 5`` on ``[-1, 3]``, the first iterate is 1.9128..., and the next interval
    is ``[1, 1.9128...]``, whose midpoint is the next point evaluated."""
    # --- act --------------------------
    result = Ridders(stopping_criterion=stopping_criterion).solve(
        lambda x: x**3 - x - 5.0, -1.0, 3.0, xtol=1e-10, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    (x1, f1), (x3, _), (x1_next, _) = result.history[2:5]
    assert (x1, f1) == (1.0, -5.0)
    assert x3 == 1.0 + 2.0 * 1.0 / math.sqrt(1.0 - 19.0 / -5.0)  # f1 / f0 = 1 and f2 / f0 = -19 / 5
    assert 1.9128 < x3 < 1.9129  # The paper prints the iterate as 1.9128..., truncated.
    assert x1_next == 0.5 * (1.0 + x3)


@pytest.mark.parametrize("stopping_criterion", _STOPPING_CRITERIA)
@pytest.mark.parametrize(
    "f, root, n_fevals",
    [
        (lambda x: x - 0.5, 0.5, 3),  # The midpoint is the root.
        (lambda x: x - 0.3, 0.3, 4),  # The first iterate is the root, as on every straight line.
    ],
)
def test_an_exact_zero_ends_the_solve_at_that_point(f, root, n_fevals, stopping_criterion):
    """An evaluation that returns exactly 0, at a midpoint or at an iterate, ends the solve under both criteria."""
    # --- act --------------------------
    result = Ridders(stopping_criterion=stopping_criterion).solve(f, 0.0, 1.0, xtol=1e-12, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (root, SolveStatus.CONVERGED, n_fevals)


@pytest.mark.parametrize("stopping_criterion", _STOPPING_CRITERIA)
@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f, stopping_criterion):
    """On `cubic` in both interval orientations, `Ridders` converges within ``xtol`` of the root."""
    # --- act --------------------------
    result = Ridders(stopping_criterion=stopping_criterion).solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10


# ==================================================================================================
#  The 2 stopping criteria
# ==================================================================================================
def test_the_original_criterion_stops_once_2_successive_iterates_lie_within_xtol():
    """The original criterion returns the last iterate, the first one that lies within ``xtol`` of the one before."""
    # --- arrange ----------------------
    xtol = 1e-10

    # --- act --------------------------
    result = Ridders(stopping_criterion="original").solve(
        cubic, 1.0, 2.0, xtol=xtol, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    iterates = [x for x, _ in result.history[3::2]]  # Every second evaluation after the bounds is an iterate.
    assert result.x == iterates[-1]
    assert abs(iterates[-1] - iterates[-2]) <= xtol
    assert all(abs(x - x_previous) > xtol for x_previous, x in itertools.pairwise(iterates[:-1]))


def test_the_corrected_criterion_stops_once_the_interval_is_at_most_2_xtol_wide():
    """The corrected criterion returns the midpoint of the final interval, which is at most ``2 * xtol`` wide."""
    # --- arrange ----------------------
    xtol = 1e-4

    # --- act --------------------------
    result = Ridders(stopping_criterion="corrected").solve(
        cubic, 1.0, 2.0, xtol=xtol, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    # The final interval lies between the last iterate and the closest earlier point on the other side of the root.
    x_last, f_last = result.history[-1]
    x_other = min((x for x, fx in result.history if (fx < 0.0) != (f_last < 0.0)), key=lambda x: abs(x - x_last))
    assert abs(x_last - x_other) <= 2.0 * xtol
    assert result.x == 0.5 * (min(x_last, x_other) + max(x_last, x_other))


def test_on_a_kinked_function_only_the_corrected_criterion_returns_a_root_within_xtol():
    """On a function that is not smooth at its root, the original criterion stops sooner but more than ``xtol`` from
    the root, while the corrected criterion stays within ``xtol``."""
    # --- arrange ----------------------
    xtol = 1e-6

    # --- act --------------------------
    original = Ridders(stopping_criterion="original").solve(_kinked_line, 0.0, 1.0, xtol=xtol, max_fevals=100)
    corrected = Ridders(stopping_criterion="corrected").solve(_kinked_line, 0.0, 1.0, xtol=xtol, max_fevals=100)

    # --- assert -----------------------
    assert original.status is corrected.status is SolveStatus.CONVERGED
    assert abs(original.x - 0.41) > 100.0 * xtol
    assert abs(corrected.x - 0.41) <= xtol
    assert original.n_fevals < corrected.n_fevals


def test_an_unknown_stopping_criterion_is_rejected():
    """A stopping criterion other than ``"original"`` or ``"corrected"`` raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="'modified'"):
        Ridders(stopping_criterion="modified")  # ty: ignore[invalid-argument-type] — the test passes a wrong value


# ==================================================================================================
#  Identity and cost
# ==================================================================================================
def test_identity_and_that_its_arithmetic_is_counted():
    """`Ridders` is named ``ridders``, at version 1, and its arithmetic, square roots included, is flop-counted."""
    # --- act --------------------------
    result = Ridders(stopping_criterion="original").solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Ridders.name, Ridders.version) == ("ridders", 1)
    assert result.flop_counts.SQRT > 0
