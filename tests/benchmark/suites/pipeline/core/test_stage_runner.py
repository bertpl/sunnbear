"""The tests of `run_stages` check that:

- it writes each stage's output and manifest into the workspace;
- a rerun replaces them;
- a stage cannot run before the stages whose outputs it reads.
"""

import hashlib

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.core.manifest import PipelineStageManifest
from sunnbear._core.benchmark.suites.pipeline.core.stage_runner import run_stages
from sunnbear._core.benchmark.suites.pipeline.core.workspace import PipelineWorkspace

from .example_stages import ExampleCheckedNumbersStage, ExampleNumbersStage


def test_each_stage_writes_its_output_and_a_manifest_that_names_the_outputs_it_read(tmp_path):
    """Each stage's manifest is in the workspace, matches the output file's bytes and rows, and records the sha256 of
    each of the stage's inputs."""
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
    assert numbers_manifest.input_sha256s == {}
    assert checked_numbers_manifest.input_sha256s == {"s1_numbers": numbers_manifest.output_sha256}
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


def test_a_stage_cannot_run_before_the_stages_whose_outputs_it_reads(tmp_path):
    """A stage whose input stage does not run before it raises `ValueError`, which names the missing stage."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=r"ExampleCheckedNumbersStage reads the outputs of \['ExampleNumbersStage'\]"):
        run_stages(PipelineWorkspace(tmp_path), [ExampleCheckedNumbersStage()])
