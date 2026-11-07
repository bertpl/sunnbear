"""`DiversityFeatureFactory` computes the candidates' diversity features, from 1 candidate's row to a set's matrix.

The class docstring defines the features and their raw form.
"""

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from sunnbear._core.benchmark.protocol import DEFAULT_N_BISECTION_FEVALS, max_fevals_for
from sunnbear._core.solvers import bracketing  # noqa: F401 - importing the shipped solvers registers their configs
from sunnbear._core.solvers.core import SolverConfig, SolverConfigRegistry
from sunnbear._core.stats import gpq, mean_pairwise_l1

from .feature_matrix import FeatureMatrix
from .feature_vector import SNUFFLED_PROPERTIES, SOLVERS_GPQ_LEVELS, FeatureBlock
from .fevals_mapping import map_fevals_to_feature

# The characterization stages solve with `DEFAULT_N_BISECTION_FEVALS`, so `_MAX_FEVALS` is the budget of each of their
# solves, the count that `map_fevals_to_feature` maps to 1.
_MAX_FEVALS = max_fevals_for(n_bisection_fevals=DEFAULT_N_BISECTION_FEVALS)


# ==================================================================================================
#  DiversityFeatureFactory
# ==================================================================================================
class DiversityFeatureFactory:
    """A `DiversityFeatureFactory` computes the candidates' diversity features, and defines what they are.

    A candidate's features form 1 block per `FeatureBlock`, in the order of `FeatureBlock`:

    - the solvers block, from the candidate's solves with each config of `solver_ids`:
      - per config, in the order of `solver_ids`: the geometric mean of `n_fevals_eff` over the candidate's solves;
      - per level of `SOLVERS_GPQ_LEVELS`: the geometric pseudo-quantile (`gpq`) of `n_fevals_eff` over the
        candidate's solves of all configs together;
    - the snuffled block, from snuffled's analyses: the mean of each property of `SNUFFLED_PROPERTIES`.

    A raw feature is a feature in natural units, untransformed: the solvers block holds evaluation counts in
    [2, max_fevals], and the snuffled block mean property scores. The factory computes them in 3 steps:

    - `compute_raw_feature_row` computes 1 candidate's raw features, in the worker that solves and analyzes it, so that
      the solves need not be kept;
    - `fit_block_scales` computes the scale of each block over a set of candidates;
    - `build_scaled_matrix` builds the matrix that `SpacingStage` and max-div take, in 2 steps: the solvers block, and
      only that block, is mapped onto [0, 1] by `map_fevals_to_feature`, as ``log(n / 2) / log(max_fevals / 2)``;
      then each block is divided by its scale.

    The factory holds no state, so a worker task can carry it.
    """

    @property
    def solver_configs(self) -> tuple[SolverConfig, ...]:
        """Return the solver configs that characterize a candidate, in the order of the solvers block.

        They are the registered configs whose role marks them for characterizing test problems, in the order of
        `SolverConfigRegistry.configs`.
        """
        return tuple(
            config for config in SolverConfigRegistry.configs() if config.role.is_used_for_problem_characterization
        )

    @property
    def solver_ids(self) -> tuple[str, ...]:
        """Return the ids of `solver_configs`, in their order.

        A test that needs fewer or other configs patches this property.
        """
        return tuple(config.solver_id for config in self.solver_configs)

    @property
    def feature_names(self) -> tuple[str, ...]:
        """Return the feature names, in the order of the features, each starting with its `FeatureBlock` value."""
        return (
            *(f"{FeatureBlock.SOLVERS}_geomean_{solver_id}" for solver_id in self.solver_ids),
            *(f"{FeatureBlock.SOLVERS}_gpq_{round(100 * level):02d}" for level in SOLVERS_GPQ_LEVELS),
            *(f"{FeatureBlock.SNUFFLED}_{prop.value}" for prop in SNUFFLED_PROPERTIES),
        )

    # --------------------------------------------------------------------------
    #  Per candidate
    # --------------------------------------------------------------------------
    def compute_raw_feature_row(self, *, n_fevals_eff: np.ndarray, snuffled_property_values: np.ndarray) -> np.ndarray:
        """Return 1 candidate's raw features, in the order of `feature_names`.

        Args:
            n_fevals_eff: The `n_fevals_eff` of the candidate's solves, 1 row per Monte Carlo sample and 1 column per
                config, in the order of `solver_ids`; the solves use `DEFAULT_N_BISECTION_FEVALS`, and an incorrect
                solve counts as its budget.
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
        """Return each block's scale over the candidates of `raw_feature_matrix`, or ``None`` if they are fewer than 2.

        A block's scale is its mean pairwise L1 distance, computed after the solvers block is mapped onto the log scale
        that `build_scaled_matrix` uses.

        A block with more features, or with values that spread more, contributes more to an L1 distance between 2
        candidates; dividing each block by its scale gives every block a mean pairwise distance of 1 over these
        candidates, so that the blocks contribute equally.

        A block whose values are the same for all the candidates gets a scale of 0, which `build_scaled_matrix` cannot
        divide by.
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
        """Return the scaled matrix of the candidates of `raw_feature_matrix`, for `SpacingStage` and max-div.

        The solvers block is mapped with `map_fevals_to_feature`; then each block is divided by its scale in
        `block_scales`. It does not check `block_scales`: a block with a scale of 0 gives infinite or NaN values.
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
        """Return the columns of each block, in the order of `feature_names`."""
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
        scale_per_block: The scale of each block, as `DiversityFeatureFactory.fit_block_scales` computes it.
    """

    scale_per_block: Mapping[FeatureBlock, float]
