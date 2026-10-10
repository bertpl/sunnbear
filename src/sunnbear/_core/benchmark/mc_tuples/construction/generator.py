"""`generate_mc_tuples` constructs a nested set of (u, v) tuples and corrects every size's means to 0.5.

The construction builds the sizes bottom-up, the smallest first, and each larger size includes the size below it, so
every size is a prefix of the next. Each axis is cut into `N_FINE_LANES` fine lanes, and no 2 tuples of the set share
a fine lane, so the largest size holds exactly 1 tuple per fine lane on each axis.

`MCTuplesGenerator` builds each size in 4 parts, each implemented in the module of this package named in parentheses:

1. it draws the size's population of candidate tuples over the fine lanes that the size below leaves free
   (`population`);
2. it allocates the new tuples to the gaps that the size below leaves on each axis, so that the size's predicted mean
   lies close to 0.5 (`allocation`);
3. One max-div solve picks the new tuples from the population (`solve`);
4. the mean correction moves the new tuples so that the size's mean u and mean v are exactly 0.5
   (`correction`).

`MCTuplesGenerator` passes each size's result (`size_result`) to the caller's `on_size_finished`, so that a
long construction can show its progress and store its tuples and max-div's solutions as it goes.
"""

import time
from collections.abc import Callable
from typing import ClassVar

import numpy as np

from sunnbear._core.benchmark.mc_tuples.core import MCTuples, MCTuplesSize

from .allocation import GapAllocation
from .correction import MeanCorrection
from .population import MCTuplesPopulation
from .size_result import MCTuplesSizeResult
from .solve import MCTuplesSizeSolve, MCTuplesSolveSettings


# ==================================================================================================
#  MCTuplesGenerator
# ==================================================================================================
class MCTuplesGenerator:
    """`MCTuplesGenerator` builds the nested tuple set size by size, 1 max-div solve per size, and reports every size.

    Attributes:
        n_workers: The number of max-div workers per solve when the total time is `MIN_T_TOTAL_AT_FULL_SCALE_SEC` or
            more; more workers search from more seeds, and may exceed the number of cores.
        seed: The seed of every random draw and of every max-div solve.
        n_population: The number of candidate tuples in each size's population.
        allocation_epsilon: The share in [0, 1) by which the allocation of new tuples to the gaps may shrink the
            smallest distance between neighboring values on an axis, to bring the predicted mean closer to 0.5
            (`AxisGaps.mean_aware_counts`).
        on_size_finished: Called with each size's result as soon as the size, its mean correction included, ends;
            None reports nothing.
    """

    MIN_T_BUDGET_FRACTION_PER_SOLVE: ClassVar[float] = 0.01
    MIN_T_TOTAL_SEC: ClassVar[float] = 1.0
    MIN_T_TOTAL_AT_FULL_SCALE_SEC: ClassVar[float] = 60.0

    def __init__(
        self,
        *,
        n_workers: int = 32,
        seed: int = 42,
        n_population: int = 2**20,
        allocation_epsilon: float = 0.1,
        on_size_finished: Callable[[MCTuplesSizeResult], None] | None = None,
    ) -> None:
        """Set the settings of every construction of this generator.

        Raises:
            ValueError: If `n_workers` or `n_population` is below 1, or `allocation_epsilon` lies outside [0, 1).
        """
        if n_workers < 1:
            raise ValueError(f"n_workers must be at least 1 (got {n_workers}).")
        if n_population < 1:
            raise ValueError(f"n_population must be at least 1 (got {n_population}).")
        if not 0 <= allocation_epsilon < 1:
            raise ValueError(f"allocation_epsilon must lie in [0, 1) (got {allocation_epsilon}).")
        self.n_workers = n_workers
        self.seed = seed
        self.n_population = n_population
        self.allocation_epsilon = allocation_epsilon
        self.on_size_finished = on_size_finished

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
            MCTuplesConstructionError: If a size cannot be built within its constraints, which can happen when
                `t_total_sec` is too short for max-div to meet them.
        """
        t_budget_per_solve_sec = self.t_budget_per_solve_sec(t_total_sec, max_size)
        settings = MCTuplesSolveSettings(
            n_workers=self.n_workers_for(t_total_sec), seed=self.seed, rng=np.random.default_rng(self.seed)
        )
        tuples: MCTuples | None = None
        for size in MCTuplesSize.up_to(max_size):
            result = self._build_size(size, tuples, t_budget_per_solve_sec[size], settings)
            if self.on_size_finished is not None:
                self.on_size_finished(result)
            tuples = result.tuples
        assert tuples is not None  # noqa: S101 -- MCTuplesSize.up_to never returns an empty tuple
        return tuples

    # --------------------------------------------------------------------------
    #  Workers and time per solve
    # --------------------------------------------------------------------------
    def n_workers_for(self, t_total_sec: float) -> int:
        """Return the worker count of a run of `t_total_sec`.

        From `MIN_T_TOTAL_AT_FULL_SCALE_SEC` up, the count is `n_workers`; below it, the count scales down in
        proportion to `t_total_sec`, to at least 1, so that a short run, such as a test, does not spend its time
        starting workers.
        """
        scale = min(1.0, t_total_sec / self.MIN_T_TOTAL_AT_FULL_SCALE_SEC)
        return max(1, round(scale * self.n_workers))

    def t_budget_per_solve_sec(self, t_total_sec: float, max_size: MCTuplesSize) -> dict[MCTuplesSize, float]:
        """Return the wall-clock budget of every size's solve in a run of `t_total_sec` up to `max_size`.

        Each solve gets `MIN_T_BUDGET_FRACTION_PER_SOLVE` of the total, so the solves of the smallest sizes, whose
        share of the work is tiny, still get time to run; the rest is split in proportion to the size times the
        solve's number of candidates, which is its population plus the tuples of the size below.

        Raises:
            ValueError: If `t_total_sec` is below `MIN_T_TOTAL_SEC`, or `max_size` is not 1 of `MCTuplesSize`.
        """
        if t_total_sec < self.MIN_T_TOTAL_SEC:
            raise ValueError(f"t_total_sec must be at least {self.MIN_T_TOTAL_SEC} s (got {t_total_sec}).")
        sizes = MCTuplesSize.up_to(max_size)
        t_min_per_solve_sec = self.MIN_T_BUDGET_FRACTION_PER_SOLVE * t_total_sec
        t_rest_sec = t_total_sec - len(sizes) * t_min_per_solve_sec
        work_per_size = {size: (self.n_population + size.n_required) * size for size in sizes}
        return {
            size: t_min_per_solve_sec + t_rest_sec * work / sum(work_per_size.values())
            for size, work in work_per_size.items()
        }

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _build_size(
        self, size: MCTuplesSize, required_tuples: MCTuples | None, t_budget_sec: float, settings: MCTuplesSolveSettings
    ) -> MCTuplesSizeResult:
        """Build `size` on `required_tuples` and return it.

        `required_tuples` holds the size below's tuples after their mean correction, or None for the smallest size.
        """
        t_start = time.perf_counter()
        required_tuple_array = required_tuples.tuple_array if required_tuples is not None else np.zeros((0, 2))
        n_new = size - size.n_required
        population = MCTuplesPopulation.draw_in_free_lanes(self.n_population, required_tuple_array, settings.rng)
        gap_allocation = GapAllocation.of(required_tuple_array, n_new, self.allocation_epsilon)
        solve = MCTuplesSizeSolve(population, required_tuple_array, size, gap_allocation, settings)
        new_tuple_array, solution = solve.run(t_budget_sec)
        uncorrected_tuple_array = np.vstack([required_tuple_array, new_tuple_array])
        return MCTuplesSizeResult(
            size=size,
            t_budget_sec=t_budget_sec,
            t_wall_sec=time.perf_counter() - t_start,
            gap_allocation=gap_allocation,
            uncorrected_tuple_array=uncorrected_tuple_array,
            mean_correction=MeanCorrection.of(uncorrected_tuple_array, size.n_required),
            solution=solution,
        )


# ==================================================================================================
#  generate_mc_tuples
# ==================================================================================================
def generate_mc_tuples(
    t_total_sec: float,
    *,
    n_workers: int = 32,
    seed: int = 42,
    max_size: MCTuplesSize = MCTuplesSize.SIZE_1024,
    n_population: int = 2**20,
    allocation_epsilon: float = 0.1,
    on_size_finished: Callable[[MCTuplesSizeResult], None] | None = None,
) -> MCTuples:
    """Construct a nested Monte Carlo (u, v) tuple set up to `max_size` in about `t_total_sec` s.

    Size `k` of the set is its first `k` tuples, and every size's mean u and mean v are 0.5 up to rounding, unless the
    mean correction cannot reach 0.5. Each axis is cut into as many equal fine lanes as the largest `MCTuplesSize`
    holds tuples, and no 2 tuples share a fine lane, so the largest size holds exactly 1 tuple per fine lane on each
    axis.

    Each size's new tuples come from 1 max-div solve over a random population of `n_population` candidate tuples; the
    solve maximizes the geomean of 3 values of gpq(0.1), the geometric pseudo-quantile at level 0.1, a soft minimum
    that `MCTuplesStats` reports: one over each tuple's distance to its nearest other tuple along u, one along v and
    one in squared L2.

    A correction then moves the new tuples to bring the size's means to 0.5.

    The construction splits `t_total_sec` over its solves: each size's solve gets 1 % of the total, plus a part of the
    rest in proportion to its size times its number of candidate tuples, which is the population plus the tuples of
    the size below.

    From 60 s up, every solve uses all `n_workers` workers; below 60 s, the worker count scales down with the time, so
    that a short run does not spend its time starting workers.

    `t_total_sec` covers only the solves; other work takes extra time:

    - drawing each size's population, allocating its new tuples to gaps, and building its problem;
    - checking and correcting each size;
    - compiling the solves' max-div functions, on their first run after an install; compiling them all takes
      seconds, and numba caches the compiled code for later runs.

    A rerun gives a set of equivalent quality, not the same set, because max-div's parallel solver runs on a
    wall-clock budget.

    Args:
        t_total_sec: The total wall-clock time of the solves, at least 1 s.
        n_workers: The number of max-div workers per solve when `t_total_sec` is 60 s or more; more workers search
            from more seeds, and may exceed the number of cores.
        seed: The seed of every random draw and of every max-div solve.
        max_size: The largest size to build, 1 of `MCTuplesSize`; every size up to it is built, however short
            `t_total_sec` is, so a short run that wants fewer sizes passes a smaller `max_size`.
        n_population: The number of candidate tuples of each size's population, at least 1.
        allocation_epsilon: The share in [0, 1) by which the allocation of new tuples to the gaps between the size
            below's tuples may shrink the smallest distance between neighboring values on an axis, to bring the
            predicted mean closer to 0.5 before the correction.
        on_size_finished: Called after every size with its `MCTuplesSizeResult`, e.g. to print the progress of a long
            construction or to store its tuples and solutions; None reports nothing.

    Raises:
        ValueError: If `t_total_sec` is below 1 s, `n_workers` or `n_population` is below 1, `allocation_epsilon`
            lies outside [0, 1), or `max_size` is not 1 of `MCTuplesSize`.
        MCTuplesConstructionError: If a size cannot be built within its constraints, which can happen when
            `t_total_sec` is too short for max-div to meet them.
    """
    generator = MCTuplesGenerator(
        n_workers=n_workers,
        seed=seed,
        n_population=n_population,
        allocation_epsilon=allocation_epsilon,
        on_size_finished=on_size_finished,
    )
    return generator.generate(t_total_sec, max_size)
