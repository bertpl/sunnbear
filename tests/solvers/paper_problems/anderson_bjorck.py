"""This module holds the test problems of Examples 1 to 7 of Anderson and Björck (1973), without results.

The paper compares the iteration counts of 4 methods, Brent's method among them, on 7 examples, most of them for
several values of an integer parameter ``n``; a problem's name holds the example's number and ``n``, e.g. ``2[n=5]``.

This module corrects a misprint in Example 5: the paper prints ``f(x) = 1 + (1 + (1 - n)^4) x - (1 - n x)^4``, whose
leading ``1 +`` makes ``f(0) = 0``. The paper takes its examples from Dowell and Jarratt (1971), whose Table 5 prints
the function without the leading ``1 +``.
"""

import functools
import math

from .problem import PaperProblem, PaperProblemEnum


# ==================================================================================================
#  The examples' functions
# ==================================================================================================
def _function_2(x: float, *, n: float) -> float:
    """Return example 2, ``2 x exp(-n) + 1 - 2 exp(-n x)``."""
    return 2.0 * x * math.exp(-n) + 1.0 - 2.0 * math.exp(-n * x)


def _function_3(x: float, *, n: float) -> float:
    """Return example 3, ``(1 + (1 - n)^2) x - (1 - n x)^2``."""
    return (1.0 + (1.0 - n) ** 2) * x - (1.0 - n * x) ** 2


def _function_4(x: float, *, n: float) -> float:
    """Return example 4, ``x^2 - (1 - x)^n``."""
    return x * x - (1.0 - x) ** n


def _function_5(x: float, *, n: float) -> float:
    """Return example 5, ``(1 + (1 - n)^4) x - (1 - n x)^4``."""
    return (1.0 + (1.0 - n) ** 4) * x - (1.0 - n * x) ** 4


def _function_6(x: float, *, n: float) -> float:
    """Return example 6, ``exp(-n x) (x - 1) + x^n``."""
    return math.exp(-n * x) * (x - 1.0) + x**n


def _function_7(x: float, *, n: float) -> float:
    """Return example 7, ``(n x - 1) / ((n - 1) x)``."""
    return (n * x - 1.0) / ((n - 1.0) * x)


# ==================================================================================================
#  The problems, in the order of the paper's examples
# ==================================================================================================
class AndersonBjorckExampleProblem(PaperProblemEnum):
    """`AndersonBjorckExampleProblem` holds the 26 problems of the paper's Examples 1 to 7, in the paper's order; a
    member's name holds the example's number and ``n``, e.g. ``EX2_N5``."""

    EX1 = PaperProblem(name="1", f=lambda x: math.sin(x) - 0.5, a=0.0, b=1.5)
    EX2_N1 = PaperProblem(name="2[n=1]", f=functools.partial(_function_2, n=1.0), a=0.0, b=1.0)
    EX2_N5 = PaperProblem(name="2[n=5]", f=functools.partial(_function_2, n=5.0), a=0.0, b=1.0)
    EX2_N15 = PaperProblem(name="2[n=15]", f=functools.partial(_function_2, n=15.0), a=0.0, b=1.0)
    EX2_N20 = PaperProblem(name="2[n=20]", f=functools.partial(_function_2, n=20.0), a=0.0, b=1.0)
    EX3_N2 = PaperProblem(name="3[n=2]", f=functools.partial(_function_3, n=2.0), a=0.0, b=1.0)
    EX3_N5 = PaperProblem(name="3[n=5]", f=functools.partial(_function_3, n=5.0), a=0.0, b=1.0)
    EX3_N15 = PaperProblem(name="3[n=15]", f=functools.partial(_function_3, n=15.0), a=0.0, b=1.0)
    EX3_N20 = PaperProblem(name="3[n=20]", f=functools.partial(_function_3, n=20.0), a=0.0, b=1.0)
    EX4_N2 = PaperProblem(name="4[n=2]", f=functools.partial(_function_4, n=2.0), a=0.0, b=1.0)
    EX4_N5 = PaperProblem(name="4[n=5]", f=functools.partial(_function_4, n=5.0), a=0.0, b=1.0)
    EX4_N15 = PaperProblem(name="4[n=15]", f=functools.partial(_function_4, n=15.0), a=0.0, b=1.0)
    EX4_N20 = PaperProblem(name="4[n=20]", f=functools.partial(_function_4, n=20.0), a=0.0, b=1.0)
    EX5_N2 = PaperProblem(name="5[n=2]", f=functools.partial(_function_5, n=2.0), a=0.0, b=1.0)
    EX5_N5 = PaperProblem(name="5[n=5]", f=functools.partial(_function_5, n=5.0), a=0.0, b=1.0)
    EX5_N15 = PaperProblem(name="5[n=15]", f=functools.partial(_function_5, n=15.0), a=0.0, b=1.0)
    EX5_N20 = PaperProblem(name="5[n=20]", f=functools.partial(_function_5, n=20.0), a=0.0, b=1.0)
    EX6_N1 = PaperProblem(name="6[n=1]", f=functools.partial(_function_6, n=1.0), a=0.0, b=1.0)
    EX6_N5 = PaperProblem(name="6[n=5]", f=functools.partial(_function_6, n=5.0), a=0.0, b=1.0)
    EX6_N10 = PaperProblem(name="6[n=10]", f=functools.partial(_function_6, n=10.0), a=0.0, b=1.0)
    EX6_N15 = PaperProblem(name="6[n=15]", f=functools.partial(_function_6, n=15.0), a=0.0, b=1.0)
    EX6_N20 = PaperProblem(name="6[n=20]", f=functools.partial(_function_6, n=20.0), a=0.0, b=1.0)
    EX7_N2 = PaperProblem(name="7[n=2]", f=functools.partial(_function_7, n=2.0), a=0.01, b=1.0)
    EX7_N5 = PaperProblem(name="7[n=5]", f=functools.partial(_function_7, n=5.0), a=0.01, b=1.0)
    EX7_N15 = PaperProblem(name="7[n=15]", f=functools.partial(_function_7, n=15.0), a=0.01, b=1.0)
    EX7_N20 = PaperProblem(name="7[n=20]", f=functools.partial(_function_7, n=20.0), a=0.01, b=1.0)
