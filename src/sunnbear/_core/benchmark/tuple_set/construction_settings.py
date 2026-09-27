"""`UvTuplesConstructionSettings` holds the settings for constructing one tuple set, derived from its total time.

From a total of `MIN_T_TOTAL_AT_FULL_SCALE_SEC` up, the construction uses:

- the full population of `FULL_POPULATION_SIZE` candidates;
- every requested worker;
- at least `MIN_T_BUDGET_PER_SIZE_AT_FULL_SCALE_SEC` for each size's solve, about what a solve on
  the full population needs to start optimizing.

Below that total, the population size, the worker count and the minimum per size scale down
together, so that short runs such as tests still run a real construction; production runs are far
longer and never scale.
"""

from dataclasses import dataclass
from typing import Self

from .tuples import UV_TUPLES_SIZES

FULL_POPULATION_SIZE = 65_536
# A population of 2 candidates per tuple at the largest size keeps the span constraints satisfiable.
MIN_POPULATION_SIZE = 2 * max(UV_TUPLES_SIZES)
MIN_T_TOTAL_SEC = 1.0
MIN_T_TOTAL_AT_FULL_SCALE_SEC = 60.0
MIN_T_BUDGET_PER_SIZE_AT_FULL_SCALE_SEC = 10.0


# ==================================================================================================
#  UvTuplesConstructionSettings
# ==================================================================================================
@dataclass(frozen=True)
class UvTuplesConstructionSettings:
    """`UvTuplesConstructionSettings` holds a construction's population size, worker count and time per size.

    Attributes:
        population_size: The number of candidate tuples.
        n_workers: The number of max-div workers per solve.
        t_budget_per_size_sec: The wall-clock budget of each size's solve, keyed by size.
    """

    population_size: int
    n_workers: int
    t_budget_per_size_sec: dict[int, float]

    @classmethod
    def from_total_time(cls, t_total_sec: float, n_workers: int) -> Self:
        """Return the settings for a construction of `t_total_sec` seconds with up to `n_workers` workers.

        With `scale = min(1, t_total_sec / MIN_T_TOTAL_AT_FULL_SCALE_SEC)`, the population size is
        `max(MIN_POPULATION_SIZE, scale · FULL_POPULATION_SIZE)` and the worker count
        `max(1, round(scale · n_workers))`. Each size's solve gets
        `scale · MIN_T_BUDGET_PER_SIZE_AT_FULL_SCALE_SEC`, and the rest of the total is split in
        proportion to the size `k`.

        Raises:
            ValueError: If `t_total_sec` is below `MIN_T_TOTAL_SEC`, or `n_workers` below 1.
        """
        if t_total_sec < MIN_T_TOTAL_SEC:
            raise ValueError(f"t_total_sec must be at least {MIN_T_TOTAL_SEC} s (got {t_total_sec}).")
        if n_workers < 1:
            raise ValueError(f"n_workers must be at least 1 (got {n_workers}).")
        scale = min(1.0, t_total_sec / MIN_T_TOTAL_AT_FULL_SCALE_SEC)
        min_t_budget_per_size_sec = scale * MIN_T_BUDGET_PER_SIZE_AT_FULL_SCALE_SEC
        t_rest_sec = t_total_sec - len(UV_TUPLES_SIZES) * min_t_budget_per_size_sec
        return cls(
            population_size=max(MIN_POPULATION_SIZE, round(scale * FULL_POPULATION_SIZE)),
            n_workers=max(1, round(scale * n_workers)),
            t_budget_per_size_sec={
                k: min_t_budget_per_size_sec + t_rest_sec * k / sum(UV_TUPLES_SIZES) for k in UV_TUPLES_SIZES
            },
        )
