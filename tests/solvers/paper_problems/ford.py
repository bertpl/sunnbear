"""This module holds the test problems of Table 4 of Ford (1997), without results, and Ford's stopping rule.

Ford's Table 4 compares the iteration counts of several Illinois-type methods, among them the Illinois, Pegasus and
Anderson-Björck methods, on 5 functions, each on 3 intervals. A problem's name holds the function's number in the
paper and the interval, e.g. ``1[0.5,2]``.

The paper stops each solve by a stopping rule of its own, which no sunnbear solver uses; `n_fevals_at_ford_stop` finds
where that rule stops in a solve's history.
"""

import math

from sunnbear.solvers import SolveResult

from .problem import PaperProblem

# Ford's stopping rule: the tolerance ``tau``, and the factor on ``eps`` below which the interval's width stops a solve.
_FORD_TAU = 1e-14
_FORD_WIDTH_FACTOR = 0.95


# ==================================================================================================
#  The problems
# ==================================================================================================
def _function_2(x: float) -> float:
    """Return Ford's function 2, ``1e-8 * (x - 1) * prod_(i=1..10) (x^2 + x + i)``."""
    product = 1.0
    for i in range(1, 11):
        product = product * (x * x + x + float(i))
    return 1e-8 * (x - 1.0) * product


_FORD_FUNCTIONS = {
    1: lambda x: math.sin(0.01 / x) - 0.01,
    2: _function_2,
    3: lambda x: math.exp(21000.0 / x) / (1.11e11 * x * x) - 1.0,
    4: lambda x: 2.0 * x * math.exp(-20.0) + 1.0 - 2.0 * math.exp(-20.0 * x),
    5: lambda x: math.exp(1.0 / x - 25.0) - 1.0,
}

# `FORD_TABLE_4_PROBLEMS` maps each problem's name to the problem, in the order of the rows of Ford's Table 4.
FORD_TABLE_4_PROBLEMS = {
    problem.name: problem
    for problem in [
        PaperProblem(
            name=f"{row['function']}[{row['a']:g},{row['b']:g}]",
            f=_FORD_FUNCTIONS[row["function"]],
            a=row["a"],
            b=row["b"],
        )
        for row in [
            {"function": 1, "a": 0.5, "b": 2.0},
            {"function": 1, "a": 0.2, "b": 6.0},
            {"function": 1, "a": 0.004, "b": 200.0},
            {"function": 2, "a": 0.9, "b": 1.1},
            {"function": 2, "a": 0.5, "b": 1.5},
            {"function": 2, "a": -5.0, "b": 10.0},
            {"function": 3, "a": 550.0, "b": 560.0},
            {"function": 3, "a": 400.0, "b": 600.0},
            {"function": 3, "a": 350.0, "b": 850.0},
            {"function": 4, "a": 0.0, "b": 1.0},
            {"function": 4, "a": -0.1, "b": 1.5},
            {"function": 4, "a": -0.5, "b": 2.0},
            {"function": 5, "a": 0.035, "b": 0.05},
            {"function": 5, "a": 0.03, "b": 0.09},
            {"function": 5, "a": 0.025, "b": 0.5},
        ]
    ]
}


# ==================================================================================================
#  Ford's stopping rule
# ==================================================================================================
def n_fevals_at_ford_stop(result: SolveResult) -> int | None:
    """Return the number of evaluations of a bracketing solve up to the first one at which Ford's stopping rule stops,
    or None when the rule stops at none of them.

    Ford stops once an evaluation gives ``|f(x)| < eps``, or leaves an interval narrower than ``0.95 * eps``, with
    ``eps = 1e-14 + 2^-53 * max(|a|, |b|, 1)`` for the initial interval ``[a, b]``. This function follows the interval
    through the solve's history: the first 2 evaluations are the interval bounds, and each later evaluation replaces
    the bound whose function value has the same sign.

    Args:
        result: A solve of a bracketing solver, with its history recorded.
    """
    assert result.history is not None
    (lower_x, lower_fx), (upper_x, _) = result.history[0], result.history[1]
    eps = _FORD_TAU + 2.0**-53 * max(abs(lower_x), abs(upper_x), 1.0)
    for n_fevals, (x, fx) in enumerate(result.history[2:], start=3):
        if (fx > 0.0) == (lower_fx > 0.0):
            lower_x, lower_fx = x, fx
        else:
            upper_x = x
        if abs(fx) < eps or abs(upper_x - lower_x) < _FORD_WIDTH_FACTOR * eps:
            return n_fevals
    return None
