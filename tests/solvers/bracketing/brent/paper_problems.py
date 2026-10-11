"""This module holds `TABLE_4_1_WITH_T`, the rows of Table 4.1 of Brent's 1973 book that `Brent` can reproduce, as
pairs of a `PaperProblem`, which holds the book's evaluation count, and the book's absolute tolerance ``t`` of the
procedure ``zero``."""

from tests.solvers.paper_problems import PaperProblem

# Each row holds:
# - the problem's name and its interval ``a``, ``b``; every row's function is x^9;
# - the book's tolerance ``t``;
# - the book's evaluation count, with the deviation that the test allows.
# The book's other 3 rows of Table 4.1 need the extended exponent range of its procedure ``zero2``, because their
# functions underflow near the root.
TABLE_4_1_WITH_T = [
    (
        PaperProblem(
            name=row["name"],
            f=lambda x: x**9,
            a=row["a"],
            b=row["b"],
            n_fevals=row["n_fevals"],
            n_fevals_tol=row["n_fevals_tol"],
            deviation_reason=(
                "the book's IBM 360 truncates the results of its hexadecimal arithmetic, while IEEE 754 doubles round "
                "them"
            ),
        ),
        row["t"],
    )
    for row in [
        {"name": "x^9[-1,1.1]", "a": -1.0, "b": 1.1, "t": 1e-9, "n_fevals": 81, "n_fevals_tol": 3},
        {"name": "x^9[-1,4]", "a": -1.0, "b": 4.0, "t": 1e-20, "n_fevals": 189, "n_fevals_tol": 2},
    ]
]
