"""This module holds the test problems of Alefeld, Potra and Shi's Algorithm 748, as the authors' test driver defines
them, without results.

The driver numbers its problems 1 to 28, and runs most of them for several values of an integer parameter ``n``; a
problem's name holds both, e.g. ``15[n=4]``.

The functions and intervals follow the driver's subroutines ``FUNC`` and ``INIT``; they are the test problems of the
paper's Table I, with the paper's problem 2 split into 10 problems, 1 per interval.
"""

import functools
import math
from collections.abc import Callable, Iterable

from .problem import PaperProblem

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
    Fortran code computes there.

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
def _for_each_n(
    problem_number: int, function: Callable[..., float], a: float, b: float, ns: Iterable[int]
) -> list[PaperProblem]:
    """Return 1 problem per value of ``n``, each with ``function`` bound to that ``n``."""
    return [PaperProblem(f"{problem_number}[n={n}]", functools.partial(function, n=float(n)), a, b) for n in ns]


ALEFELD_POTRA_SHI_PROBLEMS = [
    PaperProblem("1[n=1]", _function_1, _PI_ROUNDED / 2.0, _PI_ROUNDED),
    # Each of problems 2 to 11 takes the interval between 2 consecutive poles, i^2 and (i + 1)^2.
    *[
        PaperProblem(f"{i + 1}[n=1]", _function_2_to_11, float(i * i) + 1e-9, float((i + 1) * (i + 1)) - 1e-9)
        for i in range(1, 11)
    ],
    PaperProblem("12[n=1]", functools.partial(_function_12_to_14, scale=40.0, rate=1.0), -9.0, 31.0),
    PaperProblem("13[n=1]", functools.partial(_function_12_to_14, scale=100.0, rate=2.0), -9.0, 31.0),
    PaperProblem("14[n=1]", functools.partial(_function_12_to_14, scale=200.0, rate=3.0), -9.0, 31.0),
    *_for_each_n(15, _function_15, 0.0, 5.0, [4, 6, 8, 10, 12]),
    *_for_each_n(16, _function_16_and_17, 0.0, 5.0, [4, 6, 8, 10, 12]),
    *_for_each_n(17, _function_16_and_17, -0.95, 4.05, [8, 10, 12, 14]),
    PaperProblem("18[n=1]", _function_18, 0.0, 1.5),
    *_for_each_n(19, _function_19, 0.0, 1.0, [1, 2, 3, 4, 5, 20, 40, 60, 80, 100]),
    *_for_each_n(20, _function_20, 0.0, 1.0, [5, 10, 20]),
    *_for_each_n(21, _function_21, 0.0, 1.0, [2, 5, 10, 15, 20]),
    *_for_each_n(22, _function_22, 0.0, 1.0, [1, 2, 4, 5, 8, 15, 20]),
    *_for_each_n(23, _function_23, 0.0, 1.0, [1, 5, 10, 15, 20]),
    *_for_each_n(24, _function_24, 1e-2, 1.0, [2, 5, 15, 20]),
    *_for_each_n(25, _function_25, 1.0, 100.0, [2, 3, 4, 5, 6, 7, *range(9, 34, 2)]),
    PaperProblem("26[n=1]", _function_26, -1.0, 4.0),
    *_for_each_n(27, _function_27, -10000.0, _PI_ROUNDED / 2.0, range(1, 41)),
    *_for_each_n(28, _function_28, -10000.0, 1e-4, [*range(20, 41), *range(100, 1001, 100)]),
]
