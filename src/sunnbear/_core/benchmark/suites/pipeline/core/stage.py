"""`PipelineStage` is the base class of a stage of the benchmark suite pipeline."""

from abc import ABC, abstractmethod
from typing import ClassVar

import polars as pl


# ==================================================================================================
#  PipelineStage
# ==================================================================================================
class PipelineStage(ABC):
    """A `PipelineStage` computes its output table from the output of the stage before it.

    The stages form a chain, and each output carries forward every column of the output before it, so a stage finds
    everything that the stages before it computed in its input. A stage may drop rows, such as the candidates that
    a check rejects, but never columns.

    A stage that rejects candidates keeps them in its output and marks each one in a ``rejected_by`` column, which
    names the reason or holds ``""`` for a candidate that the stage keeps; `PipelineStageManifest` counts the
    rejections per reason.

    Class attributes:
        output_name: The name of the stage's output file in the `PipelineWorkspace`, without the suffix, e.g.
            ``s1_candidates``. It starts with ``s`` and the stage's position in the run order, so a listing of the
            workspace directory shows the outputs in run order.
    """

    output_name: ClassVar[str]

    @abstractmethod
    def compute_output(self, previous_output: pl.DataFrame) -> pl.DataFrame:
        """Return the stage's output, which keeps every column of `previous_output` and adds the stage's own.

        Args:
            previous_output: The output of the stage before this one; an empty table for the first stage.
        """
