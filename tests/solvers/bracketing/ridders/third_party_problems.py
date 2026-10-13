"""This module holds the test problems of Table 2 of Ganchovski et al. (2026), for 2 variants of `Ridders`:

- `GANCHOVSKI_ET_AL_TABLE_2_COMMONS_MATH`, for the "commons_math" variant, whose stopping rule is that of the paper's
  C# code;
- `GANCHOVSKI_ET_AL_TABLE_2_SCIPY`, for the "scipy" variant.

Each problem holds the count of the column "Rid" and Ridders' root in the paper's supplementary results, except where a
row states another root.
"""

from dataclasses import replace

from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ganchovski_et_al import GanchovskiEtAlTable2Problem, ganchovski_et_al_stop_width

# `_ROOT_AT_MIDPOINT_DEVIATION_REASON` and `_ITERATE_FORMULA_DEVIATION_REASON` each explain why the evaluation count of
# the "commons_math" variant of `Ridders` deviates from the column "Rid" of Ganchovski et al.'s Table 2. That variant
# shares the stopping rule of the paper's C# code, so each reason is a difference in what the 2 implementations compute.
_ROOT_AT_MIDPOINT_DEVIATION_REASON = (
    "the function value at a midpoint is exactly 0: the solve stops there, while the paper's C# code takes a step of 0 "
    "from the midpoint and evaluates the same x-value again"
)
_ITERATE_FORMULA_DEVIATION_REASON = (
    "the paper's C# code computes the iterate as x1 + (x1 - x0) * sign(f0) * f1 / sqrt(f1^2 - f0 * f2); in exact "
    "arithmetic that equals the formula that `Ridders` uses, but the 2 forms round differently in their last bits, "
    "which changes the iterates at a tolerance near 1e-14"
)

GANCHOVSKI_ET_AL_TABLE_2_COMMONS_MATH = [
    GanchovskiEtAlTable2Problem.F01.with_n_fevals_and_root(
        4,
        root=1.0,
        deviation=1,
        reason=_ROOT_AT_MIDPOINT_DEVIATION_REASON,
    ),
    GanchovskiEtAlTable2Problem.F02.with_n_fevals_and_root(16, root=0.399422291710968),
    GanchovskiEtAlTable2Problem.F03.with_n_fevals_and_root(14, root=0.804133097503664),
    GanchovskiEtAlTable2Problem.F04.with_n_fevals_and_root(12, root=-1.0),
    GanchovskiEtAlTable2Problem.F05.with_n_fevals_and_root(14, root=2.09455148154232),
    GanchovskiEtAlTable2Problem.F06.with_n_fevals_and_root(14, root=0.138257155056824),
    GanchovskiEtAlTable2Problem.F07.with_n_fevals_and_root(14, root=0.0693140886870234),
    GanchovskiEtAlTable2Problem.F08.with_n_fevals_and_root(12, root=0.0346573590208538),
    GanchovskiEtAlTable2Problem.F09.with_n_fevals_and_root(16, root=0.109611796797792),
    GanchovskiEtAlTable2Problem.F10.with_n_fevals_and_root(
        16,
        root=0.0524786034368101,
        deviation=2,
        reason=_ITERATE_FORMULA_DEVIATION_REASON,
    ),
    GanchovskiEtAlTable2Problem.F11.with_n_fevals_and_root(16, root=0.0256237476199882),
    GanchovskiEtAlTable2Problem.F12.with_n_fevals_and_root(14, root=0.345954815848242),
    GanchovskiEtAlTable2Problem.F13.with_n_fevals_and_root(16, root=0.245122333753307),
    GanchovskiEtAlTable2Problem.F14.with_n_fevals_and_root(16, root=0.16492095727644),
    GanchovskiEtAlTable2Problem.F15.with_n_fevals_and_root(12, root=0.00361710817890406),
    GanchovskiEtAlTable2Problem.F16.with_n_fevals_and_root(12, root=0.000151471334783891),
    GanchovskiEtAlTable2Problem.F17.with_n_fevals_and_root(12, root=7.66859512218533e-06),
    GanchovskiEtAlTable2Problem.F18.with_n_fevals_and_root(14, root=0.516153518757933),
    GanchovskiEtAlTable2Problem.F19.with_n_fevals_and_root(16, root=0.539522226908415),
    GanchovskiEtAlTable2Problem.F20.with_n_fevals_and_root(16, root=0.552704666678487),
    GanchovskiEtAlTable2Problem.F21.with_n_fevals_and_root(12, root=0.409992017989137),
    GanchovskiEtAlTable2Problem.F22.with_n_fevals_and_root(12, root=0.452509145577641),
    GanchovskiEtAlTable2Problem.F23.with_n_fevals_and_root(12, root=0.475626848596062),
    GanchovskiEtAlTable2Problem.F24.with_n_fevals_and_root(80, root=3.0),
    GanchovskiEtAlTable2Problem.F25.with_n_fevals_and_root(62, root=3.99999999999902),
    GanchovskiEtAlTable2Problem.F26.with_n_fevals_and_root(78, root=2.47457678736982),
    # f27 has a 4-fold root: within 4e-4 of that root, rounding makes the computed value of f27 0 or of the wrong sign,
    # and the returned and published roots lie 2.7e-4 apart.
    GanchovskiEtAlTable2Problem.F27.with_n_fevals_and_root(
        24,
        root=1.88905736094801,
        root_abs_tol=1e-3,
        deviation=5,
        reason=(
            f"the count deviates for 2 causes that add up: {_ITERATE_FORMULA_DEVIATION_REASON}; and "
            f"{_ROOT_AT_MIDPOINT_DEVIATION_REASON}"
        ),
    ),
    GanchovskiEtAlTable2Problem.F28.with_n_fevals_and_root(70, root=7.14299999999989),
    GanchovskiEtAlTable2Problem.F29.with_n_fevals_and_root(
        18,
        root=3.00054459411,
        deviation=1,
        reason=_ROOT_AT_MIDPOINT_DEVIATION_REASON,
    ),
    GanchovskiEtAlTable2Problem.F30.with_n_fevals_and_root(16, root=4.26716830454212),
    GanchovskiEtAlTable2Problem.F31.with_n_fevals_and_root(16, root=0.31830988618379),
    GanchovskiEtAlTable2Problem.F32.with_n_fevals_and_root(16, root=1.32581766366803),
    GanchovskiEtAlTable2Problem.F33.with_n_fevals_and_root(18, root=0.865474033101614),
    GanchovskiEtAlTable2Problem.F34.with_n_fevals_and_root(16, root=0.73908513321516),
    GanchovskiEtAlTable2Problem.F35.with_n_fevals_and_root(24, root=0.656666666666666),
    GanchovskiEtAlTable2Problem.F36.with_n_fevals_and_root(54, root=0.666666666666667),
    GanchovskiEtAlTable2Problem.F37.with_n_fevals_and_root(24, root=0.777777777777777),
    GanchovskiEtAlTable2Problem.F38.with_n_fevals_and_root(56, root=0.333333333333334),
    GanchovskiEtAlTable2Problem.F39.with_n_fevals_and_root(84, root=0.333333333329918),
    # f40 changes sign at a pole, and the returned and published roots agree only to a relative 2.3e-12.
    GanchovskiEtAlTable2Problem.F40.with_n_fevals_and_root(
        60,
        root=0.666666666665125,
        root_rel_tol=1e-11,
        deviation=10,
        reason=_ITERATE_FORMULA_DEVIATION_REASON,
    ),
    GanchovskiEtAlTable2Problem.F41.with_n_fevals_and_root(14, root=0.138257155056824),
    GanchovskiEtAlTable2Problem.F42.with_n_fevals_and_root(18, root=0.999999999999999),
    GanchovskiEtAlTable2Problem.F43.with_n_fevals_and_root(84, root=6.18534808760553e-16),
    # f44 and f45, x^5 and x^7, are nearly flat around their root at 0, and the returned and published roots, both
    # within 1e-10 of 0, lie less than 1e-15 apart.
    GanchovskiEtAlTable2Problem.F44.with_n_fevals_and_root(
        56,
        root=-6.36884555364388e-12,
        root_abs_tol=1e-14,
    ),
    GanchovskiEtAlTable2Problem.F45.with_n_fevals_and_root(
        52,
        root=-7.13945471568692e-11,
        root_abs_tol=1e-14,
    ),
    GanchovskiEtAlTable2Problem.F46.with_n_fevals_and_root(14, root=0.101624392293549),
    GanchovskiEtAlTable2Problem.F47.with_n_fevals_and_root(18, root=0.00773252320061279),
    GanchovskiEtAlTable2Problem.F48.with_n_fevals_and_root(18, root=0.00127630494573556),
    GanchovskiEtAlTable2Problem.F49.with_n_fevals_and_root(12, root=-0.682327803828019),
    GanchovskiEtAlTable2Problem.F50.with_n_fevals_and_root(14, root=-2.10380340273553),
    GanchovskiEtAlTable2Problem.F51.with_n_fevals_and_root(12, root=1.0),
    GanchovskiEtAlTable2Problem.F52.with_n_fevals_and_root(18, root=1.00004083556472),
    GanchovskiEtAlTable2Problem.F53.with_n_fevals_and_root(18, root=1.69681238680975),
    GanchovskiEtAlTable2Problem.F54.with_n_fevals_and_root(12, root=0.523598775598298),
    GanchovskiEtAlTable2Problem.F55.with_n_fevals_and_root(4, root=1.0),
    GanchovskiEtAlTable2Problem.F56.with_n_fevals_and_root(14, root=2.0),
    GanchovskiEtAlTable2Problem.F57.with_n_fevals_and_root(14, root=3.0),
    GanchovskiEtAlTable2Problem.F58.with_n_fevals_and_root(12, root=1.5574077246549),
    GanchovskiEtAlTable2Problem.F59.with_n_fevals_and_root(14, root=1.25643120862616),
    GanchovskiEtAlTable2Problem.F60.with_n_fevals_and_root(
        16,
        root=0.354463104375025,
        deviation=2,
        reason=_ITERATE_FORMULA_DEVIATION_REASON,
    ),
    GanchovskiEtAlTable2Problem.F61.with_n_fevals_and_root(18, root=1.40449164821534),
    GanchovskiEtAlTable2Problem.F62.with_n_fevals_and_root(14, root=1.89549426703398),
    GanchovskiEtAlTable2Problem.F63.with_n_fevals_and_root(10, root=0.567143290409783),
    GanchovskiEtAlTable2Problem.F64.with_n_fevals_and_root(12, root=0.1),
    GanchovskiEtAlTable2Problem.F65.with_n_fevals_and_root(16, root=-0.523598775598298),
    GanchovskiEtAlTable2Problem.F66.with_n_fevals_and_root(16, root=-0.843914568649266),
    GanchovskiEtAlTable2Problem.F67.with_n_fevals_and_root(12, root=0.835079042723559),
    GanchovskiEtAlTable2Problem.F68.with_n_fevals_and_root(10, root=0.873568526830231),
    GanchovskiEtAlTable2Problem.F69.with_n_fevals_and_root(12, root=0.111111111111111),
    GanchovskiEtAlTable2Problem.F70.with_n_fevals_and_root(16, root=-0.0370201277078609),
    GanchovskiEtAlTable2Problem.F71.with_n_fevals_and_root(16, root=-0.666666666666666),
    GanchovskiEtAlTable2Problem.F72.with_n_fevals_and_root(6, root=0.0),
    GanchovskiEtAlTable2Problem.F73.with_n_fevals_and_root(6, root=0.0),
    GanchovskiEtAlTable2Problem.F74.with_n_fevals_and_root(82, root=0.333333333333334),
    GanchovskiEtAlTable2Problem.F75.with_n_fevals_and_root(
        38,
        root=0.333333353713476,
        deviation=1,
        reason=_ROOT_AT_MIDPOINT_DEVIATION_REASON,
    ),
    GanchovskiEtAlTable2Problem.F76.with_n_fevals_and_root(52, root=-0.999999000000003),
    GanchovskiEtAlTable2Problem.F77.with_n_fevals_and_root(66, root=0.0476190476189878),
    GanchovskiEtAlTable2Problem.F78.with_n_fevals_and_root(40, root=7.7758811408552e-16),
    GanchovskiEtAlTable2Problem.F79.with_n_fevals_and_root(38, root=3.27731710121439e-16),
    GanchovskiEtAlTable2Problem.F80.with_n_fevals_and_root(26, root=-0.0447295436126949),
    GanchovskiEtAlTable2Problem.F81.with_n_fevals_and_root(40, root=-1.0),
    GanchovskiEtAlTable2Problem.F82.with_n_fevals_and_root(6, root=0.05),
    GanchovskiEtAlTable2Problem.F83.with_n_fevals_and_root(70, root=0.000495049504949891),
    GanchovskiEtAlTable2Problem.F84.with_n_fevals_and_root(20, root=5.00207435582522),
    GanchovskiEtAlTable2Problem.F85.with_n_fevals_and_root(20, root=-2.20778314488693),
    GanchovskiEtAlTable2Problem.F86.with_n_fevals_and_root(20, root=0.302804157270697),
    GanchovskiEtAlTable2Problem.F87.with_n_fevals_and_root(16, root=0.98780487804878),
    GanchovskiEtAlTable2Problem.F88.with_n_fevals_and_root(16, root=0.168362173262536),
    GanchovskiEtAlTable2Problem.F89.with_n_fevals_and_root(20, root=-3.63693954875174),
    GanchovskiEtAlTable2Problem.F90.with_n_fevals_and_root(18, root=0.02637269541443),
    GanchovskiEtAlTable2Problem.F91.with_n_fevals_and_root(14, root=0.120778011811926),
    GanchovskiEtAlTable2Problem.F92.with_n_fevals_and_root(28, root=0.1),
]

# `_SCIPY_STOPPING_AND_STEP_RULE_DEVIATION_REASON` explains why, on the rows of `_SCIPY_OVERRIDES`, the "scipy" variant
# deviates from the column "Rid" where the "commons_math" variant does not.
_SCIPY_STOPPING_AND_STEP_RULE_DEVIATION_REASON = (
    'the paper\'s C# code stops once 2 successive iterates lie within its tolerance, as the "commons_math" variant '
    'does, and does not limit the step; the "scipy" variant stops once the interval is narrower than xtol, and '
    "limits each step to keep the iterate at least xtol / 2 inside the interval"
)

# `_SCIPY_OVERRIDES` gives the rows on which the "scipy" variant needs another number of evaluations than the column
# "Rid", and a wider root tolerance on each row where the root differs from the published one by more than twice the
# paper's tolerance: where the function is nearly flat around its root (f25, f44, f45), or changes sign at a pole (f39,
# f77).
_SCIPY_OVERRIDES = {
    "f25": {"n_fevals_scipy": 74, "root_rel_tol": 1e-12},
    "f28": {"n_fevals_scipy": 76},
    "f39": {"n_fevals_scipy": 96, "root_abs_tol": 1e-11},
    "f44": {"n_fevals_scipy": 74, "root_abs_tol": 1e-10},
    "f45": {"n_fevals_scipy": 84, "root_abs_tol": 1e-10},
    "f47": {"n_fevals_scipy": 20},
    # On f72 and f73, the paper's C# code stops after 6 evaluations at x = 0, where f is -1, so its published root is
    # no root; the "scipy" variant returns the true root, 1e-6.
    "f72": {"n_fevals_scipy": 88, "root": 1e-6, "root_rel_tol": 1e-8},
    "f73": {"n_fevals_scipy": 88, "root": 1e-6, "root_rel_tol": 1e-8},
    "f77": {"n_fevals_scipy": 74, "root_rel_tol": 1e-11},
    "f79": {"n_fevals_scipy": 36},
    "f81": {"n_fevals_scipy": 38},
}


def _for_scipy_variant(problem: PaperProblem) -> PaperProblem:
    """Return ``problem`` for the "scipy" variant, with the root and root tolerances of `_SCIPY_OVERRIDES`, and with an
    allowed count deviation that reaches the count of `_SCIPY_OVERRIDES`.

    Both the paper's C# code and the "scipy" variant stop within the paper's tolerance of a root, at different
    iterates, so their roots agree to within twice that tolerance. Twice the paper's tolerance is
    `ganchovski_et_al_stop_width` at the published root, so every row checks the root with an absolute tolerance of at
    least that width.

    Every row to which `_SCIPY_OVERRIDES` gives no count keeps the count deviation and its reason from the
    "commons_math" variant, because the 2 variants compute the same iterates there.
    """
    assert problem.root is not None
    overrides = {"root_abs_tol": max(problem.root_abs_tol, ganchovski_et_al_stop_width(problem.root))}
    overrides |= _SCIPY_OVERRIDES.get(problem.name, {})
    if "n_fevals_scipy" in overrides:
        problem = problem.with_solve_n_fevals(
            overrides.pop("n_fevals_scipy"), reason=_SCIPY_STOPPING_AND_STEP_RULE_DEVIATION_REASON
        )
    return replace(problem, **overrides)


GANCHOVSKI_ET_AL_TABLE_2_SCIPY = [_for_scipy_variant(problem) for problem in GANCHOVSKI_ET_AL_TABLE_2_COMMONS_MATH]
