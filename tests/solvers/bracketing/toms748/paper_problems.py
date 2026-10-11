"""This module holds the published results of Algorithm 748 on the Alefeld-Potra-Shi test problems:

- `AUTHORS_TEST_OUTPUT`, the roots that the authors' code computes with the tolerance ``tol = 0``, as its test
  output prints them;
- `TABLES_IV_TO_VI_BY_K`, the evaluation counts of the paper's Tables IV to VI, keyed by the `TOMS748` parameter
  ``k``, which selects Algorithm 4.1 (``k = 1``) or 4.2 (``k = 2``).
"""

from dataclasses import replace

from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.alefeld_potra_shi import ALEFELD_POTRA_SHI_PROBLEMS

# The authors' test output lists, in the order of their test data, the root that their code prints to 14 significant
# digits for each problem.
PRINTED_ROOTS = {
    "1[n=1]": 1.8954942670340,
    "2[n=1]": 3.0229153472731,
    "3[n=1]": 6.6837535608081,
    "4[n=1]": 11.238701655002,
    "5[n=1]": 19.676000080623,
    "6[n=1]": 29.828227326505,
    "7[n=1]": 41.906116195289,
    "8[n=1]": 55.953595800143,
    "9[n=1]": 71.985665586588,
    "10[n=1]": 90.008868539167,
    "11[n=1]": 110.02653274833,
    "12[n=1]": 0.0,
    "13[n=1]": 0.0,
    "14[n=1]": 0.0,
    "15[n=4]": 0.66874030497642,
    "15[n=6]": 0.76472449133173,
    "15[n=8]": 0.81776543395794,
    "15[n=10]": 0.85133992252078,
    "15[n=12]": 0.87448527222117,
    "16[n=4]": 1.0000000000000,
    "16[n=6]": 1.0000000000000,
    "16[n=8]": 1.0000000000000,
    "16[n=10]": 1.0000000000000,
    "16[n=12]": 1.0000000000000,
    "17[n=8]": 1.0000000000000,
    "17[n=10]": 1.0000000000000,
    "17[n=12]": 1.0000000000000,
    "17[n=14]": 1.0000000000000,
    "18[n=1]": 0.52359877559830,
    "19[n=1]": 0.42247770964124,
    "19[n=2]": 0.30669941048320,
    "19[n=3]": 0.22370545765466,
    "19[n=4]": 0.17171914751951,
    "19[n=5]": 0.13825715505682,
    "19[n=20]": 3.4657359020854e-02,
    "19[n=40]": 1.7328679513999e-02,
    "19[n=60]": 1.1552453009332e-02,
    "19[n=80]": 8.6643397569993e-03,
    "19[n=100]": 6.9314718055995e-03,
    "20[n=5]": 3.8402551840622e-02,
    "20[n=10]": 9.9000099980005e-03,
    "20[n=20]": 2.4937500390620e-03,
    "21[n=2]": 0.50000000000000,
    "21[n=5]": 0.34595481584824,
    "21[n=10]": 0.24512233375331,
    "21[n=15]": 0.19554762353657,
    "21[n=20]": 0.16492095727644,
    "22[n=1]": 0.27550804099948,
    "22[n=2]": 0.13775402049974,
    "22[n=4]": 1.0305283778156e-02,
    "22[n=5]": 3.6171081789041e-03,
    "22[n=8]": 4.1087291849640e-04,
    "22[n=15]": 2.5989575892908e-05,
    "22[n=20]": 7.6685951221853e-06,
    "23[n=1]": 0.40105813754155,
    "23[n=5]": 0.51615351875793,
    "23[n=10]": 0.53952222690842,
    "23[n=15]": 0.54818229434066,
    "23[n=20]": 0.55270466667849,
    "24[n=2]": 0.50000000000000,
    "24[n=5]": 0.20000000000000,
    "24[n=15]": 6.6666666666667e-02,
    "24[n=20]": 5.0000000000000e-02,
    "25[n=2]": 2.0000000000000,
    "25[n=3]": 3.0000000000000,
    "25[n=4]": 4.0000000000000,
    "25[n=5]": 5.0000000000000,
    "25[n=6]": 6.0000000000000,
    "25[n=7]": 7.0000000000000,
    "25[n=9]": 9.0000000000000,
    "25[n=11]": 11.000000000000,
    "25[n=13]": 13.000000000000,
    "25[n=15]": 15.000000000000,
    "25[n=17]": 17.000000000000,
    "25[n=19]": 19.000000000000,
    "25[n=21]": 21.000000000000,
    "25[n=23]": 23.000000000000,
    "25[n=25]": 25.000000000000,
    "25[n=27]": 27.000000000000,
    "25[n=29]": 29.000000000000,
    "25[n=31]": 31.000000000000,
    "25[n=33]": 33.000000000000,
    "26[n=1]": 2.2317679157465e-02,
    "27[n=1]": 0.62380651896161,
    "27[n=2]": 0.62380651896161,
    "27[n=3]": 0.62380651896161,
    "27[n=4]": 0.62380651896161,
    "27[n=5]": 0.62380651896161,
    "27[n=6]": 0.62380651896161,
    "27[n=7]": 0.62380651896161,
    "27[n=8]": 0.62380651896161,
    "27[n=9]": 0.62380651896161,
    "27[n=10]": 0.62380651896161,
    "27[n=11]": 0.62380651896161,
    "27[n=12]": 0.62380651896161,
    "27[n=13]": 0.62380651896161,
    "27[n=14]": 0.62380651896161,
    "27[n=15]": 0.62380651896161,
    "27[n=16]": 0.62380651896161,
    "27[n=17]": 0.62380651896161,
    "27[n=18]": 0.62380651896161,
    "27[n=19]": 0.62380651896161,
    "27[n=20]": 0.62380651896161,
    "27[n=21]": 0.62380651896161,
    "27[n=22]": 0.62380651896161,
    "27[n=23]": 0.62380651896161,
    "27[n=24]": 0.62380651896161,
    "27[n=25]": 0.62380651896161,
    "27[n=26]": 0.62380651896161,
    "27[n=27]": 0.62380651896161,
    "27[n=28]": 0.62380651896161,
    "27[n=29]": 0.62380651896161,
    "27[n=30]": 0.62380651896161,
    "27[n=31]": 0.62380651896161,
    "27[n=32]": 0.62380651896161,
    "27[n=33]": 0.62380651896161,
    "27[n=34]": 0.62380651896161,
    "27[n=35]": 0.62380651896161,
    "27[n=36]": 0.62380651896161,
    "27[n=37]": 0.62380651896161,
    "27[n=38]": 0.62380651896161,
    "27[n=39]": 0.62380651896161,
    "27[n=40]": 0.62380651896161,
    "28[n=20]": 5.9051305594220e-05,
    "28[n=21]": 5.6367155339937e-05,
    "28[n=22]": 5.3916409455592e-05,
    "28[n=23]": 5.1669892394942e-05,
    "28[n=24]": 4.9603096699145e-05,
    "28[n=25]": 4.7695285287639e-05,
    "28[n=26]": 4.5928793239949e-05,
    "28[n=27]": 4.4288479195665e-05,
    "28[n=28]": 4.2761290257883e-05,
    "28[n=29]": 4.1335913915954e-05,
    "28[n=30]": 4.0002497338020e-05,
    "28[n=31]": 3.8752419296207e-05,
    "28[n=32]": 3.7578103559958e-05,
    "28[n=33]": 3.6472865219959e-05,
    "28[n=34]": 3.5430783356532e-05,
    "28[n=35]": 3.4446594929961e-05,
    "28[n=36]": 3.3515605877800e-05,
    "28[n=37]": 3.2633616249437e-05,
    "28[n=38]": 3.1796856858426e-05,
    "28[n=39]": 3.1001935436965e-05,
    "28[n=40]": 3.0245790670210e-05,
    "28[n=100]": 1.2277994232462e-05,
    "28[n=200]": 6.1695393904409e-06,
    "28[n=300]": 4.1198585298293e-06,
    "28[n=400]": 3.0924623877272e-06,
    "28[n=500]": 2.4752044261050e-06,
    "28[n=600]": 2.0633567678513e-06,
    "28[n=700]": 1.7690120078154e-06,
    "28[n=800]": 1.5481615698859e-06,
    "28[n=900]": 1.3763345366022e-06,
    "28[n=1000]": 1.2388385788997e-06,
}

# ``root_rel_tol = 1e-13`` is the precision of a root printed to 14 significant digits.
AUTHORS_TEST_OUTPUT = [
    replace(problem, root=PRINTED_ROOTS[problem.name], root_rel_tol=1e-13) for problem in ALEFELD_POTRA_SHI_PROBLEMS
]


# The paper's Tables IV to VI list the evaluation counts of Algorithms 4.1 (k = 1) and 4.2 (k = 2) on some of the
# authors' test problems at ``tol = 10^-15``, counting the 2 evaluations at the interval bounds.
#
# The paper numbers its problems as its Table I does, not as the authors' test driver does; each row names the
# driver's problem that matches the paper's problem.
_TABLES_IV_TO_VI_ROWS = [
    {"name": "26[n=1]", "paper_label": "Table IV: 13", "n_fevals_k1": 28, "n_fevals_k2": 29},
    {"name": "13[n=1]", "paper_label": "Table V: 3[a=-100,b=-2]", "n_fevals_k1": 25, "n_fevals_k2": 24},
    {"name": "27[n=10]", "paper_label": "Table V: 14[n=10]", "n_fevals_k1": 20, "n_fevals_k2": 19},
    {"name": "27[n=30]", "paper_label": "Table V: 14[n=30]", "n_fevals_k1": 20, "n_fevals_k2": 19},
    {"name": "28[n=30]", "paper_label": "Table V: 15[n=30]", "n_fevals_k1": 29, "n_fevals_k2": 31},
    {"name": "28[n=500]", "paper_label": "Table V: 15[n=500]", "n_fevals_k1": 35, "n_fevals_k2": 35},
    {"name": "1[n=1]", "paper_label": "Table VI: 1", "n_fevals_k1": 10, "n_fevals_k2": 10},
    {"name": "3[n=1]", "paper_label": "Table VI: 2[n=2]", "n_fevals_k1": 15, "n_fevals_k2": 11},
    {"name": "16[n=4]", "paper_label": "Table VI: 4[a=1,n=4]", "n_fevals_k1": 12, "n_fevals_k2": 13},
    {"name": "18[n=1]", "paper_label": "Table VI: 5", "n_fevals_k1": 11, "n_fevals_k2": 10},
    {"name": "19[n=20]", "paper_label": "Table VI: 6[n=20]", "n_fevals_k1": 12, "n_fevals_k2": 11},
    {"name": "20[n=10]", "paper_label": "Table VI: 7[n=10]", "n_fevals_k1": 7, "n_fevals_k2": 7},
    {"name": "21[n=10]", "paper_label": "Table VI: 8[n=10]", "n_fevals_k1": 12, "n_fevals_k2": 11},
    {"name": "22[n=1]", "paper_label": "Table VI: 9[n=1]", "n_fevals_k1": 11, "n_fevals_k2": 9},
    {"name": "23[n=5]", "paper_label": "Table VI: 10[n=5]", "n_fevals_k1": 12, "n_fevals_k2": 9},
    {"name": "24[n=20]", "paper_label": "Table VI: 11[n=20]", "n_fevals_k1": 17, "n_fevals_k2": 18},
    {"name": "25[n=3]", "paper_label": "Table VI: 12[n=3]", "n_fevals_k1": 6, "n_fevals_k2": 5},
]

_UNDERFLOW_DEVIATION_REASON = (
    "the function underflows to 0 on an interval around its root at 0, so the count depends on where the platform's "
    "exp underflows; the paper's Section 6 states that how this function is coded changes the results"
)
_PLATFORM_DEVIATION_REASON = (
    "the paper's platform presumably has library functions that round the function values differently from those of "
    "the platform that runs this test"
)
_REBUILT_ALGORITHM_4_1_DEVIATION_REASON = (
    "the authors' code implements only Algorithm 4.2, so `TOMS748` builds Algorithm 4.1 from the authors' "
    "subroutines, and the authors' own implementation of Algorithm 4.1 may differ in details that the paper does not "
    "state"
)
# `_TABLES_IV_TO_VI_DEVIATIONS` lists the rows whose count `TOMS748` does not reproduce exactly. It maps the test
# driver's problem name and ``k`` to the allowed deviation between the measured and the paper's count (None: the
# count is not checked) and the reason for that deviation.
_TABLES_IV_TO_VI_DEVIATIONS = {
    ("26[n=1]", 1): (None, _UNDERFLOW_DEVIATION_REASON),
    ("26[n=1]", 2): (None, _UNDERFLOW_DEVIATION_REASON),
    ("13[n=1]", 1): (1, _REBUILT_ALGORITHM_4_1_DEVIATION_REASON),
    ("3[n=1]", 1): (2, _REBUILT_ALGORITHM_4_1_DEVIATION_REASON),
    ("28[n=30]", 2): (1, _PLATFORM_DEVIATION_REASON),
}

_PROBLEMS_BY_NAME = {problem.name: problem for problem in ALEFELD_POTRA_SHI_PROBLEMS}


def _tables_iv_to_vi_problem(row: dict, k: int) -> PaperProblem:
    """Return the test driver's problem that ``row`` names, with the paper's evaluation count for ``k`` and the allowed
    deviation from that count, if any."""
    n_fevals_tol, deviation_reason = _TABLES_IV_TO_VI_DEVIATIONS.get((row["name"], k), (0, None))
    return replace(
        _PROBLEMS_BY_NAME[row["name"]],
        n_fevals=row[f"n_fevals_k{k}"],
        n_fevals_tol=n_fevals_tol,
        deviation_reason=deviation_reason,
    )


# `TABLES_IV_TO_VI_BY_K` maps ``k`` to the problems of the paper's Tables IV to VI, each with the paper's count for
# that k.
TABLES_IV_TO_VI_BY_K = {k: [_tables_iv_to_vi_problem(row, k) for row in _TABLES_IV_TO_VI_ROWS] for k in (1, 2)}
