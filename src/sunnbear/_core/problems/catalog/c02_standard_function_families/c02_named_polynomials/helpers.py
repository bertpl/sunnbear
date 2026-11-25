"""This module holds what several named polynomial formulas share: the rules for degrees and intervals, and sweeps.

Each polynomial orthogonal on ``[-1, 1]`` is a Jacobi polynomial ``P_n^(alpha, beta)`` up to a constant factor, so 1
rule gives the interval of all of them, from the degree and the 2 parameters of that Jacobi polynomial.

The formulas of those polynomials sweep their degree on a logarithmic scale, up to about 1000, where a recurrence over
the degrees already takes about 1000 steps per evaluation. The resolution falls with the number of the formula's other
parameters, so that a formula with more parameters does not produce far more parameter tuples:

- the 3 formulas whose degree is their only parameter share `JACOBI_DEGREE_ONLY_AXIS`;
- `GegenbauerPolynomial` and `JacobiPolynomial` each sweep a coarser axis of their own.
"""

import math

from sunnbear._core.problems.core import ParamAxis, ParamNotation, ParamRounding

# The axis rounds ``10^(0.01*i)``, for ``i`` from 0 to 300, to the nearest integer, and yields each degree once: every
# degree up to about 40, and fewer above. At this resolution about half of the degrees are odd, so 1 axis gives odd
# and even degrees alike. `JACOBI_DEGREE_ONLY_SUMMARY` describes the axis, so a change to the axis needs the same change
# to the summary.
JACOBI_DEGREE_ONLY_AXIS = ParamAxis("n", 0.0, 3.0, 0.01, ParamNotation.POW10, ParamRounding.NEAREST_INTEGER)
JACOBI_DEGREE_ONLY_SUMMARY = r"The degrees $\param{n}$ nearest to $10^{0.01 i}$, for $i$ from 0 to 300, each once."

# A formula whose values grow quickly with the degree sweeps every degree from 1 up to the highest degree whose range
# of values is at most ``10^VALUE_RANGE_EXPONENT_LIMIT``, so that the family's ranges of values stay modest; other
# formulas cover extreme ranges of values. The range of values is the largest absolute value on the interval divided
# by the lowest peak of the absolute value between 2 neighboring roots, at ``c = 0``. A shift by ``c`` changes the
# values at the bounds, so the range at the ends of a calibrated range of ``c`` can exceed the limit.
#
# `VALUE_RANGE_LIMIT_SUMMARY` states the limit, to follow the degrees in such a recipe's summary.
VALUE_RANGE_EXPONENT_LIMIT = 20
VALUE_RANGE_LIMIT_SUMMARY = (
    rf"the highest degree at which, for $\c = 0$, the largest absolute value on the interval is at most "
    rf"$10^{{{VALUE_RANGE_EXPONENT_LIMIT}}}$ times the lowest peak of the absolute value between 2 neighboring roots"
)


def is_valid_degree(n: float) -> bool:
    """Return whether `n` is an integer of at least 1."""
    return n == int(n) and n >= 1


def interval_by_parity_latex(odd_degree_interval: str, even_degree_interval: str) -> str:
    r"""Return a ``cases`` environment with the LaTeX of the interval for an odd and for an even degree ``n``.

    The conditions name the degree by the placeholder ``\param{n}``, so the formula's degree parameter must be named
    ``n``.

    Args:
        odd_degree_interval: The interval's LaTeX for an odd ``n``, such as ``"[-1, 1]"``.
        even_degree_interval: The interval's LaTeX for an even ``n``.
    """
    return (
        r"\begin{cases} "
        + odd_degree_interval
        + r" & \text{if } \param{n} \text{ is odd} \\ "
        + even_degree_interval
        + r" & \text{if } \param{n} \text{ is even} \end{cases}"
    )


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
