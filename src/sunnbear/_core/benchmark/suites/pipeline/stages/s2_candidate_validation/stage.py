"""`CandidateValidationStage` runs the validation checks on every candidate and keeps the candidates that pass them."""

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageOutput
from sunnbear._core.functions.core import ProblemId
from sunnbear._core.utils.worker_pool import WorkerPool

from .bound_to_width_ratio_check import exceeds_max_bound_to_width_ratio
from .c_range_calibration import CRange
from .c_range_calibration_task import CRangeCalibrationTask
from .rejection_reason import RejectionReason

# The stage adds these columns to the valid candidates: their c-ranges.
C_RANGE_SCHEMA: dict[str, pl.DataType] = {"c_min": pl.Float64(), "c_max": pl.Float64()}
# The stage adds this column to the rejected candidates: the `RejectionReason` of each.
REJECTED_BY_SCHEMA: dict[str, pl.DataType] = {"rejected_by": pl.Enum([reason.value for reason in RejectionReason])}
REJECTED_CANDIDATES_REPORT_NAME = "rejected_candidates"
REJECTIONS_PER_FORMULA_REPORT_NAME = "rejections_per_formula"


# ==================================================================================================
#  CandidateValidationStage
# ==================================================================================================
class CandidateValidationStage(PipelineStage):
    """`CandidateValidationStage` keeps the candidates that pass every check, and adds their c-ranges.

    It reports each rejected candidate with its `RejectionReason`, and the counts of the rejections per formula.
    """

    output_name = "s2_valid_candidates"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the valid candidates with their c-ranges, and the reports on the rejected candidates.

        The checks run in order, and each runs only on the candidates that passed the checks before it. Calibration
        runs in tasks on `worker_pool`; each task holds every candidate of the formulas that it covers, so each formula
        is compiled in only 1 worker.

        Args:
            previous_table: The output table of candidate generation, with the columns ``problem_id``, ``a`` and
                ``b``.
            worker_pool: The worker pool of the run, in which calibration runs.

        Returns:
            The stage's output, which holds:

            - the output table: the valid candidates, with the columns of `previous_table` and of `C_RANGE_SCHEMA`;
            - the report `REJECTED_CANDIDATES_REPORT_NAME`: the rejected candidates, with the columns of
              `previous_table` and of `REJECTED_BY_SCHEMA`;
            - the report `REJECTIONS_PER_FORMULA_REPORT_NAME`: 1 row per formula, with the columns ``formula_id``,
              ``n_candidates``, ``n_valid``, and 1 count per `RejectionReason`, named after its value.
        """
        # --- check 1: the bound-to-width ratio --
        is_ratio_too_large = previous_table.select(exceeds_max_bound_to_width_ratio()).to_series()
        ratio_rejected_problem_ids = previous_table.filter(is_ratio_too_large)["problem_id"]
        results_by_problem_id: dict[str, CRange | RejectionReason] = dict.fromkeys(
            ratio_rejected_problem_ids, RejectionReason.BOUND_TO_WIDTH_RATIO
        )

        # --- check 2: c-range calibration -------
        problem_ids_to_calibrate = previous_table.filter(~is_ratio_too_large)["problem_id"].to_list()
        batches = worker_pool.split_into_batches(
            problem_ids_to_calibrate, group_key=lambda problem_id: ProblemId.from_string(problem_id).formula_id
        )
        tasks = {batch_idx: CRangeCalibrationTask(problem_ids=tuple(batch)) for batch_idx, batch in enumerate(batches)}
        for batch_idx, results in worker_pool.run(tasks):
            results_by_problem_id.update(zip(batches[batch_idx], results, strict=True))

        # --- 1 row per candidate ----------------
        results = [results_by_problem_id[problem_id] for problem_id in previous_table["problem_id"]]
        c_mins = [result.c_min if isinstance(result, CRange) else None for result in results]
        c_maxs = [result.c_max if isinstance(result, CRange) else None for result in results]
        rejected_bys = [result.value if isinstance(result, RejectionReason) else None for result in results]
        table = previous_table.with_columns(
            pl.Series("c_min", c_mins, dtype=C_RANGE_SCHEMA["c_min"]),
            pl.Series("c_max", c_maxs, dtype=C_RANGE_SCHEMA["c_max"]),
            pl.Series("rejected_by", rejected_bys, dtype=REJECTED_BY_SCHEMA["rejected_by"]),
        )
        is_valid = pl.col("rejected_by").is_null()
        return PipelineStageOutput(
            table=table.filter(is_valid).drop(list(REJECTED_BY_SCHEMA)),
            reports={
                REJECTED_CANDIDATES_REPORT_NAME: table.filter(~is_valid).drop(list(C_RANGE_SCHEMA)),
                REJECTIONS_PER_FORMULA_REPORT_NAME: self._count_rejections_per_formula(table),
            },
        )

    @staticmethod
    def summarize_rejections_per_formula(rejections_per_formula: pl.DataFrame) -> list[str]:
        """Return a line that counts the formulas with rejected candidates, then 1 line per such formula.

        `rejections_per_formula` is the report `REJECTIONS_PER_FORMULA_REPORT_NAME`. A formula's line gives its number
        of candidates, how many of them are valid, and the number of rejected candidates per `RejectionReason` that
        rejected any.
        """
        formulas_with_rejections = rejections_per_formula.filter(pl.col("n_valid") < pl.col("n_candidates"))
        lines = [
            f"formulas with rejected candidates: {formulas_with_rejections.height} of {rejections_per_formula.height}"
        ]
        for row in formulas_with_rejections.iter_rows(named=True):
            rejections = ", ".join(
                f"{reason.value}: {row[reason.value]}" for reason in RejectionReason if row[reason.value] > 0
            )
            lines.append(
                f"  {row['formula_id']}: {row['n_valid']} of {row['n_candidates']} candidates valid; {rejections}"
            )
        return lines

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _count_rejections_per_formula(table: pl.DataFrame) -> pl.DataFrame:
        """Return the report `REJECTIONS_PER_FORMULA_REPORT_NAME` of `table`, with 1 row per formula.

        The rows follow the order of each formula's first appearance in `table`.
        """
        formula_ids = [ProblemId.from_string(problem_id).formula_id for problem_id in table["problem_id"]]
        return (
            table.with_columns(formula_id=pl.Series(formula_ids, dtype=pl.String()))
            .group_by("formula_id", maintain_order=True)
            .agg(
                n_candidates=pl.len(),
                n_valid=pl.col("rejected_by").is_null().sum(),
                **{reason.value: (pl.col("rejected_by") == reason.value).sum() for reason in RejectionReason},
            )
        )
