"""These tests assert that `ModAB`, with the stopping criterion of its C# code, reproduces the published results of
both variants: Tables 1 and 2 of Ganchovski et al. (2026) with ``"algorithms_2026"``, and Tables 3 to 5 of Tomov and
Ganchovski (2026) with ``"safeguarded_2026"``."""

import pytest

from sunnbear.solvers import Interval, ModAB, ModABVariant
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


# ==================================================================================================
#  Ganchovski et al. (2026), with "algorithms_2026"
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
    result = _ModABWithPaperStoppingCriterion(variant=ModABVariant.ALGORITHMS_2026).solve(
        problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300
    )

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
    result = _ModABWithPaperStoppingCriterion(variant=ModABVariant.ALGORITHMS_2026).solve(
        lambda x: x * x * x - 0.001, -10.0, 10.0, xtol=0.0, max_fevals=100, history_enabled=True
    )

    # --- assert -----------------------
    assert _bisection_iterations(result.history) == [1, 8, 9, 10, 11, 12, 13, 14, 15]
    assert result.n_fevals == 2 + 23


# ==================================================================================================
#  Tomov and Ganchovski (2026), with "safeguarded_2026"
# ==================================================================================================
@pytest.mark.parametrize(
    "setting, problem",
    [(setting, problem) for setting, problems in TABLE_3_BY_SETTING.items() for problem in problems],
    ids=str,
)
def test_the_evaluation_counts_of_table_3_of_the_safeguarded_paper_are_reproduced(setting: str, problem: PaperProblem):
    """With the stopping criterion of the C# code and the tolerances of the preprint's runs, the safeguarded variant
    evaluates as often as Table 3 reports on each of its 8 cases, under each of its 3 settings."""
    # --- act --------------------------
    result = _SOLVER_CLS_BY_TABLE_3_SETTING[setting](variant=ModABVariant.SAFEGUARDED_2026).solve(
        problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300
    )

    # --- assert -----------------------
    problem.assert_reproduced_by(result)


@pytest.mark.parametrize("setting, published_sum", TABLE_3_NON_STRESS_SUMS_BY_SETTING.items())
def test_the_sums_of_table_3_over_its_86_non_stress_cases_are_reproduced(setting: str, published_sum: int):
    """Under each setting of Table 3, the evaluation counts of the safeguarded variant with the C# code's stopping
    criterion sum, over the table's 86 validated non-stress cases, to the table's sum."""
    # --- arrange ----------------------
    solver = _SOLVER_CLS_BY_TABLE_3_SETTING[setting](variant=ModABVariant.SAFEGUARDED_2026)

    # --- act --------------------------
    total = sum(
        solver.solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300).n_fevals
        for problem in TABLE_3_NON_STRESS_CASES
    )

    # --- assert -----------------------
    assert len(TABLE_3_NON_STRESS_CASES) == 86
    assert total == published_sum


def test_the_row_cap_m_3_of_table_4_of_the_safeguarded_paper_is_reproduced():
    """On the preprint's equation 27 over ``[-3, 1]``, with the stopping criterion of the C# code and the tolerances of
    the preprint's runs, the safeguarded variant reproduces the row "Cap M = 3" of Table 4: it converges after 77
    evaluations, returns the x-value that the preprint's Section 7.4 prints, and leaves a final interval as wide as
    that section reports."""
    # --- act --------------------------
    result = _ModABWithPaperStoppingCriterion(variant=ModABVariant.SAFEGUARDED_2026).solve(
        TABLE_4_CAP_M_3.f, TABLE_4_CAP_M_3.a, TABLE_4_CAP_M_3.b, xtol=0.0, max_fevals=300, history_enabled=True
    )

    # --- assert -----------------------
    TABLE_4_CAP_M_3.assert_reproduced_by(result)
    assert _final_interval(result.history).width == TABLE_4_CAP_M_3_FINAL_WIDTH


@pytest.mark.parametrize("setting", TABLE_3_BY_SETTING)
def test_the_x_values_of_table_5_of_the_safeguarded_paper_are_reproduced(setting: str):
    """Under each setting of Table 3, the safeguarded variant with the C# code's stopping criterion returns the x-value
    that Table 5 prints on each of its 3 cases, and evaluates as often on the 3 cases in total as the preprint's
    Section 7.3 reports."""
    # --- arrange ----------------------
    solver = _SOLVER_CLS_BY_TABLE_3_SETTING[setting](variant=ModABVariant.SAFEGUARDED_2026)

    # --- act --------------------------
    results = [solver.solve(problem.f, problem.a, problem.b, xtol=0.0, max_fevals=300) for problem in TABLE_5]

    # --- assert -----------------------
    for problem, result in zip(TABLE_5, results, strict=True):
        problem.assert_reproduced_by(result)
    assert sum(result.n_fevals for result in results) == TABLE_5_TOTAL_N_FEVALS


# ==================================================================================================
#  Helpers
# ==================================================================================================
class _ModABWithPaperStoppingCriterion(ModAB):
    """`_ModABWithPaperStoppingCriterion` is `ModAB` with the stopping criterion and the return value of the C# code of
    both variants, at the absolute and relative tolerances ``aTol`` and ``rTol`` of both papers' runs.

    The tolerances are those of `ganchovski_et_al_stop_width`, so a test passes ``xtol = 0``, which this class ignores.
    """

    @staticmethod
    def _root_if_converged(x1: float, y1: float, x2: float, y2: float, x3: float, xtol_doubled: float) -> float | None:
        """Return ``x3`` once the interval is at most ``aTol + rTol*|x3|`` wide, or ``None`` if the solve continues.

        The C# code tests for a 0 only after evaluating ``x3``, as `ModAB` does, so this check reads no function value.
        """
        if x2 - x1 <= ganchovski_et_al_stop_width(x3):
            return x3
        else:
            return None


class _ModABWithFixedDelay(_ModABWithPaperStoppingCriterion):
    """`_ModABWithFixedDelay` is `_ModABWithPaperStoppingCriterion` with the setting "fixed delay" of Table 3 of Tomov
    and Ganchovski (2026), ``(B, M) = (16, 0)``: in the safeguarded variant, the switch sets the threshold to 16 times
    the interval width, and no residual exception is granted."""

    _SAFEGUARDED_THRESHOLD_FACTOR = 16.0
    _SAFEGUARDED_MAX_RESIDUAL_STEPS = 0


class _ModABWithEarlyFallback(_ModABWithPaperStoppingCriterion):
    """`_ModABWithEarlyFallback` is `_ModABWithPaperStoppingCriterion` with the setting "early fallback" of Table 3 of
    Tomov and Ganchovski (2026), ``(B, M) = (2, 0)``: in the safeguarded variant, the switch still sets the threshold
    to 2 times the interval width, but no residual exception is granted."""

    _SAFEGUARDED_MAX_RESIDUAL_STEPS = 0


# The solver class for each setting of Table 3 of Tomov and Ganchovski (2026). The setting "adaptive",
# (B, M) = (2, 3), is that of `ModAB` itself.
_SOLVER_CLS_BY_TABLE_3_SETTING = {
    "fixed_delay": _ModABWithFixedDelay,
    "early_fallback": _ModABWithEarlyFallback,
    "adaptive": _ModABWithPaperStoppingCriterion,
}


def _bisection_iterations(history: tuple[tuple[float, float], ...]) -> list[int]:
    """Return the 1-based numbers of the iterations whose x-value is the midpoint of the interval, in the form
    ``(x1 + x2) / 2`` of ``"algorithms_2026"``.

    The interval is replayed from ``history``: each evaluated x-value replaces the bound whose function value has the
    same sign as the function value at that x-value. The replay holds only for a solve without clamped iterations,
    which evaluate nothing.
    """
    (x1, y1), (x2, _) = history[:2]
    iterations = []
    for iteration, (x, y) in enumerate(history[2:], start=1):
        if x == (x1 + x2) / 2.0:
            iterations.append(iteration)
        if (y > 0.0) == (y1 > 0.0):
            x1, y1 = x, y
        else:
            x2 = x
    return iterations


def _final_interval(history: tuple[tuple[float, float], ...]) -> Interval:
    """Return the interval that remains after splitting the initial interval at each later x-value of ``history``.

    An iteration that evaluates nothing reuses the function value at a bound, and leaves the interval as it is, so the
    replay holds for every solve.
    """
    (a, fa), (b, fb), *evaluations = history
    interval = Interval.from_interval_bounds(a, b, fa, fb)
    for x, fx in evaluations:
        interval = interval.split_at(x, fx)
    return interval
