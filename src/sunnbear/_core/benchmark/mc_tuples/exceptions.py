"""This module defines the exception raised when a (u, v) tuple set cannot be constructed."""

from sunnbear._core.exceptions import SunnbearError


class MCTuplesConstructionError(SunnbearError):
    """`MCTuplesConstructionError` is raised when `generate_mc_tuples` selects constraint-breaking tuples.

    A selection breaks a constraint when it misses a tuple of the size below, holds a number of new tuples in a gap
    between the size below's fine lanes other than the gap's allocation, or holds 2 tuples in 1 fine lane.
    """
