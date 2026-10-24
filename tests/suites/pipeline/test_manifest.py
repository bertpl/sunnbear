"""`PipelineStageManifest.from_stage_output` derives the manifest's counts and input hashes from a stage's output."""

import datetime

import polars as pl
import pytest

from sunnbear._core.suites.pipeline.manifest import PipelineStageManifest
from sunnbear._core.suites.pipeline.stage import PipelineStage
from sunnbear._core.suites.pipeline.validation import RejectionReason


@pytest.mark.parametrize(
    "output, rejection_counts_expected",
    [
        pytest.param(
            pl.DataFrame({"rejected_by": ["interval_ratio", "", "interval_ratio"]}),
            {RejectionReason.INTERVAL_RATIO: 2},
            id="output_with_rejections",
        ),
        pytest.param(pl.DataFrame({"function_id": ["f2.1.1[p1=0.2]"]}), {}, id="output_without_rejected_by"),
    ],
)
def test_the_manifest_counts_the_rows_and_the_rejections_per_reason(output, rejection_counts_expected):
    """The manifest counts every row, and the rejected rows per reason; an output without a ``rejected_by`` column
    has no rejections."""
    # --- arrange ----------------------
    input_manifest = PipelineStageManifest.from_stage_output(
        stage=PipelineStage.CANDIDATE_GENERATION,
        output=pl.DataFrame(),
        output_sha256="ab" * 32,
        input_manifests=(),
        started_at=datetime.datetime.now(datetime.UTC),
        duration_sec=0.0,
    )

    # --- act --------------------------
    manifest = PipelineStageManifest.from_stage_output(
        stage=PipelineStage.VALIDATION,
        output=output,
        output_sha256="cd" * 32,
        input_manifests=(input_manifest,),
        started_at=datetime.datetime.now(datetime.UTC),
        duration_sec=0.0,
    )

    # --- assert -----------------------
    assert manifest.n_rows == output.height
    assert manifest.rejection_counts == rejection_counts_expected
    assert manifest.input_sha256s == {PipelineStage.CANDIDATE_GENERATION: "ab" * 32}
