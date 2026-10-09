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

# `_DEVIATION_REASONS` holds the rows whose count `CARF` does not reproduce, keyed by function number and interval.
_DEVIATION_REASONS = {
    (1, -1e4, 1e4): _STEP_CHOICE_DEVIATION_REASON,
    (1, -1e10, 1e10): _STEP_CHOICE_DEVIATION_REASON,
    (2, 1e-4, 1e4): _STEP_CHOICE_DEVIATION_REASON,
    (2, 1e-10, 1e10): _STEP_CHOICE_DEVIATION_REASON,
    (2, 1e-12, 1e12): _STEP_CHOICE_DEVIATION_REASON,
    (3, -1e6, 1e6): _STEP_CHOICE_DEVIATION_REASON,
    (3, -1e10, 1e10): _STEP_CHOICE_DEVIATION_REASON,
    (4, -1e4, 1e4): _STEP_CHOICE_DEVIATION_REASON,
    (4, -1e6, 1e6): _STEP_CHOICE_DEVIATION_REASON,
    (4, -1e10, 1e10): _STEP_CHOICE_DEVIATION_REASON,
    (8, 2e-4, 2): _LAST_STEP_DEVIATION_REASON,
    (9, 2e-4, 1): _LAST_STEP_DEVIATION_REASON,
}

# Each row of the paper's Table 4 holds:
# - the function number;
# - the 2 interval bounds;
# - CARF's evaluation count.
TABLE_4 = [
    PaperProblem(
        f"{number}[{a:g},{b:g}]",
        CHANDRUPATLA_FUNCTIONS[number],
        float(a),
        float(b),
        n_fevals=n_fevals,
        n_fevals_tol=None if (number, a, b) in _DEVIATION_REASONS else 0,
        deviation_reason=_DEVIATION_REASONS.get((number, a, b)),
    )
    for number, a, b, n_fevals in [
        (1, 2, 3, 7),
        (1, 1, 10, 9),
        (1, 1, 100, 10),
        (1, -1e4, 1e4, 23),
        (1, -1e10, 1e10, 10),
        (2, 0.5, 1.51, 10),
        (2, 1e-4, 1e4, 19),
        (2, 1e-6, 1e6, 58),
        (2, 1e-10, 1e10, 46),
        (2, 1e-12, 1e12, 57),
        (3, 0, 5, 28),
        (3, -10, 10, 32),
        (3, -1e4, 1e4, 42),
        (3, -1e6, 1e6, 45),
        (3, -1e10, 1e10, 47),
        (4, 0, 5, 18),
        (4, -10, 10, 23),
        (4, -1e4, 1e4, 39),
        (4, -1e6, 1e6, 39),
        (4, -1e10, 1e10, 53),
        (5, -1, 4, 8),
        (5, -2, 5, 16),
        (5, -1, 10, 13),
        (5, -5, 50, 16),
        (5, -10, 100, 22),
        (6, -1, 4, 8),
        (6, -2, 5, 13),
        (6, -1, 10, 3),
        (6, -5, 50, 5),
        (6, -10, 100, 8),
        (7, -1, 4, 9),
        (7, -2, 5, 7),
        (7, -1, 10, 3),
        (7, -5, 50, 13),
        (7, -10, 100, 11),
        (8, 2e-4, 2, 12),
        (8, 2e-4, 3, 13),
        (8, 2e-4, 9, 11),
        (8, 2e-4, 27, 19),
        (8, 2e-4, 81, 26),
        (9, 2e-4, 1, 7),
        (9, 2e-4, 3, 10),
        (9, 2e-4, 9, 8),
        (9, 2e-4, 27, 10),
        (9, 2e-4, 81, 12),
    ]
]
