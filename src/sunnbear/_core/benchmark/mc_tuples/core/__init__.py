"""This package holds the tuple set's building blocks, which the construction and the shipped artifact share.

- `MCTuples` holds a set of tuples and maps them onto a test function; `MCTuplesStats` reports their spread, with its
  gpq statistics at `GPQ_LEVEL`;
- `MCTuplesSize` lists the sizes of the shipped set; `N_FINE_LANES` and `fine_lanes_of` cut each axis into the fine
  lanes that follow from them.
"""

from .sizes import N_FINE_LANES, MCTuplesSize, fine_lanes_of
from .tuples import GPQ_LEVEL, MCTuples, MCTuplesStats
