"""`CoreSelectionStage` assigns each candidate its difficulty class, and chooses the Core's size and quotas."""

from collections import Counter

import polars as pl

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS
from sunnbear._core.benchmark.suites.pipeline.core import PipelineStage, PipelineStageOutput
from sunnbear._core.benchmark.suites.pipeline.stages.s5_full_characterization import FullCharacterizationStage
from sunnbear._core.utils.worker_pool import WorkerPool

from .core_composition import CoreComposition
from .difficulty_class import EDI_GPQ_LEVEL, DifficultyClass

# The stage adds this column: each candidate's `DifficultyClass`.
DIFFICULTY_CLASS_SCHEMA: dict[str, pl.DataType] = {
    "difficulty_class": pl.Enum([difficulty_class.value for difficulty_class in DifficultyClass])
}
CORE_COMPOSITION_REPORT_NAME = "core_composition"


# ==================================================================================================
#  CoreSelectionStage
# ==================================================================================================
class CoreSelectionStage(PipelineStage):
    """`CoreSelectionStage` assigns each candidate its difficulty class, and chooses the Core's size and quotas.

    A candidate's empirical difficulty index (EDI) is read back from its full feature vector, by
    `FullCharacterizationStage.solvers_gpq_fevals` at `EDI_GPQ_LEVEL`. A candidate's class follows from the EDI
    relative to `DEFAULT_N_BISECTION_FEVALS`, the `n_bisection_fevals` with which the characterization stages run every
    solve.

    The stage keeps every row; `CoreComposition.from_class_counts` chooses the Core's size and quotas, and stops the
    pipeline when the candidates fill no Core of the smallest size.
    """

    output_name = "s6_core_suite"

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return `previous_table` with each candidate's difficulty class, and the report on the Core's composition.

        Args:
            previous_table: The output table of `FullCharacterizationStage`.
            worker_pool: The worker pool of the run, which the stage does not use.

        Returns:
            The stage's output, which holds:

            - the output table: `previous_table` with the column of `DIFFICULTY_CLASS_SCHEMA`;
            - the report `CORE_COMPOSITION_REPORT_NAME`: `CoreComposition.report_table`.

        Raises:
            PipelineStopError: If the candidates fill no Core of the smallest size, as
                `CoreComposition.from_class_counts` describes it.
        """
        # --- difficulty classes -----------------
        edis = FullCharacterizationStage.solvers_gpq_fevals(previous_table, EDI_GPQ_LEVEL)
        difficulty_classes = [
            DifficultyClass.from_edi(float(edi), n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS) for edi in edis
        ]

        # --- Core size and quotas ---------------
        composition = CoreComposition.from_class_counts(Counter(difficulty_classes))
        return PipelineStageOutput(
            table=previous_table.with_columns(
                pl.Series(
                    "difficulty_class",
                    [difficulty_class.value for difficulty_class in difficulty_classes],
                    dtype=DIFFICULTY_CLASS_SCHEMA["difficulty_class"],
                )
            ),
            reports={CORE_COMPOSITION_REPORT_NAME: composition.report_table()},
        )
