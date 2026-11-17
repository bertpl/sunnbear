"""`FeatureFidelity` sets how much work goes into the candidates' feature vectors."""

from enum import Enum

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize
from sunnbear._core.benchmark.suites.pipeline.snuffled_analysis import SnuffledAnalysisBudget


# ==================================================================================================
#  FeatureFidelity
# ==================================================================================================
class FeatureFidelity(Enum):
    """A `FeatureFidelity` sets how much work goes into a feature vector: its solves and its snuffled analyses.

    Each member is the fidelity of 1 characterization stage in 1 `PipelineMode`:

    - `COARSE_PRODUCTION` and `FINE_PRODUCTION` are the fidelities of coarse and of fine characterization in
      production mode;
    - `COARSE_DRAFT` and `FINE_DRAFT` are their fidelities in draft mode.

    Each member writes out its own settings, also where 2 members' settings are equal today, so that a change to 1
    member's settings leaves the others as they are.

    A member's value starts with the member's name. An enum merges members with equal values into 1 member, and the
    name keeps 2 fidelities with the same settings apart.

    Attributes:
        solver_mc_size: The size of the Monte Carlo tuple set for the solves of the core solver configs.
        snuffled_mc_size: The size of the Monte Carlo tuple set for snuffled's analyses, 1 analysis per tuple.
        snuffled_budget: The budget of each snuffled analysis.
    """

    COARSE_PRODUCTION = (
        "COARSE_PRODUCTION",
        MCTuplesSize.SIZE_64,
        MCTuplesSize.SIZE_16,
        SnuffledAnalysisBudget.MEDIUM,
    )
    FINE_PRODUCTION = ("FINE_PRODUCTION", MCTuplesSize.SIZE_1024, MCTuplesSize.SIZE_64, SnuffledAnalysisBudget.HIGH)
    COARSE_DRAFT = ("COARSE_DRAFT", MCTuplesSize.SIZE_16, MCTuplesSize.SIZE_4, SnuffledAnalysisBudget.LOW)
    FINE_DRAFT = ("FINE_DRAFT", MCTuplesSize.SIZE_64, MCTuplesSize.SIZE_16, SnuffledAnalysisBudget.MEDIUM)

    def __init__(
        self,
        member_name: str,
        solver_mc_size: MCTuplesSize,
        snuffled_mc_size: MCTuplesSize,
        snuffled_budget: SnuffledAnalysisBudget,
    ) -> None:
        """Store the settings in the member's value as the fidelity's attributes; `member_name` is not stored."""
        self.solver_mc_size = solver_mc_size
        self.snuffled_mc_size = snuffled_mc_size
        self.snuffled_budget = snuffled_budget
