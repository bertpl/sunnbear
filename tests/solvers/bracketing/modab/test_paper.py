"""These tests assert that `ModAB` and `ModABSafeguarded`, with the stopping criterion of their C# code, reproduce their
published results: `ModAB` Tables 1 and 2 of Ganchovski et al. (2026), and `ModABSafeguarded` Tables 3 to 5 of Tomov
and Ganchovski (2026)."""

import pytest

from sunnbear.solvers import ModAB, ModABSafeguarded
from tests.solvers.paper_problems import PaperProblem
from tests.solvers.paper_problems.ganchovski_et_al import GanchovskiEtAlTable2Problem, ganchovski_et_al_stop_width

from .paper_problems import (
    TABLE_2,
    TABLE_3_BY_SETTING,
    TABLE_3_NON_STRESS_CASES,
    TABLE_3_NON_STRESS_SUMS_BY_SETTING,
    TABLE_4_CAP_M_3,
    TABLE_4_CAP_M_3_FINAL_WIDTH,
    TABLE_5,
    TABLE_5_TOTAL_N_FEVALS,
)
from .replay_from_history import bisection_iterations, final_interval


# ==================================================================================================
#  Ganchovski et al. (2026), with ModAB
# ==================================================================================================
def test_the_rows_of_table_2_name_every_problem_of_the_table_in_order():
    """`TABLE_2` holds 1 problem per member of `GanchovskiEtAlTable2Problem`, in the table's order."""
    # --- assert -----------------------
    assert [problem.name for problem in TABLE_2] == [member.value.name for member in GanchovskiEtAlTable2Problem]


@pytest.mark.parametrize("problem", TABLE_2, ids=str)
def test_the_evaluation_counts_of_table_2_of_the_paper_are_reproduced(problem: PaperProblem):
    """With the stopping criterion of the paper's C# code and the tolerances of its benchmark, `ModAB` reproduces
    modAB's published results on each problem of Table 2:

    - it returns the root that the paper's supplementary results give, within a relative 1e-13;
    - it evaluates as often as Table 2 reports, less the iterations that the paper's C# code counts but that evaluate
      nothing, except on the few problems whose count depends on how the platform rounds a library function.
    """
    # --- act --------------------------
    result = _ModABWithPaperStoppingCriterion().solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


def test_the_switches_of_table_1_of_the_paper_are_reproduced():
    """On ``x^3 - 0.001`` over ``[-10, 10]``, with the stopping criterion of the paper's C# code and the tolerances of
    its benchmark, `ModAB` switches modes in the iterations that the paper's Table 1 reports:

    - iteration 1: to Anderson-Björck mode;
    - iteration 7: back to bisection;
    - iteration 15: to Anderson-Björck mode again;
    - iteration 24: the solve stops, before evaluating.

    Each switch takes effect from the next iteration, so iterations 1 and 8 to 15 bisect, and the solve evaluates in
    iterations 1 to 23, after its 2 evaluations of the interval's bounds.
    """
    # --- act --------------------------
    result = _ModABWithPaperStoppingCriterion().solve(
        lambda x: x * x * x - 0.001, -10.0, 10.0, xtol=0.0, max_fevals=100, history_enabled=True
    )

    # --- assert -----------------------
    assert bisection_iterations(result.history, ModAB) == [1, 8, 9, 10, 11, 12, 13, 14, 15]
    assert result.n_fevals == 2 + 23


# ==================================================================================================
#  Tomov and Ganchovski (2026), with ModABSafeguarded
# ==================================================================================================
@pytest.mark.parametrize(
    "setting, problem",
    [(setting, problem) for setting, problems in TABLE_3_BY_SETTING.items() for problem in problems],
    ids=str,
)
def test_the_evaluation_counts_of_table_3_of_the_safeguarded_paper_are_reproduced(setting: str, problem: PaperProblem):
    """With the stopping criterion of the C# code and the tolerances that the preprint uses, `ModABSafeguarded`
    evaluates as often as Table 3 reports on each of its 8 cases, under each of its 3 settings."""
    # --- act --------------------------
    result = _SOLVER_CLS_BY_TABLE_3_SETTING[setting]().solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300)

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("setting, published_sum", TABLE_3_NON_STRESS_SUMS_BY_SETTING.items())
def test_the_sums_of_table_3_over_its_86_non_stress_cases_are_reproduced(setting: str, published_sum: int):
    """Under each setting of Table 3, the evaluation counts of `ModABSafeguarded` with the C# code's stopping criterion
    add up, over the table's 86 validated non-stress cases, to the table's sum."""
    # --- arrange ----------------------
    solver = _SOLVER_CLS_BY_TABLE_3_SETTING[setting]()

    # --- act --------------------------
    total = sum(
        solver.solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300).n_fevals
        for problem in TABLE_3_NON_STRESS_CASES
    )

    # --- assert -----------------------
    assert len(TABLE_3_NON_STRESS_CASES) == 86
    assert total == published_sum


def test_the_row_cap_m_3_of_table_4_of_the_safeguarded_paper_is_reproduced():
    """On the preprint's equation 27 over ``[-3, 1]``, with the stopping criterion of the C# code and the tolerances
    that the preprint uses, `ModABSafeguarded` reproduces the row "Cap M = 3" of Table 4: it converges after 77
    evaluations, returns the x-value that the preprint's Section 7.4 prints, and leaves a final interval as wide as
    that section reports."""
    # --- act --------------------------
    result = _ModABSafeguardedWithPaperStoppingCriterion().solve(
        TABLE_4_CAP_M_3.f, TABLE_4_CAP_M_3.a, TABLE_4_CAP_M_3.b, xtol=0.0, max_fevals=300, history_enabled=True
    )

    # --- assert -----------------------
    TABLE_4_CAP_M_3.assert_reproduced_by(result)
    assert final_interval(result.history).width == TABLE_4_CAP_M_3_FINAL_WIDTH


@pytest.mark.parametrize("setting", TABLE_3_BY_SETTING)
def test_the_x_values_of_table_5_of_the_safeguarded_paper_are_reproduced(setting: str):
    """Under each setting of Table 3, `ModABSafeguarded` with the C# code's stopping criterion returns the x-value that
    Table 5 prints on each of its 3 cases, and evaluates as often on the 3 cases in total as the preprint's Section 7.3
    reports."""
    # --- arrange ----------------------
    solver = _SOLVER_CLS_BY_TABLE_3_SETTING[setting]()

    # --- act --------------------------
    results = [solver.solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300) for problem in TABLE_5]

    # --- assert -----------------------
    for problem, result in zip(TABLE_5, results, strict=True):
        problem.assert_reproduced_by(result)
    assert sum(result.n_fevals for result in results) == TABLE_5_TOTAL_N_FEVALS


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _PaperStoppingCriterionMixin:
    """`_PaperStoppingCriterionMixin` gives `ModAB` or `ModABSafeguarded`, as the first base of a subclass, the stopping
    criterion and the return value of their C# code, at the absolute and relative tolerances ``aTol`` and ``rTol`` that
    both papers use.

    The tolerances are those of `ganchovski_et_al_stop_width`, so a test passes ``xtol = 0``, which this class ignores.
    """

    @staticmethod
    def _root_if_converged(x1: float, y1: float, x2: float, y2: float, x3: float, xtol_doubled: float) -> float | None:
        """Return ``x3`` once the interval is at most ``aTol + rTol*|x3|`` wide, or ``None`` if the solve continues.

        The C# code tests for a 0 only after evaluating ``x3``, as both classes do, so this check reads no function
        value.
        """
        if x2 - x1 <= ganchovski_et_al_stop_width(x3):
            return x3
        else:
            return None


class _ModABWithPaperStoppingCriterion(_PaperStoppingCriterionMixin, ModAB):
    """`_ModABWithPaperStoppingCriterion` is `ModAB` with the stopping criterion of its C# code."""


class _ModABSafeguardedWithPaperStoppingCriterion(_PaperStoppingCriterionMixin, ModABSafeguarded):
    """`_ModABSafeguardedWithPaperStoppingCriterion` is `ModABSafeguarded` with its C# code's stopping criterion."""


class _ModABSafeguardedWithFixedDelay(_ModABSafeguardedWithPaperStoppingCriterion):
    """`_ModABSafeguardedWithFixedDelay` is `_ModABSafeguardedWithPaperStoppingCriterion` with the setting "fixed delay"
    of Table 3 of Tomov and Ganchovski (2026), ``(B, M) = (16, 0)``: the switch sets the threshold to 16 times the
    interval width, and no residual exception is granted."""

    _FALLBACK_THRESHOLD_FACTOR = 16.0
    _MAX_RESIDUAL_STEPS = 0


class _ModABSafeguardedWithEarlyFallback(_ModABSafeguardedWithPaperStoppingCriterion):
    """`_ModABSafeguardedWithEarlyFallback` is `_ModABSafeguardedWithPaperStoppingCriterion` with the setting "early
    fallback" of Table 3 of Tomov and Ganchovski (2026), ``(B, M) = (2, 0)``: the switch sets the threshold to 2 times
    the interval width, as `ModABSafeguarded` does, but no residual exception is granted."""

    _MAX_RESIDUAL_STEPS = 0


# The setting "adaptive" of Table 3 of Tomov and Ganchovski (2026), (B, M) = (2, 3), is that of `ModABSafeguarded`.
_SOLVER_CLS_BY_TABLE_3_SETTING = {
    "fixed_delay": _ModABSafeguardedWithFixedDelay,
    "early_fallback": _ModABSafeguardedWithEarlyFallback,
    "adaptive": _ModABSafeguardedWithPaperStoppingCriterion,
}
