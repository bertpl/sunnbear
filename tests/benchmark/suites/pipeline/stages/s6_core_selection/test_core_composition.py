"""`CoreComposition.from_class_counts` picks the largest of `CORE_SIZES` that every quarter fills, gives Da and Db 1
shared quota with a warning when either cannot fill its own, and stops the pipeline below the smallest size."""

import warnings

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.stages import (
    CoreComposition,
    CoreCompositionWarning,
    DifficultyClass,
    DifficultyQuota,
)
from sunnbear._core.benchmark.suites.pipeline.stages.s6_core_selection.core_composition import _CLASSES_PER_QUARTER

A, B, C, DA, DB = DifficultyClass


@pytest.mark.parametrize(
    "class_counts, core_size_expected, is_interim_expected",
    [
        pytest.param({A: 600, B: 600, C: 600, DA: 450, DB: 100}, 2048, True, id="2048_with_a_short_db"),
        pytest.param({A: 512, B: 512, C: 512, DA: 384, DB: 128}, 2048, False, id="2048_all_quotas"),
        pytest.param({A: 9999, B: 9999, C: 9999, DA: 9999, DB: 9999}, 2048, False, id="capped_at_2048"),
        pytest.param({A: 64, B: 200, C: 200, DA: 48, DB: 16}, 256, True, id="a_limits_the_size"),
    ],
)
def test_the_core_size_is_the_largest_that_every_quarter_fills(class_counts, core_size_expected, is_interim_expected):
    """The size is set by the quarter with the fewest candidates; only a Core of 2048 with 5 quotas is final."""
    # --- act --------------------------
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", CoreCompositionWarning)
        composition = CoreComposition.from_class_counts(class_counts)

    # --- assert -----------------------
    assert (composition.core_size, composition.is_interim) == (core_size_expected, is_interim_expected)
    assert sum(quota.count for quota in composition.quotas) == core_size_expected


def test_every_class_gets_its_own_quota_when_da_and_db_fill_theirs():
    """At size 256, A, B and C get 64 each, Da 48 and Db 16, without a warning."""
    # --- act --------------------------
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        composition = CoreComposition.from_class_counts({A: 64, B: 64, C: 64, DA: 48, DB: 16})

    # --- assert -----------------------
    assert composition.quotas == tuple(
        DifficultyQuota(classes=frozenset({difficulty_class}), count=count)
        for difficulty_class, count in zip(DifficultyClass, [64, 64, 64, 48, 16], strict=True)
    )


@pytest.mark.parametrize(
    "class_counts, message",
    [
        pytest.param({A: 64, B: 64, C: 64, DA: 64}, r"class Db has 0 candidates, 16 short of its quota of 16", id="db"),
        pytest.param(
            {A: 64, B: 64, C: 64, DA: 40, DB: 30}, r"class Da has 40 candidates, 8 short of its quota of 48", id="da"
        ),
    ],
)
def test_da_and_db_share_1_quota_with_a_warning_when_either_is_short(class_counts, message):
    """When Da or Db cannot fill its own quota, the 2 share 1 quota of a quarter of the Core, and a warning names the
    class that lacks candidates, and how many it lacks."""
    # --- act --------------------------
    with pytest.warns(CoreCompositionWarning, match=message):
        composition = CoreComposition.from_class_counts(class_counts)

    # --- assert -----------------------
    assert composition.core_size == 256
    assert composition.quotas[-1] == DifficultyQuota(classes=frozenset({DA, DB}), count=64)
    assert composition.report_row()["quota_d"] == 64
    assert composition.report_row()["quota_da"] is None


def test_the_pipeline_stops_below_the_smallest_core_size():
    """With 20 candidates of class C and 10 of Da and Db together, the message of the `PipelineStopError` lists those
    2 quarters of a Core of 128 and by how much each is short, and not the quarters that are filled."""
    # --- act / assert -----------------
    with pytest.raises(PipelineStopError) as exc_info:
        CoreComposition.from_class_counts({A: 40, B: 40, C: 20, DA: 4, DB: 6})
    assert str(exc_info.value) == (
        "The candidates fill no Core of 128 or more: class C has 20 candidates, 12 short of 32; "
        "classes Da and Db have 10 candidates, 22 short of 32."
    )


def test_the_report_row_gives_each_classs_count_and_largest_core_size():
    """Each class's largest Core size is the largest at which its candidates fill its share on their own, null where
    they fill it at no size."""
    # --- act --------------------------
    row = CoreComposition.from_class_counts({A: 512, B: 100, C: 64, DA: 48, DB: 16}).report_row()

    # --- assert -----------------------
    assert row == {
        "core_size": 256,
        "is_interim": True,
        "quota_a": 64,
        "n_candidates_a": 512,
        "max_core_size_a": 2048,
        "quota_b": 64,
        "n_candidates_b": 100,
        "max_core_size_b": 256,
        "quota_c": 64,
        "n_candidates_c": 64,
        "max_core_size_c": 256,
        "quota_da": 48,
        "n_candidates_da": 48,
        "max_core_size_da": 256,
        "quota_db": 16,
        "n_candidates_db": 16,
        "max_core_size_db": 256,
        "quota_d": None,
        "max_core_size_d": 256,
    }


def test_the_quarters_hold_every_difficulty_class_once():
    """The 4 quarters of the Core hold every `DifficultyClass` exactly once."""
    # --- act / assert -----------------
    assert sorted(c for classes in _CLASSES_PER_QUARTER for c in classes) == sorted(DifficultyClass)
