"""`FeatureVectorDefinition` defines the candidates' feature vectors: what they hold, and how they are computed.

The definition computes the feature vectors in 3 steps:

- per candidate, in the worker that solves and analyzes it: the candidate's raw features, from its solves and snuffled
  analyses, by `FeatureVectorDefinition.compute_raw_features`;
- over a set of candidates: the scale of each `FeatureBlock`, a `FeatureBlockScales`, by
  `FeatureVectorDefinition.fit_block_scales`;
- the matrix that spacing and max-div take, by `FeatureVectorDefinition.build_scaled_matrix`.

The raw features are in natural units, evaluation counts and snuffled scores, so that they can be shown as they are.
The log scale of the solvers block and the block scales apply only in the matrix.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Self

import numpy as np

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, max_fevals_for
from sunnbear._core.solvers.core import SolverConfig
from sunnbear._core.stats import gpq, mean_pairwise_l1

from .feature_matrix import FeatureMatrix
from .feature_vector import SNUFFLED_PROPERTIES, SOLVERS_GPQ_LEVELS, FeatureBlock
from .fevals_mapping import map_fevals_to_feature

# The characterization stages solve with `DEFAULT_N_BISECTION_FEVALS`, so every evaluation count of the solvers block
# lies in [2, `_MAX_FEVALS`]: a correct solve takes at least 2 evaluations, and an incorrect one counts as the budget.
_MAX_FEVALS = max_fevals_for(n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)


# ==================================================================================================
#  FeatureVectorDefinition
# ==================================================================================================
@dataclass(frozen=True)
class FeatureVectorDefinition:
    """A `FeatureVectorDefinition` defines the feature vector of the candidates that a set of core solver configs solve.

    The vector holds 1 block per `FeatureBlock`, in the order of `FeatureBlock`:

    - the solvers block, from the solves of the core solver configs: per config, in the order of `solver_ids`, the
      geometric mean of `n_fevals_eff`, then the geometric pseudo-quantile (`gpq`) of all the candidate's solves pooled,
      at each level of `SOLVERS_GPQ_LEVELS`;
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
        """Return the names of the features, in the order of the vector, each starting with its block's value.

        The names are ``solvers_geomean_<solver_id>`` per config, ``solvers_gpq_<level in percent>`` per level, and
        ``snuffled_<property>`` per snuffled property.
        """
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
    def fit_block_scales(self, raw_features: FeatureMatrix) -> "FeatureBlockScales | None":
        """Return the scale of each block over the candidates of `raw_features`, or ``None`` for fewer than 2.

        A block's scale is its mean pairwise L1 distance, with the solvers block on the log scale of
        `build_scaled_matrix`. A block with more features, or with values that spread more, contributes more to an L1
        distance between 2 feature vectors; dividing each block by its scale gives every block a mean pairwise distance
        of 1 over these candidates, so that the blocks contribute equally.
        """
        if len(raw_features.problem_ids) < 2:
            return None
        else:
            values = self._map_solvers_block_to_log_scale(raw_features.values)
            return FeatureBlockScales(
                scale_per_block={
                    block: mean_pairwise_l1(values[:, block_slice]) for block, block_slice in self._block_slices.items()
                }
            )

    def build_scaled_matrix(self, raw_features: FeatureMatrix, block_scales: "FeatureBlockScales") -> FeatureMatrix:
        """Return the matrix that spacing and max-div take, with the candidates of `raw_features`.

        The solvers block is mapped onto a log scale, as `map_fevals_to_feature` maps its evaluation counts onto
        [0, 1]; then each block is divided by its scale in `block_scales`.
        """
        values = self._map_solvers_block_to_log_scale(raw_features.values)
        for block, block_slice in self._block_slices.items():
            values[:, block_slice] /= block_scales.scale_per_block[block]
        return FeatureMatrix(problem_ids=raw_features.problem_ids, values=values)

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

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_core_solver_configs(cls, core_solver_configs: Sequence[SolverConfig]) -> Self:
        """Return the definition whose solvers block comes from `core_solver_configs`, in their order.

        Raises:
            ValueError: If `core_solver_configs` is empty.
        """
        return cls(solver_ids=tuple(config.solver_id for config in core_solver_configs))


# ==================================================================================================
#  FeatureBlockScales
# ==================================================================================================
@dataclass(frozen=True)
class FeatureBlockScales:
    """A `FeatureBlockScales` holds the scale of each `FeatureBlock`, fitted on the candidates that 1 stage keeps.

    Attributes:
        scale_per_block: The scale of each block, as `FeatureVectorDefinition.fit_block_scales` computes it.
    """

    scale_per_block: Mapping[FeatureBlock, float]
