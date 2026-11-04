"""`CandidateGenerationStage` adds every candidate of every given formula, with its interval bounds."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.stages import CandidateGenerationStage
from sunnbear._core.benchmark.suites.pipeline.state import IntervalBounds, PipelineState
from sunnbear._core.problems.core import FormulaRegistry
from sunnbear._core.utils.worker_pool import WorkerPool


@pytest.mark.parametrize(
    "formula_numbers",
    [
        pytest.param(((2, 1, 2), (2, 1, 1)), id="2_formulas_against_number_order"),
        pytest.param((), id="no_formulas"),
    ],
)
def test_the_candidates_are_added_formula_by_formula_in_the_given_order(formula_numbers):
    """The candidates are each formula's candidates in the order of `Formula.build_all_candidates`, formula by formula
    in the given order, with their interval bounds."""
    # --- arrange ----------------------
    formulas_by_number = {formula.number: formula for formula in FormulaRegistry.formulas()}
    formulas = [formulas_by_number[number] for number in formula_numbers]
    state = PipelineState()

    # --- act --------------------------
    CandidateGenerationStage(formulas).run(
        state.create_state_accessor(PipelineStageId.CANDIDATE_GENERATION), worker_pool=WorkerPool(n_workers=1)
    )

    # --- assert -----------------------
    state.finish_stage(PipelineStageId.CANDIDATE_GENERATION)
    assert state.create_state_accessor(PipelineStageId.CANDIDATE_VALIDATION).interval_bounds() == {
        candidate.id: IntervalBounds(a=candidate.a, b=candidate.b)
        for formula in formulas
        for candidate in formula.build_all_candidates()
    }
