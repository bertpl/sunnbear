"""A stage raises `PipelineStopError` to stop the pipeline, and `run_stages` reports the stop as a `PipelineStop`.

A stop is an expected outcome while the corpus of formulas grows: a stage whose input cannot give a valid output stops
the run with a message that says what the corpus lacks.

The stages before the stopping stage have written their outputs, so a maintainer can still read them.
"""

from dataclasses import dataclass


# ==================================================================================================
#  PipelineStopError
# ==================================================================================================
class PipelineStopError(Exception):
    """A stage raises `PipelineStopError` when its input cannot give a valid output; the message says why."""


# ==================================================================================================
#  PipelineStop
# ==================================================================================================
@dataclass(frozen=True)
class PipelineStop:
    """A `PipelineStop` records which stage stopped a run, and why.

    Attributes:
        output_name: The `PipelineStage.output_name` of the stage that raised `PipelineStopError`.
        reason: The message of the `PipelineStopError`.
    """

    output_name: str
    reason: str
