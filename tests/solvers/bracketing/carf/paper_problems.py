"""This module holds `TABLE_4`, the 45 cases of Table 4 of the CARF paper, which reuses the functions and intervals of
Chandrupatla's paper, with CARF's evaluation counts in that table."""

from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.chandrupatla import CHANDRUPATLA_FUNCTIONS

# On some of the wide intervals of functions 1 to 4, ``h``, the scaled function value at ``t`` that `CARF`'s docstring
# defines, often lies within rounding error of 0 or 1, the limits that choose the kind of step.
_STEP_CHOICE_DEVIATION = (
    "h lies within rounding error of a limit that chooses the kind of step, so the count depends on how the paper's "
    "code computes the quadratic's root and the power step"
)
_LAST_STEP_DEVIATION = (
    "the last step lands on the other side of the root, or exactly on it, so a 1-ulp difference in that step changes "
    "the count"
)

# The rows whose count `CARF` does not reproduce, keyed by function number and interval.
_DEVIATIONS = {
    (1, -1e4, 1e4): _STEP_CHOICE_DEVIATION,
    (1, -1e10, 1e10): _STEP_CHOICE_DEVIATION,
    (2, 1e-4, 1e4): _STEP_CHOICE_DEVIATION,
    (2, 1e-10, 1e10): _STEP_CHOICE_DEVIATION,
    (2, 1e-12, 1e12): _STEP_CHOICE_DEVIATION,
    (3, -1e6, 1e6): _STEP_CHOICE_DEVIATION,
    (3, -1e10, 1e10): _STEP_CHOICE_DEVIATION,
    (4, -1e4, 1e4): _STEP_CHOICE_DEVIATION,
    (4, -1e6, 1e6): _STEP_CHOICE_DEVIATION,
    (4, -1e10, 1e10): _STEP_CHOICE_DEVIATION,
    (8, 2e-4, 2): _LAST_STEP_DEVIATION,
    (9, 2e-4, 1): _LAST_STEP_DEVIATION,
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
        n_fevals_tol=None if (number, a, b) in _DEVIATIONS else 0,
        deviation=_DEVIATIONS.get((number, a, b)),
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
