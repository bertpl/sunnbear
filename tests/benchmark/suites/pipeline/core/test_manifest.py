"""`PipelineStageManifest.from_stage_output` derives the manifest's counts and input hashes from a stage's output."""

import datetime

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.core.manifest import PipelineStageManifest

from .example_stages import ExampleCheckedNumbers, ExampleNumbers


@pytest.mark.parametrize(
    "output, rejection_counts_expected",
    [
        pytest.param(
            pl.DataFrame({"rejected_by": ["too_large", "", "too_large"]}),
            {"too_large": 2},
            id="output_with_rejections",
        ),
        pytest.param(pl.DataFrame({"x": [1.0]}), {}, id="output_without_rejected_by"),
    ],
)
def test_the_manifest_counts_the_rows_and_the_rejections_per_reason(output, rejection_counts_expected):
    """The manifest counts every row, and the rejected rows per reason; an output without a ``rejected_by`` column
    has no rejections."""
    # --- arrange ----------------------
    input_manifest = PipelineStageManifest.from_stage_output(
        stage=ExampleNumbers(),
        output=pl.DataFrame(),
        output_sha256="ab" * 32,
        input_manifests=(),
        started_at=datetime.datetime.now(datetime.UTC),
        duration_sec=0.0,
    )

    # --- act --------------------------
    manifest = PipelineStageManifest.from_stage_output(
        stage=ExampleCheckedNumbers(),
        output=output,
        output_sha256="cd" * 32,
        input_manifests=(input_manifest,),
        started_at=datetime.datetime.now(datetime.UTC),
        duration_sec=0.0,
    )

    # --- assert -----------------------
    assert manifest.output_name == "s2_checked_numbers"
    assert manifest.n_rows == output.height
    assert manifest.rejection_counts == rejection_counts_expected
    assert manifest.input_sha256s == {"s1_numbers": "ab" * 32}
