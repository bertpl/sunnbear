"""A `PipelineStageManifest` records how a stage of the suite pipeline built its output in the workspace.

Through their `PipelineStageManifest.input_sha256s`, the manifests trace each stage's output back to that
stage's inputs.
"""

import datetime
import importlib.metadata
from collections.abc import Sequence
from typing import Self

import polars as pl
from pydantic import BaseModel, ConfigDict

from .stage import PipelineStage
from .validation import RejectionReason


# ==================================================================================================
#  PipelineStageManifest
# ==================================================================================================
class PipelineStageManifest(BaseModel):
    """A `PipelineStageManifest` records how 1 stage built its output: from which inputs, with which code, and when.

    Pydantic's validation of the fields is strict: a value of the wrong type is refused, not converted, and
    unknown fields are refused.

    Attributes:
        output_sha256: The sha256 of the output file's bytes, as hex.
        input_sha256s: The `output_sha256` of each stage whose output this stage read, keyed by that stage.
        rejection_counts: The number of rejected candidates in the output per `RejectionReason`; a reason
            that rejected no candidate is left out.
        started_at: When the stage started, in UTC.
        duration_sec: How long the stage took to compute its output, excluding the time to write it.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    stage: PipelineStage
    output_sha256: str
    input_sha256s: dict[PipelineStage, str]
    sunnbear_version: str
    n_rows: int
    rejection_counts: dict[RejectionReason, int]
    started_at: datetime.datetime
    duration_sec: float

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _count_rejections(output: pl.DataFrame) -> dict[RejectionReason, int]:
        """Return the number of rejected candidates per `RejectionReason` in a stage's output.

        An output without a ``rejected_by`` column comes from a stage that rejects no candidate, so the result
        is an empty dict.
        """
        if "rejected_by" not in output.columns:
            return {}
        else:
            rejected = output.filter(pl.col("rejected_by") != "")
            return {
                RejectionReason(reason): count for reason, count in rejected.group_by("rejected_by").len().iter_rows()
            }

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_stage_output(
        cls,
        *,
        stage: PipelineStage,
        output: pl.DataFrame,
        output_sha256: str,
        input_manifests: Sequence[Self],
        started_at: datetime.datetime,
        duration_sec: float,
    ) -> Self:
        """Build the manifest of `stage` from its output and the manifests of the stages whose outputs it read."""
        return cls(
            stage=stage,
            output_sha256=output_sha256,
            input_sha256s={input_manifest.stage: input_manifest.output_sha256 for input_manifest in input_manifests},
            sunnbear_version=importlib.metadata.version("sunnbear"),
            n_rows=output.height,
            rejection_counts=cls._count_rejections(output),
            started_at=started_at,
            duration_sec=duration_sec,
        )
