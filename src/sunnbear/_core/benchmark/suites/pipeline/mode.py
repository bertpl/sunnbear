"""`PipelineMode` sets how much work the stages of the benchmark suite pipeline do."""

from enum import Enum

from .features import FeatureFidelity
from .selection import DEFAULT_SELECTION_SEC_PER_CANDIDATE
from .stages import FullCharacterizationStage


# ==================================================================================================
#  PipelineMode
# ==================================================================================================
class PipelineMode(Enum):
    """A `PipelineMode` sets how much work the pipeline's stages do.

    Each member sets the work of 1 kind of run:

    - `FULL` builds the benchmark suites;
    - `DRAFT` takes a fraction of a full run's time, so that a maintainer can rerun the pipeline often.

    A setting belongs to the mode only when it sets how much work a stage does. The selection rules, such as the spacing
    stage's minimum distance and the objective of `select_diverse_suite`, are the same in every mode.

    Attributes:
        full_characterization_stage_fidelity: The `FeatureFidelity` that `FullCharacterizationStage` runs at.
        selection_sec_per_candidate: The time per candidate of max-div's search in `select_diverse_suite`.
    """

    FULL = (FullCharacterizationStage.default_fidelity, DEFAULT_SELECTION_SEC_PER_CANDIDATE)
    DRAFT = (FeatureFidelity.COARSE, DEFAULT_SELECTION_SEC_PER_CANDIDATE / 10)

    def __init__(
        self, full_characterization_stage_fidelity: FeatureFidelity, selection_sec_per_candidate: float
    ) -> None:
        """Store the parts of the member's value as the mode's attributes."""
        self.full_characterization_stage_fidelity = full_characterization_stage_fidelity
        self.selection_sec_per_candidate = selection_sec_per_candidate
