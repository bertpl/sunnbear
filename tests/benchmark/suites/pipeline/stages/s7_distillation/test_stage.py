"""`DistillationStage` distills a benchmark family and a calibration family of nested suites from the Core:

- the 2 families split the Core in halves, and every suite meets the Core's quotas at its size;
- each family's smaller suites lie inside its larger ones, also when Da and Db share 1 quota;
- it records max-div's time per candidate and seed in its parameters.
"""

import numpy as np
import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyClass
from sunnbear._core.benchmark.suites.pipeline.stages import (
    DIFFICULTY_CLASS_SCHEMA,
    SUITE_COMPOSITIONS_REPORT_NAME,
    SUITE_MEMBERSHIP_SCHEMA,
    CoreCompositionWarning,
    DistillationStage,
    FullCharacterizationStage,
)
from sunnbear._core.solvers.core import SolverConfigRegistry
from sunnbear._core.utils.worker_pool import WorkerPool

A, B, C, DA, DB = DifficultyClass

# The stage runs no tasks in the pool, so its processes never start; max-div runs 1 worker per worker of the pool, and
# warns that 1 worker gains nothing over a single solve.
_TWO_WORKER_POOL = WorkerPool(n_workers=2)
# In these tests each max-div worker runs for 3.84 s on a pool of 128 candidates and 7.68 s on a pool of 256, which
# covers the start of the workers' processes and leaves time to meet every quota on a busy CI machine.
_SEC_PER_CANDIDATE = 0.03


def _core_table(class_counts: dict[DifficultyClass, int]) -> pl.DataFrame:
    """Return a Core of random full features for 1 core solver config, with `class_counts` candidates of each class.

    Every feature scale is 1, so the scaled feature vectors equal the features.
    """
    difficulty_classes = [c.value for c, count in class_counts.items() for _ in range(count)]
    column_names = FullCharacterizationStage([SolverConfigRegistry.config_from_id("bisection")]).feature_column_names
    rng = np.random.default_rng(seed=3)
    return pl.DataFrame(
        {
            "problem_id": [f"f99.{idx}" for idx in range(len(difficulty_classes))],
            **{column_name: rng.random(len(difficulty_classes)) for column_name in column_names},
        }
    ).with_columns(
        *(pl.lit(1.0).alias(column_name) for column_name in FullCharacterizationStage.feature_scale_column_names()),
        pl.Series("difficulty_class", difficulty_classes, dtype=DIFFICULTY_CLASS_SCHEMA["difficulty_class"]),
    )


def _class_counts(table: pl.DataFrame) -> dict[str, int]:
    """Return the number of rows of `table` per difficulty class, 0 for a class without rows."""
    counts = dict(table["difficulty_class"].value_counts().iter_rows())
    return {c.value: counts.get(c.value, 0) for c in DifficultyClass}


@pytest.mark.only_with_numba_jit
def test_the_families_split_a_core_of_128_into_2_suites_of_64():
    """A Core of 128 with 1 quota per class splits into a benchmark suite and a calibration suite of 64, each with 16
    of A, B and C, 12 of Da and 4 of Db; the stage keeps every row unchanged and in input order."""
    # --- arrange ----------------------
    previous_table = _core_table({A: 32, B: 32, C: 32, DA: 24, DB: 8})

    # --- act --------------------------
    output = DistillationStage(_SEC_PER_CANDIDATE).compute_output(previous_table, worker_pool=_TWO_WORKER_POOL)

    # --- assert -----------------------
    assert output.table.schema == pl.Schema({**previous_table.schema, **SUITE_MEMBERSHIP_SCHEMA})
    assert output.table.select(previous_table.columns).equals(previous_table)
    assert (output.table["smallest_suite_size"] == 64).all()
    for family in ["benchmark", "calibration"]:
        assert _class_counts(output.table.filter(pl.col("suite_family") == family)) == {
            "A": 16,
            "B": 16,
            "C": 16,
            "Da": 12,
            "Db": 4,
        }
    report = output.reports[SUITE_COMPOSITIONS_REPORT_NAME]
    assert report.select("suite_family", "size", "n_candidates_a", "n_candidates_db").rows() == [
        ("benchmark", 64, 16, 4),
        ("calibration", 64, 16, 4),
    ]
    assert report["diversity"][0] > 0.0
    assert report["diversity"][1] is None


@pytest.mark.only_with_numba_jit
def test_each_family_nests_its_suites_under_a_shared_quota_and_records_its_parameters():
    """A Core of 256 whose classes Da and Db share 1 quota, with a warning, splits into 2 families of 128, and each
    family's suite of 64 is a subset of its suite of 128 with 16 of A, B, C, and Da and Db together; the stage's
    parameters record max-div's time per candidate and seed."""
    # --- arrange ----------------------
    previous_table = _core_table({A: 64, B: 64, C: 64, DA: 40, DB: 24})
    stage = DistillationStage(_SEC_PER_CANDIDATE)

    # --- act --------------------------
    with pytest.warns(CoreCompositionWarning):
        output = stage.compute_output(previous_table, worker_pool=_TWO_WORKER_POOL)

    # --- assert -----------------------
    for family in ["benchmark", "calibration"]:
        family_rows = output.table.filter(pl.col("suite_family") == family)
        assert sorted(family_rows["smallest_suite_size"].unique()) == [64, 128]
        for size, quota_expected in [(128, 32), (64, 16)]:
            counts = _class_counts(family_rows.filter(pl.col("smallest_suite_size") <= size))
            assert [counts["A"], counts["B"], counts["C"], counts["Da"] + counts["Db"]] == [quota_expected] * 4
    report = output.reports[SUITE_COMPOSITIONS_REPORT_NAME]
    assert report.select("suite_family", "size").rows() == [
        ("benchmark", 128),
        ("benchmark", 64),
        ("calibration", 128),
        ("calibration", 64),
    ]
    assert stage.parameters == {"sec_per_candidate": _SEC_PER_CANDIDATE, "seed": stage.seed}
