"""This package constructs the nested tuple set: `generate_mc_tuples` and the `MCTuplesGenerator` behind it.

The `generator` module documents the construction and names the module of each of its parts. `MCTuplesSizeResult`
records how 1 size was built, and `MCTuplesConstructionError` is raised when a size cannot meet its constraints.
"""

from .exceptions import MCTuplesConstructionError
from .generator import MCTuplesGenerator, generate_mc_tuples
from .size_result import MCTuplesSizeResult
