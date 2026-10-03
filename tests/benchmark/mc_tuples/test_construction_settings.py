"""`MCTuplesConstructionSettings.from_total_time` derives the sizes, worker count and time per solve."""

import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesConstructionSettings, MCTuplesSize
from sunnbear._core.benchmark.mc_tuples.construction_settings import T_FRACTION_PER_STEP
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


def test_every_step_has_a_fixed_share_and_the_shares_sum_to_1():
    """`T_FRACTION_PER_STEP` names every step once, and the shares add up to the whole total."""
    # --- act / assert -----------------
    assert set(T_FRACTION_PER_STEP) == set(MCTuplesConstructionStep)
    assert sum(T_FRACTION_PER_STEP.values()) == pytest.approx(1.0)


@pytest.mark.parametrize("t_total_sec", [1.0, 30.0, 28_800.0])
def test_from_total_time_splits_each_step_s_share_by_1_percent_per_solve_and_the_rest_by_work(t_total_sec):
    """Within a step's share, each solve gets 1 % of the total, the rest in proportion to its candidates times size."""
    # --- act --------------------------
    settings = MCTuplesConstructionSettings.from_total_time(t_total_sec, n_workers=32)

    # --- assert -----------------------
    budgets = settings.t_budget_per_solve_sec
    for step, t_fraction in T_FRACTION_PER_STEP.items():
        step_budgets = {k: t for (k, s), t in budgets.items() if s == step}
        work_per_size = {k: step.n_candidates(k) * k for k in step_budgets}
        t_rest_sec = t_fraction * t_total_sec - 0.01 * t_total_sec * len(step_budgets)
        assert step_budgets == pytest.approx(
            {
                k: 0.01 * t_total_sec + t_rest_sec * work / sum(work_per_size.values())
                for k, work in work_per_size.items()
            }
        )
        assert sum(step_budgets.values()) == pytest.approx(t_fraction * t_total_sec)
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
