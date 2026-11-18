"""This module defines the exception raised when a (u, v) tuple set cannot be constructed."""

from sunnbear._core.exceptions import SunnbearError


class MCTuplesConstructionError(SunnbearError):
    """`MCTuplesConstructionError` is raised when `generate_mc_tuples` cannot build a size that meets its constraints.

    - the selection misses the dummy rotational sibling tuple or a base tuple of the size below;
    - after the selection solve, an LHS lane or a tile of the size does not hold exactly 1 tuple;
    - after the refinement solve, an LHS cell of the largest size that held a new base tuple does not hold exactly 1
      new base tuple.
    """
