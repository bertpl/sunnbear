"""This module holds `TABLE_4`, the cases of Table 4 of the CARF paper with CARF's evaluation count for each. The
table reuses the functions and intervals of Chandrupatla's paper."""

from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.chandrupatla import CHANDRUPATLA_FUNCTIONS

# On some of the wide intervals of functions 1 to 4, `CARF`'s ``h`` (the scaled function value at ``t``, defined in
# `CARF`'s docstring) often lies within rounding error of 0 or 1, the limits that `CARF` compares ``h`` with to choose
# the kind of step.
_STEP_CHOICE_DEVIATION_REASON = (
    "h lies within rounding error of a limit that CARF compares h with to choose the kind of step, so the count "
    "depends on how the paper's code computes 2 values: the root of the quadratic through the 3 points, and the power "
    "step"
)
_LAST_STEP_DEVIATION_REASON = (
    "the last step's x-value lies on the other side of the root, or exactly on it, so a 1-ulp difference in that step "
    "changes the count"
)

# Each row of the paper's Table 4 holds the function number, the 2 interval bounds and CARF's evaluation count; a row
# whose count `CARF` does not reproduce also holds a count tolerance of None and the reason.
TABLE_4 = [
    PaperProblem(
        name=f"{row['number']}[{row['a']:g},{row['b']:g}]",
        f=CHANDRUPATLA_FUNCTIONS[row["number"]],
        a=float(row["a"]),
        b=float(row["b"]),
        n_fevals=row["n_fevals"],
        n_fevals_tol=row.get("n_fevals_tol", 0),
        deviation_reason=row.get("deviation_reason"),
    )
    for row in [
        {"number": 1, "a": 2, "b": 3, "n_fevals": 7},
        {"number": 1, "a": 1, "b": 10, "n_fevals": 9},
        {"number": 1, "a": 1, "b": 100, "n_fevals": 10},
        {
            "number": 1,
            "a": -1e4,
            "b": 1e4,
            "n_fevals": 23,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {
            "number": 1,
            "a": -1e10,
            "b": 1e10,
            "n_fevals": 10,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {"number": 2, "a": 0.5, "b": 1.51, "n_fevals": 10},
        {
            "number": 2,
            "a": 1e-4,
            "b": 1e4,
            "n_fevals": 19,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {"number": 2, "a": 1e-6, "b": 1e6, "n_fevals": 58},
        {
            "number": 2,
            "a": 1e-10,
            "b": 1e10,
            "n_fevals": 46,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {
            "number": 2,
            "a": 1e-12,
            "b": 1e12,
            "n_fevals": 57,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {"number": 3, "a": 0, "b": 5, "n_fevals": 28},
        {"number": 3, "a": -10, "b": 10, "n_fevals": 32},
        {"number": 3, "a": -1e4, "b": 1e4, "n_fevals": 42},
        {
            "number": 3,
            "a": -1e6,
            "b": 1e6,
            "n_fevals": 45,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {
            "number": 3,
            "a": -1e10,
            "b": 1e10,
            "n_fevals": 47,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {"number": 4, "a": 0, "b": 5, "n_fevals": 18},
        {"number": 4, "a": -10, "b": 10, "n_fevals": 23},
        {
            "number": 4,
            "a": -1e4,
            "b": 1e4,
            "n_fevals": 39,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {
            "number": 4,
            "a": -1e6,
            "b": 1e6,
            "n_fevals": 39,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {
            "number": 4,
            "a": -1e10,
            "b": 1e10,
            "n_fevals": 53,
            "n_fevals_tol": None,
            "deviation_reason": _STEP_CHOICE_DEVIATION_REASON,
        },
        {"number": 5, "a": -1, "b": 4, "n_fevals": 8},
        {"number": 5, "a": -2, "b": 5, "n_fevals": 16},
        {"number": 5, "a": -1, "b": 10, "n_fevals": 13},
        {"number": 5, "a": -5, "b": 50, "n_fevals": 16},
        {"number": 5, "a": -10, "b": 100, "n_fevals": 22},
        {"number": 6, "a": -1, "b": 4, "n_fevals": 8},
        {"number": 6, "a": -2, "b": 5, "n_fevals": 13},
        {"number": 6, "a": -1, "b": 10, "n_fevals": 3},
        {"number": 6, "a": -5, "b": 50, "n_fevals": 5},
        {"number": 6, "a": -10, "b": 100, "n_fevals": 8},
        {"number": 7, "a": -1, "b": 4, "n_fevals": 9},
        {"number": 7, "a": -2, "b": 5, "n_fevals": 7},
        {"number": 7, "a": -1, "b": 10, "n_fevals": 3},
        {"number": 7, "a": -5, "b": 50, "n_fevals": 13},
        {"number": 7, "a": -10, "b": 100, "n_fevals": 11},
        {
            "number": 8,
            "a": 2e-4,
            "b": 2,
            "n_fevals": 12,
            "n_fevals_tol": None,
            "deviation_reason": _LAST_STEP_DEVIATION_REASON,
        },
        {"number": 8, "a": 2e-4, "b": 3, "n_fevals": 13},
        {"number": 8, "a": 2e-4, "b": 9, "n_fevals": 11},
        {"number": 8, "a": 2e-4, "b": 27, "n_fevals": 19},
        {"number": 8, "a": 2e-4, "b": 81, "n_fevals": 26},
        {
            "number": 9,
            "a": 2e-4,
            "b": 1,
            "n_fevals": 7,
            "n_fevals_tol": None,
            "deviation_reason": _LAST_STEP_DEVIATION_REASON,
        },
        {"number": 9, "a": 2e-4, "b": 3, "n_fevals": 10},
        {"number": 9, "a": 2e-4, "b": 9, "n_fevals": 8},
        {"number": 9, "a": 2e-4, "b": 27, "n_fevals": 10},
        {"number": 9, "a": 2e-4, "b": 81, "n_fevals": 12},
    ]
]
