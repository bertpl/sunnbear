"""`CandidateValidationStage` keeps the valid candidates with their c-ranges, reports each rejected candidate with its
`RejectionReason`, counts the rejections per formula, and gives the same output with 1 or 2 workers."""

import math

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import (
    REJECTED_BY_SCHEMA,
    REJECTED_CANDIDATES_REPORT_NAME,
    REJECTIONS_PER_FORMULA_REPORT_NAME,
    RejectionReason,
)
from sunnbear._core.benchmark.suites.pipeline.stages.s1_candidate_generation import (
    CANDIDATES_SCHEMA,
    CandidateGenerationStage,
)
from sunnbear._core.benchmark.suites.pipeline.stages.s2_candidate_validation import (
    C_RANGE_SCHEMA,
    CandidateValidationStage,
)
from sunnbear._core.problems.core import FormulaRegistry
from sunnbear._core.utils.module_imports import worker_pool_for_modules
from sunnbear._core.utils.worker_pool import WorkerPool
from tests.benchmark.suites.pipeline.example_formulas import define_formula_cls


def test_the_stage_keeps_the_valid_candidates_and_reports_the_others_per_check(isolated_formula_registry):
    """Of the candidates, 1 is valid and each check rejects 1 other, in the order of the checks; the counts per formula
    match these outcomes."""
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
    candidates = CandidateGenerationStage(formulas).compute_output(pl.DataFrame(), worker_pool=WorkerPool(n_workers=1))

    # --- act --------------------------
    output = CandidateValidationStage().compute_output(candidates.table, worker_pool=WorkerPool(n_workers=1))

    # --- assert -----------------------
    assert output.table.schema == pl.Schema({**CANDIDATES_SCHEMA, **C_RANGE_SCHEMA})
    [(problem_id, a, b, c_min, c_max)] = output.table.rows()
    assert (problem_id, a, b) == ("f99.901", -1.0, 1.0)
    assert c_min < 0.0 < c_max
    rejected_candidates = output.reports[REJECTED_CANDIDATES_REPORT_NAME]
    assert rejected_candidates.schema == pl.Schema({**CANDIDATES_SCHEMA, **REJECTED_BY_SCHEMA})
    assert rejected_candidates.rows() == [
        ("f99.902", 100.0, 101.0, RejectionReason.BOUND_TO_WIDTH_RATIO.value),
        ("f99.903", -1.0, 1.0, RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0.value),
        ("f99.904", -1.0, 1.0, RejectionReason.BISECTION_COUNT_NOT_EXACT.value),
        ("f99.905", -1.0, 1.0, RejectionReason.SNUFFLED_NAN_VALUES_DETECTED.value),
    ]
    rejections_per_formula = output.reports[REJECTIONS_PER_FORMULA_REPORT_NAME]
    assert rejections_per_formula.columns == [
        "formula_id",
        "n_candidates",
        "n_kept",
        *(reason.value for reason in RejectionReason),
    ]
    reason_per_formula = {
        "f99.901": None,
        "f99.902": RejectionReason.BOUND_TO_WIDTH_RATIO,
        "f99.903": RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0,
        "f99.904": RejectionReason.BISECTION_COUNT_NOT_EXACT,
        "f99.905": RejectionReason.SNUFFLED_NAN_VALUES_DETECTED,
    }
    # Each row ends with 1 count per reason, in the order of `RejectionReason`.
    assert rejections_per_formula.rows() == [
        (formula_id, 1, int(reason is None), *(int(reason is counted_reason) for counted_reason in RejectionReason))
        for formula_id, reason in reason_per_formula.items()
    ]


def test_the_stage_gives_the_same_output_with_1_or_2_workers():
    """The checks that evaluate f run in tasks of the worker pool; with 2 worker processes, the output and reports equal
    those of a run in this process, on shipped formulas with some candidates that each check rejects."""
    # --- arrange ----------------------
    # The formula numbered (1, 4, 1, 6) adds candidates that the bisection count check rejects.
    formulas = [
        formula
        for formula in FormulaRegistry.formulas()
        if formula.number[:3] in {(1, 4, 2), (2, 1, 1)} or formula.number == (1, 4, 1, 6)
    ]
    candidates = CandidateGenerationStage(formulas).compute_output(pl.DataFrame(), worker_pool=WorkerPool(n_workers=1))
    module_names = {type(formula).__module__ for formula in formulas}

    # --- act --------------------------
    in_process_output = CandidateValidationStage().compute_output(candidates.table, worker_pool=WorkerPool(n_workers=1))
    with worker_pool_for_modules(n_workers=2, module_names=module_names) as worker_pool:
        worker_processes_output = CandidateValidationStage().compute_output(candidates.table, worker_pool=worker_pool)

    # --- assert -----------------------
    rejected_by = in_process_output.reports[REJECTED_CANDIDATES_REPORT_NAME]["rejected_by"]
    assert {
        RejectionReason.BOUND_TO_WIDTH_RATIO.value,
        RejectionReason.CALIBRATION_NO_FINITE_SIGN_CHANGE_AT_0.value,
        RejectionReason.BISECTION_COUNT_NOT_EXACT.value,
    } <= set(rejected_by)
    assert in_process_output.table.height > 0
    assert worker_processes_output.table.equals(in_process_output.table)
    assert worker_processes_output.reports.keys() == in_process_output.reports.keys()
    for report_name, report in worker_processes_output.reports.items():
        assert report.equals(in_process_output.reports[report_name])
