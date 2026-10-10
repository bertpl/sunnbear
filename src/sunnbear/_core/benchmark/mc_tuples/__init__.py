"""This package holds the Monte Carlo (MC) tuple set: the class, its construction, and the shipped artifact.

The MC tuples are the (u, v) tuples that every Monte Carlo benchmark run samples from.

- `MCTuples` holds a set of tuples, maps them onto a test function, and reports their spread as
  `MCTuplesStats`;
- each axis is divided into `N_FINE_LANES` equal fine lanes, and `fine_lanes_of` returns the fine lane of each value;
  `TARGET_MEAN` is the mean to which the mean correction brings every size's u values and v values;
- `generate_mc_tuples` constructs a nested set and corrects every size's means to 0.5 on both axes, with no 2
  tuples in 1 fine lane. It delegates to `MCTuplesGenerator`, which runs 1 max-div solve and 1 mean correction per size
  (`construction`) and reports each size's `MCTuplesSizeResult`. The `DEFAULT_*` constants hold the defaults of the
  arguments of `generate_mc_tuples`, which raises `MCTuplesConstructionError` when a size cannot meet its constraints;
- `load_mc_tuples(size)` returns one size of the shipped set, 1 of `MCTuplesSize`; `MCTuplesDeclaration`
  declares the set as the data artifact `mc_tuples`.
"""

from .artifact import MCTuplesDeclaration, load_mc_tuples
from .construction import (
    DEFAULT_ALLOCATION_EPSILON,
    DEFAULT_N_POPULATION,
    DEFAULT_N_WORKERS,
    DEFAULT_SEED,
    MCTuplesConstructionError,
    MCTuplesGenerator,
    MCTuplesSizeResult,
    generate_mc_tuples,
)
from .core import N_FINE_LANES, TARGET_MEAN, MCTuples, MCTuplesSize, MCTuplesStats, fine_lanes_of
