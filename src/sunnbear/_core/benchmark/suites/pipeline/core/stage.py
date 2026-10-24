"""`PipelineStage` is the base class of a benchmark suite pipeline stage; `PipelineStageOutput` is what it returns."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import ClassVar

import polars as pl


# ==================================================================================================
#  PipelineStage
# ==================================================================================================
class PipelineStage(ABC):
    """A `PipelineStage` computes its output table from the output table of the stage before it.

    The stages form a chain of tables with 1 row per candidate, keyed by a ``function_id`` column. The first stage
    creates the rows; each later stage keeps every column of its input and may add columns, and keeps a subset of
    the input's rows. So a stage finds everything that the stages before it computed in its input, and a candidate
    that a stage drops never reaches the stages after it. A stage can explain what it dropped in its reports.

    Class attributes:
        output_name: The name of the stage's output file in the `PipelineWorkspace`, without the suffix, e.g.
            ``s1_candidates``. It starts with ``s`` and the stage's position in the run order, so a listing of the
            workspace directory shows the outputs in run order.
    """

    output_name: ClassVar[str]

    @abstractmethod
    def compute_output(self, previous_table: pl.DataFrame) -> "PipelineStageOutput":
        """Return the stage's output table, which extends `previous_table`, and the stage's reports.

        Args:
            previous_table: The output table of the stage before this one; an empty table for the first stage.
        """


# ==================================================================================================
#  PipelineStageOutput
# ==================================================================================================
@dataclass(frozen=True)
class PipelineStageOutput:
    """A `PipelineStageOutput` holds what 1 stage computed: the table that the next stage reads, and its reports.

    Attributes:
        table: The stage's output table, which the next stage receives.
        reports: Tables that the next stage does not read, keyed by a name of the stage's choice, such as the
            candidates that the stage dropped and why; empty for a stage that reports nothing.
    """

    table: pl.DataFrame
    reports: Mapping[str, pl.DataFrame] = field(default_factory=dict)
