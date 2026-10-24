"""`PipelineWorkspace` is the only code that writes the files of the benchmark suite pipeline's workspace.

The workspace directory holds:

- 1 Parquet output file per stage, named after the stage's `PipelineStage.output_name`;
- a manifests directory, which holds 1 `PipelineStageManifest` per stage as a JSON file named after the stage's
  `PipelineStage.output_name`.

Every file is written under a temporary name and then renamed, so a file under its final name is always complete.
"""

import datetime
import hashlib
import io
import json
from collections.abc import Sequence
from pathlib import Path

import polars as pl

from .manifest import PipelineStageManifest
from .stage import PipelineStage

_OUTPUT_FILE_SUFFIX = ".parquet"
_MANIFESTS_DIR_NAME = "manifests"
_MANIFEST_FILE_SUFFIX = ".json"
_TEMPORARY_FILE_SUFFIX = ".tmp"


# ==================================================================================================
#  PipelineWorkspace
# ==================================================================================================
class PipelineWorkspace:
    """`PipelineWorkspace` writes the files of the benchmark suite pipeline's workspace directory."""

    def __init__(self, path: Path) -> None:
        """Create a workspace for the directory at `path`, which need not exist yet."""
        self.path = path

    # --------------------------------------------------------------------------
    #  Stage outputs and manifests
    # --------------------------------------------------------------------------
    def write_stage(
        self,
        *,
        stage: PipelineStage,
        output: pl.DataFrame,
        input_manifests: Sequence[PipelineStageManifest],
        started_at: datetime.datetime,
        duration_sec: float,
    ) -> PipelineStageManifest:
        """Write the output of `stage` and its manifest, replacing earlier ones, and return the manifest.

        `input_manifests` are the manifests of the stages whose outputs `stage` read.
        """
        manifest = PipelineStageManifest.from_stage_output(
            stage=stage,
            output=output,
            output_sha256=self._write_stage_output(stage.output_name, output),
            input_manifests=input_manifests,
            started_at=started_at,
            duration_sec=duration_sec,
        )
        self._write_manifest(manifest)
        return manifest

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _write_stage_output(self, output_name: str, output: pl.DataFrame) -> str:
        """Write a stage's output under `output_name`, replacing an earlier one; return the file's sha256 as hex."""
        buffer = io.BytesIO()
        output.write_parquet(buffer)
        content = buffer.getvalue()
        self._write_atomically(self.path / f"{output_name}{_OUTPUT_FILE_SUFFIX}", content)
        return hashlib.sha256(content).hexdigest()

    def _write_manifest(self, manifest: PipelineStageManifest) -> None:
        """Write `manifest` to the manifest file of `manifest.output_name`, replacing an earlier one.

        The JSON has sorted keys, so the same manifest is always written as the same bytes.
        """
        manifest_file = self.path / _MANIFESTS_DIR_NAME / f"{manifest.output_name}{_MANIFEST_FILE_SUFFIX}"
        manifest_json = json.dumps(manifest.model_dump(mode="json"), sort_keys=True, indent=2) + "\n"
        self._write_atomically(manifest_file, manifest_json.encode())

    @staticmethod
    def _write_atomically(file: Path, content: bytes) -> None:
        """Write `content` to `file` under a temporary name, then rename it; create the parent directories first."""
        file.parent.mkdir(parents=True, exist_ok=True)
        temporary_file = file.with_name(file.name + _TEMPORARY_FILE_SUFFIX)
        temporary_file.write_bytes(content)
        temporary_file.replace(file)
