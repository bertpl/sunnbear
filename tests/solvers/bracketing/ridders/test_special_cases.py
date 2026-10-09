"""These tests assert that an exact zero ends a `Ridders` solve, and that on a kinked function only the
``commons_math`` variant misses the root."""

import pytest

from sunnbear.solvers import Ridders, RiddersVariant, SolveStatus


def _kinked_line(x: float) -> float:
    """Return a line through 0 at ``x = 0.41`` whose slope jumps from 1 to 1000 there; it is not smooth at its root."""
    if x < 0.41:
        return x - 0.41
    else:
        return 1000.0 * (x - 0.41)


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
