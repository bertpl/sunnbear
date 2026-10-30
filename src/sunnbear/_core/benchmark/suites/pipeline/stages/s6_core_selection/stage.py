"""`CoreSelectionStage` selects the Core: the most diverse candidates, at the largest size whose quotas they fill."""

from collections import Counter

import polars as pl

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.pipeline.core import PIPELINE_ROOT_SEED, PipelineStage, PipelineStageOutput
from sunnbear._core.benchmark.suites.pipeline.selection import (
    DEFAULT_SELECTION_SEC_PER_CANDIDATE,
    EDI_GPQ_LEVEL,
    CandidatePool,
    DifficultyClass,
    select_diverse_suite,
)
from sunnbear._core.benchmark.suites.pipeline.stages.s5_full_characterization import FullCharacterizationStage
from sunnbear._core.utils.worker_pool import WorkerPool

from .core_composition import CoreComposition

# The stage adds this column: each candidate's `DifficultyClass`.
DIFFICULTY_CLASS_SCHEMA: dict[str, pl.DataType] = {
    "difficulty_class": pl.Enum([difficulty_class.value for difficulty_class in DifficultyClass])
}
CORE_COMPOSITION_REPORT_NAME = "core_composition"


# ==================================================================================================
#  CoreSelectionStage
# ==================================================================================================
class CoreSelectionStage(PipelineStage):
    """`CoreSelectionStage` selects the Core; every benchmark suite is selected from the Core.

    A candidate's empirical difficulty index (EDI) is read back from its full feature vector, by
    `FullCharacterizationStage.solvers_gpq_fevals` at `EDI_GPQ_LEVEL`. A candidate's class follows from the EDI
    relative to `DEFAULT_N_BISECTION_FEVALS`, the `n_bisection_fevals` with which the characterization stages run every
    solve.

    The stage selects the Core in 2 steps:

    - `CoreComposition.from_class_counts` chooses the Core's size and difficulty quotas, and stops the pipeline when the
      candidates fill no Core of the smallest size;
    - `select_diverse_suite` selects the Core by max-div, and stops the pipeline when the selection misses a quota.
    """

    output_name = "s6_core_suite"

    def __init__(self, sec_per_candidate: float = DEFAULT_SELECTION_SEC_PER_CANDIDATE) -> None:
        """Create the stage, whose max-div workers each run for `sec_per_candidate` seconds per input candidate."""
        self.sec_per_candidate = sec_per_candidate
        self.seed = derive_seed(root_seed=PIPELINE_ROOT_SEED, purpose=SeedPurpose.CORE_SELECTION)

    @property
    def parameters(self) -> dict[str, float | int]:
        """Return the time per candidate and the seed of max-div's search."""
        return {"sec_per_candidate": self.sec_per_candidate, "seed": self.seed}

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the Core's candidates with their difficulty classes, and the report on the Core's composition.

        Args:
            previous_table: The output table of `FullCharacterizationStage`.
            worker_pool: The worker pool of the run, whose number of workers max-div uses; max-div starts its own
                worker processes, and the pool's workers stay idle.

        Returns:
            The stage's output, which holds:

            - the output table: the rows of `previous_table` that the Core holds, in the order of `previous_table`,
              with the column of `DIFFICULTY_CLASS_SCHEMA`;
            - the report `CORE_COMPOSITION_REPORT_NAME`: `CoreComposition.report_table`.

        Raises:
            PipelineStopError: If the candidates fill no Core of the smallest size, as
                `CoreComposition.from_class_counts` describes it, or if max-div's selection misses a quota, as
                `select_diverse_suite` describes.
        """
        # --- difficulty classes -----------------
        edis = FullCharacterizationStage.solvers_gpq_fevals(previous_table, EDI_GPQ_LEVEL)
        difficulty_classes = [
            DifficultyClass.from_edi(float(edi), n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS) for edi in edis
        ]
        table_with_classes = previous_table.with_columns(
            pl.Series(
                "difficulty_class",
                [difficulty_class.value for difficulty_class in difficulty_classes],
                dtype=DIFFICULTY_CLASS_SCHEMA["difficulty_class"],
            )
        )

        # --- Core size and quotas ---------------
        core_composition = CoreComposition.from_class_counts(Counter(difficulty_classes))

        # --- selection --------------------------
        solution = select_diverse_suite(
            self.candidate_pool(table_with_classes),
            composition=core_composition,
            seed=self.seed,
            sec_per_candidate=self.sec_per_candidate,
            n_workers=worker_pool.n_workers,
        )
        return PipelineStageOutput(
            table=table_with_classes[solution.i_selected],
            reports={CORE_COMPOSITION_REPORT_NAME: core_composition.report_table()},
        )

    @staticmethod
    def candidate_pool(table: pl.DataFrame) -> CandidatePool:
        """Return the `CandidatePool` of `table`'s rows, from their full features and their ``difficulty_class`` column.

        `table` is this stage's output table, a subset of the output table's rows, or the stage's input table with the
        column of `DIFFICULTY_CLASS_SCHEMA` added.
        """
        return CandidatePool(
            vectors=FullCharacterizationStage.scaled_feature_vectors(table),
            edi_axis=FullCharacterizationStage.scaled_feature_column_index(
                table, FullCharacterizationStage.solvers_gpq_column_name(EDI_GPQ_LEVEL)
            ),
            difficulty_classes=[DifficultyClass(value) for value in table["difficulty_class"]],
        )
