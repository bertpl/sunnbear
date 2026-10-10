"""This package constructs the nested tuple set, in which each size includes the size below it.

The `generator` module documents the construction and names the module that implements each of its steps.
"""

from .exceptions import MCTuplesConstructionError
from .generator import MCTuplesGenerator, generate_mc_tuples
from .size_result import MCTuplesSizeResult
