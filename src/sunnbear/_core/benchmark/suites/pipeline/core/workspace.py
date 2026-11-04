"""`PipelineWorkspace` is the only code that writes the files of the benchmark suite pipeline's workspace.

The workspace directory holds, under ``manifests``, the `PipelineStageManifest` of each stage that ran, as a JSON file
named after the stage's `PipelineStageId`.

Every file is written under a temporary name and then renamed, so a file under its final name is always complete.
"""

import json
from pathlib import Path

from .manifest import PipelineStageManifest

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

    def write_manifest(self, manifest: PipelineStageManifest) -> None:
        """Write `manifest` to the manifest file of its stage, replacing an earlier one.

        The JSON has sorted keys, so the same manifest is always written as the same bytes.
        """
        manifest_file = self.path / _MANIFESTS_DIR_NAME / f"{manifest.stage_id}{_MANIFEST_FILE_SUFFIX}"
        manifest_json = json.dumps(manifest.model_dump(mode="json"), sort_keys=True, indent=2) + "\n"
        self._write_atomically(manifest_file, manifest_json.encode())

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
