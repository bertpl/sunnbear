"""`PipelineStageManifest.from_stage_output` derives the manifest's row counts and input hash from a stage's output
table and the manifest of the stage before it."""

import datetime

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.core.manifest import PipelineStageManifest

from .example_stages import ExampleNumbersStage, ExampleSmallNumbersStage


def test_the_manifest_counts_the_rows_and_the_dropped_rows_and_records_the_input_hash():
    """The first stage's manifest has no input hash and drops no rows; a later stage's manifest counts the rows
    that it dropped from its input, and records the input's sha256 and the sha256 of each report."""
    # --- arrange ----------------------
    first_manifest = PipelineStageManifest.from_stage_output(
        stage=ExampleNumbersStage(),
        table=pl.DataFrame({"function_id": ["n1", "n2", "n3"]}),
        output_sha256="ab" * 32,
        report_sha256s={},
        input_manifest=None,
        started_at=datetime.datetime.now(datetime.UTC),
        duration_sec=0.0,
    )

    # --- act --------------------------
    manifest = PipelineStageManifest.from_stage_output(
        stage=ExampleSmallNumbersStage(),
        table=pl.DataFrame({"function_id": ["n1", "n2"]}),
        output_sha256="cd" * 32,
        report_sha256s={"large_numbers": "ef" * 32},
        input_manifest=first_manifest,
        started_at=datetime.datetime.now(datetime.UTC),
        duration_sec=0.0,
    )

    # --- assert -----------------------
    assert (first_manifest.input_sha256, first_manifest.n_rows, first_manifest.n_dropped_rows) == (None, 3, 0)
    assert (manifest.input_sha256, manifest.n_rows, manifest.n_dropped_rows) == ("ab" * 32, 2, 1)
    assert manifest.output_name == "s2_small_numbers"
    assert manifest.report_sha256s == {"large_numbers": "ef" * 32}
