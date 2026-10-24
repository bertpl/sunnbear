"""`run_pipeline` writes each stage's output and manifest into the workspace, and a rerun replaces them."""

import hashlib

import polars as pl

from sunnbear._core.functions.core import FormulaRegistry
from sunnbear._core.suites.pipeline.manifest import PipelineStageManifest
from sunnbear._core.suites.pipeline.runner import run_pipeline
from sunnbear._core.suites.pipeline.stage import PipelineStage

# The shipped formulas of category 2 form a small corpus, so the pipeline runs fast on them.
_CATEGORY_2_FORMULAS = [formula for formula in FormulaRegistry.formulas() if formula.number[0] == 2]


def test_each_stage_writes_its_output_and_a_manifest_that_names_the_outputs_it_read(tmp_path):
    """Each stage's manifest is in the workspace, matches the output file's bytes and rows, and records the
    sha256 of each of the stage's inputs."""
    # --- act --------------------------
    manifests = run_pipeline(workspace_dir=tmp_path, formulas=_CATEGORY_2_FORMULAS)

    # --- assert -----------------------
    generation_manifest, validation_manifest = manifests
    assert [manifest.stage for manifest in manifests] == list(PipelineStage)
    for manifest in manifests:
        output_file = tmp_path / f"{manifest.stage}.parquet"
        manifest_file = tmp_path / "manifests" / f"{manifest.stage}.json"
        assert hashlib.sha256(output_file.read_bytes()).hexdigest() == manifest.output_sha256
        assert pl.read_parquet(output_file).height == manifest.n_rows
        assert PipelineStageManifest.model_validate_json(manifest_file.read_text()) == manifest
    assert generation_manifest.input_sha256s == {}
    assert validation_manifest.input_sha256s == {PipelineStage.CANDIDATE_GENERATION: generation_manifest.output_sha256}


def test_a_rerun_replaces_the_outputs_and_manifests_and_leaves_no_temporary_files(tmp_path):
    """A second run into the same workspace replaces every file of the first, and leaves only the final files."""
    # --- arrange ----------------------
    run_pipeline(workspace_dir=tmp_path, formulas=_CATEGORY_2_FORMULAS)

    # --- act --------------------------
    manifests = run_pipeline(workspace_dir=tmp_path, formulas=_CATEGORY_2_FORMULAS[:1])

    # --- assert -----------------------
    assert pl.read_parquet(tmp_path / f"{PipelineStage.CANDIDATE_VALIDATION}.parquet").height == manifests[1].n_rows
    assert manifests[1].n_rows == len(_CATEGORY_2_FORMULAS[0].build_all_candidates())
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*.*")) == sorted(
        [f"{stage}.parquet" for stage in PipelineStage] + [f"manifests/{stage}.json" for stage in PipelineStage]
    )
