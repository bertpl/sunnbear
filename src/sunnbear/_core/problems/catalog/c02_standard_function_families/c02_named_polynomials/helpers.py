"""This module holds the rule for a valid degree, LaTeX for intervals, and what the orthogonal polynomials share.

Each polynomial orthogonal on ``[-1, 1]`` is a Jacobi polynomial ``P_n^(alpha, beta)`` up to a constant factor, so 1
rule gives the interval of all of them, from the degree and the 2 parameters of that Jacobi polynomial.
"""

import math

from sunnbear._core.problems.core import ParamAxis, ParamNotation, ParamRounding

# Each of the formulas whose polynomials are orthogonal on ``[-1, 1]`` sweeps its degree on a logarithmic scale, with
# 1 recipe for the odd and 1 for the even degrees, because an odd and an even degree differ in their intervals
# (`jacobi_interval_bounds`).
#
# Each axis rounds ``10^(0.1*i)``, for ``i`` from 0 to 30, to the nearest odd or even integer; a tie goes to the
# larger integer, so the odd degrees end at 1001 and the even degrees start at 2.
#
# The sweep ends at about 1000, where a recurrence over the degrees already takes about 1000 steps per evaluation.
JACOBI_ODD_DEGREE_AXIS = ParamAxis("n", 0.0, 3.0, 0.1, ParamNotation.POW10, ParamRounding.NEAREST_ODD_INTEGER)
JACOBI_EVEN_DEGREE_AXIS = ParamAxis("n", 0.0, 3.0, 0.1, ParamNotation.POW10, ParamRounding.NEAREST_EVEN_INTEGER)
# A recipe that sweeps 1 of the 2 axes starts its summary with that axis's summary constant, which has no final
# period, so that the recipe can name its other parameters after that text. Each summary constant describes its axis,
# so a change to an axis needs the same change to its summary constant.
JACOBI_ODD_DEGREE_SUMMARY = (
    r"The odd degrees $\param{n}$ nearest to $10^{0.1 i}$, for $i$ from 0 to 30, with a tie going to the larger degree"
)
JACOBI_EVEN_DEGREE_SUMMARY = (
    r"The even degrees $\param{n}$ nearest to $10^{0.1 i}$, for $i$ from 0 to 30, with a tie going to the larger degree"
)
# Each degree axis with its summary constant, so that a recipe takes the 2 together.
JACOBI_DEGREE_SWEEPS = (
    (JACOBI_ODD_DEGREE_AXIS, JACOBI_ODD_DEGREE_SUMMARY),
    (JACOBI_EVEN_DEGREE_AXIS, JACOBI_EVEN_DEGREE_SUMMARY),
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
