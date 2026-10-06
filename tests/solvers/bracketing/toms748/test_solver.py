"""These tests assert that `TOMS748` reproduces the results of the authors' code and paper, and stops within ``xtol``
of a root."""

import sys

import pytest

from sunnbear.solvers import TOMS748, SolveStatus
from tests.solvers.bracketing.toms748.paper_problems import PAPER_PROBLEMS, PaperProblem
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic

_MACHEPS = sys.float_info.epsilon


# ==================================================================================================
#  The authors' results
# ==================================================================================================
@pytest.mark.parametrize("problem", PAPER_PROBLEMS, ids=str)
def test_k_2_reproduces_the_root_that_the_authors_code_computes(problem: PaperProblem):
    """With ``k = 2`` and ``tol = 0``, the setting of the authors' test runs, `TOMS748` returns the root that the
    authors' code prints, within a relative 1e-13, the precision of its 14 printed digits."""
    # --- arrange ----------------------
    a, b = problem.interval

    # --- act --------------------------
    # An xtol of 0 makes tol 0.
    result = TOMS748(k=2).solve(problem.f, a, b, xtol=0.0, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.x == pytest.approx(problem.root, rel=1e-13, abs=0.0)


@pytest.mark.parametrize(
    "k, n_digits, paper_total",
    [
        (1, 7, 2696),
        (1, 10, 2835),
        (1, 15, 2908),
        (1, None, 2950),
        (2, 7, 2650),
        (2, 10, 2786),
        (2, 15, 2859),
        (2, None, 2884),
    ],
)
def test_the_total_evaluation_count_lies_within_1_1_percent_of_the_papers_table_ii(k, n_digits, paper_total):
    """Over the problems in `PAPER_PROBLEMS`, the total evaluation count lies within 1.1 % of the paper's Table II,
    for each ``k`` and for each of the paper's tolerances ``tol = 10^-n_digits`` and ``tol = 0``.

    The paper's counts include the 2 evaluations at the interval bounds, and come from a machine whose relative
    precision was 1.907e-16, not 2^-52.
    """
    # --- arrange / act ----------------
    total = sum(
        _TOMS748WithTol(k=k, n_digits=n_digits).solve(problem.f, *problem.interval, xtol=0.0, max_fevals=100).n_fevals
        for problem in PAPER_PROBLEMS
    )

    # --- assert -----------------------
    assert abs(total - paper_total) <= 0.011 * paper_total


# ==================================================================================================
#  The steps
# ==================================================================================================
@pytest.mark.parametrize("k", [1, 2])
def test_the_first_step_is_a_secant_step(k):
    """On `cubic` over ``[1, 2]``, ``f(1) = -1`` and ``f(2) = 5``, so the first step is the secant step to 1 + 1/6."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(1.0 + 1.0 / 6.0, abs=1e-15)


@pytest.mark.parametrize("k", [1, 2])
def test_an_exact_zero_ends_the_solve_at_that_point(k):
    """On a line, the first secant step lands on the root, where the function is exactly 0, and the solve returns the
    root after 3 evaluations."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(lambda x: x - 0.25, 0.0, 1.0, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.25, SolveStatus.CONVERGED, 3)


@pytest.mark.parametrize("k", [1, 2])
def test_a_point_close_to_a_bound_moves_to_the_margin_and_the_lower_bound_is_returned(k):
    """On ``x - 1e-9`` over ``[0, 1]`` with ``xtol = 1e-4``, the secant point 1e-9 lies within ``0.7 * stop_width``
    of the lower bound, so the secant point moves to ``0.7 * stop_width``. The interval ``[0, 0.7 * stop_width]``
    that remains meets the stopping criterion, and the solve returns its lower bound 0."""
    # --- arrange ----------------------
    xtol = 1e-4
    # The lower bound has the smaller |f|, and lies at 0, so stop_width is 2 * tol.
    stop_width = 2.0 * (0.5 * xtol - 2.0 * _MACHEPS * 1.0)

    # --- act --------------------------
    result = TOMS748(k=k).solve(lambda x: x - 1e-9, 0.0, 1.0, xtol=xtol, max_fevals=10, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == 0.7 * stop_width
    assert (result.x, result.status, result.n_fevals) == (0.0, SolveStatus.CONVERGED, 3)


@pytest.mark.parametrize(
    "fa, fb, fd, expected",
    [
        # The points (0, -1), (1, 1) and (2, 3) lie on the line 2x - 1, so f[a, b, d] = 0.
        (-1.0, 1.0, 3.0, 0.5),
        # The quadratic through a = 0, b = 1 and d = 2 is p(x) = -1 - x - x(x - 1); the steps start at a, where
        # p'(0) = -1 + 1 = 0.
        (-1.0, -2.0, -5.0, -1.0),
    ],
    ids=["points_on_a_line", "zero_derivative"],
)
def test_newton_quadratic_zero_returns_the_zero_of_the_line_through_a_and_b_when_newton_steps_cannot_be_taken(
    fa, fb, fd, expected
):
    """When ``f[a, b, d] = 0``, or when a Newton step meets a zero derivative of the quadratic, Newton-Quadratic
    returns the zero of the line through ``a`` and ``b``."""
    # --- act / assert -----------------
    assert TOMS748._newton_quadratic_zero(0.0, 1.0, 2.0, fa, fb, fd, 2) == expected


# ==================================================================================================
#  Accuracy
# ==================================================================================================
@pytest.mark.parametrize("k", [1, 2])
@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f, k):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `TOMS748` returns a point within
    ``xtol`` of the root."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10


def test_an_initial_interval_narrower_than_stop_width_returns_its_lower_bound_without_an_interior_evaluation():
    """An initial interval of width 1e-12, below ``xtol = 1e-10``, already meets the stopping criterion, so the solve
    returns its lower bound after the 2 evaluations at its bounds."""
    # --- act --------------------------
    result = TOMS748(k=1).solve(cubic, CUBIC_ROOT - 5e-13, CUBIC_ROOT + 5e-13, xtol=1e-10, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (CUBIC_ROOT - 5e-13, SolveStatus.CONVERGED, 2)


def test_an_xtol_below_the_machine_precision_sets_tol_to_0():
    """An ``xtol`` of 1e-17 on ``[1, 2]`` would make ``tol`` negative; with ``tol = 0``, the solve still converges,
    within ``stop_width = 4 * macheps * |u|`` of the root."""
    # --- act --------------------------
    result = TOMS748(k=1).solve(cubic, 1.0, 2.0, xtol=1e-17, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 4.0 * _MACHEPS * 2.0


# ==================================================================================================
#  Validation, identity and cost
# ==================================================================================================
def test_a_k_other_than_1_or_2_is_rejected():
    """A ``k`` other than 1 or 2 raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="3"):
        TOMS748(k=3)


def test_identity_and_that_its_arithmetic_is_counted():
    """`TOMS748` is named ``toms748``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = TOMS748(k=1).solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (TOMS748.name, TOMS748.version) == ("toms748", 1)
    assert result.flop_counts.total_count() > 0


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _TOMS748WithTol(TOMS748):
    """`_TOMS748WithTol` is `TOMS748` with the paper's ``tol`` given directly, as the authors' driver gives it."""

    def __init__(self, *, k: int, n_digits: int | None) -> None:
        """Configure ``k`` and the fixed ``tol = 10^-n_digits``, or ``tol = 0`` for ``None``."""
        super().__init__(k=k)
        self._tol = self._tol_as_the_driver_computes_it(n_digits)

    def _get_tol(self, xtol: float, a0: float, b0: float) -> float:
        """Return the fixed ``tol``."""
        return self._tol

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _tol_as_the_driver_computes_it(n_digits: int | None) -> float:
        """Return ``10^-n_digits`` by repeated division, as the subroutine ``TOLE`` of the authors' code computes it,
        or 0 for ``None``."""
        if n_digits is None:
            return 0.0
        else:
            tol = 1.0
            for _ in range(n_digits):
                tol = tol / 10.0
            return tol
