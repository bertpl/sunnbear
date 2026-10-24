"""`PipelineStage` names the stages of the suite pipeline, in run order."""

from enum import StrEnum


# ==================================================================================================
#  PipelineStage
# ==================================================================================================
class PipelineStage(StrEnum):
    """A `PipelineStage` names 1 stage of the suite pipeline.

    Its value is the name of the stage's output file in the `PipelineWorkspace`, without the suffix. Each
    value starts with ``s`` and the stage's position in the run order, so a listing of the workspace
    directory shows the outputs in run order.
    """

    CANDIDATE_GENERATION = "s1_candidates"
    CANDIDATE_VALIDATION = "s2_checked_candidates"
