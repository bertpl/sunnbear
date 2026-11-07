"""A stage raises `PipelineStopError` to stop the pipeline, and the run reports the stop as a `PipelineStop`.

A stop is an expected outcome while the corpus of formulas grows: a stage whose candidates cannot give a valid result
stops the run with a message that says what the corpus lacks.

The stages before the stopping stage have run, so their information stays available.
"""

from dataclasses import dataclass

from .stage_id import PipelineStageId


# ==================================================================================================
#  PipelineStopError
# ==================================================================================================
class PipelineStopError(Exception):
    """A stage raises `PipelineStopError` when its candidates cannot give a valid result; the message says why."""


# ==================================================================================================
#  PipelineStop
# ==================================================================================================
@dataclass(frozen=True)
class PipelineStop:
    """A `PipelineStop` records which stage stopped a run, and why.

    Attributes:
        stage_id: The `PipelineStageId` of the stage that raised `PipelineStopError`.
        reason: The message of the `PipelineStopError`.
    """

    stage_id: PipelineStageId
    reason: str
