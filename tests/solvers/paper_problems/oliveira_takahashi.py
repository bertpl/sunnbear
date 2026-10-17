"""This module holds `OliveiraTakahashiTable1Problem`, the 24 test problems of Table 1 of Oliveira and Takahashi
(2020), without any method's iteration counts.

Table 1 gives several methods' iteration counts on 24 functions, each on ``[-1, 1]``; a problem's name is the function's
name in the table in snake case, e.g. ``polynomial_fraction`` for "Poly.Frac.". The table's runs stop once the interval
is at most ``2 * XTOL`` wide, the stopping criterion of `BracketingSolver`, and its counts leave out the 2 evaluations
at the interval bounds.

References:
    - Oliveira, I. F. D. and Takahashi, R. H. C. (2020). An enhancement of the bisection method average performance
      preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), article 5.
      https://doi.org/10.1145/3423597
"""

import math

from .problem import PaperProblem, PaperProblemEnum

# The paper's experiments solve every function on [-1, 1] with this xtol, where bisection needs `N_BISECTION`
# iterations.
XTOL = 1e-10
N_BISECTION = 34


# ==================================================================================================
#  The problems' functions
# ==================================================================================================
def _sawtooth(x: float) -> float:
    """Return the paper's sawtooth function, which crosses 0 on many teeth."""
    return 202.0 * x - 2.0 * math.floor((2.0 * x + 1e-2) / (2.0 * 1e-2)) - 0.1


def _geometric(x: float) -> float:
    """Return the paper's geometric function ``1 / (21x - 1)``, set to 0 at its pole."""
    if x == 1.0 / 21.0:
        return 0.0
    else:
        return 1.0 / (21.0 * x - 1.0)


def _warsaw(x: float) -> float:
    """Return the paper's Warsaw function, ``sin(1 / (x + 1))`` right of -1 and -1 elsewhere."""
    if x > -1.0:
        return math.sin(1.0 / (x + 1.0))
    else:
        return -1.0


def _circles(x: float) -> float:
    """Return the paper's circles function, which takes the sign of ``3x + 1`` and is 0 where ``3x + 1`` is 0."""
    sign = (3.0 * x + 1.0 > 0.0) - (3.0 * x + 1.0 < 0.0)
    return sign * (1.0 - math.sqrt(1.0 - (3.0 * x + 1.0) ** 2 / 81.0))


# ==================================================================================================
#  The problems
# ==================================================================================================
class OliveiraTakahashiTable1Problem(PaperProblemEnum):
    """`OliveiraTakahashiTable1Problem` holds the 24 problems of Table 1 of Oliveira and Takahashi (2020), in the
    table's order; a member's name is the problem's name in capitals, e.g. ``LAMBERT``."""

    LAMBERT = PaperProblem(name="lambert", f=lambda x: x * math.exp(x) - 1.0, a=-1.0, b=1.0)
    TRIGONOMETRIC_1 = PaperProblem(name="trigonometric_1", f=lambda x: math.tan(x - 0.1), a=-1.0, b=1.0)
    TRIGONOMETRIC_2 = PaperProblem(name="trigonometric_2", f=lambda x: math.sin(x) + 0.5, a=-1.0, b=1.0)
    POLYNOMIAL_1 = PaperProblem(name="polynomial_1", f=lambda x: 4.0 * x**5 + x**2 + 1.0, a=-1.0, b=1.0)
    POLYNOMIAL_2 = PaperProblem(name="polynomial_2", f=lambda x: x + x**10 - 1.0, a=-1.0, b=1.0)
    EXPONENTIAL = PaperProblem(name="exponential", f=lambda x: math.pi**x - math.e, a=-1.0, b=1.0)
    LOGARITHMIC = PaperProblem(name="logarithmic", f=lambda x: -math.log(abs(x - 10.0 / 9.0)), a=-1.0, b=1.0)
    POSYNOMIAL = PaperProblem(
        name="posynomial", f=lambda x: 1.0 / 3.0 + math.copysign(abs(x) ** (1.0 / 3.0), x) + x**3, a=-1.0, b=1.0
    )
    WEIERSTRASS = PaperProblem(
        name="weierstrass",
        f=lambda x: 0.001 + sum(math.sin(math.pi * i**3 * x / 2.0) / (math.pi * i**3) for i in range(1, 11)),
        a=-1.0,
        b=1.0,
    )
    POLYNOMIAL_FRACTION = PaperProblem(
        name="polynomial_fraction", f=lambda x: (x + 2.0 / 3.0) / (x + 101.0 / 100.0), a=-1.0, b=1.0
    )
    NORMAL_CDF = PaperProblem(
        name="normal_cdf",
        f=lambda x: 0.5 * (1.0 + math.erf((x - 1.0) / math.sqrt(2.0))) - math.sqrt(2.0) / 4.0,
        a=-1.0,
        b=1.0,
    )
    NORMAL_PDF = PaperProblem(
        name="normal_pdf",
        f=lambda x: math.exp(-0.5 * (x - 1.0) ** 2) / math.sqrt(2.0 * math.pi) - math.sqrt(2.0) / 4.0,
        a=-1.0,
        b=1.0,
    )
    POLYNOMIAL_3 = PaperProblem(name="polynomial_3", f=lambda x: (x * 1e6 - 1.0) ** 3, a=-1.0, b=1.0)
    EXPONENTIAL_POLYNOMIAL = PaperProblem(
        name="exponential_polynomial", f=lambda x: math.exp(x) * (x * 1e6 - 1.0) ** 3, a=-1.0, b=1.0
    )
    TANGENT_POLYNOMIAL = PaperProblem(
        name="tangent_polynomial", f=lambda x: (x - 1.0 / 3.0) ** 2 * math.atan(x - 1.0 / 3.0), a=-1.0, b=1.0
    )
    CIRCLES = PaperProblem(name="circles", f=_circles, a=-1.0, b=1.0)
    STEP_FUNCTION = PaperProblem(
        name="step_function", f=lambda x: float(x > (1.0 - 1e6) / 1e6) * (1.0 + 1e6) / 1e6 - 1.0, a=-1.0, b=1.0
    )
    GEOMETRIC = PaperProblem(name="geometric", f=_geometric, a=-1.0, b=1.0)
    TRUNCATED_POLYNOMIAL = PaperProblem(
        name="truncated_polynomial", f=lambda x: (x / 2.0) ** 2 + math.ceil(x / 2.0) - 0.5, a=-1.0, b=1.0
    )
    STAIRCASE = PaperProblem(name="staircase", f=lambda x: math.ceil(10.0 * x - 1.0) + 0.5, a=-1.0, b=1.0)
    NOISY_LINE = PaperProblem(name="noisy_line", f=lambda x: x + math.sin(x * 1e6) / 10.0 + 1e-3, a=-1.0, b=1.0)
    WARSAW = PaperProblem(name="warsaw", f=_warsaw, a=-1.0, b=1.0)
    SAWTOOTH = PaperProblem(name="sawtooth", f=_sawtooth, a=-1.0, b=1.0)
    SAWTOOTH_CUBE = PaperProblem(name="sawtooth_cube", f=lambda x: _sawtooth(x) ** 3, a=-1.0, b=1.0)
