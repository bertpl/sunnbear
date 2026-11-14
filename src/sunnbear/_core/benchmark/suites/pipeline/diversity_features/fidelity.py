"""`FeatureFidelity` sets how much work goes into the candidates' feature vectors."""

from enum import Enum

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SnuffledAnalysisBudget


# ==================================================================================================
#  FeatureFidelity
# ==================================================================================================
class FeatureFidelity(Enum):
    """A `FeatureFidelity` sets how much work goes into a feature vector: its solves and its snuffled analyses.

    `VERY_COARSE` differs from `COARSE` only in its snuffled analyses: it runs fewer of them, each at a lower budget,
    because snuffled's analyses take most of the time to compute a feature vector.

    Attributes:
        solver_mc_size: The size of the Monte Carlo tuple set for the solves of the core solver configs.
        n_snuffled_analyses: The number of snuffled analyses, 1 at each of the first `n_snuffled_analyses` tuples of
            the shipped Monte Carlo tuple set. The number need not be one of the sizes in `MCTuplesSize`.
        snuffled_budget: The budget of each snuffled analysis.
    """

    VERY_COARSE = (MCTuplesSize.SIZE_32, 8, SnuffledAnalysisBudget.VERY_LOW)
    COARSE = (MCTuplesSize.SIZE_32, 32, SnuffledAnalysisBudget.LOW)
    FULL = (MCTuplesSize.SIZE_1024, 64, SnuffledAnalysisBudget.HIGH)

    def __init__(
        self, solver_mc_size: MCTuplesSize, n_snuffled_analyses: int, snuffled_budget: SnuffledAnalysisBudget
    ) -> None:
        """Store the parts of the member's value as the fidelity's attributes."""
        self.solver_mc_size = solver_mc_size
        self.n_snuffled_analyses = n_snuffled_analyses
        self.snuffled_budget = snuffled_budget

    @property
    def snuffled_mc_tuples(self) -> MCTuples:
        """Return the Monte Carlo tuples of the snuffled analyses, 1 per analysis.

        Every size of the shipped tuple set begins with the same tuples, so the tuples are taken from the largest size.
        """
        return load_mc_tuples(max(MCTuplesSize)).first(self.n_snuffled_analyses)
