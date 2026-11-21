"""`follows_effect_of_c` checks, by evaluating a test problem's function, whether it applies ``c`` in a given way.

Each way of `EffectOfC` gives the derivative ``df/dc`` at ``c = 0`` a form in terms of ``f`` and ``df/dx``:

- shifting x by ``s*c``: ``df/dc = -s*df/dx``;
- scaling x by a factor ``k(c)``: ``df/dc = k'(0)*x*df/dx``;
- shifting the function's value by ``s*c``: ``df/dc = s``.

A way that moves x may also multiply the function's values by a positive factor ``g(c)``, which moves no root; it adds
a term ``g'(0)*f`` to ``df/dc``. The second Wilkinson polynomial, with its zeros at ``2^-(k + c)``, does so.

The check estimates the derivatives by central differences at ``c = 0``, at x-values across the interval, fits the
coefficients of the way's form to them, and accepts the way when the fit leaves no residual beyond the differences'
error. The fit weighs each x-value by the size of its difference in c, because a function's values can span many orders
of magnitude across its interval, as an exponential's do. Where a function is flat, or so steep that a difference drowns
in float64 rounding, the check cannot tell, and says so.
"""

import math

import numpy as np

from sunnbear._core.problems.core import CandidateTestProblem, EffectOfC

# _X_FRACTIONS places the x-values in the interval, away from its bounds and from its midpoint, where many functions
# have a root or an extremum.
_X_FRACTIONS = (0.13, 0.21, 0.29, 0.37, 0.43, 0.57, 0.63, 0.71, 0.79, 0.87)
# _STEP_FRACTION is the step of a central difference, as a fraction of the interval's width for x, and as a value of c.
_STEP_FRACTION = 1e-6
# _SIGNIFICANT_ULPS is the smallest difference, in float64 units of the larger function value, that a central
# difference must reach to count: a smaller difference is mostly rounding error.
_SIGNIFICANT_ULPS = 1e4
# _RESIDUAL_RTOL is the largest residual of the fit at an x-value, relative to the difference in c there, that still
# counts as a fit.
_RESIDUAL_RTOL = 1e-4
# _MIN_X_VALUES is the fewest x-values whose differences the check fits.
_MIN_X_VALUES = 4


def follows_effect_of_c(candidate: CandidateTestProblem, effect: EffectOfC) -> bool | None:
    """Return whether `candidate`'s function applies ``c`` as `effect` says, judged at x-values across its interval.

    Returns:
        True or False, or None where fewer than `_MIN_X_VALUES` x-values give significant differences.
    """
    # --- differences at each x-value --------
    a, b = candidate.a, candidate.b
    h_x = _STEP_FRACTION * (b - a)
    rows = []
    for fraction in _X_FRACTIONS:
        x = a + fraction * (b - a)
        try:
            f = candidate.xc_fun(x, 0.0)
            difference_c = _difference(candidate.xc_fun(x, _STEP_FRACTION), candidate.xc_fun(x, -_STEP_FRACTION))
            difference_x = _difference(candidate.xc_fun(x + h_x, 0.0), candidate.xc_fun(x - h_x, 0.0))
        except (ArithmeticError, ValueError):
            continue
        if math.isfinite(f) and difference_c is not None and difference_x is not None:
            rows.append((x, f, difference_c, difference_x))
    if len(rows) < _MIN_X_VALUES:
        return None

    # --- fit of the way's form --------------
    x, f, difference_c, difference_x = (np.array(column) for column in zip(*rows, strict=True))
    if effect is EffectOfC.SHIFTS_Y:
        terms = np.ones((len(rows), 1))
    elif effect is EffectOfC.SHIFTS_X:
        terms = np.column_stack([difference_x, f])
    else:
        terms = np.column_stack([x * difference_x, f])
    weights = 1.0 / np.abs(difference_c)
    coefficients, *_ = np.linalg.lstsq(terms * weights[:, np.newaxis], difference_c * weights, rcond=None)
    relative_residuals = np.abs(terms @ coefficients - difference_c) * weights
    is_fit = bool(np.max(relative_residuals) <= _RESIDUAL_RTOL)

    # --- a way that moves x must move it ----
    # without this, a pure factor on the values would fit the form of a way that moves x, with a coefficient of 0
    moves_x = effect is EffectOfC.SHIFTS_Y or bool(
        np.max(np.abs(terms[:, 0] * coefficients[0]) * weights) > _RESIDUAL_RTOL
    )
    return is_fit and moves_x


def _difference(value_above: float, value_below: float) -> float | None:
    """Return ``value_above - value_below``, or None where it is not finite or not well above float64 rounding.

    The difference is not divided by its step: the fit's coefficients absorb the steps, which are the same at every
    x-value.
    """
    difference = value_above - value_below
    noise = _SIGNIFICANT_ULPS * math.ulp(max(abs(value_above), abs(value_below)))
    if math.isfinite(difference) and abs(difference) > noise:
        return difference
    else:
        return None
