"""`UvTuplesConstructionSettings.from_total_time` derives the population size, worker count and time per tier."""

import pytest

from sunnbear._core.benchmark.tuple_set import UV_TUPLES_SIZES, UvTuplesConstructionSettings


@pytest.mark.parametrize(
    "t_total_sec, population_size, n_workers, min_t_budget_per_tier_sec",
    [
        (1.0, 2048, 1, 1 / 6),  # population and workers at their lower bounds; all time in the minimums
        (30.0, 32_768, 16, 5.0),  # half scale; all time in the minimums
        (60.0, 65_536, 32, 10.0),  # full scale reached; all time in the minimums
        (900.0, 65_536, 32, 10.0),  # full scale; the rest goes in proportion to the size
    ],
)
def test_from_total_time_scales_below_60_s_and_saturates_above(
    t_total_sec, population_size, n_workers, min_t_budget_per_tier_sec
):
    """Below 60 s the population, the workers and the minimum per tier scale down; the rest goes ∝ size."""
    # --- act --------------------------
    settings = UvTuplesConstructionSettings.from_total_time(t_total_sec, n_workers=32)

    # --- assert -----------------------
    t_rest_sec = t_total_sec - 6 * min_t_budget_per_tier_sec
    assert settings.population_size == population_size
    assert settings.n_workers == n_workers
    assert settings.t_budget_per_tier_sec == pytest.approx(
        {k: min_t_budget_per_tier_sec + t_rest_sec * k / sum(UV_TUPLES_SIZES) for k in UV_TUPLES_SIZES}
    )
    assert sum(settings.t_budget_per_tier_sec.values()) == pytest.approx(t_total_sec)


@pytest.mark.parametrize(
    "t_total_sec, n_workers, message",
    [
        (0.5, 32, "at least 1.0 s"),
        (60.0, 0, "n_workers must be at least 1"),
    ],
)
def test_from_total_time_rejects_a_total_below_1_s_or_no_workers(t_total_sec, n_workers, message):
    """A total below 1 s, or fewer than 1 worker, raises a `ValueError`."""
    with pytest.raises(ValueError, match=message):
        UvTuplesConstructionSettings.from_total_time(t_total_sec, n_workers)
