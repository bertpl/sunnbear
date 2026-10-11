"""This module holds `TABLE_4_1`, the rows of Table 4.1 of Brent's 1973 book that `Brent` can reproduce, with the
book's evaluation counts and tolerances ``t``."""

from tests.solvers.paper_problems import PaperProblem

# The book ran its procedure on an IBM 360, whose hexadecimal arithmetic truncates results where IEEE 754 doubles
# round them.
_HEXADECIMAL_ARITHMETIC_DEVIATION_REASON = (
    "the book's IBM 360 truncates the results of its hexadecimal arithmetic, where IEEE 754 doubles round them"
)

# Each row holds the function, its interval, the book's tolerance ``t`` and its evaluation count. The book's other 3
# rows need the extended exponent range of its procedure ``zero2``, because their functions underflow near the root.
_TABLE_4_1_ROWS = [
    {"name": "x^9[-1,1.1]", "a": -1.0, "b": 1.1, "t": 1e-9, "n_fevals": 81, "n_fevals_tol": 3},
    {"name": "x^9[-1,4]", "a": -1.0, "b": 4.0, "t": 1e-20, "n_fevals": 189, "n_fevals_tol": 2},
]

TABLE_4_1 = [
    (
        PaperProblem(
            name=row["name"],
            f=lambda x: x**9,
            a=row["a"],
            b=row["b"],
            n_fevals=row["n_fevals"],
            n_fevals_tol=row["n_fevals_tol"],
            deviation_reason=_HEXADECIMAL_ARITHMETIC_DEVIATION_REASON,
        ),
        row["t"],
    )
    for row in _TABLE_4_1_ROWS
]
