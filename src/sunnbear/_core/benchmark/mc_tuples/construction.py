"""`generate_mc_tuples` constructs a nested set of (u, v) tuples that holds exactly 1 tuple per lane at every size.

The construction builds the sizes bottom-up, the smallest first, and each larger size includes the size
below it, so every size is a prefix of the next.

Each size first fixes its new u and v values, 1 per new tuple on each axis, and cuts each axis into lanes around
all values of the size, old and new, as `LaneGrid` defines them; a new lane is the lane around a new value.

The new tuples go in the cells where a new u lane crosses a new v lane, in 2 max-div steps (`construction_steps`):

- **cell selection** (`MCTuplesCellSelectionStep`): 1 cell per new lane on each axis;
- **refinement** (`MCTuplesRefinementStep`): 1 tuple inside each selected cell.

`MCTuplesGenerator` runs the construction:

- it splits the total time over the steps' max-div solves;
- for each size, it builds the lane grid and runs the 2 steps;
- it passes each step's result (`construction_step_results`) to the caller's `on_step_finished`, so that a long
  construction can show its progress and store its tuples and max-div's solutions as it goes.
"""

from collections.abc import Callable
from typing import ClassVar

from .construction_step_results import MCTuplesStepResult
from .construction_steps import (
    MCTuplesCellSelectionStep,
    MCTuplesRefinementStep,
    MCTuplesSolveSettings,
    MCTuplesStep,
)
from .lane_grid import LaneGrid
from .sizes import MCTuplesSize
from .tuples import MCTuples


# ==================================================================================================
#  MCTuplesGenerator
# ==================================================================================================
class MCTuplesGenerator:
    """`MCTuplesGenerator` builds the nested tuple set size by size, 2 max-div steps per size, and reports every step.

    The total time of a construction is split over its solves:

    - each step kind gets a fixed share of the total time, `T_BUDGET_FRACTION_PER_STEP_KIND`, independent of its
      number of candidates. Cell selection sets the L2 min separation of the result and is still improving it when
      a long budget runs out; refinement improves the L2 min separation little at the large sizes. Refinement
      therefore must not take time from cell selection just because it has more candidates;
    - the share of each step kind is split over the sizes:
      - the solve of each size gets `MIN_T_BUDGET_FRACTION_PER_SOLVE` of the total, so the solves of the smallest
        sizes, whose share of the work is tiny, still get time to run;
      - the rest of the share is split in proportion to `n · k`, the step's number of candidates times the size,
        a measure of the solve's work.

    From `MIN_T_TOTAL_AT_FULL_SCALE_SEC` up, every solve uses all `n_workers` workers; below
    `MIN_T_TOTAL_AT_FULL_SCALE_SEC`, the worker count scales down with the total time, so that a short run, such as
    a test, does not spend its time starting workers.

    Attributes:
        n_workers: The number of max-div workers per solve when the total time is `MIN_T_TOTAL_AT_FULL_SCALE_SEC`
            or more; more workers search from more seeds, and may exceed the number of cores.
        seed: The seed of every random draw and of every max-div solve.
        on_step_finished: Called with each step's result as soon as the step, its validation included, ends; None
            reports nothing.
    """

    T_BUDGET_FRACTION_PER_STEP_KIND: ClassVar[dict[type[MCTuplesStep], float]] = {
        MCTuplesCellSelectionStep: 0.9,
        MCTuplesRefinementStep: 0.1,
    }
    MIN_T_BUDGET_FRACTION_PER_SOLVE: ClassVar[float] = 0.01
    MIN_T_TOTAL_SEC: ClassVar[float] = 1.0
    MIN_T_TOTAL_AT_FULL_SCALE_SEC: ClassVar[float] = 60.0

    def __init__(
        self,
        *,
        n_workers: int = 32,
        seed: int = 42,
        on_step_finished: Callable[[MCTuplesStepResult], None] | None = None,
    ) -> None:
        """Set the settings of every construction of this generator.

        Raises:
            ValueError: If `n_workers` is below 1.
        """
        if n_workers < 1:
            raise ValueError(f"n_workers must be at least 1 (got {n_workers}).")
        self.n_workers = n_workers
        self.seed = seed
        self.on_step_finished = on_step_finished

    # --------------------------------------------------------------------------
    #  Main API
    # --------------------------------------------------------------------------
    def generate(self, t_total_sec: float, max_size: MCTuplesSize = MCTuplesSize.SIZE_1024) -> MCTuples:
        """Construct the nested set up to `max_size` in about `t_total_sec` s; size `k` is its first `k` tuples.

        `generate_mc_tuples`, the public form of this method, documents the construction's extra time beyond
        `t_total_sec` and why a rerun gives a different set.

        Args:
            t_total_sec: The total wall-clock time of the solves, at least `MIN_T_TOTAL_SEC`.
            max_size: The largest size to build, 1 of `MCTuplesSize`; every size up to it is built, however short
                `t_total_sec` is.

        Raises:
            ValueError: If `t_total_sec` is below `MIN_T_TOTAL_SEC`, or `max_size` is not 1 of `MCTuplesSize`.
            MCTuplesConstructionError: If a size misses a tuple of the size below it or does not hold exactly 1 tuple
                per lane, which can happen when `t_total_sec` is too short for max-div to meet its constraints.
        """
        t_budget_per_solve_sec = self.t_budget_per_solve_sec(t_total_sec, max_size)
        settings = MCTuplesSolveSettings.for_seed(self.n_workers_for(t_total_sec), self.seed)
        tuples: MCTuples | None = None
        for size in MCTuplesSize.up_to(max_size):
            grid = LaneGrid.for_size(size, tuples)
            cell_selection_result = MCTuplesCellSelectionStep(grid, settings).run(
                t_budget_per_solve_sec[size, MCTuplesCellSelectionStep]
            )
            if self.on_step_finished is not None:
                self.on_step_finished(cell_selection_result)
            refinement_result = MCTuplesRefinementStep(grid, cell_selection_result.cells, settings).run(
                t_budget_per_solve_sec[size, MCTuplesRefinementStep]
            )
            if self.on_step_finished is not None:
                self.on_step_finished(refinement_result)
            tuples = refinement_result.tuples
        assert tuples is not None  # noqa: S101 -- MCTuplesSize.up_to never returns an empty tuple
        return tuples

    # --------------------------------------------------------------------------
    #  Workers and time per solve
    # --------------------------------------------------------------------------
    def n_workers_for(self, t_total_sec: float) -> int:
        """Return the worker count of a run of `t_total_sec`."""
        scale = min(1.0, t_total_sec / self.MIN_T_TOTAL_AT_FULL_SCALE_SEC)
        return max(1, round(scale * self.n_workers))

    def t_budget_per_solve_sec(
        self, t_total_sec: float, max_size: MCTuplesSize
    ) -> dict[tuple[MCTuplesSize, type[MCTuplesStep]], float]:
        """Return the wall-clock budget of every solve of a run of `t_total_sec` up to `max_size`, by size and step.

        Raises:
            ValueError: If `t_total_sec` is below `MIN_T_TOTAL_SEC`, or `max_size` is not 1 of `MCTuplesSize`.
        """
        if t_total_sec < self.MIN_T_TOTAL_SEC:
            raise ValueError(f"t_total_sec must be at least {self.MIN_T_TOTAL_SEC} s (got {t_total_sec}).")
        sizes = MCTuplesSize.up_to(max_size)
        t_min_per_solve_sec = self.MIN_T_BUDGET_FRACTION_PER_SOLVE * t_total_sec
        t_budget_per_solve_sec: dict[tuple[MCTuplesSize, type[MCTuplesStep]], float] = {}
        for step_cls, t_budget_fraction in self.T_BUDGET_FRACTION_PER_STEP_KIND.items():
            work_per_size = {size: step_cls.n_candidates(size) * size for size in sizes}
            t_rest_sec = t_budget_fraction * t_total_sec - len(sizes) * t_min_per_solve_sec
            for size, work in work_per_size.items():
                t_budget_per_solve_sec[size, step_cls] = t_min_per_solve_sec + t_rest_sec * work / sum(
                    work_per_size.values()
                )
        return t_budget_per_solve_sec


# ==================================================================================================
#  generate_mc_tuples
# ==================================================================================================
def generate_mc_tuples(
    t_total_sec: float,
    *,
    n_workers: int = 32,
    seed: int = 42,
    max_size: MCTuplesSize = MCTuplesSize.SIZE_1024,
    on_step_finished: Callable[[MCTuplesStepResult], None] | None = None,
) -> MCTuples:
    """Construct a nested Monte Carlo (u, v) tuple set up to `max_size` in about `t_total_sec` s.

    Size `k` of the set is its first `k` tuples. The construction runs 2 max-div solves per size, cell selection and
    then refinement, and splits `t_total_sec` over them:

    - each of the 2 steps gets a fixed share of the total;
    - within that share, the solve of each size gets 1 % of the total, plus a part of the rest in proportion to its
      number of candidate tuples, the tuples that max-div chooses from, times its size.

    From 60 s up, every solve uses all `n_workers` workers; below 60 s, the worker count scales down with the time,
    so that a short run does not spend its time starting workers.

    `t_total_sec` covers only the solves; other work takes extra time:

    - drawing each solve's random candidate tuples, and building each solve's problem;
    - checking each size;
    - compiling the solves' max-div functions, on their first run after an install; compiling them all takes
      seconds, and numba caches the compiled code for later runs.

    A rerun gives a set of equivalent quality, not the same set, because max-div's parallel solver
    runs on a wall-clock budget.

    Args:
        t_total_sec: The total wall-clock time of the solves, at least 1 s.
        n_workers: The number of max-div workers per solve when `t_total_sec` is 60 s or more; more workers search
            from more seeds, and may exceed the number of cores.
        seed: The seed of every random draw and of every max-div solve.
        max_size: The largest size to build, 1 of `MCTuplesSize`; every size up to it is built, however short
            `t_total_sec` is, so a short run that wants fewer sizes passes a smaller `max_size`.
        on_step_finished: Called after each of the 2 steps of every size with the step's result, e.g. to print
            the progress of a long construction or to store its tuples and solutions; None reports nothing. The
            result holds:

            - the size, the kind of step, the solve's budget and wall time, and max-div's solution with its score
              checkpoints;
            - the size's tuples after the step, as a `(size, 2)` array of (u, v) values, whose spread `MCTuplesStats`
              reports;
            - the selected cells after cell selection, or the size's tuples as `MCTuples` after refinement.

    Raises:
        ValueError: If `t_total_sec` is below 1 s, `n_workers` is below 1, or `max_size` is not 1 of `MCTuplesSize`.
        MCTuplesConstructionError: If a size misses a tuple of the size below it or does not hold exactly 1 tuple
            per lane, which can happen when `t_total_sec` is too short for max-div to meet its constraints.
    """
    generator = MCTuplesGenerator(n_workers=n_workers, seed=seed, on_step_finished=on_step_finished)
    return generator.generate(t_total_sec, max_size)
