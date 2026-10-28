"""This package holds the benchmark protocol: the rules that every solve of a benchmark run follows.

- `compute_xtol_range` and `max_fevals_for` derive a solve's tolerance range and evaluation budget
  from bisection's evaluation count, `n_bisection_fevals`, whose default in `run_benchmark` is
  `DEFAULT_N_BISECTION_FEVALS`; the budget is `MAX_FEVALS_FACTOR` times `n_bisection_fevals`;
- `MCSolveSettings` maps the tuples of a Monte Carlo tuple set onto the `xtol` and the ``c`` of a test problem's
  solves, with ``c`` within a `CRange`, and gives those solves their evaluation budget;
- `derive_seed` derives a seed per `SeedPurpose`, test problem and Monte Carlo sample from a root seed;
- `is_solution_correct` judges whether a solver's answer lies within `xtol` of a root.
"""

from .c_range import CRange
from .correctness import CORRECTNESS_CHECK_MAX_FEVALS, is_solution_correct
from .mc_solve_settings import MCSolveSettings
from .seeds import SeedPurpose, derive_seed
from .tolerances import (
    DEFAULT_N_BISECTION_FEVALS,
    MAX_FEVALS_FACTOR,
    compute_xtol_range,
    max_fevals_for,
    validate_n_bisection_fevals,
)
