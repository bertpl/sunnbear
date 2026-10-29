"""`FeatureFidelity` sets how much work goes into the candidates' feature vectors, and names their columns.

A candidate's feature vector has 1 block per `FeatureBlock`:

- the solvers block, from the solves of the core solver configs: 1 geometric mean of `n_fevals_eff` per config,
  and the geometric pseudo-quantile (`gpq`) of all the candidate's solves together at each of `SOLVERS_GPQ_LEVELS`;
- the snuffled block, from snuffled's analyses: the mean of each of `SNUFFLED_PROPERTIES` over the analyses.
"""

from collections.abc import Sequence
from enum import Enum, StrEnum

import numpy as np
import polars as pl
import polars.selectors as cs
from snuffled import FunctionProperty, RootProperty

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SnuffledAnalysisBudget
from sunnbear._core.stats import mean_pairwise_l1

SOLVERS_GPQ_LEVELS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
# `SNUFFLED_PROPERTIES` lists snuffled's root and function properties in the order in which an analysis extracts
# them: the root properties first, because the function properties reuse the samples of f that the root properties
# take.
SNUFFLED_PROPERTIES = (*RootProperty, *FunctionProperty)


# ==================================================================================================
#  FeatureFidelity
# ==================================================================================================
class FeatureFidelity(Enum):
    """A `FeatureFidelity` sets how much work goes into a feature vector: its tuple sets and its snuffled budget.

    The member's name, in lower case, starts the names of its feature columns and feature scale columns, so that 1
    table can hold the columns of 2 fidelities.

    Attributes:
        solver_mc_size: The size of the Monte Carlo tuple set for the solves of the core solver configs.
        snuffled_mc_size: The size of the Monte Carlo tuple set for snuffled's analyses.
        snuffled_budget: The budget of each snuffled analysis.
    """

    COARSE = (MCTuplesSize.SIZE_32, MCTuplesSize.SIZE_32, SnuffledAnalysisBudget.LOW)

    def __init__(
        self, solver_mc_size: MCTuplesSize, snuffled_mc_size: MCTuplesSize, snuffled_budget: SnuffledAnalysisBudget
    ) -> None:
        """Store the parts of the member's value as the fidelity's attributes."""
        self.solver_mc_size = solver_mc_size
        self.snuffled_mc_size = snuffled_mc_size
        self.snuffled_budget = snuffled_budget

    def feature_column_prefix(self, block: "FeatureBlock") -> str:
        """Return the start of the name of each feature column of `block`, e.g. ``coarse_solvers_``."""
        return f"{self.name.lower()}_{block.value}_"

    def feature_column_names(self, solver_ids: Sequence[str]) -> list[str]:
        """Return the names of the feature columns for the core solver configs `solver_ids`, in the order of the vector.

        The vector holds 1 block per `FeatureBlock`, and the name of each column starts with its block's
        `feature_column_prefix`:

        - the solvers block: 1 ``geomean_<solver_id>`` per config, in the order of `solver_ids`, then 1
          ``gpq_<level in percent>`` per level of `SOLVERS_GPQ_LEVELS`;
        - the snuffled block: 1 column per property of `SNUFFLED_PROPERTIES`, named after the property's value.
        """
        solvers_prefix = self.feature_column_prefix(FeatureBlock.SOLVERS)
        return [
            *(f"{solvers_prefix}geomean_{solver_id}" for solver_id in solver_ids),
            *(f"{solvers_prefix}gpq_{round(100 * level):02d}" for level in SOLVERS_GPQ_LEVELS),
            *(f"{self.feature_column_prefix(FeatureBlock.SNUFFLED)}{prop.value}" for prop in SNUFFLED_PROPERTIES),
        ]

    def feature_scale_column_name(self, block: "FeatureBlock") -> str:
        """Return the name of the column that holds the scale of `block`'s features, which `add_feature_scales` adds.

        The name, e.g. ``coarse_feature_scale_solvers``, does not start with the block's `feature_column_prefix`, so a
        selection of the block's feature columns by that prefix never includes this column.
        """
        return f"{self.name.lower()}_feature_scale_{block.value}"

    def feature_scale_column_names(self) -> list[str]:
        """Return the names of the feature scale columns, 1 per `FeatureBlock`, in the order of `add_feature_scales`."""
        return [self.feature_scale_column_name(block) for block in FeatureBlock]

    def add_feature_scales(self, table: pl.DataFrame) -> pl.DataFrame:
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
                block: mean_pairwise_l1(table.select(cs.starts_with(self.feature_column_prefix(block))).to_numpy())
                for block in FeatureBlock
            }
        return table.with_columns(
            pl.lit(scale, dtype=pl.Float64()).alias(self.feature_scale_column_name(block))
            for block, scale in scales_by_block.items()
        )

    def balanced_feature_vectors(self, table: pl.DataFrame) -> np.ndarray:
        """Return the feature vectors of `table`, 1 row per row of `table`, with each block divided by its scale.

        `table` holds the feature columns and the feature scale columns, which `add_feature_scales` added. Over the
        candidates of that table, each block of the balanced vectors has a mean pairwise L1 distance of 1, so that the
        blocks contribute equally to an L1 distance between 2 vectors.

        The blocks follow each other in the order of `FeatureBlock`. A row whose feature scales are null, because
        `add_feature_scales` received fewer than 2 candidates, gets NaN values.
        """
        return np.hstack(
            [
                table.select(cs.starts_with(self.feature_column_prefix(block))).to_numpy()
                / table[self.feature_scale_column_name(block)].to_numpy()[:, np.newaxis]
                for block in FeatureBlock
            ]
        )


# ==================================================================================================
#  FeatureBlock
# ==================================================================================================
class FeatureBlock(StrEnum):
    """A `FeatureBlock` names a block of a feature vector after its source.

    The member's value appears in the name of each of the block's columns.
    """

    SOLVERS = "solvers"
    SNUFFLED = "snuffled"
