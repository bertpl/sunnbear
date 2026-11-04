"""`PipelineStageId` names the stages of the benchmark suite pipeline, in run order."""

from enum import StrEnum


# ==================================================================================================
#  PipelineStageId
# ==================================================================================================
class PipelineStageId(StrEnum):
    """A `PipelineStageId` names 1 stage of the benchmark suite pipeline; the members follow the run order.

    Each value starts with ``s`` and the stage's position in the run order, so files named after the values sort in run
    order.
    """

    CANDIDATE_GENERATION = "s1_candidate_generation"
    CANDIDATE_VALIDATION = "s2_candidate_validation"
    COARSE_CHARACTERIZATION = "s3_coarse_characterization"
    SPACING = "s4_spacing"
    FULL_CHARACTERIZATION = "s5_full_characterization"
    CORE_SELECTION = "s6_core_selection"
    DISTILLATION = "s7_distillation"
