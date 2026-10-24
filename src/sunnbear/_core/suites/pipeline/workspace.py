"""`PipelineWorkspace` represents the suite pipeline's workspace directory, and is the only code that writes its files.

The directory holds:

- 1 output file per stage, named after the stage, e.g. `s1_candidates.parquet`;
- `manifests/`, which holds 1 `PipelineStageManifest` per stage, e.g. `manifests/s1_candidates.json`.

Every file is written under a temporary name and then renamed, so a file that exists is complete.
"""

import hashlib
import io
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
    """`PipelineWorkspace` writes the files of the suite pipeline's workspace directory."""

    def __init__(self, path: Path) -> None:
        """Refer to the workspace directory at `path`, which need not exist yet."""
        self.path = path

    # --------------------------------------------------------------------------
    #  Stage outputs and manifests
    # --------------------------------------------------------------------------
    def write_stage_output(self, stage: PipelineStage, output: pl.DataFrame) -> str:
        """Write the output of `stage`, replacing an earlier one, and return the sha256 of the file's bytes, as hex."""
        buffer = io.BytesIO()
        output.write_parquet(buffer)
        content = buffer.getvalue()
        self._write_atomically(self.path / f"{stage}{_OUTPUT_FILE_SUFFIX}", content)
        return hashlib.sha256(content).hexdigest()

    def write_manifest(self, manifest: PipelineStageManifest) -> None:
        """Write the manifest of its stage, replacing an earlier one."""
        manifest_file = self.path / _MANIFESTS_DIR_NAME / f"{manifest.stage}{_MANIFEST_FILE_SUFFIX}"
        self._write_atomically(manifest_file, manifest.to_json().encode())

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _write_atomically(file: Path, content: bytes) -> None:
        """Write `content` to `file` under a temporary name, then rename it; create the parent directories first."""
        file.parent.mkdir(parents=True, exist_ok=True)
        temporary_file = file.with_name(file.name + _TEMPORARY_FILE_SUFFIX)
        temporary_file.write_bytes(content)
        temporary_file.replace(file)
