"""The snuffled diagnostics check rejects a candidate on which snuffled's analysis finds a problem at 1 sampled tuple.

The check samples `N_SNUFFLED_TUPLES` tuples of the largest size of the shipped tuple set. Sorted by ``c``, the sampled
tuples lie closer together near both ends of the c-range than in the middle, because a test problem's pathologies
cluster near the ends of its c-range. snuffled analyzes f at each sampled tuple:

- at `SnuffledAnalysisBudget.HIGH` at the positions `HIGH_BUDGET_POSITIONS` among the sampled tuples: the 2 outermost
  tuples and 2 near the middle;
- at `SnuffledAnalysisBudget.LOW` at the others.

The check reads only snuffled's diagnostics. It rejects the candidate at the first sampled tuple at which f raises, 1 of
the 5 diagnostics that are flags is above 0, or `MAX_ZERO_WIDTH`, the widest region around a root where f is exactly 0,
exceeds `MAX_ZERO_WIDTH_IN_XTOL` times the tuple's `xtol`.
"""

import numpy as np
from snuffled import Diagnostic

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, MCSolveSettings
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import FunctionEvaluationError, SnuffledAnalysisBudget
from sunnbear._core.problems.core import TestProblem
from sunnbear._core.utils.edge_biased_indices import select_edge_biased_indices

from .rejection_reason import RejectionReason

N_SNUFFLED_TUPLES = 32
# The positions among the sampled tuples, sorted by ``c``, at which snuffled analyzes f at the HIGH budget.
HIGH_BUDGET_POSITIONS = (0, 14, 17, 31)
# snuffled's `MAX_ZERO_WIDTH` is 1 float spacing at a root without an exact 0, and 2 at a root with 1 float where f is
# exactly 0. At the largest bound-to-width ratio that check 1 accepts, `xtol` spans only about 82 float spacings at the
# root, so the fraction stays well above 2/82, which would reject such a root.
MAX_ZERO_WIDTH_IN_XTOL = 1 / 16
# The flags of snuffled's diagnostics, each with the reason that rejects a candidate when the flag is above 0. The check
# tests them in this order: snuffled leaves its other diagnostics unspecified when f returns NaN.
_FLAG_REJECTION_REASONS = {
    Diagnostic.NAN_VALUES_DETECTED: RejectionReason.SNUFFLED_NAN_VALUES_DETECTED,
    Diagnostic.INF_VALUES_DETECTED: RejectionReason.SNUFFLED_INF_VALUES_DETECTED,
    Diagnostic.NO_ZEROS_DETECTED: RejectionReason.SNUFFLED_NO_ZEROS_DETECTED,
    Diagnostic.INTERVAL_NOT_BRACKETING_READY: RejectionReason.SNUFFLED_INTERVAL_NOT_BRACKETING_READY,
    Diagnostic.ALL_ROOTS_TOO_CLOSE_TO_EDGE: RejectionReason.SNUFFLED_ALL_ROOTS_TOO_CLOSE_TO_EDGE,
}


def find_snuffled_rejection_reason(problem: TestProblem) -> RejectionReason | None:
    """Return the reason that snuffled's analysis rejects the calibrated test problem, or None if it passes.

    The analysis runs at the sampled tuples from `select_snuffled_tuples`, in order, and stops at the first tuple at
    which a rule fails. At 1 tuple, a raise of f comes first, then the flags in the order of `_FLAG_REJECTION_REASONS`,
    then the width of the widest region of exact zeros.
    """
    mc_solve_settings = MCSolveSettings.from_test_problem(
        problem, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS, mc_tuples=load_mc_tuples(max(MCTuplesSize))
    )
    xtols = mc_solve_settings.xtols
    for mc_sample_idx, budget in select_snuffled_tuples(mc_solve_settings):
        snuffler = budget.build_snuffler(problem, mc_solve_settings=mc_solve_settings, mc_sample_idx=mc_sample_idx)
        try:
            # Extracted in the order of `Diagnostic`, which puts the NaN and inf flags last, so that they cover the
            # evaluations of f for the other diagnostics too.
            diagnostics = {diagnostic: snuffler.extract(diagnostic) for diagnostic in Diagnostic}
        except FunctionEvaluationError:
            return RejectionReason.SNUFFLED_F_RAISES
        for flag, reason in _FLAG_REJECTION_REASONS.items():
            if diagnostics[flag] > 0:
                return reason
        if diagnostics[Diagnostic.MAX_ZERO_WIDTH] > MAX_ZERO_WIDTH_IN_XTOL * xtols[mc_sample_idx]:
            return RejectionReason.SNUFFLED_MAX_ZERO_WIDTH_TOO_LARGE
    return None


def select_snuffled_tuples(mc_solve_settings: MCSolveSettings) -> list[tuple[int, SnuffledAnalysisBudget]]:
    """Return the tuple index and the budget of each sampled tuple, in ascending order of ``c``.

    `select_edge_biased_indices` picks `N_SNUFFLED_TUPLES` positions among all tuples sorted by ``c``. The sampled
    tuples at the positions `HIGH_BUDGET_POSITIONS` get `SnuffledAnalysisBudget.HIGH`, the others
    `SnuffledAnalysisBudget.LOW`.
    """
    tuple_indices_by_c = np.argsort(mc_solve_settings.cs, kind="stable")
    sampled_tuple_indices = tuple_indices_by_c[
        select_edge_biased_indices(n_selected=N_SNUFFLED_TUPLES, n_values=tuple_indices_by_c.size)
    ]
    return [
        (
            int(mc_sample_idx),
            SnuffledAnalysisBudget.HIGH if position in HIGH_BUDGET_POSITIONS else SnuffledAnalysisBudget.LOW,
        )
        for position, mc_sample_idx in enumerate(sampled_tuple_indices)
    ]
