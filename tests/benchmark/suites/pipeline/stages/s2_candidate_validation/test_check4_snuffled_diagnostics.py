"""`find_snuffled_rejection_reason` rejects a candidate for each condition that snuffled's analysis detects at a
sampled tuple, and `plan_snuffled_analyses` samples the tuples closer together near the ends of the c-range."""

import math

import numpy as np
import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, CRange, MCSolveSettings
from sunnbear._core.benchmark.suites.pipeline.core import RejectionReason
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SnuffledAnalysisBudget
from sunnbear._core.benchmark.suites.pipeline.stages.s2_candidate_validation.check4_snuffled_diagnostics import (
    N_SNUFFLED_TUPLES,
    find_snuffled_rejection_reason,
    plan_snuffled_analyses,
)
from sunnbear._core.problems.core import FormulaRegistry
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls


@pytest.mark.parametrize(
    "xc_fun, reason",
    [
        pytest.param(lambda x, c: x - c - 1 / 3, None, id="simple_root"),
        # f raises everywhere between the interval bounds
        pytest.param(
            lambda x, c: x - c - 1 / 3 if abs(x) == 1.0 else 1 / 0, RejectionReason.SNUFFLED_F_RAISES, id="f_raises"
        ),
        # the region of NaN or inf lies away from every root, which lies in [-1/6, 5/6]
        pytest.param(
            lambda x, c: math.nan if -0.9 < x < -0.7 else x - c - 1 / 3,
            RejectionReason.SNUFFLED_NAN_VALUES_DETECTED,
            id="nan_values",
        ),
        pytest.param(
            lambda x, c: math.inf if -0.9 < x < -0.7 else x - c - 1 / 3,
            RejectionReason.SNUFFLED_INF_VALUES_DETECTED,
            id="inf_values",
        ),
        pytest.param(lambda x, c: x * x + 1.0, RejectionReason.SNUFFLED_NO_ZEROS_DETECTED, id="no_zeros"),
        # f has 2 roots and the same sign at both interval bounds
        pytest.param(
            lambda x, c: x * x - 0.25, RejectionReason.SNUFFLED_INTERVAL_NOT_BRACKETING_READY, id="no_bracket"
        ),
        # the root lies within a few `xtol` of the lower bound
        pytest.param(
            lambda x, c: x + 1.0 - 1e-12, RejectionReason.SNUFFLED_ALL_ROOTS_TOO_CLOSE_TO_EDGE, id="root_at_edge"
        ),
        pytest.param(
            lambda x, c: 0.0 if abs(x - c - 1 / 3) < 1e-6 else x - c - 1 / 3,
            RejectionReason.SNUFFLED_MAX_ZERO_WIDTH_TOO_LARGE,
            id="wide_zero_region",
        ),
    ],
)
def test_the_check_rejects_a_problem_for_each_failed_condition(isolated_formula_registry, xc_fun, reason):
    """A simple root passes; each other test problem meets 1 rejection condition, and the check returns its reason."""
    # --- arrange ----------------------
    define_formula_cls((99, 931), xc_fun, -1.0, 1.0)
    problem = FormulaRegistry.candidate_from_id("f99.931").calibrated(c_min=-0.5, c_max=0.5)

    # --- act --------------------------
    rejection_reason = find_snuffled_rejection_reason(problem)

    # --- assert -----------------------
    assert rejection_reason is reason


def test_the_planned_analyses_span_the_c_range_with_the_high_budget_at_4_positions():
    """The sampled tuples are distinct and ascend in ``c`` from the smallest to the largest ``c``; the HIGH budget falls
    on the 2 outermost and on 2 near the middle."""
    # --- arrange ----------------------
    mc_solve_settings = MCSolveSettings(
        a=-1.0,
        b=1.0,
        n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS,
        c_range=CRange(c_min=-0.5, c_max=0.5),
        mc_tuples=load_mc_tuples(max(MCTuplesSize)),
    )

    # --- act --------------------------
    planned_analyses = plan_snuffled_analyses(mc_solve_settings)

    # --- assert -----------------------
    cs = mc_solve_settings.cs[[mc_sample_idx for mc_sample_idx, _ in planned_analyses]]
    assert len(planned_analyses) == N_SNUFFLED_TUPLES
    assert np.all(np.diff(cs) > 0)
    assert (cs[0], cs[-1]) == (mc_solve_settings.cs.min(), mc_solve_settings.cs.max())
    high_budget_positions = [
        position for position, (_, budget) in enumerate(planned_analyses) if budget is SnuffledAnalysisBudget.HIGH
    ]
    assert high_budget_positions == [0, 14, 17, 31]
