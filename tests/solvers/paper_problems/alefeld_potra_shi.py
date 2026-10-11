"""This module holds the test problems of Alefeld, Potra and Shi's Algorithm 748, as the authors' test driver defines
them, without results.

The driver numbers its problems 1 to 28, and runs most of them for several values of an integer parameter ``n``; a
problem's name holds both, e.g. ``15[n=4]``.

The functions and intervals follow the driver's subroutines ``FUNC`` and ``INIT``; they are the test problems of the
paper's Table I, with the paper's problem 2 split into 10 problems, 1 per interval. `AlefeldPotraShiTablesIVToVIProblem`
holds the problems whose counts the paper's Tables IV to VI list.
"""

import functools
import math

from .problem import PaperProblem, PaperProblemEnum

# The driver sets pi to this rounded value for the intervals of problems 1 and 27.
_PI_ROUNDED = 3.1416


# ==================================================================================================
#  The problems' functions
# ==================================================================================================
def _function_1(x: float) -> float:
    """Return problem 1, ``sin(x) - x / 2``."""
    return math.sin(x) - x / 2.0


def _function_2_to_11(x: float) -> float:
    """Return the function of problems 2 to 11, which has a pole at each square ``i^2``."""
    fx = 0.0
    for i in range(1, 21):
        fx = fx + (2.0 * i - 5.0) ** 2 / (x - float(i * i)) ** 3
    return -2.0 * fx


def _function_12_to_14(x: float, *, scale: float, rate: float) -> float:
    """Return the function of problems 12 to 14, ``-scale * x * exp(-rate * x)``."""
    return -scale * x * math.exp(-rate * x)


def _function_15(x: float, *, n: float) -> float:
    """Return problem 15, ``x^n - 0.2``."""
    return x**n - 0.2


def _function_16_and_17(x: float, *, n: float) -> float:
    """Return the function of problems 16 and 17, ``x^n - 1``."""
    return x**n - 1.0


def _function_18(x: float) -> float:
    """Return problem 18, ``sin(x) - 0.5``."""
    return math.sin(x) - 0.5


def _function_19(x: float, *, n: float) -> float:
    """Return problem 19, ``2x exp(-n) - 2 exp(-nx) + 1``."""
    return 2.0 * x * math.exp(-n) - 2.0 * math.exp(-n * x) + 1.0


def _function_20(x: float, *, n: float) -> float:
    """Return problem 20, ``(1 + (1 - n)^2) x - (1 - nx)^2``."""
    return (1.0 + (1.0 - n) ** 2) * x - (1.0 - n * x) ** 2


def _function_21(x: float, *, n: float) -> float:
    """Return problem 21, ``x^2 - (1 - x)^n``."""
    return x**2 - (1.0 - x) ** n


def _function_22(x: float, *, n: float) -> float:
    """Return problem 22, ``(1 + (1 - n)^4) x - (1 - nx)^4``."""
    return (1.0 + (1.0 - n) ** 4) * x - (1.0 - n * x) ** 4


def _function_23(x: float, *, n: float) -> float:
    """Return problem 23, ``(x - 1) exp(-nx) + x^n``."""
    return (x - 1.0) * math.exp(-n * x) + x**n


def _function_24(x: float, *, n: float) -> float:
    """Return problem 24, ``(nx - 1) / ((n - 1) x)``."""
    return (n * x - 1.0) / ((n - 1.0) * x)


def _function_25(x: float, *, n: float) -> float:
    """Return problem 25, ``x^(1/n) - n^(1/n)``."""
    return x ** (1.0 / n) - n ** (1.0 / n)


def _function_26(x: float) -> float:
    """Return problem 26, ``x / exp(1 / x^2)``, and 0 where the exponential overflows, which is the value that the
    authors' Fortran test driver computes there.

    Python raises where Fortran returns infinity: ``exp`` overflows for ``|x|`` below about 0.0375, and ``1 / x^2``
    for ``|x|`` below about 1e-154. The function is 0 there in both cases.
    """
    if x == 0.0:
        return 0.0
    else:
        try:
            return x / math.exp(1.0 / (x * x))
        except (OverflowError, ZeroDivisionError):
            return 0.0


def _function_27(x: float, *, n: float) -> float:
    """Return problem 27, ``(x / 1.5 + sin(x) - 1) n / 20`` for ``x >= 0``, and ``-n / 20`` below 0."""
    if x >= 0.0:
        return (x / 1.5 + math.sin(x) - 1.0) * n / 20.0
    else:
        return -n / 20.0


def _function_28(x: float, *, n: float) -> float:
    """Return problem 28, which rises steeply from -0.859 to ``e - 1.859`` over ``[0, 2e-3 / (n + 1)]``."""
    if x >= 1e-3 * 2.0 / (n + 1.0):
        return math.exp(1.0) - 1.859
    elif x >= 0.0:
        return math.exp((n + 1.0) * 0.5 * x * 1e3) - 1.859
    else:
        return -0.859


# ==================================================================================================
#  The problems, in the order of the authors' test data
# ==================================================================================================
ALEFELD_POTRA_SHI_PROBLEMS = [
    PaperProblem(name="1[n=1]", f=_function_1, a=_PI_ROUNDED / 2.0, b=_PI_ROUNDED),
    # Each of problems 2 to 11 takes the interval between 2 consecutive poles, i^2 and (i + 1)^2.
    *[
        PaperProblem(
            name=f"{i + 1}[n=1]",
            f=_function_2_to_11,
            a=float(i * i) + 1e-9,
            b=float((i + 1) * (i + 1)) - 1e-9,
        )
        for i in range(1, 11)
    ],
    PaperProblem(name="12[n=1]", f=functools.partial(_function_12_to_14, scale=40.0, rate=1.0), a=-9.0, b=31.0),
    PaperProblem(name="13[n=1]", f=functools.partial(_function_12_to_14, scale=100.0, rate=2.0), a=-9.0, b=31.0),
    PaperProblem(name="14[n=1]", f=functools.partial(_function_12_to_14, scale=200.0, rate=3.0), a=-9.0, b=31.0),
    *PaperProblem.for_each_n(problem_number=15, function=_function_15, a=0.0, b=5.0, ns=[4, 6, 8, 10, 12]),
    *PaperProblem.for_each_n(problem_number=16, function=_function_16_and_17, a=0.0, b=5.0, ns=[4, 6, 8, 10, 12]),
    *PaperProblem.for_each_n(problem_number=17, function=_function_16_and_17, a=-0.95, b=4.05, ns=[8, 10, 12, 14]),
    PaperProblem(name="18[n=1]", f=_function_18, a=0.0, b=1.5),
    *PaperProblem.for_each_n(
        problem_number=19, function=_function_19, a=0.0, b=1.0, ns=[1, 2, 3, 4, 5, 20, 40, 60, 80, 100]
    ),
    *PaperProblem.for_each_n(problem_number=20, function=_function_20, a=0.0, b=1.0, ns=[5, 10, 20]),
    *PaperProblem.for_each_n(problem_number=21, function=_function_21, a=0.0, b=1.0, ns=[2, 5, 10, 15, 20]),
    *PaperProblem.for_each_n(problem_number=22, function=_function_22, a=0.0, b=1.0, ns=[1, 2, 4, 5, 8, 15, 20]),
    *PaperProblem.for_each_n(problem_number=23, function=_function_23, a=0.0, b=1.0, ns=[1, 5, 10, 15, 20]),
    *PaperProblem.for_each_n(problem_number=24, function=_function_24, a=1e-2, b=1.0, ns=[2, 5, 15, 20]),
    *PaperProblem.for_each_n(
        problem_number=25, function=_function_25, a=1.0, b=100.0, ns=[2, 3, 4, 5, 6, 7, *range(9, 34, 2)]
    ),
    PaperProblem(name="26[n=1]", f=_function_26, a=-1.0, b=4.0),
    *PaperProblem.for_each_n(
        problem_number=27, function=_function_27, a=-10000.0, b=_PI_ROUNDED / 2.0, ns=range(1, 41)
    ),
    *PaperProblem.for_each_n(
        problem_number=28, function=_function_28, a=-10000.0, b=1e-4, ns=[*range(20, 41), *range(100, 1001, 100)]
    ),
]

ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME = {problem.name: problem for problem in ALEFELD_POTRA_SHI_PROBLEMS}


class AlefeldPotraShiTablesIVToVIProblem(PaperProblemEnum):
    """`AlefeldPotraShiTablesIVToVIProblem` holds the 17 problems of the paper's Tables IV to VI, in the tables' order,
    whose counts the paper lists at ``tol = 10^-15``.

    The paper numbers its problems as its Table I does, not as the authors' test driver does: a member's name holds the
    driver's problem number and ``n``, e.g. ``P26_N1``, and the comment above it gives the paper's label.
    """

    # Table IV: 13
    P26_N1 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["26[n=1]"]
    # Table V: 3[a=-100,b=-2]
    P13_N1 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["13[n=1]"]
    # Table V: 14[n=10]
    P27_N10 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["27[n=10]"]
    # Table V: 14[n=30]
    P27_N30 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["27[n=30]"]
    # Table V: 15[n=30]
    P28_N30 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["28[n=30]"]
    # Table V: 15[n=500]
    P28_N500 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["28[n=500]"]
    # Table VI: 1
    P1_N1 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["1[n=1]"]
    # Table VI: 2[n=2]
    P3_N1 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["3[n=1]"]
    # Table VI: 4[a=1,n=4]
    P16_N4 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["16[n=4]"]
    # Table VI: 5
    P18_N1 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["18[n=1]"]
    # Table VI: 6[n=20]
    P19_N20 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["19[n=20]"]
    # Table VI: 7[n=10]
    P20_N10 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["20[n=10]"]
    # Table VI: 8[n=10]
    P21_N10 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["21[n=10]"]
    # Table VI: 9[n=1]
    P22_N1 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["22[n=1]"]
    # Table VI: 10[n=5]
    P23_N5 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["23[n=5]"]
    # Table VI: 11[n=20]
    P24_N20 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["24[n=20]"]
    # Table VI: 12[n=3]
    P25_N3 = ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME["25[n=3]"]
