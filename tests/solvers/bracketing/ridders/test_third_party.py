"""These tests assert that `Ridders` reproduces third parties' published results for it: the evaluation counts and
roots of the column "Rid" of Table 2 of Ganchovski et al. (2026), with the "commons_math" variant.

The paper's C# code stops once 2 successive iterates lie within half of `ganchovski_et_al_stop_width` of each other,
evaluated at the newer iterate ``x``. That is the stopping rule of the "commons_math" variant, so the test sets only the
``xtol`` of `Ridders` to that tolerance.
"""

import pytest

from sunnbear.solvers import Ridders, RiddersVariant
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ganchovski_et_al import GanchovskiEtAlTable2Problem, ganchovski_et_al_stop_width

from .third_party_problems import GANCHOVSKI_ET_AL_TABLE_2


def test_the_rows_of_table_2_of_ganchovski_et_al_name_every_problem_of_the_table_in_order():
    """`GANCHOVSKI_ET_AL_TABLE_2` holds 1 problem per member of `GanchovskiEtAlTable2Problem`, in the table's order."""
    # --- assert -----------------------
    assert [problem.name for problem in GANCHOVSKI_ET_AL_TABLE_2] == [
        member.value.name for member in GanchovskiEtAlTable2Problem
    ]


@pytest.mark.parametrize("problem", GANCHOVSKI_ET_AL_TABLE_2, ids=str)
def test_the_evaluation_counts_and_roots_of_table_2_of_ganchovski_et_al_are_reproduced(problem: PaperProblem):
    """On every row of Table 2 of Ganchovski et al. (2026), `Ridders` with the "commons_math" variant and the paper's
    tolerance evaluates as often as the column "Rid" reports, and returns Ridders' root in the paper's supplementary
    results, except where the problem states an allowed deviation or a wider tolerance on the root."""
    # --- arrange ----------------------
    assert problem.root is not None
    # The solve stops with ``x`` at the root, so ``|x|`` is taken as the absolute value of the published root.
    xtol = ganchovski_et_al_stop_width(problem.root) / 2.0

    # --- act --------------------------
    result = Ridders(variant=RiddersVariant.COMMONS_MATH).solve(
        problem.f, problem.a, problem.b, xtol=xtol, max_fevals=300
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)
