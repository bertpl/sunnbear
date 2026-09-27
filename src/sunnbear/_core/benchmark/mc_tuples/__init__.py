"""This package holds the (u, v) tuple set: the class, its construction, and the shipped artifact.

- `MCTuples` holds a set of tuples, maps them onto a test function, and reports their spread as
  `MCTuplesStats`;
- `generate_mc_tuples` constructs a nested set, with settings from `MCTuplesConstructionSettings`;
- `load_mc_tuples(size)` returns one size of the shipped set, which `MCTuplesDeclaration` declares as
  the data artifact `mc_tuples`.
"""

from .artifact import MCTuplesDeclaration, load_mc_tuples
from .construction import generate_mc_tuples
from .construction_settings import MCTuplesConstructionSettings
from .exceptions import MCTuplesConstructionError
from .tuples import MC_TUPLES_SIZES, MCTuples, MCTuplesStats
