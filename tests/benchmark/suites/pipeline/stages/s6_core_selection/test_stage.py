"""`CoreSelectionStage` reads each candidate's EDI from its full features, adds its difficulty class, and reports the
Core's composition."""

import polars as pl

from sunnbear._core.benchmark.suites.pipeline.features import map_fevals_to_feature
from sunnbear._core.benchmark.suites.pipeline.stages import (
    CORE_COMPOSITION_REPORT_NAME,
    DIFFICULTY_CLASS_SCHEMA,
    CoreSelectionStage,
    FullCharacterizationStage,
)
from sunnbear._core.utils.worker_pool import WorkerPool


def test_the_stage_adds_each_candidates_class_and_reports_the_core_composition():
    """With 128 candidates whose EDIs fall 32 each in A, B and C, 24 in Da and 8 in Db, the stage chooses a Core of 128
    with all 5 quotas, an interim Core because it is smaller than 2048."""
    # --- arrange ----------------------
    edis = [5.0] * 32 + [15.0] * 32 + [30.0] * 32 + [60.0] * 24 + [120.0] * 8
    previous_table = pl.DataFrame(
        {
            "problem_id": [f"f99.{idx}" for idx in range(len(edis))],
            FullCharacterizationStage.solvers_gpq_column_name(0.5): map_fevals_to_feature(edis, max_fevals=160),
        }
    )

    # --- act --------------------------
    output = CoreSelectionStage().compute_output(previous_table, worker_pool=WorkerPool(n_workers=1))

    # --- assert -----------------------
    assert output.table.schema == pl.Schema({**previous_table.schema, **DIFFICULTY_CLASS_SCHEMA})
    assert output.table["difficulty_class"].to_list() == ["A"] * 32 + ["B"] * 32 + ["C"] * 32 + ["Da"] * 24 + ["Db"] * 8
    report = output.reports[CORE_COMPOSITION_REPORT_NAME]
    assert report.select("core_size", "is_interim", "quota_a", "quota_da", "quota_db", "quota_d").rows() == [
        (128, True, 32, 24, 8, None)
    ]
