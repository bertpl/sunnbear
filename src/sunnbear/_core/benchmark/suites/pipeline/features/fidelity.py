"""`FeatureFidelity` sets how much work goes into the candidates' feature vectors, and names their columns.

A candidate's feature vector has 2 blocks:

- the empirical block, from the solves of the core solver configs: 1 geometric mean of `n_fevals_eff` per config,
  and the geometric pseudo-quantile (`gpq`) of all the candidate's solves together at each of `EMPIRICAL_GPQ_LEVELS`;
- the analytical block, from snuffled's analyses: the mean of each of `ANALYTICAL_PROPERTIES` over the analyses.
"""

from collections.abc import Sequence
from enum import Enum

from snuffled import FunctionProperty, RootProperty

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SnuffledAnalysisBudget

EMPIRICAL_GPQ_LEVELS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
# `ANALYTICAL_PROPERTIES` lists snuffled's root and function properties in the order in which an analysis extracts
# them: the root properties first, because the function properties reuse the samples of f that the root properties
# take.
ANALYTICAL_PROPERTIES = (*RootProperty, *FunctionProperty)


# ==================================================================================================
#  FeatureFidelity
# ==================================================================================================
class FeatureFidelity(Enum):
    """A `FeatureFidelity` sets how much work goes into a feature vector: its tuple sets and its snuffled budget.

    The member's name, in lower case, starts the names of its feature columns, so that 1 table can hold the columns of
    2 fidelities.

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

    def feature_column_names(self, solver_ids: Sequence[str]) -> list[str]:
        """Return the names of the feature columns for the core solver configs `solver_ids`, in the order of the vector.

        The vector holds 2 blocks:

        - the empirical block: 1 ``geomean_<solver_id>`` per config, in the order of `solver_ids`, then 1
          ``gpq_<level in percent>`` per level of `EMPIRICAL_GPQ_LEVELS`;
        - the analytical block: 1 column per property of `ANALYTICAL_PROPERTIES`, named after the property's value.
        """
        prefix = self.name.lower()
        return [
            *(f"{prefix}_emp_geomean_{solver_id}" for solver_id in solver_ids),
            *(f"{prefix}_emp_gpq_{round(100 * level):02d}" for level in EMPIRICAL_GPQ_LEVELS),
            *(f"{prefix}_ana_{prop.value}" for prop in ANALYTICAL_PROPERTIES),
        ]
