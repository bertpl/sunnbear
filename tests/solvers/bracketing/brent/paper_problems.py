"""This module holds `TABLE_4_1_WITH_T`, the rows of Table 4.1 of Brent's 1973 book that `Brent` can reproduce. Each
row is a pair: a `PaperProblem` that holds the book's evaluation count, and the book's absolute tolerance ``t`` of its
procedure ``zero2``, which the procedure ``zero`` takes too."""

from tests.solvers.paper_problems import PaperProblem

# The docstring of this test package states why the other 3 rows of Table 4.1 are not reproduced.
TABLE_4_1_WITH_T = [
    (
        PaperProblem(
            name=row["name"],
            f=lambda x: x**9,
            a=row["a"],
            b=row["b"],
            n_fevals=row["n_fevals"],
            n_fevals_tol=row["n_fevals_tol"],
            deviation_reason=row["deviation_reason"],
        ),
        row["t"],
    )
    for row in [
        {
            "name": "x^9[-1,1.1]",
            "a": -1.0,
            "b": 1.1,
            "t": 1e-9,
            "n_fevals": 81,
            "n_fevals_tol": 3,
            "deviation_reason": (
                "cause not known: on macOS, the solve takes 78 evaluations with each of 4 ways of computing x^9, and "
                "also in an emulation of the truncating hexadecimal arithmetic of the book's IBM 360"
            ),
        },
        {
            "name": "x^9[-1,4]",
            "a": -1.0,
            "b": 4.0,
            "t": 1e-20,
            "n_fevals": 189,
            "n_fevals_tol": 3,
            "deviation_reason": (
                "the count depends on how x^9 is computed: on macOS, 4 ways of computing x^9 give 187 to 192 "
                "evaluations in float64, and 3 ways give 177 to 189 in an emulation of the truncating hexadecimal "
                "arithmetic of the book's IBM 360; with x**9, the solve takes 191 evaluations on macOS and 186 on "
                "Linux on ARM"
            ),
        },
    ]
]
