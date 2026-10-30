"""`DifficultyClass.from_edi` buckets an EDI by its ratio to `n_bisection_fevals`, and the classes' Core shares sum to
1."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.stages import DifficultyClass


@pytest.mark.parametrize(
    "edi, difficulty_class_expected",
    [
        (2.0, DifficultyClass.A),
        (9.99, DifficultyClass.A),
        (10.0, DifficultyClass.B),
        (20.0, DifficultyClass.C),
        (39.99, DifficultyClass.C),
        (40.0, DifficultyClass.DA),
        (80.0, DifficultyClass.DB),
        (160.0, DifficultyClass.DB),
    ],
)
def test_the_class_follows_the_edi_relative_to_bisections_count(edi, difficulty_class_expected):
    """With 40 bisection evaluations, the classes start at the EDIs 10, 20, 40 and 80, and an EDI of `max_fevals`,
    160, falls in Db."""
    # --- act / assert -----------------
    assert DifficultyClass.from_edi(edi, n_bisection_fevals=40) is difficulty_class_expected


def test_the_core_shares_sum_to_1():
    """A, B and C fill a quarter of the Core each, Da 3/16 and Db 1/16."""
    # --- act / assert -----------------
    assert [difficulty_class.core_share * 16 for difficulty_class in DifficultyClass] == [4, 4, 4, 3, 1]
