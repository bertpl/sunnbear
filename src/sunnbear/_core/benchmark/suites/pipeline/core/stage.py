"""`PipelineStage` is the base class of a stage of the benchmark suite pipeline."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import ClassVar

import polars as pl


# ==================================================================================================
#  PipelineStage
# ==================================================================================================
class PipelineStage(ABC):
    """A `PipelineStage` computes 1 output table from the outputs of the stages that run before it.

    A stage that rejects candidates keeps them in its output and marks each one in a ``rejected_by`` column, which
    names the reason or holds ``""`` for a candidate that the stage keeps; `PipelineStageManifest` counts the
    rejections per reason.

    Class attributes:
        output_name: The name of the stage's output file in the `PipelineWorkspace`, without the suffix, e.g.
            ``s1_candidates``. It starts with ``s`` and the stage's position in the run order, so a listing of the
            workspace directory shows the outputs in run order.
        input_stages: The stages whose outputs `compute_output` reads.
    """

    output_name: ClassVar[str]
    input_stages: ClassVar[tuple[type["PipelineStage"], ...]] = ()

    @abstractmethod
    def compute_output(self, inputs: Mapping[type["PipelineStage"], pl.DataFrame]) -> pl.DataFrame:
        """Return the stage's output, computed from `inputs`, the output of each of `input_stages`."""
