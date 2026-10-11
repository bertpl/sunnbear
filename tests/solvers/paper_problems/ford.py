"""This module holds `FordTable4Problem`, the test problems of Table 4 of Ford (1997), and Ford's stopping rule.

Ford's Table 4 compares the iteration counts of several Illinois-type methods, among them the Illinois, Pegasus and
Anderson-Björck methods, on 5 functions, each on 3 intervals. A problem's name holds the function's number in the
paper and the interval, e.g. ``1[0.5,2]``.

The paper stops each solve by a stopping rule of its own, which no sunnbear solver uses;
`assert_n_fevals_at_ford_stop_reproduced` checks a solver's evaluation count at the point where that rule stops.
"""

import math

from sunnbear.solvers import Solver, SolveResult

from .problem import PaperProblem, PaperProblemEnum

# `_MAX_FEVALS_UNDER_FORD_STOPPING_RULE` is the evaluation budget of a solve under Ford's stopping rule; it exceeds
# every count in Ford's Table 4, including the 200 of each row that Ford prints as "200+".
_MAX_FEVALS_UNDER_FORD_STOPPING_RULE = 300


# ==================================================================================================
#  The problems
# ==================================================================================================
_FORD_FUNCTIONS = {
    1: lambda x: math.sin(0.01 / x) - 0.01,
    2: lambda x: 1e-8 * (x - 1.0) * math.prod(x * x + x + i for i in range(1, 11)),
    3: lambda x: math.exp(21000.0 / x) / (1.11e11 * x * x) - 1.0,
    4: lambda x: 2.0 * x * math.exp(-20.0) + 1.0 - 2.0 * math.exp(-20.0 * x),
    5: lambda x: math.exp(1.0 / x - 25.0) - 1.0,
}


class FordTable4Problem(PaperProblemEnum):
    """`FordTable4Problem` holds the 15 problems of Ford's Table 4, in the table's order; a member's name holds the
    function's number and the interval's place among that function's 3 intervals, e.g. ``F1_I1``."""

    F1_I1 = PaperProblem(name="1[0.5,2]", f=_FORD_FUNCTIONS[1], a=0.5, b=2.0)
    F1_I2 = PaperProblem(name="1[0.2,6]", f=_FORD_FUNCTIONS[1], a=0.2, b=6.0)
    F1_I3 = PaperProblem(name="1[0.004,200]", f=_FORD_FUNCTIONS[1], a=0.004, b=200.0)
    F2_I1 = PaperProblem(name="2[0.9,1.1]", f=_FORD_FUNCTIONS[2], a=0.9, b=1.1)
    F2_I2 = PaperProblem(name="2[0.5,1.5]", f=_FORD_FUNCTIONS[2], a=0.5, b=1.5)
    F2_I3 = PaperProblem(name="2[-5,10]", f=_FORD_FUNCTIONS[2], a=-5.0, b=10.0)
    F3_I1 = PaperProblem(name="3[550,560]", f=_FORD_FUNCTIONS[3], a=550.0, b=560.0)
    F3_I2 = PaperProblem(name="3[400,600]", f=_FORD_FUNCTIONS[3], a=400.0, b=600.0)
    F3_I3 = PaperProblem(name="3[350,850]", f=_FORD_FUNCTIONS[3], a=350.0, b=850.0)
    F4_I1 = PaperProblem(name="4[0,1]", f=_FORD_FUNCTIONS[4], a=0.0, b=1.0)
    F4_I2 = PaperProblem(name="4[-0.1,1.5]", f=_FORD_FUNCTIONS[4], a=-0.1, b=1.5)
    F4_I3 = PaperProblem(name="4[-0.5,2]", f=_FORD_FUNCTIONS[4], a=-0.5, b=2.0)
    F5_I1 = PaperProblem(name="5[0.035,0.05]", f=_FORD_FUNCTIONS[5], a=0.035, b=0.05)
    F5_I2 = PaperProblem(name="5[0.03,0.09]", f=_FORD_FUNCTIONS[5], a=0.03, b=0.09)
    F5_I3 = PaperProblem(name="5[0.025,0.5]", f=_FORD_FUNCTIONS[5], a=0.025, b=0.5)


# ==================================================================================================
#  Ford's stopping rule
# ==================================================================================================
def assert_n_fevals_at_ford_stop_reproduced(solver: Solver, problem: PaperProblem) -> None:
    """Assert that ``solver`` takes the problem's published count of evaluations until Ford's stopping rule stops it.

    ``solver`` must be a bracketing solver, because `n_fevals_at_ford_stop` follows the bracketing interval through the
    solve's history. The solve uses ``xtol = 0``, so that the solver runs past the point where Ford's rule stops, and
    stops on its own only on ``f(x) == 0``, where Ford's rule stops too; `n_fevals_at_ford_stop` then finds, in the
    solve's history, the evaluation at which Ford's rule stops.
    """
    result = solver.solve(
        problem.f,
        problem.a,
        problem.b,
        xtol=0.0,
        max_fevals=_MAX_FEVALS_UNDER_FORD_STOPPING_RULE,
        history_enabled=True,
    )
    n_fevals = n_fevals_at_ford_stop(result)
    if n_fevals is None:
        # Ford's rule did not stop the solve within its budget, so the count at which it stops exceeds the budget.
        n_fevals = _MAX_FEVALS_UNDER_FORD_STOPPING_RULE + 1
    problem.assert_n_fevals_reproduced(n_fevals)


def n_fevals_at_ford_stop(result: SolveResult) -> int | None:
    """Return the number of evaluations of a bracketing solve up to and including the first evaluation at which Ford's
    stopping rule stops, or None when the rule stops at no evaluation.

    Ford stops once an evaluation gives ``|f(x)| < eps``, or leaves an interval narrower than ``0.95 * eps``, with
    ``eps = 1e-14 + 2^-53 * max(|a|, |b|, 1)`` for the initial interval ``[a, b]``.

    This function follows the interval through the solve's history: the first 2 evaluations are the interval bounds,
    and each later evaluation replaces the bound whose function value has the same sign.

    Args:
        result: A solve of a bracketing solver, with its history recorded.
    """
    assert result.history is not None
    (lower_x, lower_fx), (upper_x, _) = result.history[0], result.history[1]
    eps = 1e-14 + 2.0**-53 * max(abs(lower_x), abs(upper_x), 1.0)
    for n_fevals, (x, fx) in enumerate(result.history[2:], start=3):
        if (fx > 0.0) == (lower_fx > 0.0):
            lower_x, lower_fx = x, fx
        else:
            upper_x = x
        if abs(fx) < eps or abs(upper_x - lower_x) < 0.95 * eps:
            return n_fevals
    return None
