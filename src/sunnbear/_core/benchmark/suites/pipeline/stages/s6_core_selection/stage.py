"""`CoreSelectionStage` selects the Core: the most diverse candidates, at the largest size whose quotas they fill."""

from collections import Counter

import numpy as np
import polars as pl
from max_div import Constraint, MaxDivProblem, MaxDivSolverBuilder, Verbosity, iterations
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, SeedPurpose, derive_seed
from sunnbear._core.benchmark.suites.pipeline.core import PIPELINE_ROOT_SEED, PipelineStage, PipelineStageOutput
from sunnbear._core.benchmark.suites.pipeline.stages.s5_full_characterization import FullCharacterizationStage
from sunnbear._core.utils.worker_pool import WorkerPool

from .core_composition import CoreComposition
from .difficulty_class import EDI_GPQ_LEVEL, DifficultyClass

# The stage adds this column: each candidate's `DifficultyClass`.
DIFFICULTY_CLASS_SCHEMA: dict[str, pl.DataType] = {
    "difficulty_class": pl.Enum([difficulty_class.value for difficulty_class in DifficultyClass])
}
CORE_COMPOSITION_REPORT_NAME = "core_composition"
DEFAULT_CORE_SELECTION_N_ITERATIONS = 100_000
# A selected candidate's separation is its distance to the nearest other selected candidate. max-div's objective takes
# the geometric pseudo-quantile (gpq) of the selection's separations at this level: the lower the level, the more weight
# the objective puts on the smallest separations.
CORE_SELECTION_SEPARATION_GPQ_LEVEL = 0.1


# ==================================================================================================
#  CoreSelectionStage
# ==================================================================================================
class CoreSelectionStage(PipelineStage):
    """`CoreSelectionStage` selects the Core; every benchmark suite is selected from the Core.

    A candidate's empirical difficulty index (EDI) is read back from its full feature vector, by
    `FullCharacterizationStage.solvers_gpq_fevals` at `EDI_GPQ_LEVEL`. A candidate's class follows from the EDI
    relative to `DEFAULT_N_BISECTION_FEVALS`, the `n_bisection_fevals` with which the characterization stages run every
    solve.

    The stage selects the Core in 3 steps:

    - `CoreComposition.from_class_counts` chooses the Core's size and difficulty quotas, and stops the pipeline when the
      candidates fill no Core of the smallest size;
    - max-div selects the Core, as `_select_core` describes;
    - `CoreComposition.check_selection` checks the selection's size and quotas, because max-div treats its constraints
      as soft and returns its best selection even when it breaks one.
    """

    output_name = "s6_core_suite"

    def __init__(self, n_iterations: int = DEFAULT_CORE_SELECTION_N_ITERATIONS) -> None:
        """Create the stage, whose max-div search runs `n_iterations` iterations.

        A fixed number of iterations, not a time budget, makes the selection the same on every machine.
        """
        self.n_iterations = n_iterations
        self.seed = derive_seed(root_seed=PIPELINE_ROOT_SEED, purpose=SeedPurpose.CORE_SELECTION)

    @property
    def parameters(self) -> dict[str, int]:
        """Return the number of iterations and the seed of max-div's search."""
        return {"n_iterations": self.n_iterations, "seed": self.seed}

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the Core's candidates with their difficulty classes, and the report on the Core's composition.

        Args:
            previous_table: The output table of `FullCharacterizationStage`.
            worker_pool: The worker pool of the run, which the stage does not use: max-div searches in a single
                process, because a search across workers gives a result that depends on their timing.

        Returns:
            The stage's output, which holds:

            - the output table: the rows of `previous_table` that the Core holds, in the order of `previous_table`,
              with the column of `DIFFICULTY_CLASS_SCHEMA`;
            - the report `CORE_COMPOSITION_REPORT_NAME`: `CoreComposition.report_table`.

        Raises:
            PipelineStopError: If the candidates fill no Core of the smallest size, as
                `CoreComposition.from_class_counts` describes it, or if max-div's selection misses the Core's size or a
                quota, as `CoreComposition.check_selection` describes.
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
        selected_indices = self._select_core(previous_table, difficulty_classes, core_composition)
        core_composition.check_selection([difficulty_classes[idx] for idx in selected_indices])
        return PipelineStageOutput(
            table=table_with_classes[selected_indices],
            reports={CORE_COMPOSITION_REPORT_NAME: core_composition.report_table()},
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _select_core(
        self,
        previous_table: pl.DataFrame,
        difficulty_classes: list[DifficultyClass],
        core_composition: CoreComposition,
    ) -> np.ndarray:
        """Return the row indices of the Core in `previous_table`, ascending, as max-div selects them.

        max-div searches for the `core_composition.core_size` candidates whose scaled full feature vectors are the most
        diverse, under 1 constraint per quota of `core_composition`. Its objective is the geometric mean, with equal
        weights, of the gpq of the selection's separations at `CORE_SELECTION_SEPARATION_GPQ_LEVEL`, under each of 2
        distances:

        - the L1 distance between the scaled vectors, in which every feature block has a mean pairwise L1 distance of 1;
        - the distance along the EDI feature, which is the EDI on a log scale, so that the Core's EDIs also differ
          widely within each quota.

        The distance along the EDI feature therefore compares 2 EDIs by their ratio. `map_fevals_to_feature` and the
        scale of the solvers block multiply that distance by a constant factor, which does not change which selection
        maximizes a geometric mean.
        """
        vectors = FullCharacterizationStage.scaled_feature_vectors(previous_table)
        edi_axis = FullCharacterizationStage.scaled_feature_column_index(
            previous_table, FullCharacterizationStage.solvers_gpq_column_name(EDI_GPQ_LEVEL)
        )
        gpq_separation = DiversityMetric.gpq_separation(CORE_SELECTION_SEPARATION_GPQ_LEVEL)
        max_div_problem = MaxDivProblem.new(
            # max-div takes float32 vectors; the lost precision does not reach the output, because the Core's rows are
            # taken from `previous_table` by index.
            vectors,
            k=core_composition.core_size,
            distance_metric=DistanceMetric.l1_manhattan(),
            diversity_metric=HybridDiversityMetric.geomean_of(
                gpq_separation.over(DistanceMetric.l1_manhattan()),
                gpq_separation.over(DistanceMetric.along_axis(edi_axis)),
            ),
            constraints=[
                Constraint(
                    int_set={idx for idx, c in enumerate(difficulty_classes) if c in quota.classes},
                    min_count=quota.count,
                    max_count=quota.count,
                )
                for quota in core_composition.quotas
            ],
        )
        solution = (
            MaxDivSolverBuilder(max_div_problem)
            .with_seed(self.seed)
            .with_preset(iterations(self.n_iterations))
            .build()
            .solve(verbosity=Verbosity.SILENT)
        )
        return solution.i_selected
