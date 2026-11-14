"""This module holds what the named polynomial formulas share: the degrees that they sweep and their intervals.

Each of the formulas is a Jacobi polynomial ``P_n^(alpha, beta)`` up to a constant factor, so 1 rule gives the
interval of all of them, from the degree and the 2 parameters of that Jacobi polynomial.
"""

import itertools
import math

from sunnbear._core.problems.core import ParamTable

# Every formula sweeps these degrees: each degree up to 32, then an even and an odd degree at each power of 2 up to
# 1024. An even and an odd degree differ in their intervals (`jacobi_interval_bounds`), so the high degrees come in
# pairs too.
SWEPT_DEGREES = (
    *(float(degree) for degree in range(1, 33)),
    *(2.0**exponent + parity for exponent in range(6, 11) for parity in (0.0, 1.0)),
)


def is_valid_degree(n: float) -> bool:
    """Return whether `n` is an integer of at least 1."""
    return n == int(n) and n >= 1


def degree_sweep_recipe(param_names: tuple[str, ...], *values_per_other_param: tuple[float, ...]) -> ParamTable:
    """Return the recipe that combines each degree of `SWEPT_DEGREES` with each combination of the other values.

    Args:
        param_names: The formula's parameter names, of which the first names the degree.
        values_per_other_param: The other values: those of each parameter after the degree, in the order of
            `param_names`.
    """
    return ParamTable(names=param_names, rows=tuple(itertools.product(SWEPT_DEGREES, *values_per_other_param)))


def jacobi_interval_bounds(n: float, alpha: float, beta: float) -> tuple[float, float]:
    """Return the interval of the Jacobi polynomial ``P_n^(alpha, beta)``, which holds an odd number of its zeros.

    The polynomial has `n` zeros, all inside ``[-1, 1]``:

    - an odd `n` gets ``[-1, 1]``, which holds every zero;
    - an even `n` gets ``[a, 1]``, which leaves out the lowest zero: the lower bound ``a`` lies between the 2 lowest
      zeros.

    With ``x = -cos(theta)``, the 2 lowest zeros lie near ``theta = j_1/N`` and ``theta = j_2/N``, where
    ``N = n + (alpha + beta + 1)/2`` and ``j_1`` and ``j_2`` are the first 2 positive zeros of the Bessel function of
    order `beta`.

    McMahon's approximation puts the midpoint of ``j_1`` and ``j_2`` at ``(1.25 + beta/2)*pi``, so the lower bound is
    ``-cos(theta)`` at ``theta = (1.25 + beta/2)*pi/N``.

    The rule is an approximation, with no proof that it holds for every `n`, `alpha` and `beta`, so a caller passes
    only parameter values for which the tests check that the bound lies between the 2 lowest zeros.

    References:
        - NIST Digital Library of Mathematical Functions, §18.16(ii), for the zeros of the Jacobi polynomials, and
          §10.21(vi), for McMahon's approximation. https://dlmf.nist.gov/18.16 and https://dlmf.nist.gov/10.21
    """
    if int(n) % 2 == 1:
        return (-1.0, 1.0)
    else:
        theta_over_pi = (1.25 + beta / 2.0) / (n + (alpha + beta + 1.0) / 2.0)
        # The lower bound is -cos(theta), written as a sine so that theta = pi/2 gives exactly 0.
        return (math.sin(math.pi * (theta_over_pi - 0.5)), 1.0)
