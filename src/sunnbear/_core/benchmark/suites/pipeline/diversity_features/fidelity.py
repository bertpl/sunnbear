"""`FeatureFidelity` sets how much work goes into the candidates' feature vectors."""

from enum import Enum

from sunnbear._core.benchmark.mc_tuples import MCTuples, MCTuplesSize, load_mc_tuples
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SnuffledAnalysisBudget


# ==================================================================================================
#  FeatureFidelity
# ==================================================================================================
class FeatureFidelity(Enum):
    """A `FeatureFidelity` sets how much work goes into a feature vector: its solves and its snuffled analyses.

    Each member is the fidelity of 1 characterization stage in 1 `PipelineMode`:

    - `COARSE` and `FULL` are the fidelities of coarse and of full characterization in full mode;
    - `COARSE_DRAFT` and `FULL_DRAFT` are their fidelities in draft mode.

    `COARSE_DRAFT` differs from `COARSE` only in its snuffled analyses: it runs fewer of them, each at a lower budget,
    because snuffled's analyses take most of the time to compute a feature vector.

    A member's value starts with the member's name. An enum merges members with equal values into 1 member, and the
    name keeps 2 fidelities with the same settings apart.

    Attributes:
        solver_mc_size: The size of the Monte Carlo tuple set for the solves of the core solver configs.
        n_snuffled_analyses: The number of snuffled analyses, 1 at each of the first `n_snuffled_analyses` tuples of
            the shipped Monte Carlo tuple set. The number need not be one of the sizes in `MCTuplesSize`.
        snuffled_budget: The budget of each snuffled analysis.
    """

    COARSE = ("COARSE", MCTuplesSize.SIZE_32, 32, SnuffledAnalysisBudget.LOW)
    FULL = ("FULL", MCTuplesSize.SIZE_1024, 64, SnuffledAnalysisBudget.HIGH)
    COARSE_DRAFT = ("COARSE_DRAFT", MCTuplesSize.SIZE_32, 8, SnuffledAnalysisBudget.VERY_LOW)
    FULL_DRAFT = ("FULL_DRAFT", MCTuplesSize.SIZE_32, 32, SnuffledAnalysisBudget.LOW)

    def __init__(
        self,
        member_name: str,
        solver_mc_size: MCTuplesSize,
        n_snuffled_analyses: int,
        snuffled_budget: SnuffledAnalysisBudget,
    ) -> None:
        """Store the settings in the member's value as the fidelity's attributes; `member_name` is not stored."""
        self.solver_mc_size = solver_mc_size
        self.n_snuffled_analyses = n_snuffled_analyses
        self.snuffled_budget = snuffled_budget

    @property
    def snuffled_mc_tuples(self) -> MCTuples:
        """Return the Monte Carlo tuples of the snuffled analyses, 1 per analysis.

        Every size of the shipped tuple set begins with the same tuples, so the tuples are taken from the largest size.
        """
        return load_mc_tuples(max(MCTuplesSize)).first(self.n_snuffled_analyses)
