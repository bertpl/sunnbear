"""This package holds the Monte Carlo (MC) tuple set: the class, its construction, and the shipped artifact.

The MC tuples are the (u, v) tuples that every Monte Carlo benchmark run samples from.

- `MCTuples` holds a set of tuples, maps them onto a test function, and reports their spread as
  `MCTuplesStats`;
- `generate_mc_tuples` constructs a nested set whose sizes have means of exactly 0.5 on both axes, with no 2 tuples
  in 1 fine lane. It delegates to `MCTuplesGenerator`, which runs 1 max-div solve and 1 mean correction per size
  (`construction`) and reports each size's `MCTuplesSizeResult`;
- `load_mc_tuples(size)` returns one size of the shipped set, 1 of `MCTuplesSize`; `MCTuplesDeclaration`
  declares the set as the data artifact `mc_tuples`.
"""

from .artifact import MCTuplesDeclaration, load_mc_tuples
from .construction import MCTuplesGenerator, generate_mc_tuples
from .construction_results import MCTuplesSizeResult
from .exceptions import MCTuplesConstructionError
from .sizes import N_FINE_LANES, MCTuplesSize
from .tuples import MCTuples, MCTuplesStats
