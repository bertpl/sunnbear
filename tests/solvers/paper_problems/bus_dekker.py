"""This module holds `BusDekkerTablesIToIVProblem`, the test problems of Bus and Dekker (1975), without results.

The article's section 5 defines 4 groups of test problems, and Tables I to IV give the evaluation counts on them, 1
table per group. A problem's name holds its group and, where the group has several, its function and parameters, e.g.
``I.2[n=3]`` or ``II[a=1,b=0.0001,n=9]``.

Section 5 states no interval for Group II; its problems take ``[-1, 10]``, the interval of Group III.
"""

import functools
import math
from collections.abc import Callable

from .problem import PaperProblem, PaperProblemEnum


# ==================================================================================================
#  The problems' functions
# ==================================================================================================
def _group_1_function_1(x: float) -> float:
    """Return Group I's function 1, ``sin(x) - 0.5``."""
    return math.sin(x) - 0.5


def _group_1_function_2(x: float, *, n: float) -> float:
    """Return Group I's function 2, ``2x exp(-n) + 1 - 2 exp(-nx)``."""
    return 2.0 * x * math.exp(-n) + 1.0 - 2.0 * math.exp(-n * x)


def _group_1_function_3(x: float, *, n: float) -> float:
    """Return Group I's function 3, ``(1 + (1 - n)^2) x - (1 - nx)^2``."""
    return (1.0 + (1.0 - n) ** 2) * x - (1.0 - n * x) ** 2


def _group_1_function_4(x: float, *, n: float) -> float:
    """Return Group I's function 4, ``x^2 - (1 - x)^n``."""
    return x**2 - (1.0 - x) ** n


def _group_1_function_5(x: float, *, n: float) -> float:
    """Return Group I's function 5, ``(1 + (1 - n)^4) x - (1 - nx)^4``."""
    return (1.0 + (1.0 - n) ** 4) * x - (1.0 - n * x) ** 4


def _group_1_function_6(x: float, *, n: float) -> float:
    """Return Group I's function 6, ``(x - 1) exp(-nx) + x^n``."""
    return (x - 1.0) * math.exp(-n * x) + x**n


def _group_2_function(x: float, *, n: float, a: float, b: float) -> float:
    """Return Group II's function, ``x^n + ax + b``."""
    return x**n + a * x + b


def _group_3_function(x: float, *, n: float) -> float:
    """Return Group III's function, ``x^n``, whose root at 0 has multiplicity ``n``."""
    return x**n


def _group_4_function(x: float) -> float:
    """Return Group IV's function, ``x exp(-x^-2)``, extended by 0 at ``x = 0``, where all its derivatives vanish too.

    In float64, the function underflows to 0 for ``|x|`` below about 0.0375.
    """
    if x == 0.0:
        return 0.0
    else:
        return x * math.exp(-(x**-2))


def _group_1_problem(function_number: int, function: Callable[..., float], n: int) -> PaperProblem:
    """Return Group I's problem for ``function`` and ``n``, on ``[0, 1]``."""
    return PaperProblem(name=f"I.{function_number}[n={n}]", f=functools.partial(function, n=float(n)), a=0.0, b=1.0)


def _group_2_problem(a: float, b: float, n: int) -> PaperProblem:
    """Return Group II's problem for ``a``, ``b`` and ``n``, on ``[-1, 10]``."""
    return PaperProblem(
        name=f"II[a={a:g},b={b:g},n={n}]",
        f=functools.partial(_group_2_function, n=float(n), a=a, b=b),
        a=-1.0,
        b=10.0,
    )


def _group_3_problem(n: int) -> PaperProblem:
    """Return Group III's problem for ``n``, on ``[-1, 10]``."""
    return PaperProblem(name=f"III[n={n}]", f=functools.partial(_group_3_function, n=float(n)), a=-1.0, b=10.0)


# ==================================================================================================
#  The problems, in the order of the article's tables
# ==================================================================================================
class BusDekkerTablesIToIVProblem(PaperProblemEnum):
    """`BusDekkerTablesIToIVProblem` holds the problems of the article's Tables I to IV, in the tables' order.

    Each member is named after its group and, where the group has several, its function and parameters, e.g.
    ``I2_N3`` or ``II_A1_B1EM4_N9``.
    """

    # --------------------------------------------------------------------------
    #  Table I, Group I
    # --------------------------------------------------------------------------
    I1 = PaperProblem(name="I.1", f=_group_1_function_1, a=0.0, b=1.5)
    I2_N1 = _group_1_problem(2, _group_1_function_2, 1)
    I2_N2 = _group_1_problem(2, _group_1_function_2, 2)
    I2_N3 = _group_1_problem(2, _group_1_function_2, 3)
    I2_N4 = _group_1_problem(2, _group_1_function_2, 4)
    I3_N1 = _group_1_problem(3, _group_1_function_3, 1)
    I3_N5 = _group_1_problem(3, _group_1_function_3, 5)
    I3_N10 = _group_1_problem(3, _group_1_function_3, 10)
    I4_N1 = _group_1_problem(4, _group_1_function_4, 1)
    I4_N5 = _group_1_problem(4, _group_1_function_4, 5)
    I4_N10 = _group_1_problem(4, _group_1_function_4, 10)
    I5_N1 = _group_1_problem(5, _group_1_function_5, 1)
    I5_N4 = _group_1_problem(5, _group_1_function_5, 4)
    I5_N8 = _group_1_problem(5, _group_1_function_5, 8)
    I6_N1 = _group_1_problem(6, _group_1_function_6, 1)
    I6_N5 = _group_1_problem(6, _group_1_function_6, 5)
    I6_N10 = _group_1_problem(6, _group_1_function_6, 10)

    # --------------------------------------------------------------------------
    #  Table II, Group II
    # --------------------------------------------------------------------------
    II_A1_B0_N3 = _group_2_problem(1.0, 0.0, 3)
    II_A1_B0_N5 = _group_2_problem(1.0, 0.0, 5)
    II_A1_B0_N9 = _group_2_problem(1.0, 0.0, 9)
    II_A1_B0_N19 = _group_2_problem(1.0, 0.0, 19)
    II_A0_B1EM4_N3 = _group_2_problem(0.0, 1e-4, 3)
    II_A0_B1EM4_N5 = _group_2_problem(0.0, 1e-4, 5)
    II_A0_B1EM4_N9 = _group_2_problem(0.0, 1e-4, 9)
    II_A0_B1EM4_N19 = _group_2_problem(0.0, 1e-4, 19)
    II_A1_B1EM4_N3 = _group_2_problem(1.0, 1e-4, 3)
    II_A1_B1EM4_N5 = _group_2_problem(1.0, 1e-4, 5)
    II_A1_B1EM4_N9 = _group_2_problem(1.0, 1e-4, 9)
    II_A1_B1EM4_N19 = _group_2_problem(1.0, 1e-4, 19)

    # --------------------------------------------------------------------------
    #  Table III, Group III
    # --------------------------------------------------------------------------
    III_N3 = _group_3_problem(3)
    III_N5 = _group_3_problem(5)
    III_N7 = _group_3_problem(7)
    III_N9 = _group_3_problem(9)
    III_N19 = _group_3_problem(19)
    III_N25 = _group_3_problem(25)

    # --------------------------------------------------------------------------
    #  Table IV, Group IV
    # --------------------------------------------------------------------------
    IV = PaperProblem(name="IV", f=_group_4_function, a=-1.0, b=4.0)
