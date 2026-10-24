"""A `PipelineStageManifest` records how a stage of the suite pipeline built its output in the workspace.

Through their `PipelineStageManifest.input_sha256s`, the manifests trace each output back to the
outputs that it was computed from.
"""

import datetime
import json

from pydantic import BaseModel, ConfigDict

from .stage import PipelineStage
from .validation import RejectionReason


# ==================================================================================================
#  PipelineStageManifest
# ==================================================================================================
class PipelineStageManifest(BaseModel):
    """A `PipelineStageManifest` records how 1 stage built its output: from which inputs, with which code, and when.

    Validation is strict: a value of the wrong type is refused, not converted, and unknown fields are
    refused.

    Attributes:
        stage: The stage that built the output.
        output_sha256: The sha256 of the output file's bytes, as hex.
        input_sha256s: The `output_sha256` of each stage whose output this stage read, keyed by that stage.
        sunnbear_version: The version of sunnbear that ran the stage.
        n_rows: The number of rows of the output.
        rejection_counts: The number of rejected candidates in the output per `RejectionReason`; a reason
            that rejected no candidate is left out.
        started_at: When the stage started, in UTC.
        duration_sec: How long the stage took to compute its output, without writing it.
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

    def to_json(self) -> str:
        """Return the manifest as JSON: sorted keys, 2-space indentation, a final newline."""
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, indent=2) + "\n"
