"""This module holds the test problems of Table 4 of Ford (1997), without results, and Ford's stopping rule.

Ford's Table 4 compares the iteration counts of several Illinois-type methods, among them the Illinois, Pegasus and
Anderson-Björck methods, on 5 functions, each on 3 intervals. A problem's name holds the function's number in the
paper and the interval, e.g. ``1[0.5,2]``.

The paper stops each solve by a stopping rule of its own, which no sunnbear solver uses;
`assert_n_fevals_at_ford_stop_reproduced` checks a solver's evaluation count at the point where that rule stops.
"""

import math
from dataclasses import replace

from sunnbear.solvers import Solver, SolveResult

from .problem import PaperProblem

# `_MAX_FEVALS_UNDER_FORD_STOPPING_RULE` is the evaluation budget of a solve under Ford's stopping rule; it exceeds
# every count in Ford's Table 4, including the 200 of each row that Ford prints as "200+".
_MAX_FEVALS_UNDER_FORD_STOPPING_RULE = 300

# `F_EQUALS_ZERO_DEVIATION_REASON` explains a count 1 below Ford's on a row where the solve reaches f(x) == 0 early.
F_EQUALS_ZERO_DEVIATION_REASON = (
    "the solve reaches f(x) == 0 one iteration earlier than Ford reports; near the root, the computed function value "
    "is smaller than its rounding error, which differs between Ford's platform and the platform that runs this test"
)


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

# `FORD_TABLE_4_PROBLEMS_BY_NAME` maps each problem's name to the problem, in the order of the rows of Ford's Table 4.
FORD_TABLE_4_PROBLEMS_BY_NAME = {
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


def ford_table_4_problems(rows: list[dict], deviations: dict[str, tuple[int, str]]) -> list[PaperProblem]:
    """Return the problems of Ford's Table 4, each with 1 solver's count from the table, converted to sunnbear's
    evaluation count: Ford's iterations plus the 2 evaluations at the interval bounds.

    Args:
        rows: 1 dict per row of the table, in the table's order, with the row's ``name`` and either Ford's
            ``n_iterations`` or, for a row that Ford prints as "200+", ``n_iterations_strict_lower_bound``.
        deviations: The allowed deviation and its reason, by the name of each row whose count the solver does not
            reproduce exactly.

    Raises:
        ValueError: If ``rows`` does not name every row of the table, in its order.
    """
    if [row["name"] for row in rows] != list(FORD_TABLE_4_PROBLEMS_BY_NAME):
        raise ValueError("Give 1 row per row of Ford's Table 4, in the table's order.")
    problems = []
    for row in rows:
        problem = FORD_TABLE_4_PROBLEMS_BY_NAME[row["name"]]
        if "n_iterations_strict_lower_bound" in row:
            problems.append(replace(problem, n_fevals_strict_lower_bound=row["n_iterations_strict_lower_bound"] + 2))
        else:
            n_fevals_tol, deviation_reason = deviations.get(row["name"], (0, None))
            problems.append(
                replace(
                    problem,
                    n_fevals=row["n_iterations"] + 2,
                    n_fevals_tol=n_fevals_tol,
                    deviation_reason=deviation_reason,
                )
            )
    return problems


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
