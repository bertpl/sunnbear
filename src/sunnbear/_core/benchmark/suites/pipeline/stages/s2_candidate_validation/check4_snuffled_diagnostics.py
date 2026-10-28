"""The snuffled diagnostics check rejects a candidate on which snuffled's analysis finds a problem at any sampled tuple.

The check samples `N_SNUFFLED_TUPLES` tuples from the largest Monte Carlo tuple set that sunnbear ships; each tuple sets
the ``c`` and the `xtol` of 1 solve.

Sorted by ``c``, the sampled tuples lie closer together near both ends of the c-range than in the middle, because a
test problem's failures, such as NaN values or a root at an interval bound, occur mostly near the ends of its c-range.
snuffled analyzes f at each sampled tuple:

- at the HIGH budget, `SnuffledAnalysisBudget.HIGH`, for the sampled tuples at the positions in `HIGH_BUDGET_POSITIONS`;
- at the LOW budget, `SnuffledAnalysisBudget.LOW`, for the others.

The check reads only snuffled's diagnostics, not its function or root properties. It rejects the candidate at the first
sampled tuple at which 1 of these holds:

- f raises;
- 1 of the flags in `_FLAG_REJECTION_REASONS` is above 0;
- `MAX_ZERO_WIDTH`, the width of the widest region around a root where f is exactly 0, exceeds `MAX_ZERO_WIDTH_IN_XTOL`
  times the tuple's `xtol`.
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
# snuffled analyzes f at the HIGH budget at these positions among the sampled tuples, sorted by ``c``: the 2 outermost,
# where failures are most likely, and 2 in between, so that the larger budget also covers the middle of the c-range.
HIGH_BUDGET_POSITIONS = (0, 14, 17, 31)
# snuffled's `MAX_ZERO_WIDTH` is 1 float spacing at a root without an exact 0, and 2 at a root with 1 float where f is
# exactly 0.
#
# At `MAX_BOUND_TO_WIDTH_RATIO`, the largest bound-to-width ratio that validation accepts, `xtol` spans the fewest float
# spacings at the root. At that ratio, this fraction of `xtol` stays well above 2 float spacings, so that a root with 1
# float where f is exactly 0 is not rejected.
MAX_ZERO_WIDTH_IN_XTOL = 1 / 16
# Each flag of snuffled's diagnostics maps to the reason that rejects a candidate when the flag is above 0. The check
# tests them in this order, NaN first, because snuffled leaves its other diagnostics unspecified when f returns NaN.
_FLAG_REJECTION_REASONS = {
    Diagnostic.NAN_VALUES_DETECTED: RejectionReason.SNUFFLED_NAN_VALUES_DETECTED,
    Diagnostic.INF_VALUES_DETECTED: RejectionReason.SNUFFLED_INF_VALUES_DETECTED,
    Diagnostic.NO_ZEROS_DETECTED: RejectionReason.SNUFFLED_NO_ZEROS_DETECTED,
    Diagnostic.INTERVAL_NOT_BRACKETING_READY: RejectionReason.SNUFFLED_INTERVAL_NOT_BRACKETING_READY,
    Diagnostic.ALL_ROOTS_TOO_CLOSE_TO_EDGE: RejectionReason.SNUFFLED_ALL_ROOTS_TOO_CLOSE_TO_EDGE,
}


def find_snuffled_rejection_reason(problem: TestProblem) -> RejectionReason | None:
    """Return the reason that snuffled's analysis rejects the calibrated test problem, or None if it passes.

    The check runs up to `N_SNUFFLED_TUPLES` snuffled analyses, so it is the most expensive check of validation.

    The analyses run at the sampled tuples from `plan_snuffled_analyses`, in order, and stop at the first tuple that
    the check rejects. Within 1 tuple, the check tests the conditions in this order:

    1. f raises;
    2. a flag is above 0, with the flags in the order of `_FLAG_REJECTION_REASONS`;
    3. the widest region of exact zeros exceeds `MAX_ZERO_WIDTH_IN_XTOL` times the tuple's `xtol`.
    """
    mc_solve_settings = MCSolveSettings.from_test_problem(
        problem, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS, mc_tuples=load_mc_tuples(max(MCTuplesSize))
    )
    xtols = mc_solve_settings.xtols
    for mc_sample_idx, budget in plan_snuffled_analyses(mc_solve_settings):
        snuffler = budget.build_snuffler(problem, mc_solve_settings=mc_solve_settings, mc_sample_idx=mc_sample_idx)
        try:
            # The diagnostics are extracted in the order of `Diagnostic`, which puts the NaN and inf flags last, so that
            # those 2 flags also count the NaN and inf values that f returned while snuffled computed the other
            # diagnostics.
            diagnostics = {diagnostic: snuffler.extract(diagnostic) for diagnostic in Diagnostic}
        except FunctionEvaluationError:
            return RejectionReason.SNUFFLED_F_RAISES
        for flag, reason in _FLAG_REJECTION_REASONS.items():
            if diagnostics[flag] > 0:
                return reason
        if diagnostics[Diagnostic.MAX_ZERO_WIDTH] > MAX_ZERO_WIDTH_IN_XTOL * xtols[mc_sample_idx]:
            return RejectionReason.SNUFFLED_MAX_ZERO_WIDTH_TOO_LARGE
    return None


def plan_snuffled_analyses(mc_solve_settings: MCSolveSettings) -> list[tuple[int, SnuffledAnalysisBudget]]:
    """Return the tuple index and the budget of each of the check's analyses, in ascending order of ``c``.

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
