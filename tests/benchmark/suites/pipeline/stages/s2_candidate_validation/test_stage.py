"""`CandidateValidationStage` rejects each candidate at its first failed check, with the check's reason, stores the
c-ranges of the valid candidates, and gives the same results with 1 or 2 workers."""

import math
from collections.abc import Sequence

from sunnbear._core.benchmark.protocol import CRange
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageId
from sunnbear._core.benchmark.suites.pipeline.stages import CandidateGenerationStage, CandidateValidationStage
from sunnbear._core.benchmark.suites.pipeline.state import PipelineState
from sunnbear._core.problems.core import Formula, FormulaRegistry, ProblemId
from sunnbear._core.utils.module_imports import worker_pool_for_modules
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls


def _validate(formulas: Sequence[Formula], worker_pool: WorkerPool) -> tuple[PipelineState, dict[ProblemId, CRange]]:
    """Return the state after generation and validation of `formulas`' candidates, and the stored c-ranges."""
    state = PipelineState()
    for stage in [CandidateGenerationStage(formulas), CandidateValidationStage()]:
        state.run_stage(stage, worker_pool=worker_pool)
    return state, state.create_state_accessor(PipelineStageId.COARSE_CHARACTERIZATION).c_ranges()


def test_the_stage_rejects_a_candidate_at_each_check_and_keeps_the_valid_one(isolated_formula_registry):
    """Of the candidates, 1 is valid and each check rejects 1 other, with its reason, in the order of the checks."""
    # --- arrange ----------------------
    formulas = [
        # the offset 1 / 3 keeps the root off bisection's midpoints, so no solve ends early at an exact 0
        define_formula_cls((99, 901), lambda x, c: x - c - 1 / 3, -1.0, 1.0)(),
        define_formula_cls((99, 902), lambda x, c: x - 100.5 - c, 100.0, 101.0)(),
        define_formula_cls((99, 903), lambda x, c: x + 2.0, -1.0, 1.0)(),
        define_formula_cls((99, 904), lambda x, c: 0.0 if abs(x - c) < 0.01 else x - c, -1.0, 1.0)(),
        # f is NaN only between the lower bound and 1.5 left of its root, an interval where bisection never evaluates f
        define_formula_cls((99, 905), lambda x, c: math.nan if -1.0 < x < c - 7 / 6 else x - c - 1 / 3, -1.0, 1.0)(),
    ]

    # --- act --------------------------
    state, c_ranges = _validate(formulas, WorkerPool(n_workers=1))

    # --- assert -----------------------
    [(problem_id, c_range)] = c_ranges.items()
    assert str(problem_id) == "f99.901"
    assert c_range.c_min < 0.0 < c_range.c_max
    reasons = {
        "f99.902": "bound_to_width_ratio",
        "f99.903": "calibration_no_finite_sign_change_at_0",
        "f99.904": "bisection_count_not_exact",
        "f99.905": "snuffled_nan_values_detected",
    }
    for rejected_problem_id, reason in reasons.items():
        drop = state.drop_of(ProblemId.from_string(rejected_problem_id))
        assert (drop.stage_id, drop.reason, drop.is_rejection) == (PipelineStageId.CANDIDATE_VALIDATION, reason, True)


def test_the_stage_gives_the_same_results_with_1_or_2_workers():
    """The checks that evaluate f run in tasks of the worker pool; with 2 worker processes, the c-ranges and the
    rejections equal those of a run in this process, on shipped formulas with some candidates that each check
    rejects."""
    # --- arrange ----------------------
    # The formula numbered (1, 4, 1, 6) adds candidates that the bisection count check rejects.
    formulas = [
        formula
        for formula in FormulaRegistry.formulas()
        if formula.number[:3] in {(1, 4, 2), (2, 1, 1)} or formula.number == (1, 4, 1, 6)
    ]
    module_names = {type(formula).__module__ for formula in formulas}

    # --- act --------------------------
    in_process_state, in_process_c_ranges = _validate(formulas, WorkerPool(n_workers=1))
    with worker_pool_for_modules(n_workers=2, module_names=module_names) as worker_pool:
        worker_processes_state, worker_processes_c_ranges = _validate(formulas, worker_pool)

    # --- assert -----------------------
    problem_ids = [candidate.id for formula in formulas for candidate in formula.build_all_candidates()]
    in_process_drops = [in_process_state.drop_of(problem_id) for problem_id in problem_ids]
    assert {"bound_to_width_ratio", "calibration_no_finite_sign_change_at_0", "bisection_count_not_exact"} <= {
        drop.reason for drop in in_process_drops if drop is not None
    }
    assert len(in_process_c_ranges) > 0
    assert worker_processes_c_ranges == in_process_c_ranges
    assert [worker_processes_state.drop_of(problem_id) for problem_id in problem_ids] == in_process_drops
