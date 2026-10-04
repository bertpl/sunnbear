"""`MCTuplesConstructionSettings` holds the settings for constructing one tuple set, derived from its total time.

Each size takes 2 max-div solves (`MCTuplesConstructionStep`). The total time is split over the solves:

- each step gets a fixed share of the total, `T_BUDGET_BUDGET_FRACTION_PER_STEP`, whatever its candidate count, because
  cell selection decides the L2 min separation of the result and still improves it when a long budget ends, while
  refinement improves it little at the large sizes; the size of refinement's candidate pool therefore does not
  change the time of cell selection;
- within a step, each solve gets at least `MIN_T_BUDGET_FRACTION_PER_SOLVE` of the total, so the solves of the
  smallest sizes, whose share of the work is tiny, still get time to run, and the rest of the step's share is
  split in proportion to `n · k`, the step's number of candidates times the size, a measure of the solve's work.

From `MIN_T_TOTAL_AT_FULL_SCALE_SEC` up, the construction builds every size of `MCTuplesSize` with every
requested worker.

Below `MIN_T_TOTAL_AT_FULL_SCALE_SEC`, the number of sizes and the worker count scale down together, so that
short runs such as tests still construct a nested set. The shortest runs build only the `MIN_N_SIZES` smallest
sizes, the fewest that still test the nesting. Production runs are far longer and never scale down.
"""

from dataclasses import dataclass
from typing import Self

from .construction_steps import MCTuplesConstructionStep
from .sizes import MCTuplesSize

MIN_T_TOTAL_SEC = 1.0
MIN_T_TOTAL_AT_FULL_SCALE_SEC = 60.0
MIN_T_BUDGET_FRACTION_PER_SOLVE = 0.01
MIN_N_SIZES = 2
T_BUDGET_FRACTION_PER_STEP = {MCTuplesConstructionStep.CELL_SELECTION: 0.8, MCTuplesConstructionStep.REFINEMENT: 0.2}


# ==================================================================================================
#  MCTuplesConstructionSettings
# ==================================================================================================
@dataclass(frozen=True)
class MCTuplesConstructionSettings:
    """`MCTuplesConstructionSettings` holds a construction's sizes, worker count and time per solve.

    Attributes:
        sizes: The sizes to build, the smallest first; always the smallest sizes of `MCTuplesSize`.
        n_workers: The number of max-div workers per solve.
        t_budget_per_solve_sec: The wall-clock budget of each solve, keyed by size and step.
    """

    sizes: tuple[MCTuplesSize, ...]
    n_workers: int
    t_budget_per_solve_sec: dict[tuple[MCTuplesSize, MCTuplesConstructionStep], float]

    @classmethod
    def from_total_time(cls, t_total_sec: float, n_workers: int) -> Self:
        """Return the settings for a construction of `t_total_sec` seconds with up to `n_workers` workers.

        With `scale = min(1, t_total_sec / MIN_T_TOTAL_AT_FULL_SCALE_SEC)`:

        - the number of sizes is `MIN_N_SIZES + floor(scale · (len(MCTuplesSize) - MIN_N_SIZES))`;
        - the worker count is `max(1, round(scale · n_workers))`;
        - each step gets `T_BUDGET_FRACTION_PER_STEP` of `t_total_sec`; within it, each solve gets
          `MIN_T_BUDGET_FRACTION_PER_SOLVE · t_total_sec`, and the rest of the step's share is split in proportion
          to `n · k`, the step's number of candidates (`MCTuplesConstructionStep.n_candidates`) times the size.

        Raises:
            ValueError: If `t_total_sec` is below `MIN_T_TOTAL_SEC`, or `n_workers` below 1.
        """
        if t_total_sec < MIN_T_TOTAL_SEC:
            raise ValueError(f"t_total_sec must be at least {MIN_T_TOTAL_SEC} s (got {t_total_sec}).")
        if n_workers < 1:
            raise ValueError(f"n_workers must be at least 1 (got {n_workers}).")
        scale = min(1.0, t_total_sec / MIN_T_TOTAL_AT_FULL_SCALE_SEC)
        sizes = tuple(MCTuplesSize)[: MIN_N_SIZES + int(scale * (len(MCTuplesSize) - MIN_N_SIZES))]

        # --- time per solve ---------------------
        min_t_budget_per_solve_sec = MIN_T_BUDGET_FRACTION_PER_SOLVE * t_total_sec
        t_budget_per_solve_sec: dict[tuple[MCTuplesSize, MCTuplesConstructionStep], float] = {}
        for step, t_fraction in T_BUDGET_FRACTION_PER_STEP.items():
            work_per_size = {k: step.n_candidates(k) * k for k in sizes}
            t_rest_sec = t_fraction * t_total_sec - len(sizes) * min_t_budget_per_solve_sec
            for k, solve_work in work_per_size.items():
                t_budget_per_solve_sec[k, step] = min_t_budget_per_solve_sec + t_rest_sec * solve_work / sum(
                    work_per_size.values()
                )
        return cls(
            sizes=sizes, n_workers=max(1, round(scale * n_workers)), t_budget_per_solve_sec=t_budget_per_solve_sec
        )
