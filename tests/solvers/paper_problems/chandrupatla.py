"""This module holds the test functions of Chandrupatla's paper, keyed by their number in its Table 1, and the problems
of its Table 2, without results.

Function 7 comes in 2 versions: as the paper prints it, in `CHANDRUPATLA_FUNCTIONS`, and as the paper's BASIC listing
computes it, in `CHANDRUPATLA_BASIC_LISTING_FUNCTIONS`.

Table 2 compares the evaluation counts of the paper's method, Brent's method and bisection on 9 functions, each on 5
intervals. A problem's name holds the function's number and the interval, e.g. ``1[2,3]``.
"""

import math
from dataclasses import replace

from .problem import PaperProblem


def _function_7(x: float) -> float:
    """Return the paper's function 7, ``x * exp(-1 / x^2)``, and 0 at ``x = 0``."""
    if x == 0.0:
        return 0.0
    else:
        return x * math.exp(-1.0 / (x * x))


def _listing_function_7(x: float) -> float:
    """Return the paper's function 7, ``x * exp(-1 / x^2)``, set to 0 where ``|x| < 3.8e-4``, as the paper's BASIC
    listing does."""
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

CHANDRUPATLA_BASIC_LISTING_FUNCTIONS = {**CHANDRUPATLA_FUNCTIONS, 7: _listing_function_7}

# `CHANDRUPATLA_TABLE_2_PROBLEMS_BY_NAME` maps each problem's name to the problem, in the order of the rows of the
# paper's Table 2. The functions are those of the paper's BASIC listing, which produced the table.
CHANDRUPATLA_TABLE_2_PROBLEMS_BY_NAME = {
    problem.name: problem
    for problem in [
        PaperProblem(
            name=f"{row['number']}[{row['a']:g},{row['b']:g}]",
            f=CHANDRUPATLA_BASIC_LISTING_FUNCTIONS[row["number"]],
            a=float(row["a"]),
            b=float(row["b"]),
        )
        for row in [
            {"number": 1, "a": 2, "b": 3},
            {"number": 1, "a": 1, "b": 10},
            {"number": 1, "a": 1, "b": 100},
            {"number": 1, "a": -10000.0, "b": 10000.0},
            {"number": 1, "a": -10000000000.0, "b": 10000000000.0},
            {"number": 2, "a": 0.5, "b": 1.51},
            {"number": 2, "a": 0.0001, "b": 10000.0},
            {"number": 2, "a": 1e-06, "b": 1000000.0},
            {"number": 2, "a": 1e-10, "b": 10000000000.0},
            {"number": 2, "a": 1e-12, "b": 1000000000000.0},
            {"number": 3, "a": 0, "b": 5},
            {"number": 3, "a": -10, "b": 10},
            {"number": 3, "a": -10000.0, "b": 10000.0},
            {"number": 3, "a": -1000000.0, "b": 1000000.0},
            {"number": 3, "a": -10000000000.0, "b": 10000000000.0},
            {"number": 4, "a": 0, "b": 5},
            {"number": 4, "a": -10, "b": 10},
            {"number": 4, "a": -10000.0, "b": 10000.0},
            {"number": 4, "a": -1000000.0, "b": 1000000.0},
            {"number": 4, "a": -10000000000.0, "b": 10000000000.0},
            {"number": 5, "a": -1, "b": 4},
            {"number": 5, "a": -2, "b": 5},
            {"number": 5, "a": -1, "b": 10},
            {"number": 5, "a": -5, "b": 50},
            {"number": 5, "a": -10, "b": 100},
            {"number": 6, "a": -1, "b": 4},
            {"number": 6, "a": -2, "b": 5},
            {"number": 6, "a": -1, "b": 10},
            {"number": 6, "a": -5, "b": 50},
            {"number": 6, "a": -10, "b": 100},
            {"number": 7, "a": -1, "b": 4},
            {"number": 7, "a": -2, "b": 5},
            {"number": 7, "a": -1, "b": 10},
            {"number": 7, "a": -5, "b": 50},
            {"number": 7, "a": -10, "b": 100},
            {"number": 8, "a": 0.0002, "b": 2},
            {"number": 8, "a": 0.0002, "b": 3},
            {"number": 8, "a": 0.0002, "b": 9},
            {"number": 8, "a": 0.0002, "b": 27},
            {"number": 8, "a": 0.0002, "b": 81},
            {"number": 9, "a": 0.0002, "b": 1},
            {"number": 9, "a": 0.0002, "b": 3},
            {"number": 9, "a": 0.0002, "b": 9},
            {"number": 9, "a": 0.0002, "b": 27},
            {"number": 9, "a": 0.0002, "b": 81},
        ]
    ]
}


def chandrupatla_table_2_problems(rows: list[dict]) -> list[tuple[PaperProblem, int]]:
    """Return the problems of the paper's Table 2, each with 1 method's evaluation count from the table, and paired
    with that method's number of bisection switches on it.

    Args:
        rows: 1 dict per row of the table, in the table's order, with the row's ``name``, the method's ``n_fevals``,
            and its ``n_bisection_switches``, which the table prints in parentheses.

    Raises:
        ValueError: If ``rows`` does not name every row of the table, in its order.
    """
    if [row["name"] for row in rows] != list(CHANDRUPATLA_TABLE_2_PROBLEMS_BY_NAME):
        raise ValueError("Give 1 row per row of the paper's Table 2, in the table's order.")
    return [
        (
            replace(CHANDRUPATLA_TABLE_2_PROBLEMS_BY_NAME[row["name"]], n_fevals=row["n_fevals"]),
            row["n_bisection_switches"],
        )
        for row in rows
    ]
