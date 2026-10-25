"""This module holds the test problems of Chandrupatla's paper, keyed by their number in its Table 1, and
`ChandrupatlaTable2Problem`, the problems of its Table 2, without results.

Function 7 comes in 2 versions:

- `CHANDRUPATLA_AS_PRINTED_FUNCTIONS` holds it as the paper's Table 1 prints it, set to 0 where ``|x| < 3.8e-4``;
- `CHANDRUPATLA_FUNCTIONS` holds it computed by the formula everywhere.

Table 2 compares the evaluation counts of 3 methods, Brent's method among them, on 9 functions, each on 5 intervals. A
problem's name holds the function's number and the interval, e.g. ``1[2,3]``.
"""

import math

from .problem import PaperProblem, PaperProblemEnum


def _function_7(x: float) -> float:
    """Return the paper's function 7, ``x * exp(-1 / x^2)``, and 0 at ``x = 0``."""
    if x == 0.0:
        return 0.0
    else:
        return x * math.exp(-1.0 / (x * x))


def _as_printed_function_7(x: float) -> float:
    """Return the paper's function 7, ``x * exp(-1 / x^2)``, set to 0 where ``|x| < 3.8e-4``, as the paper's Table 1
    prints it."""
    if abs(x) < 3.8e-4:
        return 0.0
    else:
        return x * math.exp(-(x**-2))


def _function_8(x: float) -> float:
    """Return the paper's function 8."""
    xi = 0.61489
    return -3062.0 * (1.0 - xi) * math.exp(-x) / (xi + (1.0 - xi) * math.exp(-x)) - 1013.0 + 1628.0 / x


CHANDRUPATLA_FUNCTIONS = {
    1: lambda x: x**3 - 2.0 * x - 5.0,
    2: lambda x: 1.0 - 1.0 / x**2,
    3: lambda x: (x - 3.0) ** 3,
    4: lambda x: 6.0 * (x - 2.0) ** 5,
    5: lambda x: x**9,
    6: lambda x: x**19,
    7: _function_7,
    8: _function_8,
    9: lambda x: math.exp(x) - 2.0 - 0.01 / x**2 + 0.000002 / x**3,
}

CHANDRUPATLA_AS_PRINTED_FUNCTIONS = {**CHANDRUPATLA_FUNCTIONS, 7: _as_printed_function_7}


class ChandrupatlaTable2Problem(PaperProblemEnum):
    """`ChandrupatlaTable2Problem` holds the 45 problems of the paper's Table 2, in the table's order, with the
    functions as the paper's Table 1 prints them, because Table 2's counts come from those functions; a member's name
    holds the function's number and the interval's place among that function's 5 intervals, e.g. ``F1_I1``."""

    F1_I1 = PaperProblem(name="1[2,3]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[1], a=2.0, b=3.0)
    F1_I2 = PaperProblem(name="1[1,10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[1], a=1.0, b=10.0)
    F1_I3 = PaperProblem(name="1[1,100]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[1], a=1.0, b=100.0)
    F1_I4 = PaperProblem(name="1[-10000,10000]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[1], a=-10000.0, b=10000.0)
    F1_I5 = PaperProblem(name="1[-1e+10,1e+10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[1], a=-1e10, b=1e10)
    F2_I1 = PaperProblem(name="2[0.5,1.51]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[2], a=0.5, b=1.51)
    F2_I2 = PaperProblem(name="2[0.0001,10000]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[2], a=0.0001, b=10000.0)
    F2_I3 = PaperProblem(name="2[1e-06,1e+06]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[2], a=1e-6, b=1e6)
    F2_I4 = PaperProblem(name="2[1e-10,1e+10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[2], a=1e-10, b=1e10)
    F2_I5 = PaperProblem(name="2[1e-12,1e+12]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[2], a=1e-12, b=1e12)
    F3_I1 = PaperProblem(name="3[0,5]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[3], a=0.0, b=5.0)
    F3_I2 = PaperProblem(name="3[-10,10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[3], a=-10.0, b=10.0)
    F3_I3 = PaperProblem(name="3[-10000,10000]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[3], a=-10000.0, b=10000.0)
    F3_I4 = PaperProblem(name="3[-1e+06,1e+06]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[3], a=-1e6, b=1e6)
    F3_I5 = PaperProblem(name="3[-1e+10,1e+10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[3], a=-1e10, b=1e10)
    F4_I1 = PaperProblem(name="4[0,5]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[4], a=0.0, b=5.0)
    F4_I2 = PaperProblem(name="4[-10,10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[4], a=-10.0, b=10.0)
    F4_I3 = PaperProblem(name="4[-10000,10000]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[4], a=-10000.0, b=10000.0)
    F4_I4 = PaperProblem(name="4[-1e+06,1e+06]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[4], a=-1e6, b=1e6)
    F4_I5 = PaperProblem(name="4[-1e+10,1e+10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[4], a=-1e10, b=1e10)
    F5_I1 = PaperProblem(name="5[-1,4]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[5], a=-1.0, b=4.0)
    F5_I2 = PaperProblem(name="5[-2,5]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[5], a=-2.0, b=5.0)
    F5_I3 = PaperProblem(name="5[-1,10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[5], a=-1.0, b=10.0)
    F5_I4 = PaperProblem(name="5[-5,50]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[5], a=-5.0, b=50.0)
    F5_I5 = PaperProblem(name="5[-10,100]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[5], a=-10.0, b=100.0)
    F6_I1 = PaperProblem(name="6[-1,4]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[6], a=-1.0, b=4.0)
    F6_I2 = PaperProblem(name="6[-2,5]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[6], a=-2.0, b=5.0)
    F6_I3 = PaperProblem(name="6[-1,10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[6], a=-1.0, b=10.0)
    F6_I4 = PaperProblem(name="6[-5,50]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[6], a=-5.0, b=50.0)
    F6_I5 = PaperProblem(name="6[-10,100]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[6], a=-10.0, b=100.0)
    F7_I1 = PaperProblem(name="7[-1,4]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[7], a=-1.0, b=4.0)
    F7_I2 = PaperProblem(name="7[-2,5]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[7], a=-2.0, b=5.0)
    F7_I3 = PaperProblem(name="7[-1,10]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[7], a=-1.0, b=10.0)
    F7_I4 = PaperProblem(name="7[-5,50]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[7], a=-5.0, b=50.0)
    F7_I5 = PaperProblem(name="7[-10,100]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[7], a=-10.0, b=100.0)
    F8_I1 = PaperProblem(name="8[0.0002,2]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[8], a=0.0002, b=2.0)
    F8_I2 = PaperProblem(name="8[0.0002,3]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[8], a=0.0002, b=3.0)
    F8_I3 = PaperProblem(name="8[0.0002,9]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[8], a=0.0002, b=9.0)
    F8_I4 = PaperProblem(name="8[0.0002,27]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[8], a=0.0002, b=27.0)
    F8_I5 = PaperProblem(name="8[0.0002,81]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[8], a=0.0002, b=81.0)
    F9_I1 = PaperProblem(name="9[0.0002,1]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[9], a=0.0002, b=1.0)
    F9_I2 = PaperProblem(name="9[0.0002,3]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[9], a=0.0002, b=3.0)
    F9_I3 = PaperProblem(name="9[0.0002,9]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[9], a=0.0002, b=9.0)
    F9_I4 = PaperProblem(name="9[0.0002,27]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[9], a=0.0002, b=27.0)
    F9_I5 = PaperProblem(name="9[0.0002,81]", f=CHANDRUPATLA_AS_PRINTED_FUNCTIONS[9], a=0.0002, b=81.0)
