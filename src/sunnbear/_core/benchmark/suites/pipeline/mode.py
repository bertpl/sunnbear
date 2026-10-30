"""`PipelineMode` sets how much work the stages of the benchmark suite pipeline do."""

from enum import Enum

from .features import FeatureFidelity
from .stages import DEFAULT_CORE_SELECTION_SEC_PER_CANDIDATE, FullCharacterizationStage


# ==================================================================================================
#  PipelineMode
# ==================================================================================================
class PipelineMode(Enum):
    """A `PipelineMode` sets how much work the pipeline's stages do.

    A full run builds the benchmark suites; a draft run takes a fraction of a full run's time, so that a maintainer can
    rerun the pipeline often.

    A setting belongs to the mode only when it sets how much work a stage does. The selection rules, such as spacing's
    minimum distance and max-div's objective, are the same in every mode.

    Attributes:
        full_characterization_fidelity: The `FeatureFidelity` that full characterization runs at.
        core_selection_sec_per_candidate: The time per candidate of max-div's search in core selection.
    """

    FULL = (FullCharacterizationStage.default_fidelity, DEFAULT_CORE_SELECTION_SEC_PER_CANDIDATE)
    DRAFT = (FeatureFidelity.COARSE, DEFAULT_CORE_SELECTION_SEC_PER_CANDIDATE / 10)

    def __init__(
        self, full_characterization_fidelity: FeatureFidelity, core_selection_sec_per_candidate: float
    ) -> None:
        """Store the parts of the member's value as the mode's attributes."""
        self.full_characterization_fidelity = full_characterization_fidelity
        self.core_selection_sec_per_candidate = core_selection_sec_per_candidate
