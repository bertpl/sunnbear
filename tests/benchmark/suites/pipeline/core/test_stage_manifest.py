"""`PipelineStageManifest.from_stage_run` records the stage's id, parameters and counts of candidates, and when and in
how many workers it ran."""

import datetime

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStageExecutionInfo, PipelineStageManifest
from sunnbear._core.benchmark.suites.pipeline.stages import SpacingStage


def test_the_manifest_records_the_stage_and_its_run():
    """The manifest of a spacing run that kept 8 of 10 candidates records the stage's id and minimum distance, the 2
    counts, and the execution info."""
    # --- arrange ----------------------
    started_at = datetime.datetime(2026, 11, 4, 12, 0, tzinfo=datetime.UTC)
    execution_info = PipelineStageExecutionInfo(started_at=started_at, duration_sec=1.5, n_workers=4)

    # --- act --------------------------
    manifest = PipelineStageManifest.from_stage_run(
        stage=SpacingStage(min_distance=0.25), n_candidates_in=10, n_candidates_out=8, execution_info=execution_info
    )

    # --- assert -----------------------
    assert manifest.model_dump(exclude={"sunnbear_version"}) == {
        "stage_id": SpacingStage.stage_id,
        "parameters": {"min_distance": 0.25},
        "n_candidates_in": 10,
        "n_candidates_out": 8,
        "started_at": started_at,
        "duration_sec": 1.5,
        "n_workers": 4,
    }
