"""The tests of `run_stages` check that:

- each stage runs on the output of the stage before it, and writes its output and manifest into the workspace;
- a rerun replaces them;
- a stage that drops a column of its input stops the run.
"""

import hashlib

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.core.manifest import PipelineStageManifest
from sunnbear._core.benchmark.suites.pipeline.core.stage_runner import run_stages
from sunnbear._core.benchmark.suites.pipeline.core.workspace import PipelineWorkspace

from .example_stages import ExampleCheckedNumbersStage, ExampleColumnDroppingStage, ExampleNumbersStage


def test_each_stage_runs_on_the_output_before_it_and_writes_its_output_and_manifest(tmp_path):
    """Each stage's output extends the output before it; its manifest is in the workspace, matches the output file's
    bytes and rows, and records the sha256 of the output before it."""
    # --- act --------------------------
    manifests = run_stages(PipelineWorkspace(tmp_path), [ExampleNumbersStage(), ExampleCheckedNumbersStage()])

    # --- assert -----------------------
    numbers_manifest, checked_numbers_manifest = manifests
    for manifest in manifests:
        output_file = tmp_path / f"{manifest.output_name}.parquet"
        manifest_file = tmp_path / "manifests" / f"{manifest.output_name}.json"
        assert hashlib.sha256(output_file.read_bytes()).hexdigest() == manifest.output_sha256
        assert pl.read_parquet(output_file).height == manifest.n_rows
        assert PipelineStageManifest.model_validate_json(manifest_file.read_text()) == manifest
    assert pl.read_parquet(tmp_path / "s2_checked_numbers.parquet").columns == ["x", "rejected_by"]
    assert numbers_manifest.input_sha256 is None
    assert checked_numbers_manifest.input_sha256 == numbers_manifest.output_sha256
    assert checked_numbers_manifest.rejection_counts == {"too_large": 1}


def test_a_rerun_replaces_the_outputs_and_manifests_and_leaves_no_temporary_files(tmp_path):
    """A second run into the same workspace replaces every file of the first, and leaves only the final files."""
    # --- arrange ----------------------
    workspace = PipelineWorkspace(tmp_path)
    run_stages(workspace, [ExampleNumbersStage(), ExampleCheckedNumbersStage()])

    # --- act --------------------------
    second_manifests = run_stages(workspace, [ExampleNumbersStage(), ExampleCheckedNumbersStage()])

    # --- assert -----------------------
    assert [
        PipelineStageManifest.model_validate_json((tmp_path / "manifests" / f"{name}.json").read_text())
        for name in ("s1_numbers", "s2_checked_numbers")
    ] == list(second_manifests)
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*.*")) == [
        "manifests/s1_numbers.json",
        "manifests/s2_checked_numbers.json",
        "s1_numbers.parquet",
        "s2_checked_numbers.parquet",
    ]


def test_a_stage_that_drops_a_column_of_its_input_stops_the_run(tmp_path):
    """A stage whose output lacks a column of the output before it raises `ValueError`, which names the column, and
    its output is not written."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=r"ExampleColumnDroppingStage drops the columns \['x'\]"):
        run_stages(PipelineWorkspace(tmp_path), [ExampleNumbersStage(), ExampleColumnDroppingStage()])
    assert not (tmp_path / "s2_doubled_numbers.parquet").exists()
