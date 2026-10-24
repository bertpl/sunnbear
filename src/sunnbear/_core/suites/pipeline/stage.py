"""`PipelineStage` names the stages of the suite pipeline, in run order."""

from enum import StrEnum


# ==================================================================================================
#  PipelineStage
# ==================================================================================================
class PipelineStage(StrEnum):
    """A `PipelineStage` names 1 stage of the suite pipeline; its value names the stage's output in the workspace.

    Each value starts with ``s`` and the stage's position in the run order, so a listing of the
    workspace shows the outputs in run order.
    """

    CANDIDATE_GENERATION = "s1_candidates"
    VALIDATION = "s2_valid"
