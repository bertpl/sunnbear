"""`PipelineMode` sets how much work the stages of the benchmark suite pipeline do."""

from enum import Enum

from .diversity_features import FeatureFidelity
from .selection import DEFAULT_SELECTION_SEC_PER_CANDIDATE
from .stages import CoarseCharacterizationStage, FineCharacterizationStage


# ==================================================================================================
#  PipelineMode
# ==================================================================================================
class PipelineMode(Enum):
    """A `PipelineMode` sets how much work the pipeline's stages do.

    Each member sets the work of 1 kind of run:

    - `PRODUCTION` builds the benchmark suites;
    - `DRAFT` takes a fraction of a production run's time, so that a maintainer can rerun the pipeline often.

    A setting belongs to the mode only when it sets how much work a stage does. The selection rules, such as the spacing
    stage's pass over a formula's candidates and the objective of `select_diverse_problem_ids`, are the same in every
    mode. So is the number of candidates that `SpacingStage` aims to keep, although it sets the work of the stages after
    spacing: a draft run then keeps about as many candidates for suite selection as a production run.

    Attributes:
        coarse_characterization_stage_fidelity: The `FeatureFidelity` of `CoarseCharacterizationStage`.
        fine_characterization_stage_fidelity: The `FeatureFidelity` of `FineCharacterizationStage`.
        selection_sec_per_candidate: The time per candidate of max-div's search in `select_diverse_problem_ids`.
    """

    PRODUCTION = (
        CoarseCharacterizationStage.default_fidelity,
        FineCharacterizationStage.default_fidelity,
        DEFAULT_SELECTION_SEC_PER_CANDIDATE,
    )
    DRAFT = (
        FeatureFidelity.COARSE_DRAFT,
        FeatureFidelity.FINE_DRAFT,
        DEFAULT_SELECTION_SEC_PER_CANDIDATE / 10,
    )

    def __init__(
        self,
        coarse_characterization_stage_fidelity: FeatureFidelity,
        fine_characterization_stage_fidelity: FeatureFidelity,
        selection_sec_per_candidate: float,
    ) -> None:
        """Store the parts of the member's value as the mode's attributes."""
        self.coarse_characterization_stage_fidelity = coarse_characterization_stage_fidelity
        self.fine_characterization_stage_fidelity = fine_characterization_stage_fidelity
        self.selection_sec_per_candidate = selection_sec_per_candidate
