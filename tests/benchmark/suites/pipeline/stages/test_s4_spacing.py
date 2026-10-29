"""`SpacingStage` drops near-duplicate candidates of each formula:

- it keeps, in row order, the candidates at least `min_distance` apart in the balanced coarse feature space;
- it keeps at least 2 of every formula with 2 or more candidates;
- it reports each dropped candidate with its nearest kept candidate.
"""

import polars as pl
import pytest

from sunnbear._core.benchmark.suites.pipeline.features import FeatureBlock, FeatureFidelity
from sunnbear._core.benchmark.suites.pipeline.stages import (
    CANDIDATE_COUNTS_PER_FORMULA_REPORT_NAME,
    DROPPED_CANDIDATES_REPORT_NAME,
    NEAREST_KEPT_CANDIDATE_SCHEMA,
    SpacingStage,
)
from sunnbear._core.utils.worker_pool import WorkerPool

_IN_PROCESS_WORKER_POOL = WorkerPool(n_workers=1)


def _coarse_features_table(
    features_by_problem_id: dict[str, tuple[float, float]], *, scales: tuple[float | None, float | None]
) -> pl.DataFrame:
    """Return a table of coarse features for 1 core solver config, ``brent``, with the feature scales `scales`.

    Each candidate's tuple holds the value of the first feature of the solvers block and of the snuffled block, in that
    order; its other features are 0. `scales` holds the scale of each `FeatureBlock`, in their order.
    """
    fidelity = FeatureFidelity.COARSE
    column_names = fidelity.feature_column_names(["brent"])
    first_column_names = [
        next(name for name in column_names if name.startswith(fidelity.feature_column_prefix(block)))
        for block in FeatureBlock
    ]
    values_by_block = zip(*features_by_problem_id.values(), strict=True)
    return (
        pl.DataFrame({"problem_id": list(features_by_problem_id)})
        .with_columns(pl.lit(0.0).alias(column_name) for column_name in column_names)
        .with_columns(
            *(
                pl.Series(column_name, values, dtype=pl.Float64())
                for column_name, values in zip(first_column_names, values_by_block, strict=True)
            ),
            *(
                pl.lit(scale, dtype=pl.Float64()).alias(column_name)
                for column_name, scale in zip(fidelity.feature_scale_column_names(), scales, strict=True)
            ),
        )
    )


def test_the_pass_keeps_the_candidates_far_enough_from_every_kept_one_in_row_order():
    """With the solvers block divided by 2 and the snuffled block by 0.5, the pass keeps p=1, p=3 and p=5 of formula
    f99.1, and drops p=2 and p=4, each closer than 1 to the kept candidate before it; p=3 is kept over p=4 because it
    comes first.

    Formula f99.2's only candidate is kept, although it coincides with f99.1's first candidate."""
    # --- arrange ----------------------
    previous_table = _coarse_features_table(
        {
            "f99.1[p=1.0]": (0.0, 0.0),  # balanced: (0.0, 0.0)
            "f99.1[p=2.0]": (1.2, 0.0),  # balanced: (0.6, 0.0), at 0.6 from p=1
            "f99.1[p=3.0]": (1.2, 0.3),  # balanced: (0.6, 0.6), at 1.2 from p=1
            "f99.1[p=4.0]": (2.4, 0.3),  # balanced: (1.2, 0.6), at 0.6 from p=3
            "f99.1[p=5.0]": (3.0, 0.5),  # balanced: (1.5, 1.0), at 1.3 from p=3
            "f99.2": (0.0, 0.0),
        },
        scales=(2.0, 0.5),
    )

    # --- act --------------------------
    output = SpacingStage(min_distance=1.0).compute_output(previous_table, worker_pool=_IN_PROCESS_WORKER_POOL)

    # --- assert -----------------------
    assert output.table.equals(
        previous_table.filter(pl.col("problem_id").is_in(["f99.1[p=1.0]", "f99.1[p=3.0]", "f99.1[p=5.0]", "f99.2"]))
    )
    dropped_candidates = output.reports[DROPPED_CANDIDATES_REPORT_NAME]
    assert dropped_candidates.schema == pl.Schema({**previous_table.schema, **NEAREST_KEPT_CANDIDATE_SCHEMA})
    assert dropped_candidates.select("problem_id", *NEAREST_KEPT_CANDIDATE_SCHEMA).rows() == [
        ("f99.1[p=2.0]", "f99.1[p=1.0]", pytest.approx(0.6)),
        ("f99.1[p=4.0]", "f99.1[p=3.0]", pytest.approx(0.6)),
    ]
    assert output.reports[CANDIDATE_COUNTS_PER_FORMULA_REPORT_NAME].rows() == [("f99.1", 5, 3, 2), ("f99.2", 1, 1, 0)]


def test_a_formula_with_2_or_more_candidates_keeps_at_least_2():
    """Where the pass keeps only a formula's first candidate, the stage also keeps the one farthest from it: for
    f99.1 that is p=3, which then becomes the nearest kept candidate of p=2; for f99.2 it is the second of its 2
    identical candidates."""
    # --- arrange ----------------------
    previous_table = _coarse_features_table(
        {
            "f99.1[p=1.0]": (0.0, 0.0),
            "f99.1[p=2.0]": (0.4, 0.0),  # balanced: (0.2, 0.0), at 0.2 from p=1 and 0.1 from p=3
            "f99.1[p=3.0]": (0.6, 0.0),  # balanced: (0.3, 0.0), at 0.3 from p=1
            "f99.2[p=1.0]": (0.0, 0.0),
            "f99.2[p=2.0]": (0.0, 0.0),
        },
        scales=(2.0, 0.5),
    )

    # --- act --------------------------
    output = SpacingStage(min_distance=1.0).compute_output(previous_table, worker_pool=_IN_PROCESS_WORKER_POOL)

    # --- assert -----------------------
    assert output.table["problem_id"].to_list() == ["f99.1[p=1.0]", "f99.1[p=3.0]", "f99.2[p=1.0]", "f99.2[p=2.0]"]
    assert output.reports[DROPPED_CANDIDATES_REPORT_NAME].select(
        "problem_id", *NEAREST_KEPT_CANDIDATE_SCHEMA
    ).rows() == [("f99.1[p=2.0]", "f99.1[p=3.0]", pytest.approx(0.1))]


def test_a_single_candidate_with_null_scales_is_kept():
    """Coarse characterization leaves the feature scales null when it keeps fewer than 2 candidates; the stage keeps the
    only candidate, and its reports hold no dropped candidate."""
    # --- arrange ----------------------
    previous_table = _coarse_features_table({"f99.1": (0.5, 0.5)}, scales=(None, None))

    # --- act --------------------------
    output = SpacingStage().compute_output(previous_table, worker_pool=_IN_PROCESS_WORKER_POOL)

    # --- assert -----------------------
    assert output.table.equals(previous_table)
    assert output.reports[DROPPED_CANDIDATES_REPORT_NAME].is_empty()
    assert output.reports[CANDIDATE_COUNTS_PER_FORMULA_REPORT_NAME].rows() == [("f99.1", 1, 1, 0)]
