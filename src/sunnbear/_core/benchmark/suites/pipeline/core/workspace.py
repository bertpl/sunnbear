"""`PipelineWorkspace` is the only code that reads or writes the files of the benchmark suite pipeline's workspace.

The workspace directory holds, for each stage, files named after the stage's `PipelineStage.output_name`:

- its output table, as a Parquet file in the directory itself;
- its reports, as Parquet files named after the reports, in a reports directory of its own under ``reports``;
- its `PipelineStageManifest`, as a JSON file under ``manifests``.

Every file is written under a temporary name and then renamed, so a file under its final name is always complete.
"""

import hashlib
import io
import json
import shutil
from pathlib import Path

import polars as pl

from .manifest import PipelineStageExecutionInfo, PipelineStageManifest
from .stage import PipelineStage, PipelineStageOutput

_TABLE_FILE_SUFFIX = ".parquet"
_REPORTS_DIR_NAME = "reports"
_MANIFESTS_DIR_NAME = "manifests"
_MANIFEST_FILE_SUFFIX = ".json"
_TEMPORARY_FILE_SUFFIX = ".tmp"


# ==================================================================================================
#  PipelineWorkspace
# ==================================================================================================
class PipelineWorkspace:
    """`PipelineWorkspace` reads and writes the files of the benchmark suite pipeline's workspace directory."""

    def __init__(self, path: Path) -> None:
        """Create a workspace for the directory at `path`, which need not exist yet."""
        self.path = path

    # --------------------------------------------------------------------------
    #  Stage outputs and manifests
    # --------------------------------------------------------------------------
    def write_stage_output_and_manifest(
        self,
        *,
        stage: PipelineStage,
        output: PipelineStageOutput,
        input_manifest: PipelineStageManifest | None,
        execution_info: PipelineStageExecutionInfo,
    ) -> PipelineStageManifest:
        """Write the output table, reports and manifest of `stage`, replacing earlier ones, and return the manifest.

        The reports of an earlier run of `stage` are removed first, so the reports directory of `stage` holds exactly
        the reports in `output`. `input_manifest` is the manifest of the stage before `stage`, or ``None`` for the
        first stage.
        """
        reports_dir = self._reports_dir(stage.output_name)
        shutil.rmtree(reports_dir, ignore_errors=True)
        manifest = PipelineStageManifest.from_stage_output(
            stage=stage,
            table=output.table,
            output_sha256=self._write_table(self.path / f"{stage.output_name}{_TABLE_FILE_SUFFIX}", output.table),
            report_sha256s={
                report_name: self._write_table(reports_dir / f"{report_name}{_TABLE_FILE_SUFFIX}", report)
                for report_name, report in output.reports.items()
            },
            input_manifest=input_manifest,
            execution_info=execution_info,
        )
        self._write_manifest(manifest)
        return manifest

    def read_report(self, output_name: str, report_name: str) -> pl.DataFrame:
        """Return the report named `report_name` of the stage whose `PipelineStage.output_name` is `output_name`."""
        return pl.read_parquet(self._reports_dir(output_name) / f"{report_name}{_TABLE_FILE_SUFFIX}")

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _reports_dir(self, output_name: str) -> Path:
        """Return the directory of the reports of the stage whose `PipelineStage.output_name` is `output_name`."""
        return self.path / _REPORTS_DIR_NAME / output_name

    def _write_table(self, file: Path, table: pl.DataFrame) -> str:
        """Write `table` to `file` as Parquet, replacing an earlier file, and return the file's sha256 as hex."""
        buffer = io.BytesIO()
        table.write_parquet(buffer)
        content = buffer.getvalue()
        self._write_atomically(file, content)
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
