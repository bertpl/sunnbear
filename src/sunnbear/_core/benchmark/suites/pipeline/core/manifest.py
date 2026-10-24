"""A `PipelineStageManifest` records how a stage of the benchmark suite pipeline built its output.

Through `PipelineStageManifest.input_sha256`, the manifests of a run trace each stage's output back to the output
before it.
"""

import datetime
import importlib.metadata
from typing import Self

import polars as pl
from pydantic import BaseModel, ConfigDict

from .stage import PipelineStage


# ==================================================================================================
#  PipelineStageManifest
# ==================================================================================================
class PipelineStageManifest(BaseModel):
    """A `PipelineStageManifest` records how 1 stage built its output: from which input, with which code, and when.

    Pydantic's validation of the fields is strict: a value of the wrong type is refused, not converted, and unknown
    fields are refused.

    Attributes:
        output_name: The `PipelineStage.output_name` of the stage that built the output.
        output_sha256: The sha256 of the output file's bytes, as hex.
        input_sha256: The `output_sha256` of the stage before this one, whose output this stage read; ``None`` for
            the first stage.
        rejection_counts: The number of rejected candidates in the output per reason in its ``rejected_by`` column;
            a reason that rejected no candidate is left out.
        started_at: When the stage started, in UTC.
        duration_sec: How long the stage took to compute its output, excluding the time to write it.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    output_name: str
    output_sha256: str
    input_sha256: str | None
    sunnbear_version: str
    n_rows: int
    rejection_counts: dict[str, int]
    started_at: datetime.datetime
    duration_sec: float

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _count_rejections(output: pl.DataFrame) -> dict[str, int]:
        """Return the number of rejected candidates per reason in a stage's output.

        An output without a ``rejected_by`` column comes from a stage that rejects no candidate, so the result is an
        empty dict.
        """
        if "rejected_by" not in output.columns:
            return {}
        else:
            rejected = output.filter(pl.col("rejected_by") != "")
            return {str(reason): count for reason, count in rejected.group_by("rejected_by").len().iter_rows()}

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
        input_manifest: Self | None,
        started_at: datetime.datetime,
        duration_sec: float,
    ) -> Self:
        """Build the manifest of `stage` from its output and the manifest of the stage before it, if any."""
        return cls(
            output_name=stage.output_name,
            output_sha256=output_sha256,
            input_sha256=input_manifest.output_sha256 if input_manifest is not None else None,
            sunnbear_version=importlib.metadata.version("sunnbear"),
            n_rows=output.height,
            rejection_counts=cls._count_rejections(output),
            started_at=started_at,
            duration_sec=duration_sec,
        )
