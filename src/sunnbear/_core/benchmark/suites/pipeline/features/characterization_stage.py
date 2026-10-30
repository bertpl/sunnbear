"""`CandidateCharacterizationStage` is the base class of the stages that compute the candidates' feature vectors."""

import dataclasses
from collections.abc import Sequence
from typing import ClassVar

import numpy as np
import polars as pl
import polars.selectors as cs

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, max_fevals_for
from sunnbear._core.benchmark.suites.pipeline.core import (
    PipelineStage,
    PipelineStageOutput,
    RejectionReason,
)
from sunnbear._core.solvers.core import SolverConfig
from sunnbear._core.stats import mean_pairwise_l1
from sunnbear._core.utils.worker_pool import WorkerPool

from .characterization_task import CandidateCharacterizationResult, CandidateCharacterizationTask
from .feature_vector import SNUFFLED_PROPERTIES, SOLVERS_GPQ_LEVELS, FeatureBlock
from .fevals_mapping import map_feature_to_fevals
from .fidelity import FeatureFidelity

INCORRECT_SOLVES_PER_CONFIG_REPORT_NAME = "incorrect_solves_per_config"


# ==================================================================================================
#  CandidateCharacterizationStage
# ==================================================================================================
class CandidateCharacterizationStage(PipelineStage):
    """`CandidateCharacterizationStage` adds feature vectors, and rejects candidates whose solves or analyses fail.

    The stage also adds the scale of each block of the features, as `_add_feature_scales` computes it. A stage reads
    only the output table of the stage before it, so the scales are stored in this stage's output table, where the
    next stage can read them, with the same value in every row.

    A child class is 1 stage of the pipeline: it sets `output_name`, `column_prefix` and `fidelity`, the only things in
    which the characterization stages differ. `column_prefix` starts the name of each column that the stage adds, so
    that 1 table can hold the columns of 2 characterization stages. A later stage reads these columns through the class
    methods of the child class that added them, such as `scaled_feature_vectors`.

    A candidate is rejected when 1 of its solves ends with `SolveStatus.FUNCTION_ERROR`, or when snuffled's diagnostics
    reject it at 1 of its analyses, by the rules of `extract_properties_or_rejection_reason`.

    Besides the rejection reports, the stage reports, for each core solver config, the fraction of its solves on the
    kept candidates that end without a correct answer. An incorrect solve counts as `max_fevals` in `n_fevals_eff`,
    from which the solvers block is computed, so the fraction shows how much each config's incorrect solves affect the
    features.

    The report informs the choice of the core solver configs and never rejects a candidate.

    Class attributes:
        column_prefix: The start of the name of each column that the stage adds, e.g. ``coarse`` in
            ``coarse_solvers_gpq_50``.
        fidelity: The `FeatureFidelity` of the feature vectors.
    """

    column_prefix: ClassVar[str]
    fidelity: ClassVar[FeatureFidelity]

    def __init__(self, core_solver_configs: Sequence[SolverConfig]) -> None:
        """Create the stage, which solves each candidate with `core_solver_configs`.

        Raises:
            ValueError: If `core_solver_configs` is empty.
        """
        if not core_solver_configs:
            raise ValueError("A characterization stage needs at least 1 core solver config.")
        else:
            self.solver_ids = tuple(config.solver_id for config in core_solver_configs)

    def compute_output(self, previous_table: pl.DataFrame, *, worker_pool: WorkerPool) -> PipelineStageOutput:
        """Return the kept candidates with their feature vectors, and the reports on the rejected candidates.

        The candidates are characterized in `CandidateCharacterizationTask` tasks on `worker_pool`, by
        `_run_in_formula_batches`.

        Args:
            previous_table: The output table of the stage before, with the columns ``problem_id``, ``c_min`` and
                ``c_max``.
            worker_pool: The worker pool of the run, in which the candidates are characterized.

        Returns:
            The stage's output, as `_build_output_with_rejection_reports` describes it, with 1 more report,
            `INCORRECT_SOLVES_PER_CONFIG_REPORT_NAME`, which holds 1 row per core solver config, in the order of
            `solver_ids`, with these columns:

            - ``solver_id``;
            - ``n_solves``: the config's number of solves over the kept candidates;
            - ``n_incorrect_solves``;
            - ``incorrect_fraction``, which is null when the stage keeps no candidate.

            The output's table holds these columns; every added column has type `pl.Float64`:

            - the columns of `previous_table`;
            - the columns of `feature_column_names`;
            - the columns of `feature_scale_column_names`, each holding, in every row, the scale that
              `_add_feature_scales` computes, or null when fewer than 2 candidates are kept.
        """
        # --- characterize, in the worker pool ---
        column_names = self.feature_column_names
        results_by_problem_id = self._run_in_formula_batches(
            previous_table.select("problem_id", "c_min", "c_max").rows(),
            problem_id_key=lambda candidate: candidate[0],
            build_task=lambda batch: CandidateCharacterizationTask(
                candidates=batch,
                solver_ids=self.solver_ids,
                feature_column_names=tuple(column_names),
                fidelity=self.fidelity,
            ),
            worker_pool=worker_pool,
        )

        # --- 1 row per candidate ----------------
        results = [results_by_problem_id[problem_id] for problem_id in previous_table["problem_id"]]
        table = previous_table.with_columns(
            pl.Series(
                column_name,
                [None if isinstance(result, RejectionReason) else result.features[column_name] for result in results],
                dtype=pl.Float64(),
            )
            for column_name in column_names
        )
        output = self._build_output_with_rejection_reports(table, results, added_columns=column_names)
        kept_results = [result for result in results if isinstance(result, CandidateCharacterizationResult)]
        return dataclasses.replace(
            output,
            table=self._add_feature_scales(output.table),
            reports={
                **output.reports,
                INCORRECT_SOLVES_PER_CONFIG_REPORT_NAME: self._build_incorrect_solves_report(kept_results),
            },
        )

    # --------------------------------------------------------------------------
    #  Column names
    # --------------------------------------------------------------------------
    @property
    def feature_column_names(self) -> list[str]:
        """Return the names of the stage's feature columns, in the order of the feature vector.

        The vector holds 1 block per `FeatureBlock`, and the name of each column starts with its block's
        `feature_column_prefix`:

        - the solvers block: 1 ``geomean_<solver_id>`` per config, in the order of `solver_ids`, then 1
          ``gpq_<level in percent>`` per level of `SOLVERS_GPQ_LEVELS`;
        - the snuffled block: 1 column per property of `SNUFFLED_PROPERTIES`, named after the property's value.
        """
        solvers_prefix = self.feature_column_prefix(FeatureBlock.SOLVERS)
        return [
            *(f"{solvers_prefix}geomean_{solver_id}" for solver_id in self.solver_ids),
            *(self.solvers_gpq_column_name(level) for level in SOLVERS_GPQ_LEVELS),
            *(f"{self.feature_column_prefix(FeatureBlock.SNUFFLED)}{prop.value}" for prop in SNUFFLED_PROPERTIES),
        ]

    @classmethod
    def feature_column_prefix(cls, block: FeatureBlock) -> str:
        """Return the start of the name of each feature column of `block`, e.g. ``coarse_solvers_``."""
        return f"{cls.column_prefix}_{block.value}_"

    @classmethod
    def solvers_gpq_column_name(cls, level: float) -> str:
        """Return the name of the solvers block's column of the gpq at `level`, e.g. ``coarse_solvers_gpq_50``."""
        return f"{cls.feature_column_prefix(FeatureBlock.SOLVERS)}gpq_{round(100 * level):02d}"

    @classmethod
    def feature_scale_column_name(cls, block: FeatureBlock) -> str:
        """Return the name of the column that holds the scale of `block`'s features.

        The name, e.g. ``coarse_feature_scale_solvers``, does not start with the block's `feature_column_prefix`, so a
        selection of the block's feature columns by that prefix never includes this column.
        """
        return f"{cls.column_prefix}_feature_scale_{block.value}"

    @classmethod
    def feature_scale_column_names(cls) -> list[str]:
        """Return the names of the feature scale columns, 1 per `FeatureBlock`, in the order of `FeatureBlock`."""
        return [cls.feature_scale_column_name(block) for block in FeatureBlock]

    # --------------------------------------------------------------------------
    #  Reading an output table
    # --------------------------------------------------------------------------
    @classmethod
    def scaled_feature_vectors(cls, table: pl.DataFrame) -> np.ndarray:
        """Return the feature vectors of `table`, 1 row per row of `table`, with each block divided by its scale.

        `table` is an output table of this class's stage, or a table of its rows with the same columns. Over the
        candidates of the stage's output table, each block of the scaled vectors has a mean pairwise L1 distance of 1,
        so that the blocks contribute equally to an L1 distance between 2 vectors.

        The blocks follow each other in the order of `FeatureBlock`. A row whose feature scales are null, because the
        stage kept fewer than 2 candidates, gets NaN values.
        """
        return np.hstack(
            [
                table.select(cs.starts_with(cls.feature_column_prefix(block))).to_numpy()
                / table[cls.feature_scale_column_name(block)].to_numpy()[:, np.newaxis]
                for block in FeatureBlock
            ]
        )

    @classmethod
    def solvers_gpq_fevals(cls, table: pl.DataFrame, level: float) -> np.ndarray:
        """Return each row's gpq at `level` of the solvers block in `table`, as an evaluation count.

        `table` is an output table of this class's stage, or a table of its rows with the same columns. The stage
        solves with `DEFAULT_N_BISECTION_FEVALS`, so the evaluation budget that the feature was mapped with is
        `max_fevals_for` of that count.
        """
        return map_feature_to_fevals(
            table[cls.solvers_gpq_column_name(level)].to_numpy(),
            max_fevals=max_fevals_for(n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS),
        )

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @classmethod
    def _add_feature_scales(cls, table: pl.DataFrame) -> pl.DataFrame:
        """Return `table` with 1 added column per `FeatureBlock`, each holding the scale of that block's features.

        A block's scale is its mean pairwise L1 distance over the candidates of `table`, the same value in every row.

        A block with more dimensions, or with values that spread more, contributes more to an L1 distance between 2
        feature vectors; dividing each block's features by its scale gives every block a mean pairwise distance of 1,
        so that the blocks contribute equally.

        With fewer than 2 candidates, no pair exists, and the scale columns hold nulls.
        """
        if table.height < 2:
            scales_by_block = dict.fromkeys(FeatureBlock)
        else:
            scales_by_block = {
                block: mean_pairwise_l1(table.select(cs.starts_with(cls.feature_column_prefix(block))).to_numpy())
                for block in FeatureBlock
            }
        return table.with_columns(
            pl.lit(scale, dtype=pl.Float64()).alias(cls.feature_scale_column_name(block))
            for block, scale in scales_by_block.items()
        )

    def _build_incorrect_solves_report(self, kept_results: Sequence[CandidateCharacterizationResult]) -> pl.DataFrame:
        """Return the report `INCORRECT_SOLVES_PER_CONFIG_REPORT_NAME` over the kept candidates' results."""
        n_incorrect_solves = np.zeros(len(self.solver_ids), dtype=np.int64)
        for result in kept_results:
            n_incorrect_solves += result.n_incorrect_solves_per_config
        n_solves = len(kept_results) * self.fidelity.solver_mc_size
        return pl.DataFrame(
            {
                "solver_id": list(self.solver_ids),
                "n_solves": [n_solves] * len(self.solver_ids),
                "n_incorrect_solves": n_incorrect_solves,
            },
            schema={"solver_id": pl.String(), "n_solves": pl.Int64(), "n_incorrect_solves": pl.Int64()},
        ).with_columns(
            incorrect_fraction=pl.when(pl.col("n_solves") > 0).then(pl.col("n_incorrect_solves") / pl.col("n_solves"))
        )
