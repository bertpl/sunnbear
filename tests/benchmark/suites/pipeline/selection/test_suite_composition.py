"""`SuiteComposition` checks that a selection has the suite's size and meets every quota, and halves its quotas."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.core import PipelineStopError
from sunnbear._core.benchmark.suites.pipeline.selection import DifficultyClass, DifficultyQuota, SuiteComposition

A, B, C, DA, DB = DifficultyClass


def _composition(counts: dict[frozenset[DifficultyClass], int]) -> SuiteComposition:
    """Return the composition with 1 quota per entry of `counts`, which maps the quota's classes to its count."""
    return SuiteComposition(
        quotas=tuple(DifficultyQuota(classes=classes, count=count) for classes, count in counts.items())
    )


_QUOTA_PER_CLASS_128 = _composition(
    {frozenset({A}): 32, frozenset({B}): 32, frozenset({C}): 32, frozenset({DA}): 24, frozenset({DB}): 8}
)
_SHARED_D_QUOTA_128 = _composition(
    {frozenset({A}): 32, frozenset({B}): 32, frozenset({C}): 32, frozenset({DA, DB}): 32}
)


@pytest.mark.parametrize(
    "selected_classes, message",
    [
        pytest.param([A] * 32 + [B] * 32 + [C] * 32 + [DA] * 24 + [DB] * 8, None, id="met"),
        pytest.param([A] * 33 + [B] * 31 + [C] * 32 + [DA] * 24 + [DB] * 8, r"A: 33 of 32; B: 31 of 32\.", id="unmet"),
        pytest.param([A] * 32 + [B] * 32 + [C] * 32 + [DA] * 24, r"120 candidates .* Db: 0 of 8\.", id="too_few"),
    ],
)
def test_a_selection_must_have_the_suites_size_and_meet_every_quota(selected_classes, message):
    """A selection of the suite's size that meets every quota passes; one that misses a quota or the size stops the
    pipeline, with a message that names each unmet quota and the selection's count."""
    # --- act / assert -----------------
    if message is None:
        _QUOTA_PER_CLASS_128.check_selection(selected_classes)
    else:
        with pytest.raises(PipelineStopError, match=message):
            _QUOTA_PER_CLASS_128.check_selection(selected_classes)


@pytest.mark.parametrize(
    "composition, composition_expected",
    [
        pytest.param(
            _QUOTA_PER_CLASS_128,
            _composition(
                {frozenset({A}): 16, frozenset({B}): 16, frozenset({C}): 16, frozenset({DA}): 12, frozenset({DB}): 4}
            ),
            id="quota_per_class",
        ),
        pytest.param(
            _SHARED_D_QUOTA_128,
            _composition({frozenset({A}): 16, frozenset({B}): 16, frozenset({C}): 16, frozenset({DA, DB}): 16}),
            id="shared_d_quota",
        ),
    ],
)
def test_a_halved_composition_holds_half_of_each_quota(composition, composition_expected):
    """Halving a suite of 128 gives a suite of 64 whose quotas count the same classes, each at half the count."""
    # --- act --------------------------
    halved = composition.halved()

    # --- assert -----------------------
    assert halved == composition_expected
    assert halved.size == 64


def test_a_composition_with_an_odd_quota_cannot_be_halved():
    """A quota of 3 has no half, so halving raises."""
    # --- arrange ----------------------
    composition = _composition({frozenset({A}): 3, frozenset({B}): 4})

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="A suite of 7 with an odd quota"):
        composition.halved()
