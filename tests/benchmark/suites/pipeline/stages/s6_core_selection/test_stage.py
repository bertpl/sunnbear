"""`CoreSelectionStage` selects the Core from the candidates' full features:

- it reads each candidate's EDI from its full features and adds its difficulty class;
- it selects the Core by max-div under the difficulty quotas;
- it gives the same Core in every run.
"""

import numpy as np
import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.features import map_fevals_to_feature
from sunnbear._core.benchmark.suites.pipeline.stages import (
    CORE_COMPOSITION_REPORT_NAME,
    DIFFICULTY_CLASS_SCHEMA,
    CoreCompositionWarning,
    CoreSelectionStage,
    FullCharacterizationStage,
)
from sunnbear._core.solvers.core import SolverConfigRegistry
from sunnbear._core.utils.worker_pool import WorkerPool

_IN_PROCESS_WORKER_POOL = WorkerPool(n_workers=1)


def _full_features_table(edis: list[float]) -> pl.DataFrame:
    """Return a table of full features for 1 core solver config, with the EDI feature from `edis` and the others random.

    Every feature scale is 1, so the scaled feature vectors equal the features.
    """
    column_names = FullCharacterizationStage([SolverConfigRegistry.config_from_id("bisection")]).feature_column_names
    rng = np.random.default_rng(seed=3)
    return pl.DataFrame(
        {
            "problem_id": [f"f99.{idx}" for idx in range(len(edis))],
            **{column_name: rng.random(len(edis)) for column_name in column_names},
        }
    ).with_columns(
        pl.Series(FullCharacterizationStage.solvers_gpq_column_name(0.5), map_fevals_to_feature(edis, max_fevals=160)),
        *(pl.lit(1.0).alias(column_name) for column_name in FullCharacterizationStage.feature_scale_column_names()),
    )


@pytest.mark.only_with_numba_jit
def test_the_stage_selects_a_core_that_meets_every_quota():
    """From 160 candidates whose EDIs fall 40 each in A, B and C, 30 in Da and 10 in Db, the stage selects a Core of
    128 with 32 each of A, B and C, 24 of Da and 8 of Db, an interim Core because it is smaller than 2048, and keeps
    each selected row unchanged and in input order."""
    # --- arrange ----------------------
    edis = [5.0] * 40 + [15.0] * 40 + [30.0] * 40 + [60.0] * 30 + [120.0] * 10
    previous_table = _full_features_table(edis)

    # --- act --------------------------
    output = CoreSelectionStage(n_iterations=1000).compute_output(previous_table, worker_pool=_IN_PROCESS_WORKER_POOL)

    # --- assert -----------------------
    assert output.table.schema == pl.Schema({**previous_table.schema, **DIFFICULTY_CLASS_SCHEMA})
    assert output.table.select(previous_table.columns).equals(
        previous_table.filter(pl.col("problem_id").is_in(output.table["problem_id"].to_list()))
    )
    assert dict(output.table["difficulty_class"].value_counts().iter_rows()) == {
        "A": 32,
        "B": 32,
        "C": 32,
        "Da": 24,
        "Db": 8,
    }
    report = output.reports[CORE_COMPOSITION_REPORT_NAME]
    assert report.select("core_size", "is_interim", "quota_a", "quota_da", "quota_db", "quota_d").rows() == [
        (128, True, 32, 24, 8, None)
    ]


@pytest.mark.only_with_numba_jit
def test_the_stage_selects_the_same_core_in_every_run():
    """With the stage's fixed seed and number of iterations, 2 runs select the same Core, and the stage's parameters
    record the seed and the number of iterations; the candidates hold no Db, so Da and Db share 1 quota, with a
    warning."""
    # --- arrange ----------------------
    previous_table = _full_features_table([5.0] * 40 + [15.0] * 40 + [30.0] * 40 + [60.0] * 40)
    stage = CoreSelectionStage(n_iterations=1000)

    # --- act --------------------------
    with pytest.warns(CoreCompositionWarning):
        outputs = [stage.compute_output(previous_table, worker_pool=_IN_PROCESS_WORKER_POOL) for _ in range(2)]

    # --- assert -----------------------
    assert outputs[0].table.equals(outputs[1].table)
    assert stage.parameters == {"n_iterations": 1000, "seed": stage.seed}
