"""The snuffled diagnostics check rejects a candidate on which snuffled's analysis finds a problem at any sampled tuple.

The check samples `N_SNUFFLED_TUPLES` tuples from the largest Monte Carlo tuple set that sunnbear ships; each tuple sets
the ``c`` and the `xtol` of 1 solve.

Sorted by ``c``, the sampled tuples lie closer together near both ends of the c-range than in the middle, because a
test problem's failures, such as NaN values or a root at an interval bound, occur mostly near the ends of its c-range.
snuffled analyzes f at each sampled tuple:

- at the HIGH budget, `SnuffledAnalysisBudget.HIGH`, for the sampled tuples at the positions in `HIGH_BUDGET_POSITIONS`;
- at the LOW budget, `SnuffledAnalysisBudget.LOW`, for the others.

The check reads only snuffled's diagnostics, not its function or root properties. It rejects the candidate at the first
sampled tuple at which the diagnostics reject it, by the rules of `extract_properties_or_rejection_reason`.
"""

import numpy as np

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, MCSolveSettings
from sunnbear._core.benchmark.suites.pipeline.core import RejectionReason
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SnuffledAnalysisBudget
from sunnbear._core.problems.core import TestProblem
from sunnbear._core.utils.edge_biased_indices import select_edge_biased_indices

N_SNUFFLED_TUPLES = 32
# snuffled analyzes f at the HIGH budget at these positions among the sampled tuples, sorted by ``c``: the 2 outermost,
# where failures are most likely, and 2 in between, so that the larger budget also covers the middle of the c-range.
HIGH_BUDGET_POSITIONS = (0, 14, 17, 31)


def find_snuffled_rejection_reason(problem: TestProblem) -> RejectionReason | None:
    """Return the reason that snuffled's analysis rejects the calibrated test problem, or None if it passes.

    The check runs up to `N_SNUFFLED_TUPLES` snuffled analyses, so it is the most expensive check of validation.

    The analyses run at the sampled tuples from `plan_snuffled_analyses`, in order, and stop at the first tuple at
    which `extract_properties_or_rejection_reason` rejects the test problem.
    """
    mc_solve_settings = MCSolveSettings.from_test_problem(
        problem, n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS, mc_tuples=load_mc_tuples(max(MCTuplesSize))
    )
    for mc_sample_idx, budget in plan_snuffled_analyses(mc_solve_settings):
        result = budget.analyze_or_reject(problem, (), mc_solve_settings=mc_solve_settings, mc_sample_idx=mc_sample_idx)
        if isinstance(result, RejectionReason):
            return result
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
