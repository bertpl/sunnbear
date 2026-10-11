"""This module holds the problems on which third parties publish evaluation counts for Brent's method, each with
the published count for `Brent`:

- `CHANDRUPATLA_TABLE_2` and `CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES`: the column "Brent's" of Table 2 of
  Chandrupatla (1997);
- `ALEFELD_POTRA_SHI_TABLES_IV_TO_VI`: the column "BR" of Tables IV to VI of Alefeld, Potra and Shi (1995);
- `ANDERSON_BJORCK_EXAMPLES_SINGLE_PRECISION`: the column "Brent" of Examples 1 to 7 of Anderson and Björck (1973).
"""

from dataclasses import replace

from tests.solvers.paper_problems.alefeld_potra_shi import (
    ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME,
    TABLES_IV_TO_VI_PAPER_LABELS,
)
from tests.solvers.paper_problems.anderson_bjorck import ANDERSON_BJORCK_EXAMPLES
from tests.solvers.paper_problems.chandrupatla import chandrupatla_table_2_problems

# ==================================================================================================
#  Chandrupatla (1997), Table 2
# ==================================================================================================
# `_CHANDRUPATLA_TABLE_2_ROWS` holds the rows of the paper's Table 2, with the evaluation count of Brent's method,
# followed in the table by the number of times that it switches to bisection, in parentheses.
_CHANDRUPATLA_TABLE_2_ROWS = [
    {"name": "1[2,3]", "n_fevals": 7, "n_bisection_switches": 0},
    {"name": "1[1,10]", "n_fevals": 13, "n_bisection_switches": 2},
    {"name": "1[1,100]", "n_fevals": 14, "n_bisection_switches": 2},
    {"name": "1[-10000,10000]", "n_fevals": 34, "n_bisection_switches": 13},
    {"name": "1[-1e+10,1e+10]", "n_fevals": 74, "n_bisection_switches": 34},
    {"name": "2[0.5,1.51]", "n_fevals": 9, "n_bisection_switches": 1},
    {"name": "2[0.0001,10000]", "n_fevals": 23, "n_bisection_switches": 14},
    {"name": "2[1e-06,1e+06]", "n_fevals": 28, "n_bisection_switches": 20},
    {"name": "2[1e-10,1e+10]", "n_fevals": 43, "n_bisection_switches": 33},
    {"name": "2[1e-12,1e+12]", "n_fevals": 49, "n_bisection_switches": 40},
    {"name": "3[0,5]", "n_fevals": 49, "n_bisection_switches": 13},
    {"name": "3[-10,10]", "n_fevals": 63, "n_bisection_switches": 15},
    {"name": "3[-10000,10000]", "n_fevals": 86, "n_bisection_switches": 26},
    {"name": "3[-1e+06,1e+06]", "n_fevals": 101, "n_bisection_switches": 32},
    {"name": "3[-1e+10,1e+10]", "n_fevals": 101, "n_bisection_switches": 32},
    {"name": "4[0,5]", "n_fevals": 50, "n_bisection_switches": 13},
    {"name": "4[-10,10]", "n_fevals": 50, "n_bisection_switches": 13},
    {"name": "4[-10000,10000]", "n_fevals": 84, "n_bisection_switches": 24},
    {"name": "4[-1e+06,1e+06]", "n_fevals": 105, "n_bisection_switches": 31},
    {"name": "4[-1e+10,1e+10]", "n_fevals": 146, "n_bisection_switches": 46},
    {"name": "5[-1,4]", "n_fevals": 53, "n_bisection_switches": 15},
    {"name": "5[-2,5]", "n_fevals": 54, "n_bisection_switches": 15},
    {"name": "5[-1,10]", "n_fevals": 58, "n_bisection_switches": 17},
    {"name": "5[-5,50]", "n_fevals": 64, "n_bisection_switches": 19},
    {"name": "5[-10,100]", "n_fevals": 66, "n_bisection_switches": 19},
    {"name": "6[-1,4]", "n_fevals": 53, "n_bisection_switches": 16},
    {"name": "6[-2,5]", "n_fevals": 56, "n_bisection_switches": 17},
    {"name": "6[-1,10]", "n_fevals": 59, "n_bisection_switches": 18},
    {"name": "6[-5,50]", "n_fevals": 66, "n_bisection_switches": 20},
    {"name": "6[-10,100]", "n_fevals": 63, "n_bisection_switches": 19},
    {"name": "7[-1,4]", "n_fevals": 18, "n_bisection_switches": 5},
    {"name": "7[-2,5]", "n_fevals": 21, "n_bisection_switches": 6},
    {"name": "7[-1,10]", "n_fevals": 24, "n_bisection_switches": 7},
    {"name": "7[-5,50]", "n_fevals": 27, "n_bisection_switches": 8},
    {"name": "7[-10,100]", "n_fevals": 33, "n_bisection_switches": 10},
    {"name": "8[0.0002,2]", "n_fevals": 9, "n_bisection_switches": 1},
    {"name": "8[0.0002,3]", "n_fevals": 11, "n_bisection_switches": 2},
    {"name": "8[0.0002,9]", "n_fevals": 12, "n_bisection_switches": 3},
    {"name": "8[0.0002,27]", "n_fevals": 14, "n_bisection_switches": 5},
    {"name": "8[0.0002,81]", "n_fevals": 16, "n_bisection_switches": 7},
    {"name": "9[0.0002,1]", "n_fevals": 7, "n_bisection_switches": 0},
    {"name": "9[0.0002,3]", "n_fevals": 9, "n_bisection_switches": 1},
    {"name": "9[0.0002,9]", "n_fevals": 14, "n_bisection_switches": 3},
    {"name": "9[0.0002,27]", "n_fevals": 18, "n_bisection_switches": 4},
    {"name": "9[0.0002,81]", "n_fevals": 19, "n_bisection_switches": 5},
]

# Each pair holds a problem of Table 2, with the count of Brent's method, and the number of bisection switches on it.
CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES = chandrupatla_table_2_problems(_CHANDRUPATLA_TABLE_2_ROWS)

CHANDRUPATLA_TABLE_2 = [problem for problem, _ in CHANDRUPATLA_TABLE_2_WITH_N_BISECTION_SWITCHES]


# ==================================================================================================
#  Alefeld, Potra and Shi (1995), Tables IV to VI
# ==================================================================================================
# `_ALEFELD_POTRA_SHI_N_FEVALS` maps the name of each problem of `TABLES_IV_TO_VI_PAPER_LABELS` to the evaluation count
# of the column "BR", which counts the 2 evaluations at the interval bounds.
_ALEFELD_POTRA_SHI_N_FEVALS = {
    "26[n=1]": 23,
    "13[n=1]": 19,
    "27[n=10]": 21,
    "27[n=30]": 21,
    "28[n=30]": 36,
    "28[n=500]": 39,
    "1[n=1]": 9,
    "3[n=1]": 10,
    "16[n=4]": 15,
    "18[n=1]": 10,
    "19[n=20]": 13,
    "20[n=10]": 9,
    "21[n=10]": 11,
    "22[n=1]": 10,
    "23[n=5]": 9,
    "24[n=20]": 14,
    "25[n=3]": 10,
}

# `_ALEFELD_POTRA_SHI_DEVIATIONS` maps the name of each problem whose count `Brent` does not reproduce exactly to the
# allowed deviation (None: the count is not checked) and its reason.
_ALEFELD_POTRA_SHI_DEVIATIONS = {
    "26[n=1]": (
        None,
        "the function underflows to 0 on an interval around its root at 0, so the count depends on where the "
        "platform's exp underflows; the paper's Section 6 states that how this function is coded changes the results",
    ),
}

ALEFELD_POTRA_SHI_TABLES_IV_TO_VI = [
    replace(
        ALEFELD_POTRA_SHI_PROBLEMS_BY_NAME[name],
        n_fevals=_ALEFELD_POTRA_SHI_N_FEVALS[name],
        n_fevals_tol=_ALEFELD_POTRA_SHI_DEVIATIONS.get(name, (0, None))[0],
        deviation_reason=_ALEFELD_POTRA_SHI_DEVIATIONS.get(name, (0, None))[1],
    )
    for name in TABLES_IV_TO_VI_PAPER_LABELS
]


# ==================================================================================================
#  Anderson and Björck (1973), Examples 1 to 7
# ==================================================================================================
# `_ANDERSON_BJORCK_N_ITERATIONS` maps the name of each example to the iteration count of the column "Brent", from the
# paper's runs in single precision.
_ANDERSON_BJORCK_N_ITERATIONS = {
    "1": 6,
    "2[n=1]": 5,
    "2[n=5]": 8,
    "2[n=15]": 9,
    "2[n=20]": 9,
    "3[n=2]": 7,
    "3[n=5]": 6,
    "3[n=15]": 5,
    "3[n=20]": 5,
    "4[n=2]": 1,
    "4[n=5]": 6,
    "4[n=15]": 8,
    "4[n=20]": 10,
    "5[n=2]": 8,
    "5[n=5]": 5,
    "5[n=15]": 4,
    "5[n=20]": 4,
    "6[n=1]": 6,
    "6[n=5]": 6,
    "6[n=10]": 6,
    "6[n=15]": 9,
    "6[n=20]": 10,
    "7[n=2]": 3,
    "7[n=5]": 10,
    "7[n=15]": 9,
    "7[n=20]": 11,
}

# `_ANDERSON_BJORCK_DEVIATION_REASON` explains each count that `Brent` does not reproduce exactly.
_ANDERSON_BJORCK_DEVIATION_REASON = (
    "the paper ran the examples in the 27-bit single precision of the UNIVAC 1108, which rounds the iterates near the "
    "stop differently from float64"
)
_ANDERSON_BJORCK_DEVIATING_NAMES = {"2[n=5]", "5[n=2]", "7[n=2]", "7[n=15]"}

ANDERSON_BJORCK_EXAMPLES_SINGLE_PRECISION = [
    replace(
        problem,
        n_fevals=_ANDERSON_BJORCK_N_ITERATIONS[problem.name] + 2,
        n_fevals_tol=1 if problem.name in _ANDERSON_BJORCK_DEVIATING_NAMES else 0,
        deviation_reason=(
            _ANDERSON_BJORCK_DEVIATION_REASON if problem.name in _ANDERSON_BJORCK_DEVIATING_NAMES else None
        ),
    )
    for problem in ANDERSON_BJORCK_EXAMPLES
]
