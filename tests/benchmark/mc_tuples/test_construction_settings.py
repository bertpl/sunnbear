"""`MCTuplesConstructionSettings.from_total_time` derives the sizes, worker count and time per solve."""

import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesConstructionSettings, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction_steps import MCTuplesConstructionStep


@pytest.mark.parametrize(
    "t_total_sec, sizes, n_workers",
    [
        (1.0, (32, 64), 1),  # the 2 smallest sizes, and 1 worker
        (15.0, (32, 64, 128), 8),  # a quarter of full scale: 1 size more
        (30.0, (32, 64, 128, 256), 16),  # half scale
        (60.0, tuple(MCTuplesSize), 32),  # full scale reached
        (28_800.0, tuple(MCTuplesSize), 32),  # full scale
    ],
)
def test_from_total_time_builds_fewer_sizes_with_fewer_workers_below_60_s(t_total_sec, sizes, n_workers):
    """Below 60 s, sizes and workers scale down, to the 2 smallest sizes and 1 worker; from 60 s up, all are used."""
    # --- act --------------------------
    settings = MCTuplesConstructionSettings.from_total_time(t_total_sec, n_workers=32)

    # --- assert -----------------------
    assert settings.sizes == sizes
    assert settings.n_workers == n_workers
    assert set(settings.t_budget_per_solve_sec) == {(k, step) for k in sizes for step in MCTuplesConstructionStep}


@pytest.mark.parametrize("t_total_sec", [1.0, 30.0, 28_800.0])
def test_from_total_time_gives_each_solve_1_percent_and_splits_the_rest_by_work(t_total_sec):
    """Each solve gets 1 % of the total, the rest in proportion to its pool size times its size; all of it is used."""
    # --- act --------------------------
    settings = MCTuplesConstructionSettings.from_total_time(t_total_sec, n_workers=32)

    # --- assert -----------------------
    budgets = settings.t_budget_per_solve_sec
    work = {(k, step): step.pool_size(k) * k for k, step in budgets}
    t_rest_sec = t_total_sec * (1 - 0.01 * len(budgets))
    assert budgets == pytest.approx(
        {key: 0.01 * t_total_sec + t_rest_sec * solve_work / sum(work.values()) for key, solve_work in work.items()}
    )
    assert sum(budgets.values()) == pytest.approx(t_total_sec)


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
