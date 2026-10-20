"""This module holds the 48 test problems of Ellithy (2026) and the article's iteration counts of its 4 methods on them:

- `PROBLEMS_BY_NUMBER`, the problems of the article's section 5.4, without results, keyed by their number in the
  article;
- `TABLE_12_BY_VARIANT`, the problems of Table 12, each with the table's iteration count for the method of each
  variant of `Ellithy`, and `TABLE_12_FIXED_DELTA_PROBLEM_NAMES`, the problems on which that count reproduces only with
  a fixed ``delta = 1e-4``;
- `TABLES_2_TO_5_BY_VARIANT`, the problems of the case studies in Tables 2 to 5, with their iteration counts;
- `TABLE_7_BY_VARIANT`, the statistics of the iteration counts in Table 7.

The functions follow the article's section 5.4. The authors' code defines 2 constants in a different form, with no
effect on any count: for f43 the article prints ``2.7e-5`` where the code has ``0.000027027``, and for f45 it prints
``24.618`` where the code has ``0.08206 * 300``, which evaluates to the same float64.
"""

import math
from dataclasses import replace

from sunnbear.solvers import EllithyVariant
from tests.solvers.paper_problems import PaperProblem

# ==================================================================================================
#  The problems
# ==================================================================================================
PROBLEMS_BY_NUMBER = {
    1: PaperProblem(name="f1", f=lambda x: x * math.exp(x) - 7.0, a=1.0, b=2.0),
    2: PaperProblem(name="f2", f=lambda x: x**3 - x - 1.0, a=1.0, b=2.0),
    3: PaperProblem(name="f3", f=lambda x: x**2 - x - 2.0, a=1.0, b=4.0),
    4: PaperProblem(name="f4", f=lambda x: x - math.cos(x), a=0.0, b=1.0),
    5: PaperProblem(name="f5", f=lambda x: x**2 - 10.0, a=3.0, b=4.0),
    6: PaperProblem(name="f6", f=lambda x: math.sin(x) - x**2, a=0.5, b=1.0),
    7: PaperProblem(name="f7", f=lambda x: x + math.log(x), a=0.1, b=1.0),
    8: PaperProblem(name="f8", f=lambda x: math.exp(x) - 3.0 * x - 2.0, a=2.0, b=3.0),
    9: PaperProblem(name="f9", f=lambda x: x**2 + math.exp(x / 2.0) - 5.0, a=1.0, b=2.0),
    10: PaperProblem(name="f10", f=lambda x: x * math.sin(x) - 1.0, a=0.0, b=2.0),
    11: PaperProblem(name="f11", f=lambda x: x * math.cos(x) + 1.0, a=-2.0, b=4.0),
    12: PaperProblem(name="f12", f=lambda x: x**10 - 1.0, a=0.0, b=1.3),
    13: PaperProblem(name="f13", f=lambda x: x**2 + 2.0 * x - 7.0, a=1.0, b=3.0),
    14: PaperProblem(name="f14", f=lambda x: x**3 - 2.0 * x - 5.0, a=2.0, b=3.0),
    15: PaperProblem(name="f15", f=lambda x: math.exp(x) - 3.0 * x**2, a=0.0, b=1.0),
    16: PaperProblem(name="f16", f=lambda x: math.sin(10.0 * x) - 0.5 * x, a=0.1, b=0.4),
    17: PaperProblem(name="f17", f=lambda x: x - 0.8 * math.sin(x) - 1.2, a=1.0, b=3.0),
    18: PaperProblem(name="f18", f=lambda x: x**2 - math.exp(x) - 3.0 * x + 2.0, a=0.0, b=1.0),
    19: PaperProblem(name="f19", f=lambda x: (x - 1.0) ** 3 + 4.0 * (x - 1.0) ** 2 - 10.0, a=0.0, b=3.0),
    20: PaperProblem(name="f20", f=lambda x: math.exp(x**2) - math.exp(math.sqrt(2.0) * x), a=0.5, b=1.5),
    21: PaperProblem(name="f21", f=lambda x: (x**2 - 4.0) * (x + 1.5) * (x - 0.5), a=0.0, b=2.0),
    22: PaperProblem(name="f22", f=lambda x: x**3 - 3.0 * x**2 - 4.0 * x + 13.0, a=-3.0, b=-2.0),
    23: PaperProblem(name="f23", f=lambda x: -0.9 * x**2 + 1.7 * x + 2.5, a=2.8, b=3.0),
    24: PaperProblem(name="f24", f=lambda x: 1.0 - 0.61 * x, a=1.5, b=2.0),
    25: PaperProblem(name="f25", f=lambda x: x**2 * abs(math.sin(x)) - 4.1, a=0.0, b=4.0),
    26: PaperProblem(name="f26", f=lambda x: x**5 - 3.0 * x**4 + 25.0, a=-3.0, b=-1.0),
    27: PaperProblem(name="f27", f=lambda x: x**4 - 2.0 * x**2 - 4.0, a=1.0, b=3.0),
    28: PaperProblem(name="f28", f=lambda x: x - 0.5 * math.sin(x) - 1.0, a=0.0, b=3.0),
    29: PaperProblem(name="f29", f=lambda x: math.exp(-x) - math.cos(3.0 * x) - 0.5, a=0.0, b=1.0),
    30: PaperProblem(name="f30", f=lambda x: math.prod(x - k for k in range(1, 21)), a=0.0, b=1.5),
    31: PaperProblem(name="f31", f=lambda x: math.prod(x - k for k in range(1, 21)), a=19.0, b=21.0),
    32: PaperProblem(name="f32", f=lambda x: x**4 + 2.0 * x**2 - x - 1.0, a=-0.5, b=0.0),
    33: PaperProblem(name="f33", f=lambda x: x**4 - 10.0 * x**3 + 35.0 * x**2 - 50.0 * x + 24.0, a=0.0, b=1.5),
    34: PaperProblem(name="f34", f=lambda x: 4.0 * math.sin(x) - x + 1.0, a=-1.0, b=0.0),
    35: PaperProblem(name="f35", f=lambda x: x**25 - 1.0, a=0.0, b=2.0),
    36: PaperProblem(name="f36", f=lambda x: (x - 1.8) ** 6 * (x - 1.81), a=0.0, b=2.0),
    37: PaperProblem(name="f37", f=lambda x: math.sin(20.0 * x) - 0.3 * x, a=0.05, b=0.25),
    38: PaperProblem(name="f38", f=lambda x: x**4 + 2.0 * x**3 - 13.0 * x**2 - 14.0 * x + 24.0, a=-3.0, b=1.0),
    39: PaperProblem(name="f39", f=lambda x: math.exp(x**2) - math.exp(1.2 * x), a=0.0, b=2.0),
    40: PaperProblem(name="f40", f=lambda x: x**5 - 3.0 * x**4 + 2.0 * x**3 - x + 0.1, a=-1.0, b=3.0),
    41: PaperProblem(name="f41", f=lambda x: (x + 0.3) ** 7 - 0.01, a=-2.0, b=1.0),
    42: PaperProblem(name="f42", f=lambda x: x**6 - 8.0 * x**5 + 24.0 * x**4 - 32.0 * x**3 + 16.0 * x**2, a=0.0, b=4.0),
    43: PaperProblem(
        name="f43",
        f=lambda x: -2.0 * math.log10(2.7e-5 + 2.51 / (1e7 * math.sqrt(x))) - 1.0 / math.sqrt(x),
        a=0.008,
        b=0.03,
    ),
    44: PaperProblem(name="f44", f=lambda x: x - 0.99 * math.sin(x) - 2.0, a=2.0, b=3.0),
    45: PaperProblem(name="f45", f=lambda x: (10.0 + 3.592 / x**2) * (x - 0.04267) - 24.618, a=2.0, b=3.0),
    46: PaperProblem(name="f46", f=lambda x: x * math.exp(x / 2.0) - 1.5, a=0.0, b=1.0),
    47: PaperProblem(name="f47", f=lambda x: math.cos(x) + (1.0 - math.cos(x)) ** 2 - 0.05 * x**2, a=3.0, b=6.0),
    48: PaperProblem(name="f48", f=lambda x: 0.05 - x**3 / ((1.0 - x) * (0.8 - 2.0 * x) ** 2), a=0.01, b=0.3),
}


# ==================================================================================================
#  Table 12
# ==================================================================================================
# Each row holds a problem's number and the iteration count of each method in Table 12, keyed by the value of the
# variant of `Ellithy` that implements the method: Opt.BF under "bf", Opt.BFMS under "bfms", and so on.
_TABLE_12_ROWS = [
    {"number": 1, "bf": 9, "bfms": 3, "tf": 7, "tfms": 3},
    {"number": 2, "bf": 8, "bfms": 3, "tf": 5, "tfms": 3},
    {"number": 3, "bf": 8, "bfms": 3, "tf": 1, "tfms": 1},
    {"number": 4, "bf": 7, "bfms": 3, "tf": 6, "tfms": 3},
    {"number": 5, "bf": 7, "bfms": 3, "tf": 6, "tfms": 3},
    {"number": 6, "bf": 8, "bfms": 3, "tf": 7, "tfms": 3},
    {"number": 7, "bf": 6, "bfms": 3, "tf": 6, "tfms": 3},
    {"number": 8, "bf": 9, "bfms": 3, "tf": 7, "tfms": 3},
    {"number": 9, "bf": 8, "bfms": 3, "tf": 5, "tfms": 3},
    {"number": 10, "bf": 5, "bfms": 3, "tf": 5, "tfms": 3},
    {"number": 11, "bf": 8, "bfms": 3, "tf": 6, "tfms": 3},
    {"number": 12, "bf": 11, "bfms": 4, "tf": 8, "tfms": 5},
    {"number": 13, "bf": 7, "bfms": 3, "tf": 7, "tfms": 3},
    {"number": 14, "bf": 9, "bfms": 3, "tf": 7, "tfms": 3},
    {"number": 15, "bf": 7, "bfms": 3, "tf": 6, "tfms": 3},
    {"number": 16, "bf": 5, "bfms": 3, "tf": 4, "tfms": 2},
    {"number": 17, "bf": 6, "bfms": 3, "tf": 7, "tfms": 3},
    {"number": 18, "bf": 6, "bfms": 3, "tf": 6, "tfms": 2},
    {"number": 19, "bf": 9, "bfms": 4, "tf": 7, "tfms": 3},
    {"number": 20, "bf": 9, "bfms": 4, "tf": 7, "tfms": 4},
    {"number": 21, "bf": 1, "bfms": 1, "tf": 1, "tfms": 1},
    {"number": 22, "bf": 10, "bfms": 3, "tf": 7, "tfms": 3},
    {"number": 23, "bf": 6, "bfms": 2, "tf": 4, "tfms": 2},
    {"number": 24, "bf": 1, "bfms": 1, "tf": 1, "tfms": 1},
    {"number": 25, "bf": 9, "bfms": 4, "tf": 7, "tfms": 4},
    {"number": 26, "bf": 9, "bfms": 4, "tf": 7, "tfms": 4},
    {"number": 27, "bf": 9, "bfms": 4, "tf": 8, "tfms": 3},
    {"number": 28, "bf": 4, "bfms": 2, "tf": 7, "tfms": 3},
    {"number": 29, "bf": 6, "bfms": 3, "tf": 6, "tfms": 3},
    {"number": 30, "bf": 11, "bfms": 5, "tf": 1, "tfms": 1},
    {"number": 31, "bf": 1, "bfms": 1, "tf": 1, "tfms": 1},
    {"number": 32, "bf": 6, "bfms": 3, "tf": 5, "tfms": 3},
    {"number": 33, "bf": 10, "bfms": 4, "tf": 1, "tfms": 1},
    {"number": 34, "bf": 7, "bfms": 3, "tf": 5, "tfms": 2},
    {"number": 35, "bf": 1, "bfms": 1, "tf": 9, "tfms": 6},
    {"number": 36, "bf": 6, "bfms": 6, "tf": 4, "tfms": 4},
    {"number": 37, "bf": 5, "bfms": 3, "tf": 4, "tfms": 3},
    {"number": 38, "bf": 1, "bfms": 1, "tf": 1, "tfms": 1},
    {"number": 39, "bf": 1, "bfms": 1, "tf": 1, "tfms": 1},
    {"number": 40, "bf": 12, "bfms": 5, "tf": 9, "tfms": 4},
    {"number": 41, "bf": 9, "bfms": 5, "tf": 8, "tfms": 5},
    {"number": 42, "bf": 1, "bfms": 1, "tf": 1, "tfms": 1},
    {"number": 43, "bf": 8, "bfms": 4, "tf": 7, "tfms": 4},
    {"number": 44, "bf": 7, "bfms": 2, "tf": 5, "tfms": 3},
    {"number": 45, "bf": 5, "bfms": 2, "tf": 5, "tfms": 2},
    {"number": 46, "bf": 6, "bfms": 3, "tf": 6, "tfms": 3},
    {"number": 47, "bf": 8, "bfms": 4, "tf": 7, "tfms": 3},
    {"number": 48, "bf": 9, "bfms": 4, "tf": 6, "tfms": 4},
]

# `TABLE_12_BY_VARIANT` maps each variant to the table's problems, in the table's order, each with the table's iteration
# count for the variant's method.
TABLE_12_BY_VARIANT = {
    variant: [replace(PROBLEMS_BY_NUMBER[row["number"]], n_iterations=row[variant]) for row in _TABLE_12_ROWS]
    for variant in EllithyVariant
}

# On these problems, the count of Opt.BFMS or Opt.TFMS in Table 12 reproduces only with a fixed delta = 1e-4, and the
# article's adaptive delta gives 1 iteration fewer.
TABLE_12_FIXED_DELTA_PROBLEM_NAMES = {
    EllithyVariant.BFMS: frozenset(f"f{number}" for number in (4, 5, 7, 10, 16, 18, 19, 34, 37, 43, 47)),
    EllithyVariant.TFMS: frozenset(
        f"f{number}" for number in (2, 4, 5, 9, 10, 12, 13, 20, 22, 26, 29, 32, 35, 37, 43, 44, 46, 48)
    ),
}


# ==================================================================================================
#  Tables 2 to 5 and 7
# ==================================================================================================
# Each row holds the problem of 1 case study, in the order of Tables 2 to 5, and the iteration count of each method in
# that table, keyed as in `_TABLE_12_ROWS`.
_TABLES_2_TO_5_ROWS = [
    {"number": 19, "bf": 9, "bfms": 3, "tf": 7, "tfms": 3},
    {"number": 44, "bf": 7, "bfms": 2, "tf": 5, "tfms": 2},
    {"number": 30, "bf": 11, "bfms": 5, "tf": 1, "tfms": 1},
    {"number": 48, "bf": 9, "bfms": 4, "tf": 6, "tfms": 3},
]

# `TABLES_2_TO_5_BY_VARIANT` maps each variant to the problems of Tables 2 to 5, each with the table's iteration count
# for the variant's method.
TABLES_2_TO_5_BY_VARIANT = {
    variant: [replace(PROBLEMS_BY_NUMBER[row["number"]], n_iterations=row[variant]) for row in _TABLES_2_TO_5_ROWS]
    for variant in EllithyVariant
}

# `TABLE_7_BY_VARIANT` maps each variant to Table 7's statistics of its method's iteration counts on the 48 problems.
# The table rounds the mean and the standard deviation to 9 decimals.
TABLE_7_BY_VARIANT = {
    EllithyVariant.BF: {"mean": 6.6875, "min": 1, "max": 12, "median": 7, "std_dev": 2.895086852},
    EllithyVariant.BFMS: {"mean": 2.791666667, "min": 1, "max": 6, "median": 3, "std_dev": 1.171864647},
    EllithyVariant.TF: {"mean": 5.291666667, "min": 1, "max": 9, "median": 6, "std_dev": 2.362542878},
    EllithyVariant.TFMS: {"mean": 2.4375, "min": 1, "max": 5, "median": 2, "std_dev": 1.018706326},
}
