"""This module holds the test problems of Examples 1 to 7 of Anderson and Björck (1973), without results.

The paper compares the iteration counts of 4 methods, Brent's method among them, on 7 examples, most of them for
several values of an integer parameter ``n``; a problem's name holds the example's number and ``n``, e.g. ``2[n=5]``.

This module corrects a misprint in Example 5: the paper prints ``f(x) = 1 + (1 + (1 - n)^4) x - (1 - n x)^4``, whose
leading ``1 +`` makes ``f(0) = 0``. The paper takes its examples from Dowell and Jarratt (1971), whose Table 5 prints
the function without the leading ``1 +``.
"""

import math

from .problem import PaperProblem


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
ANDERSON_BJORCK_PROBLEMS = [
    PaperProblem(name="1", f=lambda x: math.sin(x) - 0.5, a=0.0, b=1.5),
    *PaperProblem.for_each_n(problem_number=2, function=_function_2, a=0.0, b=1.0, ns=[1, 5, 15, 20]),
    *PaperProblem.for_each_n(problem_number=3, function=_function_3, a=0.0, b=1.0, ns=[2, 5, 15, 20]),
    *PaperProblem.for_each_n(problem_number=4, function=_function_4, a=0.0, b=1.0, ns=[2, 5, 15, 20]),
    *PaperProblem.for_each_n(problem_number=5, function=_function_5, a=0.0, b=1.0, ns=[2, 5, 15, 20]),
    *PaperProblem.for_each_n(problem_number=6, function=_function_6, a=0.0, b=1.0, ns=[1, 5, 10, 15, 20]),
    *PaperProblem.for_each_n(problem_number=7, function=_function_7, a=0.01, b=1.0, ns=[2, 5, 15, 20]),
]
