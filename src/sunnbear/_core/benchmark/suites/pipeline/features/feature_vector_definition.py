"""`FeatureVectorDefinition` defines the candidates' feature vectors: what they hold, and how they are computed.

The definition computes the feature vectors in 3 steps:

- per candidate, in the worker that solves and analyzes it: the candidate's raw features, from its solves and snuffled
  analyses, by `FeatureVectorDefinition.compute_raw_features`;
- over a set of candidates: the scale of each `FeatureBlock`, a `FeatureBlockScales`, by
  `FeatureVectorDefinition.fit_block_scales`;
- the scaled matrix for the spacing stage and max-div, by `FeatureVectorDefinition.build_scaled_matrix`.

The raw features are in natural units (evaluation counts and snuffled scores), so that they can be shown as they are.
Only the matrix maps the solvers block onto a log scale, with `map_fevals_to_feature`, and divides each block by its
scale.
"""

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, max_fevals_for
from sunnbear._core.stats import gpq, mean_pairwise_l1

from .feature_matrix import FeatureMatrix
from .feature_vector import SNUFFLED_PROPERTIES, SOLVERS_GPQ_LEVELS, FeatureBlock
from .fevals_mapping import map_fevals_to_feature

# The characterization stages solve with `DEFAULT_N_BISECTION_FEVALS`, so every evaluation count of the solvers block
# lies in [2, `_MAX_FEVALS`]: a correct solve takes at least 2 evaluations, and an incorrect one is counted as
# `_MAX_FEVALS` evaluations, the solve's budget.
_MAX_FEVALS = max_fevals_for(n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)


# ==================================================================================================
#  FeatureVectorDefinition
# ==================================================================================================
@dataclass(frozen=True)
class FeatureVectorDefinition:
    """A `FeatureVectorDefinition` defines the candidates' feature vector for a set of core solver configs.

    The vector holds 1 block per `FeatureBlock`, in the order of `FeatureBlock`:

    - the solvers block, from the solves of the core solver configs: per config, in the order of `solver_ids`, the
      geometric mean of `n_fevals_eff`, then, at each level of `SOLVERS_GPQ_LEVELS`, the geometric pseudo-quantile
      (`gpq`) of `n_fevals_eff` over the candidate's solves of all configs together;
    - the snuffled block, from snuffled's analyses: the mean of each property of `SNUFFLED_PROPERTIES`.

    The definition is picklable, so that a worker task can carry it.

    Attributes:
        solver_ids: The ids of the core solver configs.
    """

    solver_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        """Check that the solvers block has at least 1 config.

        Raises:
            ValueError: If `solver_ids` is empty.
        """
        if not self.solver_ids:
            raise ValueError("A feature vector definition needs at least 1 core solver config.")

    @property
    def feature_names(self) -> tuple[str, ...]:
        """Return the names of the features, in the order of the vector, each starting with the value of its block."""
        return (
            *(f"{FeatureBlock.SOLVERS}_geomean_{solver_id}" for solver_id in self.solver_ids),
            *(f"{FeatureBlock.SOLVERS}_gpq_{round(100 * level):02d}" for level in SOLVERS_GPQ_LEVELS),
            *(f"{FeatureBlock.SNUFFLED}_{prop.value}" for prop in SNUFFLED_PROPERTIES),
        )

    # --------------------------------------------------------------------------
    #  Per candidate
    # --------------------------------------------------------------------------
    def compute_raw_features(self, *, n_fevals_eff: np.ndarray, snuffled_property_values: np.ndarray) -> np.ndarray:
        """Return 1 candidate's raw features, in the order of `feature_names`.

        Args:
            n_fevals_eff: The `n_fevals_eff` of the candidate's solves, 1 row per tuple and 1 column per config, in the
                order of `solver_ids`.
            snuffled_property_values: The properties of the candidate's snuffled analyses, 1 row per analysis and 1
                column per property, in the order of `SNUFFLED_PROPERTIES`.

        Raises:
            ValueError: If either array is not 2-dimensional, or its number of columns differs from the number of
                configs or properties.
        """
        if n_fevals_eff.ndim != 2 or n_fevals_eff.shape[1] != len(self.solver_ids):
            raise ValueError(f"Expected 1 column of n_fevals_eff per config, got shape {n_fevals_eff.shape}.")
        elif snuffled_property_values.ndim != 2 or snuffled_property_values.shape[1] != len(SNUFFLED_PROPERTIES):
            raise ValueError(
                f"Expected 1 column of snuffled values per property, got shape {snuffled_property_values.shape}."
            )
        else:
            return np.array(
                [
                    *np.exp(np.log(n_fevals_eff).mean(axis=0)),
                    *(gpq(n_fevals_eff.ravel(), level) for level in SOLVERS_GPQ_LEVELS),
                    *snuffled_property_values.mean(axis=0),
                ]
            )

    # --------------------------------------------------------------------------
    #  Over a set of candidates
    # --------------------------------------------------------------------------
    def fit_block_scales(self, raw_feature_matrix: FeatureMatrix) -> "FeatureBlockScales | None":
        """Return the scale of each block over the candidates of `raw_feature_matrix`, or ``None`` for fewer than 2.

        A block's scale is its mean pairwise L1 distance, computed after the solvers block is mapped onto the log scale
        that `build_scaled_matrix` uses.

        A block with more features, or with values that spread more, contributes more to an L1 distance between 2
        feature vectors; dividing each block by its scale gives every block a mean pairwise distance of 1 over these
        candidates, so that the blocks contribute equally. A block whose values are the same for all the candidates
        gets a scale of 0, which `build_scaled_matrix` cannot divide by.
        """
        if len(raw_feature_matrix.problem_ids) < 2:
            return None
        else:
            values = self._map_solvers_block_to_log_scale(raw_feature_matrix.values)
            return FeatureBlockScales(
                scale_per_block={
                    block: mean_pairwise_l1(values[:, block_slice]) for block, block_slice in self._block_slices.items()
                }
            )

    def build_scaled_matrix(
        self, raw_feature_matrix: FeatureMatrix, block_scales: "FeatureBlockScales"
    ) -> FeatureMatrix:
        """Return the scaled matrix of the candidates of `raw_feature_matrix`, for the spacing stage and max-div.

        `map_fevals_to_feature` maps the evaluation counts of the solvers block onto [0, 1] on a log scale; then each
        block is divided by its scale in `block_scales`.
        """
        values = self._map_solvers_block_to_log_scale(raw_feature_matrix.values)
        for block, block_slice in self._block_slices.items():
            values[:, block_slice] /= block_scales.scale_per_block[block]
        return FeatureMatrix(problem_ids=raw_feature_matrix.problem_ids, values=values)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @property
    def _block_slices(self) -> dict[FeatureBlock, slice]:
        """Return the columns of each block in the feature vector."""
        n_solvers_features = len(self.solver_ids) + len(SOLVERS_GPQ_LEVELS)
        return {
            FeatureBlock.SOLVERS: slice(0, n_solvers_features),
            FeatureBlock.SNUFFLED: slice(n_solvers_features, n_solvers_features + len(SNUFFLED_PROPERTIES)),
        }

    def _map_solvers_block_to_log_scale(self, raw_values: np.ndarray) -> np.ndarray:
        """Return a copy of `raw_values` with the solvers block mapped by `map_fevals_to_feature`."""
        values = np.array(raw_values, dtype=np.float64)
        solvers_slice = self._block_slices[FeatureBlock.SOLVERS]
        values[:, solvers_slice] = map_fevals_to_feature(values[:, solvers_slice], max_fevals=_MAX_FEVALS)
        return values


# ==================================================================================================
#  FeatureBlockScales
# ==================================================================================================
@dataclass(frozen=True)
class FeatureBlockScales:
    """A `FeatureBlockScales` holds the scale of each `FeatureBlock` over a set of candidates.

    Attributes:
        scale_per_block: The scale of each block, as `FeatureVectorDefinition.fit_block_scales` computes it.
    """

    scale_per_block: Mapping[FeatureBlock, float]
