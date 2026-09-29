"""`MCTuplesConstructionSettings.from_total_time` derives the population size, worker count and time per size."""

import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesConstructionSettings, MCTuplesSize


@pytest.mark.parametrize(
    "t_total_sec, population_size, n_workers, min_t_budget_per_size_sec",
    [
        (1.0, 2048, 1, 1 / 6),  # population and workers at their lower bounds; all time goes to the per-size minimums
        (30.0, 32_768, 16, 5.0),  # half scale; all time goes to the per-size minimums
        (60.0, 65_536, 32, 10.0),  # full scale reached; all time goes to the per-size minimums
        (900.0, 65_536, 32, 10.0),  # full scale; the rest goes in proportion to the size
    ],
)
def test_from_total_time_scales_below_60_s_and_saturates_above(
    t_total_sec, population_size, n_workers, min_t_budget_per_size_sec
):
    """Below 60 s, the population, workers and minimum time per size scale down; the rest is split by size."""
    # --- act --------------------------
    settings = MCTuplesConstructionSettings.from_total_time(t_total_sec, n_workers=32)

    # --- assert -----------------------
    t_rest_sec = t_total_sec - 6 * min_t_budget_per_size_sec
    assert settings.population_size == population_size
    assert settings.n_workers == n_workers
    assert settings.t_budget_per_size_sec == pytest.approx(
        {k: min_t_budget_per_size_sec + t_rest_sec * k / sum(MCTuplesSize) for k in MCTuplesSize}
    )
    assert sum(settings.t_budget_per_size_sec.values()) == pytest.approx(t_total_sec)


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
        MCTuplesConstructionSettings.from_total_time(t_total_sec, n_workers)
