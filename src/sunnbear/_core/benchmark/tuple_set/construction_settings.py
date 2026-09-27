"""`UvTuplesConstructionSettings` holds the settings of one tuple-set construction, derived from its total time.

From a total of 60 s up, the construction uses the full population and every requested worker, and
gives each tier (one solve per size) at least 10 s, about what a solve on the full population
needs to start optimizing. Below 60 s all three scale down together, so that short runs such as
tests still run a real construction; production runs are far longer and never scale.
"""

from dataclasses import dataclass
from typing import Self

from .tuples import UV_TUPLES_SIZES

FULL_POPULATION_SIZE = 65_536
# 2 candidates per tuple at the largest size keep the span constraints satisfiable.
MIN_POPULATION_SIZE = 2 * max(UV_TUPLES_SIZES)
MIN_T_TOTAL_SEC = 1.0
# From this total up, nothing scales down.
T_TOTAL_AT_FULL_SCALE_SEC = 60.0
MIN_T_BUDGET_PER_TIER_AT_FULL_SCALE_SEC = 10.0


# ==================================================================================================
#  UvTuplesConstructionSettings
# ==================================================================================================
@dataclass(frozen=True)
class UvTuplesConstructionSettings:
    """`UvTuplesConstructionSettings` holds the population size, worker count and time budget per tier of a construction.

    Attributes:
        population_size: The number of candidate tuples the construction selects from.
        n_workers: The number of max-div workers per solve.
        t_budget_per_tier_sec: The wall-clock budget of each size's solve, keyed by size.
    """

    population_size: int
    n_workers: int
    t_budget_per_tier_sec: dict[int, float]

    @classmethod
    def from_total_time(cls, t_total_sec: float, n_workers: int) -> Self:
        """Return the settings for a construction of `t_total_sec` seconds with up to `n_workers` workers.

        With `scale = min(1, t_total_sec / 60 s)`, the population size is
        `max(2048, scale · 65,536)` and the worker count `max(1, round(scale · n_workers))`. Each
        tier gets `scale · 10 s`, and the rest of the total is split in proportion to the size `k`.

        Raises:
            ValueError: If `t_total_sec` is below 1 s, or `n_workers` below 1.
        """
        if t_total_sec < MIN_T_TOTAL_SEC:
            raise ValueError(f"t_total_sec must be at least {MIN_T_TOTAL_SEC} s (got {t_total_sec}).")
        if n_workers < 1:
            raise ValueError(f"n_workers must be at least 1 (got {n_workers}).")
        scale = min(1.0, t_total_sec / T_TOTAL_AT_FULL_SCALE_SEC)
        min_t_budget_per_tier_sec = scale * MIN_T_BUDGET_PER_TIER_AT_FULL_SCALE_SEC
        t_rest_sec = t_total_sec - len(UV_TUPLES_SIZES) * min_t_budget_per_tier_sec
        return cls(
            population_size=max(MIN_POPULATION_SIZE, round(scale * FULL_POPULATION_SIZE)),
            n_workers=max(1, round(scale * n_workers)),
            t_budget_per_tier_sec={
                k: min_t_budget_per_tier_sec + t_rest_sec * k / sum(UV_TUPLES_SIZES) for k in UV_TUPLES_SIZES
            },
        )
