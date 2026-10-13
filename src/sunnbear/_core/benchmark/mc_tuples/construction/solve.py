"""`MCTuplesSolve` is the base class of a size's 2 max-div solves: the selection and the refinement.

Each solve picks the size's new tuples from its own population of candidate tuples, and keeps the tuples of the size
below. The candidates of the max-div problem are the tuples of the size below, followed by the population.

The objective is the geomean of 3 gpq terms at `GPQ_LEVEL` over the nearest-neighbor separations: along u, along v
and in squared L2. Since gpq(d²) = gpq(d)², the L2 term weighs as much as the 2 axis terms together.

A subclass passes its population to the constructor, and its hooks set:

- the constraints on the new tuples (`_new_tuple_constraints`);
- the starting selection (`_initial_new_selection`);
- the check of the selection (`_check_new_selection`).

The `generator` module names the 2 subclasses and the order in which they run.

Besides the subclass's constraints, a weighted constraint keeps every tuple of the size below; this weighted constraint
outweighs the others, so max-div meets it first.

max-div satisfies its constraints before it raises the diversity score, so it finds a selection that meets every
constraint within its first iterations. A time budget that runs out before then leaves a constraint unmet, so `run`
checks max-div's selected tuples before it returns them.
"""

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
from max_div import Constraint, MaxDivProblem
from max_div.metrics import DistanceMetric, DiversityMetric, HybridDiversityMetric
from max_div.solver import (
    DistanceStorageType,
    ParallelMaxDivSolution,
    ParallelMaxDivSolverBuilder,
    ParallelSolvingWarning,
    Verbosity,
    seconds,
)

from sunnbear._core.benchmark.mc_tuples.core import GPQ_LEVEL, MCTuplesSize

from .exceptions import MCTuplesConstructionError
from .population import MCTuplesPopulation

# The constraint that keeps the tuples of the size below outweighs the other constraints, so max-div meets it first.
INCLUSION_CONSTRAINT_WEIGHT = 10.0


# ==================================================================================================
#  MCTuplesSolve
# ==================================================================================================
class MCTuplesSolve(ABC):
    """`MCTuplesSolve` is 1 max-div solve that picks the new tuples of 1 size from a population of candidates.

    Attributes:
        population: The solve's candidate tuples for the size's new tuples.
        required_tuple_array: The tuples of the size below, as an `(n, 2)` array; empty for the smallest size.
        size: The size under construction.
        settings: The construction's settings, the same for every max-div solve.
    """

    def __init__(
        self,
        population: MCTuplesPopulation,
        required_tuple_array: np.ndarray,
        size: MCTuplesSize,
        settings: "MCTuplesSolveSettings",
    ) -> None:
        """Set the solve's population, the size below, the size and the settings."""
        self.population = population
        self.required_tuple_array = required_tuple_array
        self.size = size
        self.settings = settings

    # --------------------------------------------------------------------------
    #  Main API
    # --------------------------------------------------------------------------
    def run(self, t_budget_sec: float) -> tuple[np.ndarray, ParallelMaxDivSolution]:
        """Run the solve within `t_budget_sec` and return the size's tuples and max-div's solution.

        Returns:
            The size's tuples, as a `(size, 2)` array of (u, v) values: the size below's tuples first, then the new
            tuples in ascending candidate order; and max-div's solution of the solve, with its score checkpoints and
            timeline.

        Raises:
            MCTuplesConstructionError: If the solve cannot form a starting selection, or its selection misses a tuple
                of the size below or breaks a constraint of the subclass, which can happen when `t_budget_sec` is too
                short for max-div to meet the constraints.
        """
        n_required = self.size.n_required
        gpq = DiversityMetric.gpq_separation(GPQ_LEVEL)
        problem = MaxDivProblem.new(
            # max-div works on a float32 copy; the selected candidates are taken by index.
            np.vstack([self.required_tuple_array, self.population.tuple_array]).astype(np.float32),
            k=int(self.size),
            distance_metric=DistanceMetric.l2s_euclidean_squared(),
            # The geomean of gpq along u, along v, and over the problem's own distance, squared L2.
            diversity_metric=HybridDiversityMetric.geomean_of(
                gpq.over(DistanceMetric.along_axis(0)), gpq.over(DistanceMetric.along_axis(1)), gpq
            ),
            constraints=self._constraints(),
        )
        initial_selection = np.concatenate([np.arange(n_required), n_required + self._initial_new_selection()])
        with warnings.catch_warnings():
            # max-div warns when a short run scales down to 1 worker, and when the workers outnumber the cores; both
            # are deliberate here (the second searches from more seeds).
            warnings.simplefilter("ignore", ParallelSolvingWarning)
            solver = (
                ParallelMaxDivSolverBuilder(problem)
                .with_seed(self.settings.seed)
                .with_workers(seconds(t_budget_sec), self.settings.n_workers)
                .with_end_to_end_budget()
                .with_initial_selection(initial_selection)
                # Every checkpoint also stores its selection, so the solution shows how the selection changed.
                .with_intermediate_selections()
                .with_distance_storage(DistanceStorageType.LAZY)
                .build()
            )
        solution = solver.solve(verbosity=Verbosity.SILENT)
        new = self._validated_new_selection(np.sort(np.asarray(solution.i_selected, dtype=np.int64)))
        return np.vstack([self.required_tuple_array, self.population.tuple_array[new]]), solution

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    @abstractmethod
    def _new_tuple_constraints(self) -> list[Constraint]:
        """Return the constraints on the new tuples, over the size below's tuples followed by the population."""

    @abstractmethod
    def _initial_new_selection(self) -> np.ndarray:
        """Return the starting selection of new candidates, ascending, as indices into the population."""

    @abstractmethod
    def _check_new_selection(self, new_selection: np.ndarray) -> None:
        """Raise `MCTuplesConstructionError` if `new_selection` breaks a constraint on the new tuples.

        `new_selection` holds the selected new candidates, as indices into the population.
        """

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _constraints(self) -> list[Constraint]:
        """Return the subclass's constraints and the weighted constraint that keeps the size below's tuples.

        The smallest size has no size below, so it gets only the subclass's constraints.
        """
        constraints = self._new_tuple_constraints()
        n_required = self.size.n_required
        if n_required > 0:
            constraints.append(
                Constraint(
                    int_set=set(range(n_required)),
                    min_count=n_required,
                    max_count=n_required,
                    weight=INCLUSION_CONSTRAINT_WEIGHT,
                )
            )
        return constraints

    def _validated_new_selection(self, selection: np.ndarray) -> np.ndarray:
        """Return the selected new candidates as indices into the population, after checking the constraints.

        Raises:
            MCTuplesConstructionError: If a tuple of the size below is missing, or the new candidates break a
                constraint of the subclass.
        """
        n_required = self.size.n_required
        n_missing = n_required - int((selection < n_required).sum())
        if n_missing > 0:
            raise MCTuplesConstructionError(
                f"Size {self.size}: {n_missing} tuples of the size below it are not selected."
            )
        new = selection[selection >= n_required] - n_required
        self._check_new_selection(new)
        return new


# ==================================================================================================
#  MCTuplesSolveSettings
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class MCTuplesSolveSettings:
    """`MCTuplesSolveSettings` holds what every max-div solve of a construction shares.

    Attributes:
        n_workers: The number of max-div workers of each solve.
        seed: The seed of each max-div solve.
        rng: The random generator of the construction's own draws: the populations and the starting selections.
    """

    n_workers: int
    seed: int
    rng: np.random.Generator
