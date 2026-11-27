"""`follows_effect_of_c` checks, by evaluating a test problem's function, whether it applies ``c`` in a given way.

For each way of `EffectOfC`, the derivative ``df/dc`` at ``c = 0`` takes a known form in terms of ``f`` and
``df/dx``:

- shifting x by ``s*c``: ``df/dc = -s*df/dx``;
- scaling x by a factor ``k(c)``: ``df/dc = k'(0)*x*df/dx``;
- shifting the function's value by ``s*c``: ``df/dc = s``.

A formula whose ``c`` moves x may also multiply the function's values by a positive factor ``g(c)``, which moves no
root; the factor adds a term ``g'(0)*f`` to ``df/dc``.

The check runs in these steps:

- it estimates the derivatives by central differences at ``c = 0``, at x-values across the interval;
- it fits the coefficients of the way's form of ``df/dc`` to the differences, weighting each x-value by the inverse of
  its difference in c: a function's values can span many orders of magnitude across its interval, as an exponential's
  do, so each residual must count relative to the difference at its x-value;
- it accepts the way when every residual, relative to its difference in c, stays within `_RESIDUAL_RTOL`.

The check runs these steps at each scale of `_STEP_SCALES`, from the largest down, and accepts the way at the first
scale at which every residual stays within `_RESIDUAL_RTOL`. A function with a structure finer than the largest
difference steps, such as a ripple or a tooth, gives differences that the way's form cannot fit at those steps, but can
at smaller ones.

Where too few x-values give a difference well above float64 rounding error at every scale, as for a flat function or
one whose values are very large, the check cannot decide and returns None.
"""

import math

import numpy as np

from sunnbear._core.problems.core import CandidateTestProblem, EffectOfC

# _X_FRACTIONS places the x-values in the interval, away from its bounds and from its midpoint, where many functions
# have a root or an extremum.
_X_FRACTIONS = (0.13, 0.21, 0.29, 0.37, 0.43, 0.57, 0.63, 0.71, 0.79, 0.87)
# _X_STEP_FRACTION is the step in x of a central difference, as a fraction of the interval's width.
_X_STEP_FRACTION = 1e-6
# _C_STEP is the step in c of a central difference. It is large enough that rounding in the function's evaluation stays
# far below _RESIDUAL_RTOL also where c moves x only by c/n^2 at a degree n above 1000, and small enough that the
# differences' truncation error does too.
_C_STEP = 1e-4
# _MIN_SIGNIFICANT_ULPS is the smallest difference, in float64 units of the larger function value, that a central
# difference must reach to count: a smaller difference is mostly rounding error.
_MIN_SIGNIFICANT_ULPS = 1e4
# _RESIDUAL_RTOL is the largest residual of the fit at an x-value, relative to the difference in c there, that still
# counts as a fit.
_RESIDUAL_RTOL = 1e-4
# _MIN_X_VALUES is the smallest number of x-values with significant differences that the check needs to decide.
_MIN_X_VALUES = 4
# _STEP_SCALES multiply _X_STEP_FRACTION and _C_STEP, 1 scale per pass of the check, from the largest down.
_STEP_SCALES = (1.0, 1e-2, 1e-4)


def follows_effect_of_c(candidate: CandidateTestProblem, effect_of_c: EffectOfC) -> bool | None:
    """Return whether `candidate`'s function applies ``c`` as `effect_of_c` says, judged across its interval.

    Returns:
        True if every residual stays within `_RESIDUAL_RTOL` at any scale of `_STEP_SCALES`; otherwise False if at
        least 1 scale decides, and None if fewer than `_MIN_X_VALUES` x-values give significant differences at every
        scale.
    """
    is_decided = False
    for step_scale in _STEP_SCALES:
        result = _follows_effect_of_c_at_step_scale(candidate, effect_of_c, step_scale)
        if result is True:
            return True
        elif result is False:
            is_decided = True
    if is_decided:
        return False
    else:
        return None


def _follows_effect_of_c_at_step_scale(
    candidate: CandidateTestProblem, effect_of_c: EffectOfC, step_scale: float
) -> bool | None:
    """Return the check's verdict with its steps in x and c multiplied by `step_scale`, or None if it cannot decide."""
    # --- differences at each x-value ------------
    a, b = candidate.a, candidate.b
    h_x = step_scale * _X_STEP_FRACTION * (b - a)
    h_c = step_scale * _C_STEP
    rows = []
    for fraction in _X_FRACTIONS:
        x = a + fraction * (b - a)
        try:
            f = candidate.xc_fun(x, 0.0)
            difference_c = _significant_difference(candidate.xc_fun(x, h_c), candidate.xc_fun(x, -h_c))
            difference_x = _significant_difference(candidate.xc_fun(x + h_x, 0.0), candidate.xc_fun(x - h_x, 0.0))
        except (ArithmeticError, ValueError):
            continue
        if math.isfinite(f) and difference_c is not None and difference_x is not None:
            rows.append((x, f, difference_c, difference_x))
    if len(rows) < _MIN_X_VALUES:
        return None

    # --- fit of the way's form ------------------
    x, f, difference_c, difference_x = (np.array(column) for column in zip(*rows, strict=True))
    if effect_of_c is EffectOfC.SHIFTS_Y:
        terms = np.ones((len(rows), 1))
    elif effect_of_c is EffectOfC.SHIFTS_X:
        terms = np.column_stack([difference_x, f])
    else:
        terms = np.column_stack([x * difference_x, f])
    weights = 1.0 / np.abs(difference_c)
    coefficients, *_ = np.linalg.lstsq(terms * weights[:, np.newaxis], difference_c * weights, rcond=None)
    relative_residuals = np.abs(terms @ coefficients - difference_c) * weights
    is_fit = bool(np.max(relative_residuals) <= _RESIDUAL_RTOL)

    # --- a way that moves x needs its x term ----
    # without this check, a function that c only multiplies by a factor g(c) would fit the form of a way that moves x,
    # with a coefficient of 0 on the term that moves x
    if effect_of_c is EffectOfC.SHIFTS_Y:
        has_x_term_where_needed = True
    else:
        has_x_term_where_needed = bool(np.max(np.abs(terms[:, 0] * coefficients[0]) * weights) > _RESIDUAL_RTOL)
    return is_fit and has_x_term_where_needed


def _significant_difference(value_above: float, value_below: float) -> float | None:
    """Return ``value_above - value_below``, or None where it is not finite or not well above float64 rounding.

    The difference is not divided by its step: the steps are the same at every x-value, so they only scale the fit's
    coefficients.
    """
    difference = value_above - value_below
    min_significant_difference = _MIN_SIGNIFICANT_ULPS * math.ulp(max(abs(value_above), abs(value_below)))
    if math.isfinite(difference) and abs(difference) > min_significant_difference:
        return difference
    else:
        return None
