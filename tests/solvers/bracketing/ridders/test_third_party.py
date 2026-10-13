"""These tests assert that `Ridders` reproduces third parties' published results for it: the evaluation counts and
roots of the column "Rid" of Table 2 of Ganchovski et al. (2026). They test 2 variants: the "scipy" variant, which is
the core variant (role ``SolverRole.BUILTIN_CORE``), and the "commons_math" variant, whose stopping rule is that of the
paper's C# code.

The paper's C# code stops once 2 successive iterates lie within half of `ganchovski_et_al_stop_width` of each other,
evaluated at the newer iterate ``x``. The tests set the ``xtol`` of `Ridders` to half of `ganchovski_et_al_stop_width`,
evaluated at the published root. The "scipy" variant stops once its interval is narrower than ``xtol``, so with the
same ``xtol`` it too stops within that tolerance of the root.
"""

import pytest

from sunnbear.solvers import Ridders, RiddersVariant
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ganchovski_et_al import GanchovskiEtAlTable2Problem, ganchovski_et_al_stop_width

from .third_party_problems import GANCHOVSKI_ET_AL_TABLE_2_COMMONS_MATH, GANCHOVSKI_ET_AL_TABLE_2_SCIPY

_ROWS_BY_VARIANT = {
    RiddersVariant.SCIPY: GANCHOVSKI_ET_AL_TABLE_2_SCIPY,
    RiddersVariant.COMMONS_MATH: GANCHOVSKI_ET_AL_TABLE_2_COMMONS_MATH,
}


@pytest.mark.parametrize("variant", list(_ROWS_BY_VARIANT), ids=str)
def test_the_rows_of_table_2_of_ganchovski_et_al_name_every_problem_of_the_table_in_order(variant: RiddersVariant):
    """Each variant's rows hold 1 problem per member of `GanchovskiEtAlTable2Problem`, in the table's order."""
    # --- assert -----------------------
    assert [problem.name for problem in _ROWS_BY_VARIANT[variant]] == [
        member.value.name for member in GanchovskiEtAlTable2Problem
    ]


@pytest.mark.parametrize(
    "variant, problem",
    [
        pytest.param(variant, problem, id=f"{variant}-{problem}")
        for variant, problems in _ROWS_BY_VARIANT.items()
        for problem in problems
    ],
)
def test_the_evaluation_counts_and_roots_of_table_2_of_ganchovski_et_al_are_reproduced(
    variant: RiddersVariant, problem: PaperProblem
):
    """On every row of Table 2 of Ganchovski et al. (2026), `Ridders` with the given variant and the paper's tolerance
    evaluates as often as the column "Rid" reports, and returns Ridders' root in the paper's supplementary results,
    except where the problem states an allowed deviation, a wider tolerance on the root, or another root."""
    # --- arrange ----------------------
    assert problem.root is not None
    # The solve stops with ``x`` at the root, so ``|x|`` is taken as the absolute value of the published root.
    xtol = ganchovski_et_al_stop_width(problem.root) / 2.0

    # --- act --------------------------
    result = Ridders(variant=variant).solve(problem.f, problem.a, problem.b, xtol=xtol, max_fevals=300)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
