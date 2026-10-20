"""These tests assert that the individual steps of `Ford` follow its algorithm."""

import pytest

from sunnbear.solvers import Ford, FordVariant, SolveStatus
from tests.solvers.example_functions import cubic


def _quadratic(x: float) -> float:
    """Return ``x^2 - 2``, whose divided differences are ``f[u, v] = u + v``, so that the factor ``gamma`` of each
    method can be computed by hand."""
    return x * x - 2.0


def _cubic_with_a_local_maximum(x: float) -> float:
    """Return ``x^3 - 2x + 2``, whose root is near -1.77. Between the root and 0, f has a local maximum of about 3.09
    near -0.82, and the first iterate from ``[-3, 0]`` lands where f is above f(0) = 2, so that iterate raises ``|f|``.
    """
    return x**3 - 2.0 * x + 2.0


@pytest.mark.parametrize("variant", FordVariant)
def test_the_first_2_steps_are_unmodified_regula_falsi_steps(variant):
    """On `_quadratic` over ``[0, 2]``, every variant starts with 2 unmodified steps of the article's equation 3:

    - the first from ``s = 2``, the upper bound, and ``r = 0``, which gives 1;
    - ``f(1) = -1``, so 1 replaced the retained bound 0, and the second step is from ``s = 1`` and ``r = 2``, with the
      unscaled ``f(2) = 2``, which gives 4/3.
    """
    # --- act --------------------------
    history = Ford(variant=variant).solve(_quadratic, 0.0, 2.0, xtol=1e-9, max_fevals=60, history_enabled=True).history

    # --- assert -----------------------
    (x1, f1), (x2, _) = history[2:4]
    assert (x1, f1) == (1.0, -1.0)
    assert x2 == 4.0 / 3.0


@pytest.mark.parametrize(
    "variant, x3",
    [
        (FordVariant.METHOD_1, 10.0 / 7.0),  # gamma = (8/3) / 4 = 2/3
        (FordVariant.METHOD_3, 58.0 / 41.0),  # gamma = (8/3) / (10/3) = 4/5
        (FordVariant.METHOD_4, 38.0 / 27.0),  # gamma = (8/3) / 3 = 8/9
    ],
)
def test_each_method_scales_the_retained_f_by_its_own_gamma(variant, x3):
    """On `_quadratic` over ``[0, 2]``, the second iterate 4/3 lies on the same side of the root as the first iterate 1,
    so the third step scales ``f(2) = 2`` by the method's ``gamma``.

    With ``x_(i-1) = 2``, ``x_i = 1`` and ``x_(i+1) = 4/3``, and ``f[u, v] = u + v``, the numerator of ``gamma`` is
    ``7/3 + 10/3 - 3 = 8/3`` for every method, and the denominator is ``10/3 + 3 - 7/3 = 4`` for Method 1, ``10/3`` for
    Method 3, and ``3`` for Method 4. The third iterate is the zero of the secant through ``(4/3, -2/9)`` and
    ``(2, 2*gamma)``.
    """
    # --- act --------------------------
    history = Ford(variant=variant).solve(_quadratic, 0.0, 2.0, xtol=1e-9, max_fevals=60, history_enabled=True).history

    # --- assert -----------------------
    # Rounding moves the computed gamma, and the third iterate with it, by a few float spacings.
    assert history[4][0] == pytest.approx(x3, rel=1e-12)


@pytest.mark.parametrize("variant", FordVariant)
def test_a_gamma_that_is_not_positive_falls_back_to_0_5(variant):
    """On `_cubic_with_a_local_maximum` over ``[-3, 0]``, the first iterate has a function value above ``f(0) > 0``, so
    it replaces the upper bound, on the same side of the root, and the second step is modified.

    The numerator of ``gamma``, the slope at the first iterate of the quadratic through the 3 x-values, is negative, as
    f's own slope is there, while every method's denominator is positive; so every variant halves ``f(-3)``.
    """
    # --- arrange ----------------------
    a, b = -3.0, 0.0
    fa, fb = _cubic_with_a_local_maximum(a), _cubic_with_a_local_maximum(b)

    # --- act --------------------------
    history = (
        Ford(variant=variant)
        .solve(_cubic_with_a_local_maximum, a, b, xtol=1e-9, max_fevals=60, history_enabled=True)
        .history
    )

    # --- assert -----------------------
    (x1, f1), (x2, _) = history[2:4]
    assert f1 > fb > 0.0
    assert x2 == (x1 * (0.5 * fa) - a * f1) / (0.5 * fa - f1)


@pytest.mark.parametrize("variant", FordVariant)
def test_a_step_that_rounds_onto_the_most_recent_iterate_takes_the_factor_0_5(variant):
    """On `cubic` over ``[1, 2]`` at ``xtol = 0``, an iterate reaches a float next to the root, and the next 2 steps
    round onto that iterate.

    Each time, ``f[x_(i+1), x_i]`` is ``0 / 0``; the factor 0.5, taken at each of them, then moves the following step
    away from that iterate.
    """
    # --- act --------------------------
    result = Ford(variant=variant).solve(cubic, 1.0, 2.0, xtol=0.0, max_fevals=20, history_enabled=True)

    # --- assert -----------------------
    x_values = result.evaluated_x_values
    first_repeat = next(i for i in range(2, len(x_values) - 1) if x_values[i] == x_values[i + 1])
    iterate, next_x_1, next_x_2, next_x_3 = x_values[first_repeat : first_repeat + 4]
    assert iterate == next_x_1 == next_x_2 != next_x_3
    # At xtol = 0, the solve runs until its budget is spent; a division of 0 by 0 would have ended it as SOLVER_ERROR.
    assert result.status is SolveStatus.MAX_FEVALS


def test_a_denominator_of_method_1_that_rounds_to_0_takes_the_factor_0_5():
    """On a function with ``f(0) = -1`` and ``f(1.5) = 3e-16``, the first iterate ``x_(i+1)`` lies 1 float spacing below
    1.5. The test gives ``x_(i+1)`` a positive function value, so the second step is modified, and chooses that value
    so that Method 1's denominator rounds to exactly 0.

    `Ford` then takes ``gamma = 0.5`` and continues, until the evaluation budget ends the solve.
    """
    # --- arrange ----------------------
    a, b, fa, fb = 0.0, 1.5, -1.0, 3e-16
    x_ip1 = (b * fa - a * fb) / (fa - fb)
    assert x_ip1 == b - 2.0**-52
    # At this value of f(x_(i+1)), the rounded sum f[x_(i+1), a] + f[b, a] equals f[x_(i+1), b].
    f_ip1 = 3.9405267666248834e-18
    slope_ip1_i = (f_ip1 - fb) / (x_ip1 - b)
    slope_ip1_im1 = (f_ip1 - fa) / (x_ip1 - a)
    slope_i_im1 = (fb - fa) / (b - a)
    assert slope_ip1_im1 + slope_i_im1 - slope_ip1_i == 0.0
    function_values = {a: fa, b: fb, x_ip1: f_ip1}

    # --- act --------------------------
    result = Ford(variant=FordVariant.METHOD_1).solve(
        lambda x: function_values[x], a, b, xtol=0.0, max_fevals=3, history_enabled=True
    )

    # --- assert -----------------------
    assert result.evaluated_x_values == (a, b, x_ip1)
    # The budget ended the solve while it evaluated the third iterate; a division by 0 would have ended it as
    # SOLVER_ERROR before that.
    assert result.status is SolveStatus.MAX_FEVALS
