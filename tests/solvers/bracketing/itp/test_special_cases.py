"""These tests assert that a root at the midpoint ends an `ITP` solve after 1 iteration, and that rounding errors can
make `ITP` exceed its bound on the iteration count."""

import pytest

from sunnbear.solvers import ITP, ITPVariant, SolveStatus

from .paper_problems import N_BISECTION, TABLE_1, XTOL


@pytest.mark.parametrize(
    "name, variant",
    [
        ("polynomial_2", ITPVariant.PAPER_PSEUDOCODE),
        ("step_function", ITPVariant.PAPER_EXPERIMENTS),
    ],
)
def test_rounding_errors_can_push_either_variant_past_n_max(name, variant):
    """Without slack, rounding errors can make `ITP` take 1 iteration more than ``n_max = 34``, in either variant."""
    # --- arrange ----------------------
    problem = next(problem for problem in TABLE_1 if problem.name == name)

    # --- act --------------------------
    result = ITP(n_slack=0, variant=variant).solve(problem.f, problem.a, problem.b, xtol=XTOL, max_fevals=100)

    # --- assert -----------------------
    assert result.n_fevals - 2 == N_BISECTION + 1


@pytest.mark.parametrize("variant", ITPVariant)
def test_a_root_at_the_midpoint_is_found_in_1_iteration(variant):
    """On a line through 0 over ``[-1, 1]``, the interpolation point is the midpoint, which is the root."""
    # --- act --------------------------
    result = ITP(n_slack=0, variant=variant).solve(lambda x: x, -1.0, 1.0, xtol=XTOL, max_fevals=10)

    # --- assert -----------------------
    assert (result.x, result.status, result.n_fevals) == (0.0, SolveStatus.CONVERGED, 3)
