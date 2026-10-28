"""This package holds the Monte Carlo (MC) tuple set: the class, its construction, and the shipped artifact.

The MC tuples are the (u, v) tuples that every Monte Carlo benchmark run samples from.

- `MCTuples` holds a set of tuples, maps them onto a test problem, reports their spread as `MCTuplesStats`, and
  reports how many bits of information their values hold as `MCTuplesBitStats`;
- each axis is divided into `N_FINE_LANES` equal fine lanes, and `fine_lanes_of` returns the fine lane of each value;
  `MIN_N_BITS` is the fewest bits of information that `generate_mc_tuples` leaves in any value;
- `generate_mc_tuples` constructs a nested set that is symmetric under rotations by 90 degrees around (0.5, 0.5), so
  every size's means are 0.5 on both axes, with no 2 tuples in 1 fine lane. It delegates to `MCTuplesGenerator`, which
  runs 2 max-div solves per size (`construction`) and reports each size's `MCTuplesSizeResult`;
- `generate_mc_tuples` raises `MCTuplesConstructionError` when a size cannot meet its constraints;
- the `DEFAULT_*` constants hold the defaults of the arguments of `generate_mc_tuples`;
- `load_mc_tuples(size)` returns one size of the shipped set, 1 of `MCTuplesSize`; `MCTuplesDeclaration`
  declares the set as the data artifact `mc_tuples`.
"""

from .artifact import MCTuplesDeclaration, load_mc_tuples
from .construction import (
    DEFAULT_N_POPULATION,
    DEFAULT_N_REFINEMENT_RANDOM_CANDIDATES_PER_CELL,
    DEFAULT_N_WORKERS,
    DEFAULT_SEED,
    MCTuplesConstructionError,
    MCTuplesGenerator,
    MCTuplesSizeResult,
    generate_mc_tuples,
)
from .core import (
    MIN_N_BITS,
    N_FINE_LANES,
    MCTuples,
    MCTuplesBitStats,
    MCTuplesSize,
    MCTuplesStats,
    fine_lanes_of,
)
