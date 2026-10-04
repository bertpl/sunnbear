"""This package holds the Monte Carlo (MC) tuple set: the class, its construction, and the shipped artifact.

The MC tuples are the (u, v) tuples that every Monte Carlo benchmark run samples from.

- `MCTuples` holds a set of tuples, maps them onto a test function, and reports their spread as
  `MCTuplesStats`;
- `generate_mc_tuples` constructs a nested set that holds exactly 1 tuple per lane at every size, with the lanes as
  `LaneGrid` defines them. It delegates to `MCTuplesGenerator`, which runs 2 max-div steps per size
  (`construction_steps`) and reports each step's `MCTuplesStepResult`;
- `load_mc_tuples(size)` returns one size of the shipped set, 1 of `MCTuplesSize`; `MCTuplesDeclaration`
  declares the set as the data artifact `mc_tuples`.
"""

from .artifact import MCTuplesDeclaration, load_mc_tuples
from .construction import MCTuplesGenerator, generate_mc_tuples
from .construction_results import (
    MCTuplesCellSelectionResult,
    MCTuplesRefinementResult,
    MCTuplesStepKind,
    MCTuplesStepResult,
)
from .exceptions import MCTuplesConstructionError
from .sizes import MCTuplesSize
from .tuples import MCTuples, MCTuplesStats
