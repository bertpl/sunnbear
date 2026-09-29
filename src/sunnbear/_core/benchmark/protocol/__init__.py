"""This package holds the benchmark protocol: the rules that every solve of a benchmark run follows.

- `compute_xtol_range` and `max_fevals_for` derive a solve's tolerance range and evaluation budget
  from bisection's evaluation count, `n_bisection_fevals`;
- `derive_seed` derives every seed of a run from its root seed;
- `is_solution_correct` judges whether a solver's answer lies within `xtol` of a root.
"""

from .correctness import CORRECTNESS_CHECK_MAX_FEVALS, is_solution_correct
from .seeds import SeedPurpose, derive_seed
from .tolerances import N_BISECTION_FEVALS, compute_xtol_range, max_fevals_for, validate_n_bisection_fevals
