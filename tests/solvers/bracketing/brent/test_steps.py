"""These tests assert that the individual steps of both variants of `Brent` follow their algorithms."""

import pytest

from sunnbear.solvers import Brent, BrentVariant
from tests.solvers.example_functions import cubic


@pytest.mark.parametrize("variant", BrentVariant)
def test_the_first_step_is_a_secant_step_from_the_bound_with_the_smaller_abs_f(variant):
    """On `cubic` over ``[1, 2]``, ``f(1) = -1`` and ``f(2) = 5``, so the first step of both variants is the secant step
    from 1 to 1 + 1/6."""
    # --- act --------------------------
    result = Brent(variant=variant).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[2][0] == pytest.approx(1.0 + 1.0 / 6.0, abs=1e-15)


@pytest.mark.parametrize(
    "variant, x_after_second_step",
    [
        (BrentVariant.HYPERBOLIC, 937.0 / 696.0),
        (BrentVariant.INVERSE_QUADRATIC, 180517.0 / 131586.0),
    ],
)
def test_the_second_step_interpolates_through_3_x_values_by_the_formula_of_the_variant(variant, x_after_second_step):
    """On `cubic` over ``[1, 2]``, the second step interpolates through ``a = 1``, ``b = 7/6`` and ``c = 2``, and each
    variant reaches the zero of its own interpolation: 937/696 for the hyperbolic one, 180517/131586 for the inverse
    quadratic one.

    With ``f(7/6) = -125/216``, the divided differences of the hyperbolic step are ``f[a, b] = 91/36`` and
    ``f[c, b] = 241/36``, so its step ``-fb*(fc - fa) / (fc*f[a, b] - fa*f[c, b])`` from ``b`` is 125/696.
    """
    # --- act --------------------------
    result = Brent(variant=variant).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.history[3][0] == pytest.approx(x_after_second_step, abs=1e-15)
