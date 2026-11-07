"""`FeatureFidelity` sets how much work goes into the candidates' feature vectors."""

from enum import Enum

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SnuffledAnalysisBudget


# ==================================================================================================
#  FeatureFidelity
# ==================================================================================================
class FeatureFidelity(Enum):
    """A `FeatureFidelity` sets how much work goes into a feature vector: its tuple sets and its snuffled budget.

    Attributes:
        solver_mc_size: The size of the Monte Carlo tuple set for the solves of the core solver configs.
        snuffled_mc_size: The size of the Monte Carlo tuple set for snuffled's analyses.
        snuffled_budget: The budget of each snuffled analysis.
    """

    COARSE = (MCTuplesSize.SIZE_32, MCTuplesSize.SIZE_32, SnuffledAnalysisBudget.LOW)
    FULL = (MCTuplesSize.SIZE_1024, MCTuplesSize.SIZE_64, SnuffledAnalysisBudget.HIGH)

    def __init__(
        self, solver_mc_size: MCTuplesSize, snuffled_mc_size: MCTuplesSize, snuffled_budget: SnuffledAnalysisBudget
    ) -> None:
        """Store the parts of the member's value as the fidelity's attributes."""
        self.solver_mc_size = solver_mc_size
        self.snuffled_mc_size = snuffled_mc_size
        self.snuffled_budget = snuffled_budget
