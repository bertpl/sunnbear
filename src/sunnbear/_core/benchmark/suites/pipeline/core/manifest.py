"""A `PipelineStageManifest` records how a stage of the benchmark suite pipeline built its output.

Through `PipelineStageManifest.input_sha256`, the manifests of a run trace each stage's output back to the output
before it.
"""

import datetime
import importlib.metadata
from collections.abc import Mapping
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
        output_sha256: The sha256 of the output table's file, as hex.
        report_sha256s: The sha256 of each report's file, as hex, keyed by the report's name.
        input_sha256: The `output_sha256` of the stage before this one, whose output table this stage read; ``None``
            for the first stage.
        n_rows: The number of rows of the output table.
        n_dropped_rows: The number of rows of the input table that the output table does not hold; 0 for the first
            stage, which creates the rows.
        started_at: When the stage started, in UTC.
        duration_sec: How long the stage took to compute its output, excluding the time to write it.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    output_name: str
    output_sha256: str
    report_sha256s: dict[str, str]
    input_sha256: str | None
    sunnbear_version: str
    n_rows: int
    n_dropped_rows: int
    started_at: datetime.datetime
    duration_sec: float

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def from_stage_output(
        cls,
        *,
        stage: PipelineStage,
        table: pl.DataFrame,
        output_sha256: str,
        report_sha256s: Mapping[str, str],
        input_manifest: Self | None,
        started_at: datetime.datetime,
        duration_sec: float,
    ) -> Self:
        """Build the manifest of `stage` from its output table and the manifest of the stage before it, if any."""
        return cls(
            output_name=stage.output_name,
            output_sha256=output_sha256,
            report_sha256s=dict(report_sha256s),
            input_sha256=input_manifest.output_sha256 if input_manifest is not None else None,
            sunnbear_version=importlib.metadata.version("sunnbear"),
            n_rows=table.height,
            n_dropped_rows=input_manifest.n_rows - table.height if input_manifest is not None else 0,
            started_at=started_at,
            duration_sec=duration_sec,
        )
