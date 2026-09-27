"""Real `Bisection` runs spend exactly `n_bisection_fevals` inside the range that `compute_xtol_range` returns.

`max_fevals_for` returns the evaluation budget derived from that count.
"""

import pytest

from sunnbear._core.benchmark.tolerances import N_BISECTION_FEVALS, compute_xtol_range, max_fevals_for
from sunnbear.solvers import Bisection, SolveStatus
from tests.solvers.example_functions import cubic


# ==================================================================================================
#  compute_xtol_range
# ==================================================================================================
@pytest.mark.parametrize("a, b", [(1.0, 2.0), (0.0, 4.0), (1.3, 1.4)])  # Each interval holds the cubic's root.
@pytest.mark.parametrize("n_bisection_fevals", [3, 10, N_BISECTION_FEVALS])
@pytest.mark.parametrize(
    "edge, xtol_factor, n_fevals_offset",
    [
        ("lower", 1.01, 0),  # just inside the range
        ("upper", 0.99, 0),
        ("lower", 0.99, 1),  # just outside: 1 more step below the range, 1 fewer above it
        ("upper", 1.01, -1),
    ],
)
def test_bisection_takes_exactly_n_bisection_fevals_inside_the_xtol_range_only(
    a, b, n_bisection_fevals, edge, xtol_factor, n_fevals_offset
):
    """Bisection takes exactly `n_bisection_fevals` for an `xtol` just inside the range, 1 more or 1 fewer just outside.

    The 1 % margins keep `xtol` away from each edge, where the rounding of the midpoints can change the step
    count when the interval bounds are not exact binary fractions, as for [1.3, 1.4].
    """
    # --- arrange ----------------------
    xtol_lower, xtol_upper = compute_xtol_range(a=a, b=b, n_bisection_fevals=n_bisection_fevals)
    xtol = xtol_factor * (xtol_lower if edge == "lower" else xtol_upper)

    # --- act --------------------------
    result = Bisection().solve(cubic, a, b, xtol=xtol, max_fevals=max_fevals_for(n_bisection_fevals=n_bisection_fevals))

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals == n_bisection_fevals + n_fevals_offset


def test_compute_xtol_range_matches_its_closed_form_on_a_known_interval():
    """On [-1, 3] with 5 evaluations, the range is `(0.25, 0.5)`: the width 4 times `2^(1 - 5)`, and twice that."""
    # --- act --------------------------
    xtol_range = compute_xtol_range(a=-1.0, b=3.0, n_bisection_fevals=5)

    # --- assert -----------------------
    assert xtol_range == (0.25, 0.5)


@pytest.mark.parametrize(
    "a, b, n_bisection_fevals, message",
    [
        (1.0, 1.0, 40, "a < b"),
        (2.0, 1.0, 40, "a < b"),
        (1.0, 2.0, 1, "at least 2"),
    ],
)
def test_compute_xtol_range_rejects_an_ill_ordered_interval_or_too_few_evaluations(a, b, n_bisection_fevals, message):
    """`compute_xtol_range` raises `ValueError` when `a >= b` or `n_bisection_fevals` is below 2."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        compute_xtol_range(a=a, b=b, n_bisection_fevals=n_bisection_fevals)


# ==================================================================================================
#  max_fevals_for
# ==================================================================================================
def test_the_default_evaluation_budget_is_160_evaluations():
    """The default `n_bisection_fevals` gives a budget of 160 evaluations."""
    # --- act / assert -----------------
    assert max_fevals_for(n_bisection_fevals=N_BISECTION_FEVALS) == 160


def test_max_fevals_for_rejects_too_few_evaluations():
    """`max_fevals_for` raises `ValueError` when `n_bisection_fevals` is below 2."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="at least 2"):
        max_fevals_for(n_bisection_fevals=1)
