"""A `PipelineStageManifest` records how a stage of the benchmark suite pipeline ran."""

import datetime
import importlib.metadata
from dataclasses import dataclass
from typing import Any, Self

from pydantic import BaseModel, ConfigDict

from .stage import PipelineStage, PipelineStageParameterValue
from .stage_id import PipelineStageId


# ==================================================================================================
#  PipelineStageManifest
# ==================================================================================================
class PipelineStageManifest(BaseModel):
    """A `PipelineStageManifest` records how 1 stage ran: with which code and parameters, on how many candidates, when.

    Pydantic's validation of the fields is strict: a value of the wrong type is refused, not converted, and unknown
    fields are refused.

    Attributes:
        stage_id: The stage's `PipelineStageId`.
        parameters: The stage's `PipelineStage.parameters`.
        sunnbear_version: The version of sunnbear that ran the stage.
        n_candidates_in: The number of candidates that no stage had dropped when the stage started; 0 for the first
            stage, which creates the candidates.
        n_candidates_out: The number of candidates that no stage had dropped when the stage ended.
        started_at: When the stage started, in UTC.
        duration_sec: How long the stage took.
        n_workers: The number of workers of the run's worker pool, in which the stage could run tasks. The number of
            workers changes `duration_sec`, never the stage's results.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    stage_id: PipelineStageId
    parameters: dict[str, PipelineStageParameterValue]
    sunnbear_version: str
    n_candidates_in: int
    n_candidates_out: int
    started_at: datetime.datetime
    duration_sec: float
    n_workers: int

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_stage_run(
        cls,
        *,
        stage: PipelineStage[Any],
        n_candidates_in: int,
        n_candidates_out: int,
        execution_info: "PipelineStageExecutionInfo",
    ) -> Self:
        """Build the manifest of a run of `stage`, from the counts of candidates at its start and at its end."""
        return cls(
            stage_id=stage.stage_id,
            parameters=dict(stage.parameters),
            sunnbear_version=importlib.metadata.version("sunnbear"),
            n_candidates_in=n_candidates_in,
            n_candidates_out=n_candidates_out,
            started_at=execution_info.started_at,
            duration_sec=execution_info.duration_sec,
            n_workers=execution_info.n_workers,
        )


# ==================================================================================================
#  PipelineStageExecutionInfo
# ==================================================================================================
@dataclass(frozen=True)
class PipelineStageExecutionInfo:
    """`PipelineStageExecutionInfo` records when a stage started, how long it took, and its worker pool's size."""

    started_at: datetime.datetime
    duration_sec: float
    n_workers: int
