"""`MCTuplesSolve` is the base class of a size's 2 max-div solves: the selection and the refinement.

A candidate of the max-div problem is a base tuple, which stands for its 4 tuples (`rotations`), so a size of `S`
tuples selects `S/4` base tuples. Each solve picks the size's new base tuples from its own population of candidates.
The candidates of the max-div problem are, in this order:

1. the placeholder (`distances`);
2. the size below's base tuples;
3. the population.

The objective is the geomean of 2 gpq terms at `GPQ_LEVEL` over the nearest-neighbor distances (`distances`):

- along the axes, with weight 2: one metric covers both axes, because the nearest-neighbor distances along u and
  along v are the same values;
- in squared L2, with weight 1.

The axis term stands for both u and v, so the weights make the objective that of 3 equal terms, along u, along v and in
squared L2.

A subclass passes its population to the constructor, and its hooks set:

- the constraints on the new base tuples (`_new_base_tuple_constraints`);
- the starting selection (`_initial_new_selection`);
- the check of the selection (`_check_new_selection`).

The `generator` module names the 2 subclasses and the order in which they run.

Besides the subclass's constraints, a weighted constraint keeps the placeholder and every base tuple of the size below
(`INCLUSION_CONSTRAINT_WEIGHT`).

max-div satisfies its constraints before it raises the diversity score, so it finds a selection that meets every
constraint within its first iterations. A time budget that runs out before then leaves a constraint unmet, so `run`
checks max-div's selected candidates before it returns them.
"""

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
from max_div import Constraint, MaxDivProblem
from max_div.metrics import DiversityMetric, HybridDiversityMetric
from max_div.solver import (
    DistanceStorageType,
    ParallelMaxDivSolution,
    ParallelMaxDivSolverBuilder,
    ParallelSolvingWarning,
    Verbosity,
    seconds,
)

from sunnbear._core.benchmark.mc_tuples.core import GPQ_LEVEL, MCTuplesSize

from .distances import BASE_TUPLE_SQUARED_L2_DISTANCE_METRIC, BASE_TUPLE_VALUE_DISTANCE_METRIC, PLACEHOLDER_TUPLE_ARRAY
from .exceptions import MCTuplesConstructionError
from .population import MCTuplesPopulation

# The constraint that keeps the placeholder and the size below outweighs the other constraints, so max-div meets it
# first.
INCLUSION_CONSTRAINT_WEIGHT = 10.0


# ==================================================================================================
#  MCTuplesSolve
# ==================================================================================================
class MCTuplesSolve(ABC):
    """`MCTuplesSolve` is 1 max-div solve that picks the new base tuples of 1 size from a population of candidates.

    Attributes:
        population: The solve's candidate base tuples for the size's new base tuples.
        required_base_tuple_array: The base tuples of the size below, as an `(n, 2)` array; empty for the smallest
            size.
        size: The size under construction, in tuples.
        settings: The construction's settings, the same for every max-div solve.
    """

    def __init__(
        self,
        population: MCTuplesPopulation,
        required_base_tuple_array: np.ndarray,
        size: MCTuplesSize,
        settings: "MCTuplesSolveSettings",
    ) -> None:
        """Set the solve's population, the size below's base tuples, the size and the settings."""
        self.population = population
        self.required_base_tuple_array = required_base_tuple_array
        self.size = size
        self.settings = settings

    @property
    def n_always_selected_candidates(self) -> int:
        """Return how many candidates every selection holds: the placeholder and the size below's base tuples."""
        return 1 + self.required_base_tuple_array.shape[0]

    @property
    def n_new_base_tuples(self) -> int:
        """Return the number of base tuples that the size adds, a quarter of its new tuples."""
        return self.size.n_new // 4

    # --------------------------------------------------------------------------
    #  Main API
    # --------------------------------------------------------------------------
    def run(self, t_budget_sec: float) -> tuple[np.ndarray, ParallelMaxDivSolution]:
        """Run the solve within `t_budget_sec` and return the size's base tuples and max-div's solution.

        Returns:
            The size's base tuples, as a `(size / 4, 2)` array: the size below's base tuples first, then the new base
            tuples in ascending candidate order; and max-div's solution of the solve, with its score checkpoints and
            timeline.

        Raises:
            MCTuplesConstructionError: If the solve cannot form a starting selection, or its selection misses the
                placeholder or a base tuple of the size below, or breaks a constraint of the subclass, which can happen
                when `t_budget_sec` is too short for max-div to meet the constraints.
        """
        gpq = DiversityMetric.gpq_separation(GPQ_LEVEL)
        problem = MaxDivProblem.new(
            # max-div works on a float32 copy; the selected candidates are taken by index.
            np.vstack(
                [PLACEHOLDER_TUPLE_ARRAY, self.required_base_tuple_array, self.population.base_tuple_array]
            ).astype(np.float32),
            k=self.n_always_selected_candidates + self.n_new_base_tuples,
            distance_metric=BASE_TUPLE_SQUARED_L2_DISTANCE_METRIC,
            # The weights (2, 1) make the objective that of 3 equal terms: along u, along v and in squared L2.
            diversity_metric=HybridDiversityMetric.geomean_of(
                gpq.over(BASE_TUPLE_VALUE_DISTANCE_METRIC), gpq, weights=(2.0, 1.0)
            ),
            constraints=self._constraints(),
        )
        initial_selection = np.concatenate(
            [
                np.arange(self.n_always_selected_candidates),
                self.n_always_selected_candidates + self._initial_new_selection(),
            ]
        )
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
        return np.vstack([self.required_base_tuple_array, self.population.base_tuple_array[new]]), solution

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    @abstractmethod
    def _new_base_tuple_constraints(self) -> list[Constraint]:
        """Return the constraints on the new base tuples, over the problem's candidates."""

    @abstractmethod
    def _initial_new_selection(self) -> np.ndarray:
        """Return the starting selection of new candidates, ascending, as indices into the population."""

    @abstractmethod
    def _check_new_selection(self, new_selection: np.ndarray) -> None:
        """Raise `MCTuplesConstructionError` if `new_selection` breaks a constraint on the new base tuples.

        `new_selection` holds the selected new candidates, as indices into the population.
        """

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _constraints(self) -> list[Constraint]:
        """Return the subclass's constraints, plus the weighted one that keeps the placeholder and the size below."""
        constraints = self._new_base_tuple_constraints()
        constraints.append(
            Constraint(
                int_set=set(range(self.n_always_selected_candidates)),
                min_count=self.n_always_selected_candidates,
                max_count=self.n_always_selected_candidates,
                weight=INCLUSION_CONSTRAINT_WEIGHT,
            )
        )
        return constraints

    def _validated_new_selection(self, selection: np.ndarray) -> np.ndarray:
        """Return the selected new candidates as indices into the population, after checking the constraints.

        Raises:
            MCTuplesConstructionError: If the placeholder or a base tuple of the size below is missing, or the new
                candidates break a constraint of the subclass.
        """
        n_missing = self.n_always_selected_candidates - int((selection < self.n_always_selected_candidates).sum())
        if n_missing > 0:
            raise MCTuplesConstructionError(
                f"Size {self.size}: {n_missing} of the placeholder and the size below's base tuples are not selected."
            )
        new = selection[selection >= self.n_always_selected_candidates] - self.n_always_selected_candidates
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
